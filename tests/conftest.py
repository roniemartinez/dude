from pathlib import Path
from typing import Any, Dict, List

import pytest
from bs4 import BeautifulSoup
from playwright import async_api, sync_api

from dude import Scraper
from dude.playwright import PlaywrightScraper


class IsInteger:
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, int)

    def __repr__(self) -> str:
        return "IsInteger"


@pytest.fixture()
def test_url() -> str:
    return f"file://{(Path(__file__).resolve().parent.parent / 'examples/dude.html').absolute()}"


@pytest.fixture()
def scraper_application() -> Scraper:
    return Scraper()


@pytest.fixture()
def scraper_application_with_parser() -> Scraper:
    return Scraper(scraper=PlaywrightScraper())


@pytest.fixture()
def playwright_select(scraper_application: Scraper) -> None:
    @scraper_application.group(selector=":root")  # will be skipped
    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title")
    def title(element: sync_api.ElementHandle) -> Dict:
        return {"item": element.text_content()}

    @scraper_application.select(css=".title", group=".custom-group")
    def empty(element: sync_api.ElementHandle) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title", url=r"example\.com")
    def url_dont_match(element: sync_api.ElementHandle) -> Dict:
        return {"item": element.text_content()}


@pytest.fixture()
def bs4_select(scraper_application: Scraper) -> None:
    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title")
    def title(element: BeautifulSoup) -> Dict:
        return {"item": element.get_text()}

    @scraper_application.select(css=".title", group=".custom-group")
    def empty(element: BeautifulSoup) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title", url=r"example\.com")
    def url_dont_match(element: BeautifulSoup) -> Dict:
        return {"item": element.get_text()}


@pytest.fixture()
def playwright_select_with_parser(scraper_application_with_parser: Scraper) -> None:
    @scraper_application_with_parser.group(selector=":root")  # will be skipped
    @scraper_application_with_parser.group(css=".custom-group")
    @scraper_application_with_parser.select(css=".title")
    def title(element: sync_api.ElementHandle) -> Dict:
        return {"item": element.text_content()}

    @scraper_application_with_parser.select(css=".title", group=".custom-group")
    def empty(element: sync_api.ElementHandle) -> Dict:
        return {}

    @scraper_application_with_parser.group(css=".custom-group")
    @scraper_application_with_parser.select(css=".title", url=r"example\.com")
    def url_dont_match(element: sync_api.ElementHandle) -> Dict:
        return {"item": element.text_content()}


@pytest.fixture()
def playwright_setup(scraper_application: Scraper) -> None:
    @scraper_application.select(selector=":root", setup=True)
    def check_page(element: sync_api.ElementHandle, page: sync_api.Page) -> None:
        assert element is not None
        assert page is not None


@pytest.fixture()
def playwright_navigate(scraper_application: Scraper) -> None:
    @scraper_application.select(selector=":root", navigate=True)
    def next_page(element: sync_api.ElementHandle, page: sync_api.Page) -> bool:
        assert element is not None
        assert page is not None
        return True


@pytest.fixture()
def async_playwright_select(scraper_application: Scraper) -> None:
    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title")
    async def title(element: async_api.ElementHandle) -> Dict:
        return {"item": await element.text_content()}

    @scraper_application.select(css=".title", group=".custom-group")
    async def empty(element: async_api.ElementHandle) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title", url=r"example\.com")
    async def url_dont_match(element: async_api.ElementHandle) -> Dict:
        return {"item": await element.text_content()}


@pytest.fixture()
def async_bs4_select(scraper_application: Scraper) -> None:
    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title")
    async def title(element: BeautifulSoup) -> Dict:
        return {"item": element.get_text()}

    @scraper_application.select(css=".title", group=".custom-group")
    async def empty(element: BeautifulSoup) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title", url=r"example\.com")
    async def url_dont_match(element: BeautifulSoup) -> Dict:
        return {"item": element.get_text()}


@pytest.fixture()
def async_playwright_setup(scraper_application: Scraper) -> None:
    @scraper_application.select(css=":root", setup=True)
    async def check_page(element: async_api.ElementHandle, page: async_api.Page) -> None:
        assert element is not None
        assert page is not None


@pytest.fixture()
def async_playwright_navigate(scraper_application: Scraper) -> None:
    @scraper_application.select(css=":root", navigate=True)
    async def next_page(element: async_api.ElementHandle, page: async_api.Page) -> bool:
        assert element is not None
        assert page is not None
        return True


@pytest.fixture()
def expected_data(test_url: str) -> List[Dict]:
    is_integer = IsInteger()
    return [
        {
            "_page_number": 1,
            "_page_url": test_url,
            "_group_id": is_integer,
            "_group_index": 0,
            "_element_index": 0,
            "item": "Title 1",
        },
        {
            "_page_number": 1,
            "_page_url": test_url,
            "_group_id": is_integer,
            "_group_index": 1,
            "_element_index": 0,
            "item": "Title 2",
        },
        {
            "_page_number": 1,
            "_page_url": test_url,
            "_group_id": is_integer,
            "_group_index": 2,
            "_element_index": 0,
            "item": "Title 3",
        },
    ]
