from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.base import AgentContext, AgentResult
from src.agents.compliance_reviewer import ComplianceReviewerAgent
from src.agents.founder_copilot import FounderCopilotAgent
from src.agents.llm_client import llm_client
from src.agents.note_writer import NoteWriterAgent
from src.agents.strategy_planner import StrategyPlannerAgent
from src.agents.visual_designer import VisualDesignerAgent
from src.core.config import settings
from src.core.storage import storage
from src.models import (
    Asset,
    AssetPack,
    GenerationJob,
    GenerationTask,
    ImageAsset,
    Merchant,
    MerchantRules,
    NotePackage,
    Product,
    TextAsset,
)
from src.services import (
    analytics_service,
    fatigue_service,
    image_generation_service,
    image_render_service,
)

logger = logging.getLogger(__name__)


class GenerationOrchestrator:
    """Orchestrates the agent pipeline for content generation.

    Pipeline: Founder Copilot -> Strategy Planner -> [Note Writer || Visual Designer] -> Compliance Reviewer
    """

    def __init__(self) -> None:
        self.copilot = FounderCopilotAgent(llm_client=llm_client)
        self.planner = StrategyPlannerAgent(llm_client=llm_client)
        self.writer = NoteWriterAgent(llm_client=llm_client)
        self.designer = VisualDesignerAgent(llm_client=llm_client)
        self.compliance = ComplianceReviewerAgent(llm_client=llm_client)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run_on_demand(
        self,
        db: AsyncSession,
        merchant_id: UUID,
        product_id: UUID | None = None,
        user_message: str = "",
        objective: str = "seeding",
        persona: str = "",
        style_preference: str = "",
        special_instructions: str = "",
        is_juguang: bool = False,
        is_pugongying: bool = False,
        job_id: UUID | None = None,
    ) -> dict:
        """Run the full on-demand generation pipeline.

        Returns dict with generation_job_id, note_package data, and pipeline_log.
        """
        ctx = await self._build_context(
            db,
            merchant_id,
            product_id,
            user_message,
            objective,
            persona,
            style_preference,
            special_instructions,
        )

        if job_id is not None:
            job = await db.get(GenerationJob, job_id)
            if not job:
                return {"error": "Generation job not found"}
            if job.merchant_id != merchant_id:
                return {"error": "Job does not belong to this merchant"}
            if job.status != "pending":
                return {"error": f"Job is not pending (status={job.status})"}
            job.status = "running"
            await db.flush()
        else:
            job = GenerationJob(
                merchant_id=merchant_id,
                source_mode="on_demand",
                trigger_type="user_request",
                status="running",
            )
            db.add(job)
            await db.flush()
        ctx.job_id = job.id

        pipeline_log: list[dict] = []

        try:
            # Step 1 — Founder Copilot (only for free-text input)
            if user_message and not ctx.structured_job:
                copilot_result = await self._run_agent_task(
                    db, job.id, self.copilot, ctx, "strategy", "founder_copilot"
                )
                pipeline_log.append({"agent": "founder_copilot", "success": copilot_result.success})
                if not copilot_result.success:
                    return await self._fail_job(db, job, pipeline_log, copilot_result.error or "Copilot failed")
                # Propagate user-facing response into structured_job for the return value
                if copilot_result.output.get("response_to_user"):
                    ctx.structured_job["response_to_user"] = copilot_result.output["response_to_user"]
            else:
                ctx.structured_job = {
                    "product_id": str(product_id) if product_id else None,
                    "product_name": ctx.product_name,
                    "product_category": ctx.product_category,
                    "product_description": ctx.product_description,
                    "objective": objective,
                    "persona": persona,
                    "style_preference": style_preference,
                    "special_instructions": special_instructions,
                    "is_juguang": is_juguang,
                    "is_pugongying": is_pugongying,
                }

            # Step 2 — Strategy Planner
            planner_result = await self._run_agent_task(
                db, job.id, self.planner, ctx, "strategy", "strategy_planner"
            )
            pipeline_log.append({"agent": "strategy_planner", "success": planner_result.success})
            if not planner_result.success:
                return await self._fail_job(db, job, pipeline_log, planner_result.error or "Planner failed")

            # Step 3 — Note Writer then Visual Designer (sequential: shared session cannot flush concurrently)
            writer_result = await self._run_agent_task(
                db, job.id, self.writer, ctx, "text_gen", "xhs_note_writer"
            )
            designer_result = await self._run_agent_task(
                db, job.id, self.designer, ctx, "image_gen", "cartoon_visual_designer"
            )

            pipeline_log.append({"agent": "xhs_note_writer", "success": writer_result.success})
            pipeline_log.append({"agent": "cartoon_visual_designer", "success": designer_result.success})

            if not writer_result.success:
                return await self._fail_job(db, job, pipeline_log, writer_result.error or "Writer failed")

            # Step 4 — Compliance Reviewer
            compliance_result = await self._run_agent_task(
                db, job.id, self.compliance, ctx, "compliance", "compliance_reviewer"
            )
            pipeline_log.append({"agent": "compliance_reviewer", "success": compliance_result.success})

            # Step 5 — Persist note package (requires product_id)
            note_package_data: dict = {}
            if product_id:
                note_package = await self._persist_note_package(
                    db, ctx, job.id, merchant_id, product_id
                )
                note_package_data = {"note_package_id": str(note_package.id)}

            # Step 6 — Mark job complete
            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()

            return {
                "generation_job_id": str(job.id),
                **note_package_data,
                "note_content": ctx.note_content,
                "visual_assets": ctx.visual_assets,
                "compliance_report": ctx.compliance_report,
                "strategy_plan": ctx.strategy_plan,
                "pipeline_log": pipeline_log,
                "response_to_user": ctx.structured_job.get("response_to_user", ""),
            }

        except Exception as e:
            logger.exception("Pipeline error for merchant %s", merchant_id)
            return await self._fail_job(db, job, pipeline_log, str(e))

    async def run_daily_product(
        self,
        db: AsyncSession,
        merchant_id: UUID,
        product_id: UUID,
        objective: str = "seeding",
    ) -> dict:
        """
        Run pipeline for daily-auto mode: no Copilot, structured_job from product.
        Returns same shape as run_on_demand (generation_job_id, note_package_id, etc.).
        """
        ctx = await self._build_context(
            db, merchant_id, product_id,
            user_message="",
            objective=objective,
            persona="",
            style_preference="",
            special_instructions="",
        )
        # Build structured_job from product for planner
        product = await db.get(Product, product_id)
        if not product:
            return {"error": "Product not found"}
        ctx.structured_job = {
            "product_id": str(product_id),
            "product_name": product.name,
            "product_category": product.category or "",
            "product_description": product.description or "",
            "objective": objective,
            "persona": "",
            "style_preference": "",
            "special_instructions": "",
            "is_juguang": False,
            "is_pugongying": False,
        }

        # BL-204: Inject performance summary and fatigue for strategy diversification
        try:
            perf = await analytics_service.get_product_performance(db, product_id)
            ctx.performance_summary = (
                f"近30日表现：曝光{perf.get('total_impressions', 0)}，"
                f"点击{perf.get('total_clicks', 0)}，收藏{perf.get('total_saves', 0)}，"
                f"转化{perf.get('total_conversions', 0)}。"
            )
        except Exception:
            ctx.performance_summary = ""
        try:
            fatigue_data = await fatigue_service.get_product_fatigue(db, product_id)
            ctx.fatigue_signals = fatigue_data.get("dimensions", [])
        except Exception:
            ctx.fatigue_signals = []

        job = GenerationJob(
            merchant_id=merchant_id,
            source_mode="daily_auto",
            trigger_type="scheduler",
            status="running",
        )
        db.add(job)
        await db.flush()
        ctx.job_id = job.id
        pipeline_log: list[dict] = []

        try:
            # Planner
            planner_result = await self._run_agent_task(
                db, job.id, self.planner, ctx, "strategy", "strategy_planner"
            )
            pipeline_log.append({"agent": "strategy_planner", "success": planner_result.success})
            if not planner_result.success:
                return await self._fail_job(db, job, pipeline_log, planner_result.error or "Planner failed")

            writer_task = self._run_agent_task(
                db, job.id, self.writer, ctx, "text_gen", "xhs_note_writer"
            )
            designer_task = self._run_agent_task(
                db, job.id, self.designer, ctx, "image_gen", "cartoon_visual_designer"
            )
            writer_result, designer_result = await asyncio.gather(writer_task, designer_task)
            pipeline_log.append({"agent": "xhs_note_writer", "success": writer_result.success})
            pipeline_log.append({"agent": "cartoon_visual_designer", "success": designer_result.success})
            if not writer_result.success:
                return await self._fail_job(db, job, pipeline_log, writer_result.error or "Writer failed")

            compliance_result = await self._run_agent_task(
                db, job.id, self.compliance, ctx, "compliance", "compliance_reviewer"
            )
            pipeline_log.append({"agent": "compliance_reviewer", "success": compliance_result.success})

            note_package = await self._persist_note_package(
                db, ctx, job.id, merchant_id, product_id, source_mode="daily_auto"
            )
            await db.flush()

            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()

            return {
                "generation_job_id": str(job.id),
                "note_package_id": str(note_package.id),
                "pipeline_log": pipeline_log,
            }
        except Exception as e:
            logger.exception("Daily pipeline error for product %s", product_id)
            return await self._fail_job(db, job, pipeline_log, str(e))

    # ------------------------------------------------------------------
    # Context building
    # ------------------------------------------------------------------

    async def _build_context(
        self,
        db: AsyncSession,
        merchant_id: UUID,
        product_id: UUID | None,
        user_message: str,
        objective: str,
        persona: str,
        style_preference: str,
        special_instructions: str,
    ) -> AgentContext:
        """Load merchant/product data and build the initial agent context."""
        ctx = AgentContext(merchant_id=merchant_id, product_id=product_id)
        ctx.user_message = user_message

        merchant = await db.get(Merchant, merchant_id)
        if merchant:
            ctx.merchant_name = merchant.name
            ctx.merchant_industry = merchant.industry

        rules_stmt = select(MerchantRules).where(MerchantRules.merchant_id == merchant_id)
        rules_result = await db.execute(rules_stmt)
        rules = rules_result.scalar_one_or_none()
        if rules:
            ctx.merchant_rules = {
                "tone_preset": rules.tone_preset or "",
                "banned_words": rules.banned_words or [],
                "required_claims": rules.required_claims or [],
                "banned_claims": rules.banned_claims or [],
                "compliance_level": rules.compliance_level,
            }

        if product_id:
            product = await db.get(Product, product_id)
            if product:
                ctx.product_name = product.name
                ctx.product_category = product.category
                ctx.product_description = product.description or ""

        if product_id:
            pack_stmt = select(AssetPack).where(
                AssetPack.merchant_id == merchant_id,
                AssetPack.status == "active",
            )
            pack_result = await db.execute(pack_stmt)
            pack = pack_result.scalar_one_or_none()
            if pack:
                asset_stmt = select(Asset).where(
                    Asset.asset_pack_id == pack.id,
                    Asset.approval_status == "approved",
                )
                asset_result = await db.execute(asset_stmt)
                assets = asset_result.scalars().all()
                ctx.asset_urls = [a.storage_url for a in assets if a.storage_url]

        return ctx

    # ------------------------------------------------------------------
    # Agent task runner
    # ------------------------------------------------------------------

    async def _run_agent_task(
        self,
        db: AsyncSession,
        job_id: UUID,
        agent,
        ctx: AgentContext,
        task_type: str,
        agent_role: str,
    ) -> AgentResult:
        """Run a single agent and record it as a GenerationTask."""
        task = GenerationTask(
            job_id=job_id,
            task_type=task_type,
            agent_role=agent_role,
            status="running",
            input_json={"context_summary": f"Running {agent_role}"},
        )
        db.add(task)
        await db.flush()

        result = await agent.execute(ctx)

        task.status = "completed" if result.success else "failed"
        task.output_json = result.output if result.success else {"error": result.error}
        task.completed_at = datetime.now(timezone.utc)
        await db.flush()

        return result

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    async def _persist_note_package(
        self,
        db: AsyncSession,
        ctx: AgentContext,
        job_id: UUID,
        merchant_id: UUID,
        product_id: UUID,
        source_mode: str = "on_demand",
    ) -> NotePackage:
        """Create NotePackage and child TextAsset / ImageAsset records."""
        compliance = ctx.compliance_report or {}
        strategy = ctx.strategy_plan or {}

        compliance_status = compliance.get("status", "pending")
        if compliance_status == "failed":
            review_status = "rejected"
        else:
            review_status = "pending"

        persona_value = strategy.get("persona", "")
        if isinstance(persona_value, dict):
            persona_value = persona_value.get("description", "")

        package = NotePackage(
            merchant_id=merchant_id,
            product_id=product_id,
            generation_job_id=job_id,
            source_mode=source_mode,
            objective=strategy.get("objective", "seeding"),
            persona=persona_value or "",
            style_family=strategy.get("style_family", ""),
            compliance_status=compliance_status,
            ranking_score=float(compliance.get("confidence", 0.5)),
            review_status=review_status,
        )
        db.add(package)
        await db.flush()

        # --- Text Assets ---
        note = ctx.note_content or {}

        for i, title in enumerate(note.get("title_variants", []), 1):
            text = title.get("title", title) if isinstance(title, dict) else str(title)
            db.add(TextAsset(
                note_package_id=package.id,
                asset_role="title",
                content=text,
                version=i,
            ))

        for i, body in enumerate(note.get("body_variants", []), 1):
            body_text = body.get("body", body) if isinstance(body, dict) else str(body)
            db.add(TextAsset(
                note_package_id=package.id,
                asset_role="body",
                content=body_text,
                version=i,
            ))

        first_comment = note.get("first_comment", "")
        if first_comment:
            db.add(TextAsset(
                note_package_id=package.id,
                asset_role="first_comment",
                content=first_comment,
            ))

        for tag in note.get("hashtags", []):
            db.add(TextAsset(
                note_package_id=package.id,
                asset_role="hashtag",
                content=tag,
            ))

        for cover_text in note.get("cover_text_suggestions", []):
            text = cover_text
            if isinstance(cover_text, dict):
                main = cover_text.get("main_text", "")
                sub = cover_text.get("sub_text", "")
                text = f"{main} | {sub}" if sub else main
            db.add(TextAsset(
                note_package_id=package.id,
                asset_role="cover_text",
                content=text,
            ))

        # --- Image Assets (briefs only — actual images generated later) ---
        visual = ctx.visual_assets or {}

        cover_brief = visual.get("cover_brief", {})
        if cover_brief:
            db.add(ImageAsset(
                note_package_id=package.id,
                asset_role="cover",
                prompt_version="v1",
                image_url="",
                metadata_json=cover_brief,
            ))

        for i, carousel_brief in enumerate(visual.get("carousel_briefs", []), 1):
            db.add(ImageAsset(
                note_package_id=package.id,
                asset_role=f"carousel_{i}",
                prompt_version="v1",
                image_url="",
                metadata_json=carousel_brief,
            ))

        await db.flush()
        await self._hydrate_image_assets(
            db,
            package,
            merchant_id,
            note,
            visual,
            strategy,
            product_name=ctx.product_name,
        )
        await db.flush()
        return package

    async def _hydrate_image_assets(
        self,
        db: AsyncSession,
        package: NotePackage,
        merchant_id: UUID,
        note: dict,
        visual: dict,
        strategy: dict,
        product_name: str | None = None,
    ) -> None:
        """Upload cover/carousel images: OpenAI Images when enabled, else placeholder PNGs."""
        img_stmt = select(ImageAsset).where(ImageAsset.note_package_id == package.id)
        assets = list((await db.execute(img_stmt)).scalars().all())
        titles = note.get("title_variants") or []
        headline = ""
        if titles:
            t0 = titles[0]
            headline = t0.get("title", t0) if isinstance(t0, dict) else str(t0)
        headline = (headline or "笔记封面")[:80]
        subtitle = str(strategy.get("style_family") or visual.get("style_family") or "封面预览")

        pack_key = f"gen/{package.id.hex[:8]}"
        for ia in assets:
            if (ia.image_url or "").strip():
                continue
            meta = ia.metadata_json if isinstance(ia.metadata_json, dict) else {}
            size = (
                settings.image_gen_size_cover
                if ia.asset_role == "cover"
                else settings.image_gen_size_carousel
            )
            prompt, neg = image_generation_service.prompt_from_brief(meta, ia.asset_role)
            if product_name and product_name.strip():
                pn = product_name.strip()
                if pn.lower() not in prompt.lower():
                    prompt = f"Product: {pn}. {prompt}"

            png = await image_generation_service.generate_image_bytes(
                prompt=prompt,
                negative=neg,
                size=size,
            )
            if not png:
                h1, h2 = image_render_service.headline_from_visual_metadata(meta)
                line1 = h1 if ia.asset_role != "cover" else headline
                line2 = h2 if ia.asset_role != "cover" else subtitle
                png = image_render_service.render_note_visual_placeholder(
                    headline=line1,
                    subtitle=f"{line2} · {ia.asset_role}",
                )

            url = await storage.upload_file(
                file_content=png,
                content_type="image/png",
                merchant_id=str(merchant_id),
                asset_pack_id=pack_key,
                original_filename=f"{ia.asset_role}.png",
            )
            ia.image_url = url

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    async def _fail_job(
        self,
        db: AsyncSession,
        job: GenerationJob,
        pipeline_log: list[dict],
        error_message: str,
    ) -> dict:
        """Mark job as failed and return error result."""
        job.status = "failed"
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()
        return {
            "generation_job_id": str(job.id),
            "error": error_message,
            "pipeline_log": pipeline_log,
        }


orchestrator = GenerationOrchestrator()
