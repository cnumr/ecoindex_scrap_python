from datetime import datetime
from pathlib import Path
from typing import Any

from ecoindex.models import Ecoindex
from pydantic import BaseModel
from pydantic.networks import HttpUrl
from sqlmodel import Field, SQLModel

PageType = str


class PageMetrics(SQLModel):
    size: float = Field(
        default=...,
        title="Page size",
        description="Is the size of the page and of the downloaded elements of the page in KB",
        ge=0,
    )
    nodes: int = Field(
        default=...,
        title="Page nodes",
        description="Is the number of the DOM elements in the page",
        ge=0,
    )
    requests: int = Field(
        default=...,
        title="Page requests",
        description="Is the number of external requests made by the page",
        ge=0,
    )


class WindowSize(BaseModel):
    height: int = Field(
        default=...,
        title="Window height",
        description="Height of the simulated window in pixel",
    )
    width: int = Field(
        default=...,
        title="Window width",
        description="Width of the simulated window in pixel",
    )

    def __str__(self) -> str:
        return f"{self.width},{self.height}"


class WebPage(SQLModel):
    width: int | None = Field(
        default=None,
        title="Page Width",
        description="Width of the simulated window in pixel",
    )
    height: int | None = Field(
        default=None,
        title="Page Height",
        description="Height of the simulated window in pixel",
    )
    url: HttpUrl | None = Field(
        default=None, title="Page url", description="Url of the analysed page"
    )


class Result(Ecoindex, PageMetrics, WebPage):
    date: datetime | None = Field(
        default=None, title="Analysis datetime", description="Date of the analysis"
    )
    page_type: PageType | None = Field(
        default=None,
        title="Page type",
        description="Is the type of the page, based ton the [opengraph type tag](https://ogp.me/#types)",
    )


class ScreenShot(BaseModel):
    id: str
    folder: str

    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)
        path = Path(__pydantic_self__.folder)
        path.mkdir(parents=True, exist_ok=True)

    def __str__(self) -> str:
        return f"{self.folder}/{self.id}"

    def get_png(self) -> str:
        return f"{self.__str__()}.png"

    def get_webp(self) -> str:
        return f"{self.__str__()}.webp"
