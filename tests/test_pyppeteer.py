from typing import Dict, List
from unittest import mock

import pytest
from braveblock import Adblocker
from pyppeteer.element_handle import ElementHandle
from pyppeteer.page import Page

from dude import Scraper
from dude.optional.pyppeteer_scraper import PyppeteerScraper


@pytest.fixture()
def scraper_application_with_pyppeteer_parser() -> Scraper:
    scraper = PyppeteerScraper()
    scraper.adblock = Adblocker(rules=["https://dude.ron.sh/blockme.css"])
    return Scraper(scraper=scraper)


@pytest.fixture()
def async_pyppeteer_select(scraper_application: Scraper) -> None:
    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title")
    async def title(element: ElementHandle, page: Page) -> Dict:
        return {"title": await page.evaluate("(element) => element.textContent", element)}

    @scraper_application.select(css=".title", group_css=".custom-group")
    async def empty(element: ElementHandle, page: Page) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title", url=r"example\.com")
    async def url_dont_match(element: ElementHandle, page: Page) -> Dict:
        return {"title": await page.evaluate("(element) => element.textContent", element)}

    @scraper_application.select(css=".url", group_css=".custom-group")
    async def url(element: ElementHandle, page: Page) -> Dict:
        handle = await element.getProperty("href")
        return {"url": await handle.jsonValue()}


@pytest.fixture()
def async_pyppeteer_select_with_parser(scraper_application_with_pyppeteer_parser: Scraper) -> None:
    @scraper_application_with_pyppeteer_parser.group(css=".custom-group")
    @scraper_application_with_pyppeteer_parser.select(css=".title")
    async def title(element: ElementHandle, page: Page) -> Dict:
        return {"title": await page.evaluate("(element) => element.textContent", element)}

    @scraper_application_with_pyppeteer_parser.select(css=".title", group_css=".custom-group")
    async def empty(element: ElementHandle, page: Page) -> Dict:
        return {}

    @scraper_application_with_pyppeteer_parser.group(css=".custom-group")
    @scraper_application_with_pyppeteer_parser.select(css=".title", url=r"example\.com")
    async def url_dont_match(element: ElementHandle, page: Page) -> Dict:
        return {"title": await page.evaluate("(element) => element.textContent", element)}

    @scraper_application_with_pyppeteer_parser.select(css=".url", group_css=".custom-group")
    async def url(element: ElementHandle, page: Page) -> Dict:
        handle = await element.getProperty("href")
        return {"url": await handle.jsonValue()}


@pytest.fixture()
def async_pyppeteer_xpath(scraper_application: Scraper) -> None:
    @scraper_application.select(
        xpath='.//p[contains(@class, "title")]', group_xpath='.//div[contains(@class, "custom-group")]'
    )
    async def title(element: ElementHandle, page: Page) -> Dict:
        return {"title": await page.evaluate("(element) => element.textContent", element)}

    @scraper_application.select(
        xpath='.//a[contains(@class, "url")]', group_xpath='.//div[contains(@class, "custom-group")]'
    )
    async def url(element: ElementHandle, page: Page) -> Dict:
        handle = await element.getProperty("href")
        return {"url": await handle.jsonValue()}


@pytest.fixture()
def async_pyppeteer_text(scraper_application: Scraper) -> None:
    @scraper_application.select(text="Title", group_css=".custom-group")
    async def title(element: ElementHandle, page: Page) -> Dict:
        return {"title": await page.evaluate("(element) => element.textContent", element)}

    @scraper_application.select(xpath='.//a[contains(@class, "url")]', group_css=".custom-group")
    async def url(element: ElementHandle, page: Page) -> Dict:
        handle = await element.getProperty("href")
        return {"url": await handle.jsonValue()}


@pytest.fixture()
def async_pyppeteer_regex(scraper_application: Scraper) -> None:
    @scraper_application.select(regex=".*", group_css=".custom-group")
    async def url(element: ElementHandle, page: Page) -> Dict:
        return {}


@pytest.fixture()
def async_pyppeteer_setup(scraper_application: Scraper) -> None:
    @scraper_application.select(css=":root", setup=True)
    async def check_page(element: ElementHandle, page: Page) -> None:
        assert element is not None
        assert page is not None


@pytest.fixture()
def async_pyppeteer_navigate(scraper_application: Scraper) -> None:
    @scraper_application.select(css=":root", navigate=True)
    async def next_page(element: ElementHandle, page: Page) -> bool:
        assert element is not None
        assert page is not None
        return True


def test_full_flow(
    scraper_application: Scraper,
    async_pyppeteer_select: None,
    async_pyppeteer_setup: None,
    async_pyppeteer_navigate: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 6
    mock_save = mock.MagicMock()
    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="pyppeteer", follow_urls=True)
    mock_save.assert_called_with(expected_data, None)


def test_full_flow_async_without_setup_and_navigate(
    scraper_application: Scraper,
    async_pyppeteer_select: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()
    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="pyppeteer")
    mock_save.assert_called_with(expected_data, None)


def test_full_flow_xpath(
    scraper_application: Scraper,
    async_pyppeteer_xpath: None,
    async_pyppeteer_setup: None,
    async_pyppeteer_navigate: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()
    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="pyppeteer")
    mock_save.assert_called_with(expected_data, None)


def test_full_flow_text(
    scraper_application: Scraper,
    async_pyppeteer_text: None,
    async_pyppeteer_setup: None,
    async_pyppeteer_navigate: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()
    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="pyppeteer")
    mock_save.assert_called_with(expected_data, None)


def test_unsupported_regex(
    scraper_application: Scraper,
    async_pyppeteer_regex: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 1
    mock_save = mock.MagicMock()
    scraper_application.save(format="custom")(mock_save)
    with pytest.raises(Exception):
        scraper_application.run(urls=[test_url], pages=2, format="custom", parser="pyppeteer")


def test_scraper_with_parser(
    scraper_application_with_pyppeteer_parser: Scraper,
    async_pyppeteer_select_with_parser: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application_with_pyppeteer_parser.has_async is True
    assert scraper_application_with_pyppeteer_parser.scraper is not None
    assert len(scraper_application_with_pyppeteer_parser.scraper.rules) == 4
    mock_save = mock.MagicMock()
    scraper_application_with_pyppeteer_parser.save(format="custom")(mock_save)
    scraper_application_with_pyppeteer_parser.run(urls=[test_url], pages=2, format="custom", parser="pyppeteer")
    mock_save.assert_called_with(expected_data, None)
