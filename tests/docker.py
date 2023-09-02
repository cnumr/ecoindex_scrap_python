import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from ecoindex_scraper.scrap import EcoindexScraper


def run_page_analysis(url):
    try:
        ecoindex = asyncio.run(
            EcoindexScraper(
                url=url,
                driver_executable_path="/usr/bin/chromedriver",
                chrome_executable_path="/opt/chrome/chrome",
                chrome_version_main=114,
            )
            .init_chromedriver()
            .get_page_analysis()
        )

        return ecoindex

    except Exception as e:
        print(e)


with ThreadPoolExecutor(max_workers=8) as executor:
    future_to_analysis = {}

    url = "https://www.ecoindex.fr"

    for i in range(20):
        future_to_analysis[
            executor.submit(
                run_page_analysis,
                url,
            )
        ] = url

    for future in as_completed(future_to_analysis):
        try:
            print(future.result())
        except Exception as e:
            print(e)
