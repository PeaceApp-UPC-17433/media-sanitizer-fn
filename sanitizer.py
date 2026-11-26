from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BYTES = 25 * 1024 * 1024
MAX_PIXELS = 40_000_000
Image.MAX_IMAGE_PIXELS = MAX_PIXELS


class EvidenceTooLarge(ValueError):
    pass


class EvidenceInvalid(ValueError):
    pass


def sanitize_image(raw: bytes, max_side: int = 1920, quality: int = 85) -> bytes:
    if len(raw) > MAX_BYTES:
        raise EvidenceTooLarge(f"evidence exceeds {MAX_BYTES} bytes")
    try:
        with Image.open(BytesIO(raw)) as source:
            oriented = ImageOps.exif_transpose(source).convert("RGB")
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError) as error:
        raise EvidenceInvalid("not a supported image") from error
    oriented.thumbnail((max_side, max_side))
    clean = Image.new("RGB", oriented.size)
    clean.paste(oriented)
    out = BytesIO()
    clean.save(out, format="JPEG", quality=quality, optimize=True)
    return out.getvalue()
