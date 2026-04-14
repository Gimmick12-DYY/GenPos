from __future__ import annotations

from .base import AgentContext, AgentResult, BaseAgent

_SYSTEM_PROMPT = """\
你是一位资深的内容合规审核专家「合规审核师」，专注于中国广告法和小红书平台规范的合规审核。

## 审核维度

你必须从以下六个维度全面审核内容：

1. **广告法违规词**（ad_law_violation）
   - 绝对化用语：最、第一、唯一、首选、顶级、极致等
   - 虚假权威：国家级、世界领先、全网销量第一等
   - 违规承诺：包治、根治、永久、100%有效等

2. **夸大宣传**（exaggerated_claim）
   - 功效夸大：无科学依据的功效声明
   - 效果承诺：保证效果、立竿见影等
   - 数据造假：虚假统计数据或比较

3. **虚假承诺**（false_promise）
   - 退款承诺：无条件退款等不实承诺
   - 效果保证：保证XX天见效等
   - 收益承诺：保证收益、稳赚等

4. **敏感词**（sensitive_term）
   - 政治敏感：涉及政治、领导人等
   - 社会敏感：涉及歧视、暴力等
   - 医疗敏感：非医疗产品的医疗声明

5. **IP侵权风险**（ip_infringement）
   - 品牌名称：未授权使用其他品牌名
   - 明星肖像：未授权引用明星
   - 版权内容：引用受版权保护的内容

6. **硬广风险**（hard_sell_risk）
   - 直接推销：过于直白的购买引导
   - 价格强调：过度强调价格优惠
   - 缺乏内容价值：纯广告无信息价值

## 输出要求

始终以JSON格式输出：
```json
{
  "status": "passed | failed | review_needed",
  "confidence": 0.0到1.0之间的置信度,
  "summary": "审核结论摘要",
  "issues": [
    {
      "severity": "critical | major | minor | suggestion",
      "rule_type": "ad_law_violation | exaggerated_claim | false_promise | sensitive_term | ip_infringement | hard_sell_risk",
      "location": "title_variant_1 | body_variant_2 | first_comment | hashtag | cover_brief | carousel_1",
      "original_text": "问题原文",
      "detail": "问题详细说明",
      "suggestion": "修改建议"
    }
  ],
  "merchant_rule_checks": {
    "banned_words_found": ["发现的禁用词"],
    "required_claims_present": true | false,
    "missing_required_claims": ["缺失的必要声明"],
    "banned_claims_found": ["发现的禁止声明"]
  },
  "pass_rate": {
    "titles": "通过/总数",
    "bodies": "通过/总数",
    "visuals": "通过/总数"
  }
}
```

## 严重程度定义
- `critical`：必须修改，否则不能发布（广告法违规、严重虚假宣传）
- `major`：强烈建议修改（夸大宣传、敏感词）
- `minor`：建议修改（轻微硬广风险、语气问题）
- `suggestion`：优化建议（提升内容质量的建议）

## 判定规则
- 存在任何 critical issue → status = "failed"
- 存在 major issue 但无 critical → status = "review_needed"
- 仅有 minor/suggestion 或无 issue → status = "passed"
"""


