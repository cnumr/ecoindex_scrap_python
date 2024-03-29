from ecoindex_scraper.scrap import EcoindexScraper
from ecoindex.models import ScreenShot, WindowSize
from urllib.parse import urlparse


def test_scraper_init():
    url = "https://www.example.com"
    scraper = EcoindexScraper(url=url)  # type: ignore
    assert scraper.url == url
    assert scraper.window_size == WindowSize(width=1920, height=1080)
    assert scraper.wait_before_scroll == 1
    assert scraper.wait_after_scroll == 1
    assert scraper.screenshot is None
    assert scraper.screenshot_uid is None
    assert scraper.screenshot_gid is None
    assert scraper.chrome_version_main is None
    assert scraper.page_load_timeout == 20


def test_scraper_init_with_options():
    url = "https://www.example.com"
    window_size = WindowSize(width=800, height=600)
    wait_before_scroll = 2
    wait_after_scroll = 2
    screenshot_uid = 123
    screenshot_gid = 456
    chrome_version_main = 91
    page_load_timeout = 30
    screenshot_id = "123"
    screenshot_folder = "/tmp/screenshots"

    scraper = EcoindexScraper(
        url=url,  # type: ignore
        window_size=window_size,
        wait_before_scroll=wait_before_scroll,
        wait_after_scroll=wait_after_scroll,
        screenshot=ScreenShot(id=screenshot_id, folder=screenshot_folder),
        screenshot_uid=screenshot_uid,
        screenshot_gid=screenshot_gid,
        chrome_version_main=chrome_version_main,
        page_load_timeout=page_load_timeout,
    )

    assert scraper.url == url
    assert scraper.window_size == window_size
    assert scraper.wait_before_scroll == wait_before_scroll
    assert scraper.wait_after_scroll == wait_after_scroll
    assert scraper.screenshot.get_png() == f"{screenshot_folder}/{screenshot_id}.png"  # type: ignore
    assert scraper.screenshot.get_webp() == f"{screenshot_folder}/{screenshot_id}.webp"  # type: ignore
    assert scraper.screenshot_gid == screenshot_gid
    assert scraper.chrome_version_main == chrome_version_main
    assert scraper.page_load_timeout == page_load_timeout
