from io import BytesIO

import pytest
from PIL import Image

from sanitizer import MAX_BYTES, EvidenceInvalid, EvidenceTooLarge, sanitize_image

GPS_IFD = 0x8825


def photo_with_gps(size=(3000, 2000)) -> bytes:
    image = Image.new("RGB", size, (200, 30, 30))
    exif = Image.Exif()
    exif[0x010F] = "TestCam"
    exif[GPS_IFD] = {1: "S", 2: (12.0, 2.0, 40.0), 3: "W", 4: (77.0, 1.0, 50.0)}
    out = BytesIO()
    image.save(out, format="JPEG", exif=exif)
    return out.getvalue()


def test_input_really_carries_gps():
    with Image.open(BytesIO(photo_with_gps())) as image:
        assert GPS_IFD in image.getexif()


def test_output_has_no_exif_or_gps():
    with Image.open(BytesIO(sanitize_image(photo_with_gps()))) as image:
        assert len(image.getexif()) == 0
        assert GPS_IFD not in image.getexif()


def test_longest_side_is_capped():
    with Image.open(BytesIO(sanitize_image(photo_with_gps()))) as image:
        assert max(image.size) == 1920


def test_small_image_is_not_upscaled():
    with Image.open(BytesIO(sanitize_image(photo_with_gps((400, 300))))) as image:
        assert image.size == (400, 300)


def test_output_is_jpeg():
    assert sanitize_image(photo_with_gps()).startswith(b"\xff\xd8")


def test_oversized_evidence_is_rejected():
    with pytest.raises(EvidenceTooLarge):
        sanitize_image(b"0" * (MAX_BYTES + 1))


def test_non_image_is_rejected():
    with pytest.raises(EvidenceInvalid):
        sanitize_image(b"not an image")
