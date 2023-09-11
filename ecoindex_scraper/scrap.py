import asyncio
from datetime import datetime
from os import chmod, remove
from shutil import copyfile
from time import sleep
from typing import Dict, Tuple
from uuid import uuid4

import undetected_chromedriver as uc
from ecoindex.ecoindex import get_ecoindex
from ecoindex.models import PageMetrics, PageType, Result, ScreenShot, WindowSize
from genericpath import exists
from pydantic.networks import HttpUrl
from selenium.common.exceptions import JavascriptException, NoSuchElementException

from ecoindex_scraper.utils import convert_screenshot_to_webp, set_screenshot_rights


class EcoindexScraper:
    def __init__(
        self,
        url: HttpUrl,
        chrome_version_main: int | None = None,
        driver_executable_path: str | None = None,
        chrome_executable_path: str | None = None,
        window_size: WindowSize = WindowSize(width=1920, height=1080),
        wait_before_scroll: float = 1,
        wait_after_scroll: float = 1,
        screenshot: ScreenShot | None = None,
        screenshot_uid: int | None = None,
        screenshot_gid: int | None = None,
        page_load_timeout: int = 20,
    ):
        self.url = url
        self.window_size = window_size
        self.wait_before_scroll = wait_before_scroll
        self.wait_after_scroll = wait_after_scroll
        self.screenshot = screenshot
        self.screenshot_uid = screenshot_uid
        self.screenshot_gid = screenshot_gid
        self.chrome_version_main = chrome_version_main
        self.chrome_executable_path = chrome_executable_path
        self.page_load_timeout = page_load_timeout

        self.chrome_options = uc.ChromeOptions()
        self.chrome_options.add_argument(f"--window-size={self.window_size}")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--ignore-certificate-errors")
        self.chrome_options.add_argument("--headless=new")

        self.all_requests = {}
        self.page_response = False

        if driver_executable_path:
            self.driver_executable_path = f"/tmp/chromedriver_{uuid4()}"
            copyfile(driver_executable_path, self.driver_executable_path)
            chmod(self.driver_executable_path, 0o755)
        else:
            self.driver_executable_path = None

    def __del__(self):
        if self.driver_executable_path and exists(self.driver_executable_path):
            remove(self.driver_executable_path)

    def _handle_network_response_received(self, eventdata):
        if eventdata["params"]["response"]["url"].startswith("http"):
            self.all_requests[eventdata["params"]["requestId"]] = {
                "url": eventdata["params"]["response"]["url"],
                "size": 0,
                "type": eventdata["params"]["type"],
            }

            if not self.page_response:
                self.page_response = True
                asyncio.run(self.check_page_response(eventdata["params"]["response"]))

    def _handle_network_data_received(self, eventdata):
        if eventdata["params"]["requestId"] in self.all_requests:
            self.all_requests[eventdata["params"]["requestId"]]["size"] += eventdata[
                "params"
            ]["encodedDataLength"]

    def _handle_network_loading_finished(self, eventdata):
        if eventdata["params"]["requestId"] in self.all_requests:
            self.all_requests[eventdata["params"]["requestId"]]["size"] = eventdata[
                "params"
            ]["encodedDataLength"]

    def init_chromedriver(self):
        self.driver = uc.Chrome(
            options=self.chrome_options,
            version_main=self.chrome_version_main,
            driver_executable_path=self.driver_executable_path,
            browser_executable_path=self.chrome_executable_path,
            enable_cdp_events=True,
        )

        self.driver.add_cdp_listener(
            "Network.dataReceived", self._handle_network_data_received
        )
        self.driver.add_cdp_listener(
            "Network.responseReceived", self._handle_network_response_received
        )
        self.driver.add_cdp_listener(
            "Network.loadingFinished", self._handle_network_loading_finished
        )

        if self.page_load_timeout is not None:
            self.driver.set_page_load_timeout(float(self.page_load_timeout))

        return self

    async def get_page_analysis(
        self,
    ) -> Result:
        try:
            page_metrics, page_type = await self.scrap_page()
        except Exception as e:
            self.__del__()
            raise e

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

    async def scrap_page(self) -> Tuple[PageMetrics, PageType | None]:
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
                (
                    "window.scrollTo({ top: "
                    "document.body.scrollHeight, behavior: 'smooth' })"
                )
            )
        except JavascriptException:
            pass

    async def get_page_metrics(self) -> PageMetrics:
        nodes = self.driver.find_elements("xpath", "//*")
        nb_svg_children = await self.get_svg_children_count()

        downloaded_data = [request["size"] for request in self.all_requests.values()]

        return PageMetrics(
            size=sum(downloaded_data) / (10**3),
            nodes=(len(nodes) - nb_svg_children),
            requests=len(self.all_requests),
        )

    @staticmethod
    async def check_page_response(response: Dict) -> None:
        if response["mimeType"] != "text/html":
            raise TypeError(
                {
                    "mimetype": response["mimeType"],
                    "message": (
                        "This resource is not "
                        "a standard page with mimeType 'text/html'"
                    ),
                }
            )

        if response["status"] != 200:
            raise ConnectionError(
                {
                    "status": response["status"],
                    "message": (
                        "This page can not be analyzed "
                        "because the response status code is not 200"
                    ),
                }
            )

    async def get_page_type(self) -> PageType | None:
        try:
            return self.driver.find_element(
                "xpath", "//meta[@property='og:type']"
            ).get_attribute("content")
        except NoSuchElementException:
            return None

    async def get_svg_children_count(self) -> int:
        try:
            return len(self.driver.find_elements("xpath", "//*[local-name()='svg']//*"))
        except NoSuchElementException:
            return 0
