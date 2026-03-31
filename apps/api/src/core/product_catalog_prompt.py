"""Format merchant product catalog for LLM prompts (no DB; safe for agent imports)."""


def format_catalog_text_for_prompt(catalog: list[dict]) -> str:
    """Human-readable block for system / user prompts."""
    if not catalog:
        return (
            "【当前商户尚未在「我的产品库」中添加在售商品。"
            "若用户要生成笔记，请友好提示其先到「我的产品库」添加产品后再试。"
            "若仅为运营咨询，可正常回答。】"
        )
    lines: list[str] = [
        "【以下为该商户在「我的产品库」中的真实商品。你必须以此为准："
        "不要编造未列出的 SKU；用户用简称、代号、昵称或拼音指代商品时，"
        "根据名称/分类/描述匹配到唯一一条，并在需要时使用其 product_id（UUID）。】",
        "",
    ]
    for p in catalog:
        lines.append(f"- product_id={p['id']}")
        lines.append(f"  名称：「{p['name']}」 | 分类：{p['category']}")
        if p.get("primary_objective"):
            lines.append(f"  主推目标：{p['primary_objective']}")
        if p.get("description"):
            lines.append(f"  描述：{p['description']}")
        lines.append("")
    return "\n".join(lines).strip()
