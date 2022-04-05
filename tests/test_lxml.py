from typing import Dict, List
from unittest import mock
from urllib.parse import urljoin

import pytest
from lxml.etree import _Element
from respx import Router

from dude import Scraper


@pytest.fixture()
def lxml_css(scraper_application: Scraper) -> None:
    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title")
    def title(element: _Element) -> Dict:
        return {"title": element.text}

    @scraper_application.select(css=".title", group_css=".custom-group")
    def empty(element: _Element) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title", url="example.com")
    def url_dont_match(element: _Element) -> Dict:
        return {"title": element.text}

    @scraper_application.select(css=".url", group_css=".custom-group")
    def url(element: _Element) -> Dict:
        return {"url": element.attrib["href"]}


@pytest.fixture()
def async_lxml_css(scraper_application: Scraper) -> None:
    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title")
    async def title(element: _Element) -> Dict:
        return {"title": element.text}

    @scraper_application.select(css=".title", group_css=".custom-group")
    async def empty(element: _Element) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title", url="example.com")
    async def url_dont_match(element: _Element) -> Dict:
        return {"title": element.text}

    @scraper_application.select(css=".url", group_css=".custom-group")
    async def url(element: _Element) -> Dict:
        return {"url": element.attrib["href"]}


@pytest.fixture()
def lxml_xpath(scraper_application: Scraper) -> None:
    @scraper_application.select(
        xpath='.//p[contains(@class, "title")]/text()', group_xpath='.//div[contains(@class, "custom-group")]'
    )
    def title(text: str) -> Dict:
        return {"title": text}

    @scraper_application.select(
        xpath='.//a[contains(@class, "url")]/@href', group_xpath='.//div[contains(@class, "custom-group")]'
    )
    def url(href: str) -> Dict:
        return {"url": href}


@pytest.fixture()
def lxml_text(scraper_application: Scraper) -> None:
    @scraper_application.select(text="Title", group_css=".custom-group")
    def title(element: _Element) -> Dict:
        return {"title": element.text}

    @scraper_application.select(css=".url", group_css=".custom-group")
    def url(element: _Element) -> Dict:
        return {"url": element.attrib["href"]}


@pytest.fixture()
def lxml_regex(scraper_application: Scraper) -> None:
    @scraper_application.select(regex=r"Title\s\d", group_css=".custom-group")
    def title(element: _Element) -> Dict:
        return {"title": element.text}

    @scraper_application.select(css=".url", group_css=".custom-group")
    def url(element: _Element) -> Dict:
        return {"url": element.attrib["href"]}


def test_full_flow_lxml(
    scraper_application: Scraper,
    lxml_css: None,
    expected_data: List[Dict],
    base_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[base_url], pages=2, format="custom", parser="lxml")

    mock_database.save.assert_called_with(expected_data)


def test_lxml_httpx_exception(
    scraper_application: Scraper,
    lxml_css: None,
    expected_data: List[Dict],
    scraper_save: None,
    mock_database: mock.MagicMock,
    base_url: str,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[urljoin(base_url, "error.html")], pages=2, format="custom", parser="lxml")

    mock_database.save.assert_not_called()


def test_full_flow_lxml_async(
    scraper_application: Scraper,
    async_lxml_css: None,
    expected_data: List[Dict],
    base_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[base_url], pages=2, format="custom", parser="lxml")

    mock_database.save.assert_called_with(expected_data)


def test_full_flow_lxml_httpx_async(
    scraper_application: Scraper,
    async_lxml_css: None,
    expected_data: List[Dict],
    base_url: str,
    scraper_save: None,
    mock_database_per_page: mock.MagicMock,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[base_url], pages=2, format="custom", parser="lxml", follow_urls=True)

    mock_database_per_page.save.assert_called_with(expected_data)


def test_lxml_httpx_exception_async(
    scraper_application: Scraper,
    async_lxml_css: None,
    expected_data: List[Dict],
    scraper_save: None,
    mock_database: mock.MagicMock,
    base_url: str,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[urljoin(base_url, "error.html")], pages=2, format="custom", parser="lxml")

    mock_database.save.assert_not_called()


def test_full_flow_lxml_xpath(
    scraper_application: Scraper,
    lxml_xpath: None,
    expected_data: List[Dict],
    base_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 2

    scraper_application.run(urls=[base_url], pages=2, format="custom", parser="lxml")

    mock_database.save.assert_called_with(expected_data)


def test_full_flow_lxml_text(
    scraper_application: Scraper,
    lxml_text: None,
    expected_data: List[Dict],
    base_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 2

    scraper_application.run(urls=[base_url], pages=2, format="custom", parser="lxml")

    mock_database.save.assert_called_with(expected_data)


def test_full_flow_lxml_regex(
    scraper_application: Scraper,
    lxml_regex: None,
    expected_data: List[Dict],
    base_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
    mock_httpx: Router,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 2

    scraper_application.run(urls=[base_url], pages=2, format="custom", parser="lxml")

    mock_database.save.assert_called_with(expected_data)
