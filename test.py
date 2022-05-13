import asyncio
from pprint import pprint

from ecoindex_scraper import get_page_analysis

page_analysis = asyncio.run(get_page_analysis(url="https://www.itsonus.fr"))
pprint(page_analysis)
