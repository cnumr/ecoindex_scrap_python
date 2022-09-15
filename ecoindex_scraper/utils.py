from os import unlink

from PIL import Image

from ecoindex_scraper.models import ScreenShot


def convert_screenshot_to_webp(screenshot: ScreenShot) -> None:
    image = Image.open(rf"{screenshot.__str__()}")
    width, height = image.size
    ratio = 800 / height if width > height else 600 / width

    image.convert("RGB").resize(size=(int(width * ratio), int(height * ratio))).save(
        rf"{screenshot.folder}/{screenshot.id}.webp",
        format="webp",
    )

    unlink(f"{screenshot.__str__()}")
