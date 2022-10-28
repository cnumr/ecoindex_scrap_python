from os import rmdir
from os.path import isdir

from ecoindex_scraper.models import Result, ScreenShot


def test_result_model():
    result = Result(
        size=119,
        nodes=45,
        requests=8,
        url="http://www.myurl.com",
        width=1920,
        height=1080,
        grade="A",
        score=89,
        ges=1.22,
        water=1.89,
    )
    assert result.page_type is None
    assert result.size == 119
    assert result.nodes == 45
    assert result.requests == 8
    assert result.width == 1920
    assert result.height == 1080
    assert result.grade == "A"
    assert result.score == 89
    assert result.ges == 1.22
    assert result.water == 1.89
    assert result.ecoindex_version is not None


def test_screenshot_model():
    id = "screenshot_test_id"
    folder = "./screenshot_test"

    screenshot = ScreenShot(id=id, folder=folder)

    assert isdir(folder) == True
    assert screenshot.id == id
    assert screenshot.folder == folder
    assert screenshot.get_png() == f"{folder}/{id}.png"
    assert screenshot.get_webp() == f"{folder}/{id}.webp"

    rmdir(folder)
    assert isdir(folder) == False
