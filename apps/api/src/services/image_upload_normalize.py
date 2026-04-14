"""BL-302 minimal: normalize raster uploads before storage (resize, re-encode, EXIF)."""

from __future__ import annotations

import io
import logging

logger = logging.getLogger(__name__)

_MAX_EDGE = 2048
_JPEG_QUALITY = 88


def normalize_image_upload(raw: bytes, asset_type: str) -> tuple[bytes, str, int, int] | None:
    """Resize (max longest edge), strip EXIF by re-encoding, apply EXIF orientation.

    Returns ``(bytes, content_type, width, height)`` or ``None`` to keep the original blob.
    """
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return None

    try:
        im = Image.open(io.BytesIO(raw))
        im = ImageOps.exif_transpose(im)
    except Exception:
        return None

    try:
        w, h = im.size
        m = max(w, h)
        if m > _MAX_EDGE:
            scale = _MAX_EDGE / float(m)
            nw = max(1, int(w * scale))
            nh = max(1, int(h * scale))
            im = im.resize((nw, nh), Image.Resampling.LANCZOS)

        has_alpha = im.mode in ("RGBA", "LA") or (
            im.mode == "P" and "transparency" in im.info
        )
        preserve_png = asset_type == "cutout" or has_alpha

        buf = io.BytesIO()
        if preserve_png:
            if im.mode != "RGBA":
                im = im.convert("RGBA")
            im.save(buf, format="PNG", optimize=True)
            content_type = "image/png"
        else:
            rgb = im.convert("RGB")
            rgb.save(buf, format="JPEG", quality=_JPEG_QUALITY, optimize=True)
            content_type = "image/jpeg"

        out = buf.getvalue()
        im2 = Image.open(io.BytesIO(out))
        ow, oh = im2.size
        return out, content_type, ow, oh
    except Exception:
        logger.debug("Image normalize skipped", exc_info=True)
        return None
