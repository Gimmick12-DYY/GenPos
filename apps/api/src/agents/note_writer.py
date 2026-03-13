from __future__ import annotations

import json

from .base import AgentContext, AgentResult, BaseAgent

_SYSTEM_PROMPT = """\
你是一位专业的小红书文案创作者「笔记写手」，精通小红书平台的内容创作规则和流行文风。

## 核心能力

1. **标题创作**：为每篇笔记创作3个差异化标题（≤20字符），运用以下钩子技巧：
   - 好奇心钩子：「原来XX竟然是这样的？」
   - 利益钩子：「省了XX元，效果翻倍！」
   - 社交证明：「XX万人都在用的XX」
   - 紧迫感：「再不知道就晚了！」

2. **正文创作**：生成2个风格差异的正文版本（200-800字符），要求：
   - 自然融入emoji，不过度堆砌
   - 口语化表达，像朋友在分享真实体验
   - 信息密度高但不枯燥
   - 段落清晰，适合手机阅读
   - 自然植入产品卖点，避免硬广感

3. **首条评论**：创作引导互动的首条评论

4. **话题标签**：推荐5个精准话题标签（含#号）

5. **封面文案**：建议封面图上的文字内容

## 输出要求

始终以JSON格式输出：
```json
{
  "title_variants": [
    {
      "variant_id": 1,
      "title": "标题内容（≤20字符）",
      "hook_type": "curiosity | benefit | social_proof | urgency",
      "reasoning": "选择此钩子的原因"
    }
  ],
  "body_variants": [
    {
      "variant_id": 1,
      "body": "正文内容（200-800字符）",
      "style": "风格描述",
      "word_count": 字数
    }
  ],
  "first_comment": "首条评论内容",
  "hashtags": ["#话题标签1", "#话题标签2", "#话题标签3", "#话题标签4", "#话题标签5"],
  "cover_text_suggestions": [
    {
      "main_text": "封面主文案",
      "sub_text": "封面副文案"
    }
  ]
}
```

## 规则
- 严格遵守策略方案中的message_angles和persona定义
- 正文中不得出现商家禁用词
- 必须包含商家要求的必要声明
- 标题不超过20个字符
- 正文200-800字符
- 话题标签要贴合小红书平台热门话题格式
- 保持真实感和亲和力，避免广告感
"""


class NoteWriterAgent(BaseAgent):
    """Creates XiaoHongShu-native note content following a strategy plan."""

    role_key = "xhs_note_writer"
    display_name = "笔记写手"

    async def execute(self, ctx: AgentContext) -> AgentResult:
        if not ctx.strategy_plan:
            return AgentResult(
                success=False,
                error="缺少策略方案，无法生成笔记内容",
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
                error=f"笔记写作LLM调用失败: {exc}",
            )

        content = result["content"]
        if content.get("parse_error"):
            self._logger.warning("LLM returned unparseable JSON for note content")
            return AgentResult(
                success=False,
                output=content,
                error="笔记内容返回了无法解析的JSON",
                token_usage=result["usage"],
            )

        required_keys = {"title_variants", "body_variants", "hashtags"}
        missing = required_keys - set(content.keys())
        if missing:
            self._logger.warning("Note content missing keys: %s", missing)
            return AgentResult(
                success=False,
                output=content,
                error=f"笔记内容缺少必要字段: {', '.join(missing)}",
                token_usage=result["usage"],
            )

        ctx.note_content = content

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
        parts.append(f"- 营销目标：{plan.get('objective', '未指定')}")
        parts.append(f"- CTA类型：{plan.get('cta_type', '未指定')}")
        parts.append(f"- 视觉风格：{plan.get('style_family', '未指定')}")

        persona = plan.get("persona", {})
        if isinstance(persona, dict):
            parts.append(f"- 目标受众：{persona.get('description', '未指定')}")
            if persona.get("pain_points"):
                parts.append(f"- 受众痛点：{', '.join(persona['pain_points'])}")
        elif isinstance(persona, str):
            parts.append(f"- 目标受众：{persona}")

        angles = plan.get("message_angles", [])
        if angles:
            parts.append("\n## 内容角度")
            for angle in angles:
                aid = angle.get("angle_id", "?")
                theme = angle.get("theme", "")
                hook = angle.get("hook", "")
                parts.append(f"角度{aid}：{theme}（钩子：{hook}）")

        # Product info
        parts.append("\n## 产品信息")
        parts.append(f"- 产品名称：{ctx.product_name or '未知'}")
        parts.append(f"- 产品分类：{ctx.product_category or '未知'}")
        if ctx.product_description:
            parts.append(f"- 产品描述：{ctx.product_description[:800]}")

        # Merchant rules
        if ctx.merchant_rules:
            parts.append("\n## 内容合规规则")
            self._append_content_rules(parts, ctx.merchant_rules)

        # Safety rules from strategy
        safety = plan.get("safety_rules", {})
        if safety:
            parts.append("\n## 策略安全规则")
            if safety.get("must_include"):
                parts.append(f"- 必须包含：{', '.join(safety['must_include'])}")
            if safety.get("must_avoid"):
                parts.append(f"- 必须避免：{', '.join(safety['must_avoid'])}")
            if safety.get("tone_guardrails"):
                parts.append(f"- 语调护栏：{', '.join(safety['tone_guardrails'])}")

        parts.append("\n请根据以上策略方案和产品信息，创作小红书笔记内容，以JSON格式返回。")
        return "\n".join(parts)

    @staticmethod
    def _append_content_rules(parts: list[str], rules: dict) -> None:
        banned = rules.get("banned_words")
        if banned:
            words = banned if isinstance(banned, list) else banned.get("words", [])
            if words:
                parts.append(f"- 禁用词（不得出现）：{', '.join(words[:30])}")
        required = rules.get("required_claims")
        if required:
            claims = required if isinstance(required, list) else required.get("claims", [])
            if claims:
                parts.append(f"- 必须包含声明：{', '.join(claims)}")
        banned_claims = rules.get("banned_claims")
        if banned_claims:
            claims = banned_claims if isinstance(banned_claims, list) else banned_claims.get("claims", [])
            if claims:
                parts.append(f"- 禁止声明：{', '.join(claims)}")
