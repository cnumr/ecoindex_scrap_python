import asyncio
from pprint import pprint

from ecoindex_scraper import get_page_analysis

page_analysis = asyncio.run(get_page_analysis(url="http://ecoindex.fr"))
pprint(page_analysis)
