import platform
from pathlib import Path
from typing import Any, Callable, Dict, List
from unittest import mock

import pytest
from braveblock import Adblocker
from playwright import async_api, sync_api

from dude import Scraper
from dude.playwright_scraper import PlaywrightScraper


class IsInteger:
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, int)

    def __repr__(self) -> str:
        return "IsInteger"


class IsUrl:
    def __init__(self, url: str):
        self.url = url

    def __eq__(self, other: Any) -> bool:
        """
        When loading an HTML file from local, Pyppeteer and Selenium prepends "file://" to href.
        On Windows, "file:///<Drive>:" is prepended, e.g. "file:///D:".
        """
        return isinstance(other, str) and (
            other == self.url or (other.startswith("file://") and other.endswith(self.url))
        )

    def __repr__(self) -> str:
        return f"IsUrl: {self.url}"


@pytest.fixture()
def test_html_path() -> str:
    return str((Path(__file__).resolve().parent.parent / "examples/dude.html").absolute())


@pytest.fixture()
def side_effect_func(test_html_path: str) -> Callable:
    def side_effect(url: str) -> mock.MagicMock:
        mock_response = mock.MagicMock()
        if url == "https://dude.ron.sh":
            with open(test_html_path) as f:
                mock_response.text = f.read()
        else:
            mock_response.text = ""
        return mock_response

    return side_effect


@pytest.fixture()
def test_url(test_html_path: str) -> str:
    if platform.system() == "Windows":
        return f"file:///{test_html_path}".replace("\\", "/")
    return f"file://{test_html_path}"


@pytest.fixture()
def scraper_application() -> Scraper:
    return Scraper()


@pytest.fixture()
def scraper_application_with_parser() -> Scraper:
    scraper = PlaywrightScraper()
    scraper.adblock = Adblocker(rules=["https://dude.ron.sh/blockme.css"])
    return Scraper(scraper=scraper)


@pytest.fixture()
def playwright_select(scraper_application: Scraper) -> None:
    @scraper_application.group(selector=":root")  # will be skipped
    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title")
    def title(element: sync_api.ElementHandle) -> Dict:
        return {"title": element.text_content()}

    @scraper_application.select(css=".title", group_css=".custom-group")
    def empty(element: sync_api.ElementHandle) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title", url=r"example\.com")
    def url_dont_match(element: sync_api.ElementHandle) -> Dict:
        return {"title": element.text_content()}

    @scraper_application.select(css=".url", group_css=".custom-group")
    def url(element: sync_api.ElementHandle) -> Dict:
        return {"url": element.get_attribute("href")}


@pytest.fixture()
def playwright_select_with_parser(scraper_application_with_parser: Scraper) -> None:
    @scraper_application_with_parser.group(selector=":root")  # will be skipped
    @scraper_application_with_parser.group(css=".custom-group")
    @scraper_application_with_parser.select(css=".title")
    def title(element: sync_api.ElementHandle) -> Dict:
        return {"title": element.text_content()}

    @scraper_application_with_parser.select(css=".title", group_css=".custom-group")
    def empty(element: sync_api.ElementHandle) -> Dict:
        return {}

    @scraper_application_with_parser.group(css=".custom-group")
    @scraper_application_with_parser.select(css=".title", url=r"example\.com")
    def url_dont_match(element: sync_api.ElementHandle) -> Dict:
        return {"title": element.text_content()}

    @scraper_application_with_parser.select(css=".url", group_css=".custom-group")
    def url(element: sync_api.ElementHandle) -> Dict:
        return {"url": element.get_attribute("href")}


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
        return {"title": await element.text_content()}

    @scraper_application.select(css=".title", group_css=".custom-group")
    async def empty(element: async_api.ElementHandle) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title", url=r"example\.com")
    async def url_dont_match(element: async_api.ElementHandle) -> Dict:
        return {"title": await element.text_content()}

    @scraper_application.select(css=".url", group_css=".custom-group")
    async def url(element: async_api.ElementHandle) -> Dict:
        return {"url": await element.get_attribute("href")}


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
def playwright_xpath(scraper_application: Scraper) -> None:
    @scraper_application.select(
        xpath='.//p[contains(@class, "title")]', group_xpath='.//div[contains(@class, "custom-group")]'
    )
    def title(element: sync_api.ElementHandle) -> Dict:
        return {"title": element.text_content()}

    @scraper_application.select(
        xpath='.//a[contains(@class, "url")]', group_xpath='.//div[contains(@class, "custom-group")]'
    )
    def url(element: sync_api.ElementHandle) -> Dict:
        return {"url": element.get_attribute("href")}


@pytest.fixture()
def async_playwright_xpath(scraper_application: Scraper) -> None:
    @scraper_application.select(
        xpath='.//p[contains(@class, "title")]', group_xpath='.//div[contains(@class, "custom-group")]'
    )
    async def title(element: async_api.ElementHandle) -> Dict:
        return {"title": await element.text_content()}

    @scraper_application.select(
        xpath='.//a[contains(@class, "url")]', group_xpath='.//div[contains(@class, "custom-group")]'
    )
    async def url(element: async_api.ElementHandle) -> Dict:
        return {"url": await element.get_attribute("href")}


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
            "url": IsUrl(url="/url-1.html"),
            "title": "Title 1",
        },
        {
            "_page_number": 1,
            "_page_url": test_url,
            "_group_id": is_integer,
            "_group_index": 1,
            "_element_index": 0,
            "url": IsUrl(url="/url-2.html"),
            "title": "Title 2",
        },
        {
            "_page_number": 1,
            "_page_url": test_url,
            "_group_id": is_integer,
            "_group_index": 2,
            "_element_index": 0,
            "url": IsUrl(url="/url-3.html"),
            "title": "Title 3",
        },
    ]
