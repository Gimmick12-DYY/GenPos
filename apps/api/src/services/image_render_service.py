"""BL-106/BL-112: Placeholder cover/carousel PNGs until real diffusion/compositing is wired."""

from __future__ import annotations

import io
from typing import Any

from PIL import Image, ImageDraw, ImageFont


def render_note_visual_placeholder(
    *,
    headline: str,
    subtitle: str,
    aspect_width: int = 768,
    aspect_height: int = 1024,
) -> bytes:
    """Return PNG bytes (3:4 style). Text may truncate to fit."""
    img = Image.new("RGB", (aspect_width, aspect_height), color=(245, 240, 235))
    draw = ImageDraw.Draw(img)
    for y in range(0, aspect_height, 48):
        draw.line([(0, y), (aspect_width, y)], fill=(238, 232, 226), width=1)

    title = (headline or "GenPos")[:40]
    sub = (subtitle or "封面预览 · 占位图")[:60]
    font_lg = _load_font(32)
    font_sm = _load_font(20)

    tw, th = _textbbox(draw, title, font_lg)
    sw, sh = _textbbox(draw, sub, font_sm)
    cx, cy = aspect_width // 2, aspect_height // 2
    draw.text((cx - tw // 2, cy - th // 2 - 30), title, fill=(55, 48, 42), font=font_lg)
    draw.text((cx - sw // 2, cy + sh // 2), sub, fill=(120, 113, 108), font=font_sm)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


_FONT_CANDIDATES = (
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
)


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _textbbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def headline_from_visual_metadata(meta: dict[str, Any] | None) -> tuple[str, str]:
    if not meta:
        return "笔记封面", "AI 生成占位图"
    scene = str(meta.get("scene_description") or meta.get("composition_notes") or "")[:80]
    style = str(meta.get("style_notes") or meta.get("style_family") or "")[:40]
    line1 = scene.split("\n")[0].strip() if scene else "笔记封面"
    line2 = style or "视觉方案预览"
    return line1, line2
