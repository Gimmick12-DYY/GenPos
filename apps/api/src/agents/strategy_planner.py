from __future__ import annotations

import json

from .base import AgentContext, AgentResult, BaseAgent

_SYSTEM_PROMPT = """\
你是一位资深的小红书内容策略专家「策略规划师」。你的核心职责是根据产品信息、目标受众和营销目标，制定最优的小红书内容创作策略。

## 核心能力

1. **受众洞察**：深入分析目标受众的痛点、需求和内容偏好
2. **内容角度**：为每个产品设计3个差异化的内容切入角度
3. **风格选择**：从平台验证的视觉风格库中选择最适合的风格
4. **合规前置**：在策略阶段就预判合规风险并设置安全规则
5. **CTA优化**：根据营销目标推荐最有效的行动号召类型

## 可选视觉风格库

根据产品和受众特征，从以下经过平台验证的风格中选择：
- `治愈系插画`：温暖柔和，适合美妆护肤、健康食品
- `轻漫画分镜`：叙事感强，适合场景化种草、使用教程
- `可爱Q版生活场景`：亲和力强，适合日用品、母婴、宠物
- `手账贴纸风`：清新文艺，适合文具、饰品、生活好物
- `极简软萌插画`：简洁高级，适合科技产品、轻奢品

## 输出要求

始终以JSON格式输出：
```json
{
  "objective": "seeding | conversion | awareness | engagement",
  "persona": {
    "description": "目标受众详细画像",
    "age_range": "年龄段",
    "interests": ["兴趣标签"],
    "pain_points": ["痛点"],
    "content_preferences": ["内容偏好"]
  },
  "message_angles": [
    {
      "angle_id": 1,
      "theme": "角度主题",
      "hook": "吸引力钩子",
      "value_proposition": "核心价值主张",
      "tone": "语调描述"
    }
  ],
  "style_family": "从视觉风格库中选择",
  "cta_type": "收藏 | 关注 | 评论 | 私信 | 购买链接",
  "safety_rules": {
    "must_include": ["必须包含的声明"],
    "must_avoid": ["必须避免的内容"],
    "tone_guardrails": ["语调护栏"]
  },
  "reasoning": "策略制定的推理过程"
}
```

## 规则
- 每个message_angle必须有差异化的切入点，不能雷同
- style_family必须从指定的视觉风格库中选择
- safety_rules必须结合商家合规规则和行业通用规则
- 始终考虑小红书平台的算法偏好和社区规范
"""


class StrategyPlannerAgent(BaseAgent):
    """Analyses product/audience data and produces a creative strategy plan."""

    role_key = "strategy_planner"
    display_name = "策略规划师"

    async def execute(self, ctx: AgentContext) -> AgentResult:
        system_prompt = self._build_system_prompt(ctx)
        user_prompt = self._build_user_prompt(ctx)

        try:
            result = await self._llm.chat_completion_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=3072,
            )
        except Exception as exc:
            self._logger.error("LLM call failed: %s", exc, exc_info=True)
            return AgentResult(
                success=False,
                error=f"策略规划LLM调用失败: {exc}",
            )

        content = result["content"]
        if content.get("parse_error"):
            self._logger.warning("LLM returned unparseable JSON for strategy plan")
            return AgentResult(
                success=False,
                output=content,
                error="策略规划返回了无法解析的JSON",
                token_usage=result["usage"],
            )

        required_keys = {"objective", "persona", "message_angles", "style_family", "cta_type"}
        missing = required_keys - set(content.keys())
        if missing:
            self._logger.warning("Strategy plan missing keys: %s", missing)
            return AgentResult(
                success=False,
                output=content,
                error=f"策略方案缺少必要字段: {', '.join(missing)}",
                token_usage=result["usage"],
            )

        ctx.strategy_plan = content

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

        parts.append("## 生成任务")
        job = ctx.structured_job
        if job:
            parts.append(f"- 营销目标：{job.get('objective', '未指定')}")
            parts.append(f"- 目标受众：{job.get('persona', '未指定')}")
            parts.append(f"- 风格偏好：{job.get('style_preference', '未指定')}")
            if job.get("special_instructions"):
                parts.append(f"- 特殊要求：{job['special_instructions']}")

        parts.append("\n## 产品信息")
        parts.append(f"- 产品名称：{ctx.product_name or '未知'}")
        parts.append(f"- 产品分类：{ctx.product_category or '未知'}")
        if ctx.product_description:
            parts.append(f"- 产品描述：{ctx.product_description[:1000]}")

        parts.append("\n## 商家规则")
        if ctx.merchant_rules:
            parts.append(f"- 行业：{ctx.merchant_industry or '未知'}")
            self._append_rules(parts, ctx.merchant_rules)
        else:
            parts.append("无特殊规则")

        parts.append("\n请根据以上信息，制定完整的内容策略方案，以JSON格式返回。")
        return "\n".join(parts)

    @staticmethod
    def _append_rules(parts: list[str], rules: dict) -> None:
        if rules.get("tone_preset"):
            parts.append(f"- 语调预设：{rules['tone_preset']}")
        banned = rules.get("banned_words")
        if banned:
            words = banned if isinstance(banned, list) else banned.get("words", [])
            if words:
                parts.append(f"- 禁用词：{', '.join(words[:20])}")
        required = rules.get("required_claims")
        if required:
            claims = required if isinstance(required, list) else required.get("claims", [])
            if claims:
                parts.append(f"- 必须包含的声明：{', '.join(claims)}")
        banned_claims = rules.get("banned_claims")
        if banned_claims:
            claims = banned_claims if isinstance(banned_claims, list) else banned_claims.get("claims", [])
            if claims:
                parts.append(f"- 禁止使用的声明：{', '.join(claims)}")
        if rules.get("compliance_level"):
            parts.append(f"- 合规等级：{rules['compliance_level']}")
