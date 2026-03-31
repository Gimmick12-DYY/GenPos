"""Primary image generation: OpenAI Images API → PNG bytes (BL-106 / BL-112)."""

from __future__ import annotations

import base64
import logging
import re

from openai import AsyncOpenAI

from src.core.config import settings

logger = logging.getLogger(__name__)


def prompt_from_brief(metadata: dict | None, asset_role: str) -> tuple[str, str | None]:
    """Build (prompt, negative) from visual designer `metadata_json`."""
    if not metadata:
        return (
            "Soft pastel cartoon illustration for a Xiaohongshu lifestyle product note, "
            "clean composition, no text in image.",
            None,
        )
    primary = (metadata.get("image_prompt") or "").strip()
    if not primary:
        scene = (metadata.get("scene_description") or "").strip()
        style = (metadata.get("style_notes") or "").strip()
        place = (metadata.get("product_placement") or "").strip()
        bits = [b for b in (scene, place, style) if b]
        primary = " ".join(bits) if bits else ""
    if not primary:
        primary = (
            "Cute flat vector illustration showcasing a consumer product, "
            "warm lighting, Xiaohongshu aesthetic, no text in image."
        )
    role_hint = "Hero cover shot, vertical composition." if asset_role == "cover" else "Carousel slide, square composition."
    if role_hint.lower() not in primary.lower():
        primary = f"{role_hint} {primary}"

    neg = metadata.get("negative_prompt")
    neg_s = neg.strip() if isinstance(neg, str) and neg.strip() else None
    return primary, neg_s


def _merge_negative(prompt: str, negative: str | None) -> str:
    if not negative:
        return prompt
    return f"{prompt}\n\nAvoid: {negative}"


def _sanitize_for_openai(prompt: str, max_len: int = 3800) -> str:
    """DALL-E 3 is sensitive to length; trim whitespace and cap size."""
    s = re.sub(r"\s+", " ", prompt).strip()
    return s[:max_len]


async def generate_image_bytes(
    *,
    prompt: str,
    negative: str | None = None,
    size: str,
) -> bytes | None:
    """
    Call OpenAI Images and return decoded PNG/JPEG bytes, or None if disabled / error.
    """
    if not settings.image_generation_enabled:
        return None
    if not (settings.openai_api_key or "").strip():
        logger.info("Skipping remote image generation: OPENAI_API_KEY not set")
        return None

    merged = _merge_negative(prompt, negative)
    merged = _sanitize_for_openai(merged)

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    model = settings.image_gen_model

    extra_attempts: list[dict] = [
        {
            "size": size,
            "quality": settings.image_gen_quality,
            "style": settings.image_gen_style,
        },
        {"size": size},
        {},
    ]

    response = None
    last_err: Exception | None = None
    for extra in extra_attempts:
        try:
            kwargs: dict = {
                "model": model,
                "prompt": merged,
                "n": 1,
                "response_format": "b64_json",
                **extra,
            }
            kwargs = {k: v for k, v in kwargs.items() if v is not None and v != ""}
            response = await client.images.generate(**kwargs)
            break
        except Exception as exc:
            last_err = exc
            logger.debug("image.generate attempt failed (%s): %s", extra.keys(), exc)

    if response is None:
        logger.warning(
            "OpenAI image generation exhausted retries (will fall back to placeholder): %s",
            last_err,
        )
        return None

    try:
        data = response.data[0] if response.data else None
        if data is None:
            logger.warning("OpenAI images.generate returned no data")
            return None
        b64 = getattr(data, "b64_json", None)
        if not b64:
            logger.warning("OpenAI image response missing b64_json")
            return None
        raw = base64.b64decode(b64)
        return raw if raw else None
    except Exception as exc:
        logger.warning("OpenAI image decode failed (will fall back to placeholder): %s", exc)
        return None
