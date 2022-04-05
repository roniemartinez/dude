from typing import Any, Dict, Iterable, List, Optional
from unittest import mock
from urllib.parse import urljoin

import pytest
from braveblock import Adblocker
from bs4 import BeautifulSoup
from httpx import Request
from respx import Router

from dude import Scraper
from dude.optional.beautifulsoup_scraper import BeautifulSoupScraper


@pytest.fixture()
def scraper_application_with_bs4_parser(blocked_url: str) -> Scraper:
    scraper = BeautifulSoupScraper()
    scraper.adblock = Adblocker(rules=[blocked_url])
    return Scraper(scraper=scraper)


@pytest.fixture()
def bs4_select(scraper_application: Scraper) -> None:
    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title")
    def title(element: BeautifulSoup) -> Dict:
        return {"title": element.get_text()}

    @scraper_application.select(css=".title", group_css=".custom-group")
    def empty(element: BeautifulSoup) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title", url="example.com")
    def url_dont_match(element: BeautifulSoup) -> Dict:
        return {"title": element.get_text()}

    @scraper_application.select(css=".url", group_css=".custom-group")
    def url(element: BeautifulSoup) -> Dict:
        return {"url": element["href"]}


@pytest.fixture()
def async_bs4_select(scraper_application: Scraper) -> None:
    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title")
    async def title(element: BeautifulSoup) -> Dict:
        return {"title": element.get_text()}

    @scraper_application.select(css=".title", group_css=".custom-group")
    async def empty(element: BeautifulSoup) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title", url="example.com")
    async def url_dont_match(element: BeautifulSoup) -> Dict:
        return {"title": element.get_text()}

    @scraper_application.select(css=".url", group_css=".custom-group")
    async def url(element: BeautifulSoup) -> Dict:
        return {"url": element["href"]}


@pytest.fixture()
def bs4_xpath(scraper_application: Scraper) -> None:
    @scraper_application.select(
        xpath='.//p[contains(@class, "title")]/text()', group_xpath='.//div[contains(@class, "custom-group")]'
    )
    def title(element: BeautifulSoup) -> Dict:
        return {"title": element.get_text()}

    @scraper_application.select(
        xpath='.//a[contains(@class, "url")]/@href', group_xpath='.//div[contains(@class, "custom-group")]'
    )
    def url(element: BeautifulSoup) -> Dict:
        return {"url": element["href"]}


@pytest.fixture()
def bs4_text(scraper_application: Scraper) -> None:
    @scraper_application.select(text="Title", group_css=".custom-group")
    def title(element: BeautifulSoup) -> Dict:
        return {"title": element.get_text()}

    @scraper_application.select(css=".url", group_css=".custom-group")
    def url(element: BeautifulSoup) -> Dict:
        return {"url": element["href"]}


@pytest.fixture()
def bs4_regex(scraper_application: Scraper) -> None:
    @scraper_application.select(regex=r"Title\s\d", group_css=".custom-group")
    def title(element: BeautifulSoup) -> Dict:
        return {"title": element.get_text()}

    @scraper_application.select(css=".url", group_css=".custom-group")
    def url(element: BeautifulSoup) -> Dict:
        return {"url": element["href"]}


@pytest.fixture()
def bs4_select_with_parser(scraper_application_with_bs4_parser: Scraper) -> None:
    @scraper_application_with_bs4_parser.group(css=".custom-group")
    @scraper_application_with_bs4_parser.select(css=".title")
    def title(element: BeautifulSoup) -> Dict:
        return {"title": element.get_text()}

    @scraper_application_with_bs4_parser.select(css=".title", group_css=".custom-group")
    def empty(element: BeautifulSoup) -> Dict:
        return {}

    @scraper_application_with_bs4_parser.group(css=".custom-group")
    @scraper_application_with_bs4_parser.select(css=".title", url="example.com")
    def url_dont_match(element: BeautifulSoup) -> Dict:
        return {"title": element.get_text()}

    @scraper_application_with_bs4_parser.select(css=".url", group_css=".custom-group")
    def url(element: BeautifulSoup) -> Dict:
        return {"url": element["href"]}


@pytest.fixture()
def async_bs4_select_with_parser(scraper_application_with_bs4_parser: Scraper) -> None:
    @scraper_application_with_bs4_parser.group(css=".custom-group")
    @scraper_application_with_bs4_parser.select(css=".title")
    async def title(element: BeautifulSoup) -> Dict:
        return {"title": element.get_text()}

    @scraper_application_with_bs4_parser.select(css=".title", group_css=".custom-group")
    async def empty(element: BeautifulSoup) -> Dict:
        return {}

    @scraper_application_with_bs4_parser.group(css=".custom-group")
    @scraper_application_with_bs4_parser.select(css=".title", url="example.com")
    async def url_dont_match(element: BeautifulSoup) -> Dict:
        return {"title": element.get_text()}

    @scraper_application_with_bs4_parser.select(css=".url", group_css=".custom-group")
    async def url(element: BeautifulSoup) -> Dict:
        return {"url": element["href"]}


