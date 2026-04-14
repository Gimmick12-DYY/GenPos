"""BL-302 minimal: image upload normalization."""

from __future__ import annotations

from io import BytesIO

from PIL import Image

from src.services.image_upload_normalize import normalize_image_upload


def test_normalize_resizes_large_rgb_to_jpeg() -> None:
    im = Image.new("RGB", (3000, 2000), color=(200, 100, 50))
    buf = BytesIO()
    im.save(buf, format="JPEG", quality=95)
    raw = buf.getvalue()

    out = normalize_image_upload(raw, "packshot")
    assert out is not None
    blob, ctype, w, h = out
    assert ctype == "image/jpeg"
    assert max(w, h) <= 2048
    assert len(blob) > 0


def test_normalize_preserves_cutout_as_png() -> None:
    im = Image.new("RGBA", (400, 400), color=(255, 0, 0, 128))
    buf = BytesIO()
    im.save(buf, format="PNG")
    raw = buf.getvalue()

    out = normalize_image_upload(raw, "cutout")
    assert out is not None
    blob, ctype, w, h = out
    assert ctype == "image/png"
    assert w == 400 and h == 400
