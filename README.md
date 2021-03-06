# ECOINDEX SCRAPER PYTHON

![Quality check](https://github.com/cnumr/ecoindex_scrap_python/workflows/Quality%20checks/badge.svg)
[![PyPI version](https://badge.fury.io/py/ecoindex-scraper.svg)](https://badge.fury.io/py/ecoindex-scraper)

This module provides a simple interface to get the [Ecoindex](http://www.ecoindex.fr) of a given webpage using module [ecoindex-python](https://pypi.org/project/ecoindex/)

## Requirements

- Python ^3.8 with [pip](https://pip.pypa.io/en/stable/installation/)
- Google Chrome installed on your computer

## Install

```shell
pip install ecoindex-scraper
```

## Use

### Get a page analysis

You can run a page analysis by calling the function `get_page_analysis()`:

```python
(function) get_page_analysis: (url: HttpUrl, window_size: WindowSize | None = WindowSize(width=1920, height=1080), wait_before_scroll: int | None = 1, wait_after_scroll: int | None = 1) -> Coroutine[Any, Any, Result]
```

Example:

```python
import asyncio
from pprint import pprint

from ecoindex_scraper import get_page_analysis

page_analysis = asyncio.run(get_page_analysis(url="http://ecoindex.fr"))
pprint(page_analysis)
```

Result example:

```python
Result(width=1920, height=1080, url=HttpUrl('http://ecoindex.fr', scheme='http', host='ecoindex.fr', tld='fr', host_type='domain'), size=422.126, nodes=54, requests=12, grade='A', score=86.0, ges=1.28, water=1.92, date=datetime.datetime(2021, 10, 8, 10, 20, 14, 73831), page_type=None)
```

> **Default behaviour:** By default, the page analysis simulates:
>
> - Window size of **1920x1080** pixels (can be set with parameter `window_size`)
> - Wait for **1 second when page is loaded** (can be set with parameter `wait_before_scroll`)
> - Scroll to the bottom of the page (if it is possible)
> - Wait for **1 second after** having scrolled to the bottom of the page (can be set with parameter `wait_after_scroll`)

## Contribute

You need [poetry](https://python-poetry.org/) to install and manage dependencies. Once poetry installed, run :

```bash
poetry install
```

## Tests

```shell
poetry run pytest
```

## [Contributing](CONTRIBUTING.md)

## [Code of conduct](CODE_OF_CONDUCT.md)