@pytest.fixture()
def scraper_with_parser_save(scraper_application_with_bs4_parser: Scraper, mock_database: mock.MagicMock) -> None:
    @scraper_application_with_bs4_parser.save("custom")
    def save_to_database(data: Any, output: Optional[str]) -> bool:
        mock_database.save(data)
        return True


def test_full_flow_bs4(
    scraper_application: Scraper,
    bs4_select: None,
    expected_data: List[Dict],
    base_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
    mock_database_per_page: mock.MagicMock,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[base_url], pages=2, format="custom", parser="bs4", follow_urls=True)

    mock_database_per_page.save.assert_called_with(expected_data)
    mock_database.save.assert_not_called()


def test_bs4_httpx_exception(
    scraper_application: Scraper,
    bs4_select: None,
    expected_data: List[Dict],
    scraper_save: None,
    mock_database: mock.MagicMock,
    base_url: str,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[urljoin(base_url, "error.html")], pages=2, format="custom", parser="bs4")

    mock_database.save.assert_not_called()


def test_full_flow_bs4_async(
    scraper_application: Scraper,
    async_bs4_select: None,
    expected_data: List[Dict],
    base_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[base_url], pages=2, format="custom", parser="bs4")

    mock_database.save.assert_called_with(expected_data)


def test_full_flow_bs4_httpx_async(
    scraper_application: Scraper,
    async_bs4_select: None,
    expected_data: List[Dict],
    base_url: str,
    scraper_save: None,
    mock_database_per_page: mock.MagicMock,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[base_url], pages=2, format="custom", parser="bs4", follow_urls=True)

    mock_database_per_page.save.assert_called_with(expected_data)


def test_bs4_httpx_exception_async(
    scraper_application: Scraper,
    async_bs4_select: None,
    expected_data: List[Dict],
    scraper_save: None,
    mock_database: mock.MagicMock,
    base_url: str,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[urljoin(base_url, "error.html")], pages=2, format="custom", parser="bs4")

    mock_database.save.assert_not_called()


def test_unsupported_xpath(
    scraper_application: Scraper,
    bs4_xpath: None,
    expected_data: List[Dict],
    base_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 2

    with pytest.raises(Exception):
        scraper_application.run(urls=[base_url], pages=2, format="custom", parser="bs4")


def test_unsupported_text(
    scraper_application: Scraper,
    bs4_text: None,
    expected_data: List[Dict],
    base_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 2

    with pytest.raises(Exception):
        scraper_application.run(urls=[base_url], pages=2, format="custom", parser="bs4")


def test_unsupported_regex(
    scraper_application: Scraper,
    bs4_regex: None,
    expected_data: List[Dict],
    base_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 2

    with pytest.raises(Exception):
        scraper_application.run(urls=[base_url], pages=2, format="custom", parser="bs4")


def test_scraper_with_parser(
    scraper_application_with_bs4_parser: Scraper,
    bs4_select_with_parser: None,
    scraper_with_parser_save: None,
    mock_database: mock.MagicMock,
    blocked_url: str,
    mock_httpx: Router,
) -> None:
    assert scraper_application_with_bs4_parser.has_async is False
    assert scraper_application_with_bs4_parser.scraper is not None
    assert len(scraper_application_with_bs4_parser.scraper.rules) == 4

    scraper_application_with_bs4_parser.run(urls=[blocked_url], pages=2, format="custom", parser="bs4")

    mock_database.save.assert_not_called()


def test_async_scraper_with_parser(
    scraper_application_with_bs4_parser: Scraper,
    async_bs4_select_with_parser: None,
    scraper_with_parser_save: None,
    mock_database: mock.MagicMock,
    blocked_url: str,
    mock_httpx: Router,
) -> None:
    assert scraper_application_with_bs4_parser.has_async is True
    assert scraper_application_with_bs4_parser.scraper is not None
    assert len(scraper_application_with_bs4_parser.scraper.rules) == 4

    scraper_application_with_bs4_parser.run(urls=[blocked_url], pages=2, format="custom", parser="bs4")

    mock_database.save.assert_not_called()


@pytest.mark.parametrize("method", ("POST", "PUT", "PATCH"))
def test_full_flow_post_bs4(
    scraper_application: Scraper,
    bs4_select: None,
    expected_data: List[Dict],
    base_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
    mock_database_per_page: mock.MagicMock,
    mock_httpx: Router,
    method: str,
) -> None:
    @scraper_application.start_requests()
    def start_requests() -> Iterable[Request]:
        yield Request(method=method, url=base_url)

    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4

    scraper_application.run(
        urls=[urljoin(base_url, "empty.html")], pages=2, format="custom", parser="bs4", follow_urls=True
    )

    mock_database_per_page.save.assert_called_with(expected_data)
    mock_database.save.assert_not_called()
