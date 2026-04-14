from __future__ import annotations

from src.core.product_catalog_prompt import format_catalog_text_for_prompt

from .base import AgentContext, AgentResult, BaseAgent

_SYSTEM_PROMPT = """\
你是一位专业的小红书营销AI助手「创始人副驾」，帮助商家创建小红书内容。你的核心职责是：

1. **意图识别**：准确理解商家的自然语言请求，将其归类为以下意图之一：
   - `generate_note`：创建新的小红书笔记内容
   - `modify_existing`：修改已有的笔记内容
   - `ask_question`：咨询小红书运营相关问题
   - `manage_assets`：管理素材（上传、查看、删除）
   - `export`：导出笔记或数据

2. **需求解构**：将模糊的商家需求转化为结构化的生成任务，包含：
   - `product_id`：关联的产品ID（**必须**来自用户消息中「本商户产品库」列表里的 UUID；用户用简称、代号、昵称指代商品时，根据名称/分类/描述匹配到唯一一条并填入该 ID）
   - `objective`：营销目标（seeding/conversion/awareness/engagement）
   - `persona`：目标受众描述
   - `style_preference`：风格偏好
   - `special_instructions`：特殊要求
   - `urgency`：紧急程度（low/normal/high）

3. **智能追问**：当信息不足时，用友好的方式向商家提出必要的澄清问题。

4. **上下文感知**：利用对话历史和商家配置信息提供连贯的交互体验。

## 输出要求

始终以JSON格式输出，包含以下字段：
```json
{
  "intent": "generate_note | modify_existing | ask_question | manage_assets | export",
  "needs_clarification": true | false,
  "response_to_user": "给商家的中文回复",
  "structured_job": {
    "product_id": "产品ID或null",
    "objective": "seeding | conversion | awareness | engagement",
    "persona": "目标受众描述",
    "style_preference": "风格偏好",
    "special_instructions": "特殊要求",
    "urgency": "low | normal | high"
  },
  "reasoning": "意图识别和解构的推理过程"
}
```

## 规则
- 始终用中文回复商家
- 保持友好、专业、高效的对话风格
- **产品库优先**：用户消息中会附带「本商户产品库」。若用户提到某商品，请只依据该列表中的真实名称与描述作答；不要虚构库里未出现的 SKU。
- 当意图为 `generate_note` 且产品库非空时，`structured_job.product_id` 必须设为库中某条商品的 UUID；若简称可唯一匹配（如「M1」对应名称「M1」），直接匹配，不要反问「请提供产品信息」。
- 当意图不是 generate_note 时，structured_job 可以为空对象
- 当 needs_clarification 为 true 时，response_to_user 应包含具体的追问问题
- 即使信息不完整，也尽量推断合理的默认值
"""


class FounderCopilotAgent(BaseAgent):
    """Interprets merchant requests and translates them into structured generation jobs."""

    role_key = "founder_copilot"
    display_name = "创始人副驾"

    def _build_system_prompt(self, ctx: AgentContext) -> str:
        base = super()._build_system_prompt(ctx)
        if ctx.product_catalog:
            return (
                base + "\n\n## 产品库约束\n"
                "你已收到「本商户产品库」全文（见用户消息）。生成笔记时必须使用其中的 product_id。"
            )
        return base

    async def execute(self, ctx: AgentContext) -> AgentResult:
        system_prompt = self._build_system_prompt(ctx)
        user_prompt = self._build_user_prompt(ctx)

        try:
            result = await self._llm.chat_completion_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.5,
                max_tokens=2048,
            )
        except Exception as exc:
            self._logger.error("LLM call failed: %s", exc, exc_info=True)
            return AgentResult(
                success=False,
                error=f"LLM调用失败: {exc}",
            )

        content = result["content"]
        if content.get("parse_error"):
            self._logger.warning("LLM returned unparseable JSON")
            return AgentResult(
                success=False,
                output=content,
                error="LLM返回了无法解析的JSON",
                token_usage=result["usage"],
            )

        structured_job = content.get("structured_job", {})
        if structured_job:
            ctx.structured_job = structured_job

        return AgentResult(
            success=True,
            output={
                "intent": content.get("intent", "ask_question"),
                "needs_clarification": content.get("needs_clarification", False),
                "response_to_user": content.get("response_to_user", ""),
                "structured_job": structured_job,
                "reasoning": content.get("reasoning", ""),
            },
            token_usage=result["usage"],
        )

    def _get_role_prompt(self) -> str:
        return _SYSTEM_PROMPT

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def _build_user_prompt(self, ctx: AgentContext) -> str:
        parts: list[str] = []

        parts.append("## 商家信息")
        parts.append(f"- 商家名称：{ctx.merchant_name or '未知'}")
        parts.append(f"- 所属行业：{ctx.merchant_industry or '未知'}")
        if ctx.merchant_rules:
            rules_summary = self._summarise_rules(ctx.merchant_rules)
            parts.append(f"- 商家规则：{rules_summary}")

        parts.append("\n## 本商户产品库")
        parts.append(format_catalog_text_for_prompt(ctx.product_catalog))

        if ctx.product_name:
            parts.append("\n## 当前产品")
            parts.append(f"- 产品名称：{ctx.product_name}")
            parts.append(f"- 产品分类：{ctx.product_category or '未知'}")
            if ctx.product_description:
                desc = ctx.product_description[:500]
                parts.append(f"- 产品描述：{desc}")

        if ctx.conversation_history:
            parts.append("\n## 对话历史")
            for msg in ctx.conversation_history[-10:]:
                role = "商家" if msg.get("role") == "user" else "助手"
                parts.append(f"[{role}]：{msg.get('content', '')}")

        parts.append("\n## 当前消息")
        parts.append(ctx.user_message)

        parts.append("\n请以JSON格式返回你的分析结果。")
        return "\n".join(parts)

    @staticmethod
    def _summarise_rules(rules: dict) -> str:
        summary_parts: list[str] = []
        if rules.get("tone_preset"):
            summary_parts.append(f"语调={rules['tone_preset']}")
        banned = rules.get("banned_words")
        if banned:
            words = banned if isinstance(banned, list) else banned.get("words", [])
            if words:
                summary_parts.append(f"禁用词{len(words)}个")
        if rules.get("compliance_level"):
            summary_parts.append(f"合规等级={rules['compliance_level']}")
        return "，".join(summary_parts) if summary_parts else "无特殊规则"
