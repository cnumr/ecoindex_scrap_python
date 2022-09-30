from datetime import datetime
from json import loads
from sys import getsizeof
from time import sleep
from typing import Optional, Tuple
from warnings import filterwarnings

import undetected_chromedriver.v2 as uc
from ecoindex.ecoindex import get_ecoindex
from pydantic.networks import HttpUrl
from selenium.common.exceptions import JavascriptException, NoSuchElementException
from selenium.webdriver import DesiredCapabilities

from ecoindex_scraper.models import (
    Page,
    PageMetrics,
    PageType,
    Result,
    ScreenShot,
    WindowSize,
)
from ecoindex_scraper.utils import convert_screenshot_to_webp, set_screenshot_rights


class EcoindexScraper:
    def __init__(
        self,
        url: HttpUrl,
        window_size: Optional[WindowSize] = WindowSize(width=1920, height=1080),
        wait_before_scroll: Optional[int] = 1,
        wait_after_scroll: Optional[int] = 1,
        screenshot: Optional[ScreenShot] = None,
        screenshot_uid: Optional[int] = None,
        screenshot_gid: Optional[int] = None,
    ):
        filterwarnings(action="ignore")

        self.url = url
        self.window_size = window_size
        self.wait_before_scroll = wait_before_scroll
        self.wait_after_scroll = wait_after_scroll
        self.screenshot = screenshot
        self.screenshot_uid = screenshot_uid
        self.screenshot_gid = screenshot_gid

        self.chrome_options = uc.ChromeOptions()
        self.chrome_options.headless = True
        self.chrome_options.add_argument(f"--window-size={self.window_size}")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")

        self.capbs = DesiredCapabilities.CHROME.copy()
        self.capbs["goog:loggingPrefs"] = {"performance": "ALL"}

    def __del__(self):
        if self.driver:
            self.driver.quit()

    def init_chromedriver(self):
        self.driver = uc.Chrome(
            options=self.chrome_options, desired_capabilities=self.capbs
        )

        return self

    async def get_page_analysis(
        self,
    ) -> Result:
        page_metrics, page_type = await self.scrap_page()
        ecoindex = await get_ecoindex(
            dom=page_metrics.nodes,
            size=page_metrics.size,
            requests=page_metrics.requests,
        )
        return Result(
            score=ecoindex.score,
            ges=ecoindex.ges,
            water=ecoindex.water,
            grade=ecoindex.grade,
            url=self.url,
            date=datetime.now(),
            width=self.window_size.width,
            height=self.window_size.height,
            nodes=page_metrics.nodes,
            size=page_metrics.size,
            requests=page_metrics.requests,
            page_type=page_type,
        )

    async def scrap_page(self) -> Tuple[PageMetrics, PageType]:
        self.driver.set_script_timeout(10)
        self.driver.get(self.url)
        sleep(self.wait_before_scroll)

        await self.generate_screenshot()
        await self.scroll_to_bottom()

        sleep(self.wait_after_scroll)

        page_type = await self.get_page_type()
        page_metrics = await self.get_page_metrics()

        return page_metrics, page_type

    async def generate_screenshot(self) -> None:
        if self.screenshot and self.screenshot.folder and self.screenshot.id:
            self.driver.save_screenshot(self.screenshot.get_png())
            convert_screenshot_to_webp(self.screenshot)
            set_screenshot_rights(
                screenshot=self.screenshot,
                uid=self.screenshot_uid,
                gid=self.screenshot_gid,
            )

    async def scroll_to_bottom(self) -> None:
        try:
            self.driver.execute_script(
                "window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })"
            )
        except JavascriptException:
            pass

    async def get_page_metrics(self) -> PageMetrics:
        page = Page(
            logs=self.driver.get_log("performance"),
            outer_html=self.driver.execute_script(
                "return document.documentElement.outerHTML"
            ),
            nodes=self.driver.find_elements("xpath", "//*"),
        )

        nb_svg_children = await self.get_svg_children_count()

        downloaded_data = [
            loads(log["message"])["message"]["params"]["encodedDataLength"]
            for log in page.logs
            if "INFO" == log["level"] and "Network.loadingFinished" in log["message"]
        ]

        return PageMetrics(
            size=(sum(downloaded_data) + getsizeof(page.outer_html)) / (10**3),
            nodes=len(page.nodes) - nb_svg_children,
            requests=len(downloaded_data),
        )

    async def get_page_type(self) -> Optional[PageType]:
        try:
            return self.driver.find_element(
                "xpath", "//meta[@property='og:type']"
            ).get_attribute("content")
        except (NoSuchElementException):
            return None

    async def get_svg_children_count(self) -> int:
        try:
            return len(self.driver.find_elements("xpath", "//*[local-name()='svg']/*"))
        except (NoSuchElementException):
            return 0
