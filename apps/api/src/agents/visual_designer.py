from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent

_SYSTEM_PROMPT = """\
你是一位专业的小红书视觉设计专家「视觉设计师」，擅长卡通插画风格的内容创作。

## 核心设计原则

**保持产品真实，卡通化场景** — 这是你最重要的创作原则：
- 产品本身必须保持真实、准确的外观描述
- 产品所处的场景、背景、装饰元素使用卡通插画风格
- 产品与卡通场景自然融合，不突兀

## 核心能力

1. **封面设计**：创作吸引眼球的封面图方案，包含：
   - 场景描述：产品所在的卡通化场景
   - 产品放置：产品在画面中的位置和展示方式
   - 风格说明：具体的视觉风格指导
   - 文字覆盖：封面上的文字排版方案
   - 英文图像提示词：供图像生成模型使用的详细英文prompt

2. **轮播图设计**：为笔记创作3张差异化的轮播图方案

## 输出要求

始终以JSON格式输出：
```json
{
  "cover_brief": {
    "scene_description": "场景描述（中文）",
    "product_placement": "产品放置方式",
    "style_notes": "视觉风格详细说明",
    "text_overlay": {
      "main_text": "主标题文字",
      "sub_text": "副标题文字",
      "text_position": "文字位置",
      "text_style": "文字样式"
    },
    "image_prompt": "Detailed English prompt for image generation model. Must describe the scene, style, product placement, lighting, color palette, and composition. Start with the style descriptor.",
    "negative_prompt": "English negative prompt for image generation (what to avoid)"
  },
  "carousel_briefs": [
    {
      "slide_number": 1,
      "purpose": "这张轮播图的目的",
      "scene_description": "场景描述（中文）",
      "product_placement": "产品放置方式",
      "style_notes": "视觉风格说明",
      "text_overlay": {
        "main_text": "主文字",
        "sub_text": "副文字"
      },
      "image_prompt": "Detailed English prompt for this slide",
      "negative_prompt": "English negative prompt"
    }
  ],
  "style_guide": {
    "color_palette": ["#hex1", "#hex2", "#hex3"],
    "overall_mood": "整体氛围",
    "consistency_notes": "保持视觉一致性的注意事项"
  }
}
```

## 规则
- image_prompt必须使用英文，且足够详细供图像生成模型使用
- 产品描述必须真实准确，不得卡通化产品本身
- 轮播图之间要有视觉叙事逻辑
- 封面图必须具有强烈的停留吸引力（thumb-stopping power）
- 文字排版要考虑手机屏幕阅读体验
- 颜色方案要与选定的视觉风格一致
"""


class VisualDesignerAgent(BaseAgent):
    """Creates image generation briefs with cartoon-contextualised product visuals."""

    role_key = "cartoon_visual_designer"
    display_name = "视觉设计师"

    async def execute(self, ctx: AgentContext) -> AgentResult:
        if not ctx.strategy_plan:
            return AgentResult(
                success=False,
                error="缺少策略方案，无法生成视觉设计方案",
            )

        system_prompt = self._build_system_prompt(ctx)
        user_prompt = self._build_user_prompt(ctx)

        try:
            result = await self._llm.chat_completion_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.8,
                max_tokens=4096,
            )
        except Exception as exc:
            self._logger.error("LLM call failed: %s", exc, exc_info=True)
            return AgentResult(
                success=False,
                error=f"视觉设计LLM调用失败: {exc}",
            )

        content = result["content"]
        if content.get("parse_error"):
            self._logger.warning("LLM returned unparseable JSON for visual design")
            return AgentResult(
                success=False,
                output=content,
                error="视觉设计返回了无法解析的JSON",
                token_usage=result["usage"],
            )

        required_keys = {"cover_brief", "carousel_briefs"}
        missing = required_keys - set(content.keys())
        if missing:
            self._logger.warning("Visual design missing keys: %s", missing)
            return AgentResult(
                success=False,
                output=content,
                error=f"视觉设计缺少必要字段: {', '.join(missing)}",
                token_usage=result["usage"],
            )

        ctx.visual_assets = content

        return AgentResult(
            success=True,
            output=content,
            token_usage=result["usage"],
        )

    def _get_role_prompt(self) -> str:
        return _SYSTEM_PROMPT

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def _build_user_prompt(self, ctx: AgentContext) -> str:
        parts: list[str] = []

        # Strategy plan
        plan = ctx.strategy_plan
        parts.append("## 内容策略方案")
        parts.append(f"- 视觉风格：{plan.get('style_family', '未指定')}")
        parts.append(f"- 营销目标：{plan.get('objective', '未指定')}")
        parts.append(f"- CTA类型：{plan.get('cta_type', '未指定')}")

        persona = plan.get("persona", {})
        if isinstance(persona, dict):
            parts.append(f"- 目标受众：{persona.get('description', '未指定')}")
        elif isinstance(persona, str):
            parts.append(f"- 目标受众：{persona}")

        angles = plan.get("message_angles", [])
        if angles:
            parts.append("\n## 内容角度（视觉需呼应文案角度）")
            for angle in angles:
                aid = angle.get("angle_id", "?")
                theme = angle.get("theme", "")
                parts.append(f"角度{aid}：{theme}")

        # Product info
        parts.append("\n## 产品信息")
        parts.append(f"- 产品名称：{ctx.product_name or '未知'}")
        parts.append(f"- 产品分类：{ctx.product_category or '未知'}")
        if ctx.product_description:
            parts.append(f"- 产品外观描述：{ctx.product_description[:600]}")

        # Asset references
        if ctx.asset_urls:
            parts.append("\n## 已有素材参考")
            for i, url in enumerate(ctx.asset_urls[:5], 1):
                parts.append(f"{i}. {url}")

        # Note content for cover text
        if ctx.note_content:
            titles = ctx.note_content.get("title_variants", [])
            if titles:
                parts.append("\n## 笔记标题参考（用于封面文字）")
                for t in titles:
                    parts.append(f"- {t.get('title', '')}")
            cover_suggestions = ctx.note_content.get("cover_text_suggestions", [])
            if cover_suggestions:
                parts.append("\n## 文案建议的封面文字")
                for s in cover_suggestions:
                    parts.append(f"- 主：{s.get('main_text', '')}  副：{s.get('sub_text', '')}")

        parts.append("\n请根据以上信息，创作封面图和3张轮播图的视觉设计方案，以JSON格式返回。")
        return "\n".join(parts)