class ComplianceReviewerAgent(BaseAgent):
    """Reviews generated content for regulatory and platform compliance."""

    role_key = "compliance_reviewer"
    display_name = "合规审核师"

    async def execute(self, ctx: AgentContext) -> AgentResult:
        if not ctx.note_content:
            return AgentResult(
                success=False,
                error="缺少笔记内容，无法进行合规审核",
            )

        system_prompt = self._build_system_prompt(ctx)
        user_prompt = self._build_user_prompt(ctx)

        try:
            result = await self._llm.chat_completion_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=4096,
            )
        except Exception as exc:
            self._logger.error("LLM call failed: %s", exc, exc_info=True)
            return AgentResult(
                success=False,
                error=f"合规审核LLM调用失败: {exc}",
            )

        content = result["content"]
        if content.get("parse_error"):
            self._logger.warning("LLM returned unparseable JSON for compliance review")
            return AgentResult(
                success=False,
                output=content,
                error="合规审核返回了无法解析的JSON",
                token_usage=result["usage"],
            )

        required_keys = {"status", "issues"}
        missing = required_keys - set(content.keys())
        if missing:
            self._logger.warning("Compliance report missing keys: %s", missing)
            return AgentResult(
                success=False,
                output=content,
                error=f"合规报告缺少必要字段: {', '.join(missing)}",
                token_usage=result["usage"],
            )

        valid_statuses = {"passed", "failed", "review_needed"}
        if content.get("status") not in valid_statuses:
            self._logger.warning("Invalid compliance status: %s", content.get("status"))
            content["status"] = "review_needed"

        ctx.compliance_report = content

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

        # Note content to review
        parts.append("## 待审核笔记内容\n")
        note = ctx.note_content

        titles = note.get("title_variants", [])
        if titles:
            parts.append("### 标题方案")
            for t in titles:
                vid = t.get("variant_id", "?")
                parts.append(f"标题{vid}：{t.get('title', '')}")

        bodies = note.get("body_variants", [])
        if bodies:
            parts.append("\n### 正文方案")
            for b in bodies:
                vid = b.get("variant_id", "?")
                parts.append(f"--- 正文{vid} ---")
                parts.append(b.get("body", ""))

        first_comment = note.get("first_comment", "")
        if first_comment:
            parts.append(f"\n### 首条评论\n{first_comment}")

        hashtags = note.get("hashtags", [])
        if hashtags:
            parts.append(f"\n### 话题标签\n{' '.join(hashtags)}")

        # Visual assets to review
        visuals = ctx.visual_assets
        if visuals:
            parts.append("\n## 待审核视觉方案\n")
            cover = visuals.get("cover_brief", {})
            if cover:
                parts.append("### 封面方案")
                text_overlay = cover.get("text_overlay", {})
                if isinstance(text_overlay, dict):
                    parts.append(f"封面主文字：{text_overlay.get('main_text', '')}")
                    parts.append(f"封面副文字：{text_overlay.get('sub_text', '')}")
                parts.append(f"场景描述：{cover.get('scene_description', '')}")

            carousel = visuals.get("carousel_briefs", [])
            if carousel:
                parts.append("\n### 轮播图方案")
                for slide in carousel:
                    sn = slide.get("slide_number", "?")
                    parts.append(f"轮播{sn}：{slide.get('scene_description', '')}")
                    overlay = slide.get("text_overlay", {})
                    if isinstance(overlay, dict):
                        parts.append(f"  文字：{overlay.get('main_text', '')}")

        # Merchant rules
        parts.append("\n## 商家合规规则\n")
        if ctx.merchant_rules:
            self._append_merchant_rules(parts, ctx.merchant_rules)
        else:
            parts.append("无特殊商家规则，请按通用广告法和小红书平台规范审核。")

        parts.append(f"\n- 商家行业：{ctx.merchant_industry or '未知'}")
        parts.append(f"- 产品分类：{ctx.product_category or '未知'}")

        parts.append("\n请全面审核以上内容，以JSON格式返回审核报告。")
        return "\n".join(parts)

    @staticmethod
    def _append_merchant_rules(parts: list[str], rules: dict) -> None:
        banned = rules.get("banned_words")
        if banned:
            words = banned if isinstance(banned, list) else banned.get("words", [])
            if words:
                parts.append(f"- 商家禁用词：{', '.join(words)}")
        required = rules.get("required_claims")
        if required:
            claims = required if isinstance(required, list) else required.get("claims", [])
            if claims:
                parts.append(f"- 必须包含声明：{', '.join(claims)}")
        banned_claims = rules.get("banned_claims")
        if banned_claims:
            claims = banned_claims if isinstance(banned_claims, list) else banned_claims.get("claims", [])
            if claims:
                parts.append(f"- 禁止使用声明：{', '.join(claims)}")
        if rules.get("compliance_level"):
            parts.append(f"- 合规等级：{rules['compliance_level']}")
