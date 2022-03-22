import json
import sys
from typing import Any, Dict, List, Optional
from unittest import mock

import pytest
from playwright import async_api, sync_api

from dude import Scraper


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
def async_playwright_startup(scraper_application: Scraper, mock_database: mock.MagicMock) -> None:
    @scraper_application.startup()
    async def setup_database() -> None:
        mock_database.setup()


@pytest.fixture()
def async_playwright_pre_setup(scraper_application: Scraper) -> None:
    @scraper_application.pre_setup()
    async def pre_setup(page: async_api.Page) -> None:
        assert page is not None


@pytest.fixture()
def async_playwright_post_setup(scraper_application: Scraper) -> None:
    @scraper_application.post_setup()
    async def post_setup(page: async_api.Page) -> None:
        assert page is not None


@pytest.fixture()
def playwright_save(scraper_application: Scraper, mock_database: mock.MagicMock) -> None:
    @scraper_application.save("custom")
    def save_to_database(data: Any, output: Optional[str]) -> bool:
        mock_database.save(data)
        return True


def test_full_flow(
    scraper_application: Scraper,
    async_playwright_select: None,
    async_playwright_setup: None,
    async_playwright_navigate: None,
    async_playwright_startup: None,
    async_playwright_pre_setup: None,
    async_playwright_post_setup: None,
    playwright_save: None,
    expected_data: List[Dict],
    test_url: str,
    mock_database: mock.MagicMock,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 6

    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="playwright", follow_urls=True)

    mock_database.setup.assert_called_once()
    mock_database.save.assert_called_with(expected_data)


def test_full_flow_xpath(
    scraper_application: Scraper,
    async_playwright_xpath: None,
    async_playwright_setup: None,
    async_playwright_navigate: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()
    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="playwright")
    mock_save.assert_called_with(expected_data, None)


def test_custom_save(
    scraper_application: Scraper, async_playwright_select: None, expected_data: List[Dict], test_url: str
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()
    mock_save.return_value = True
    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="playwright")
    mock_save.assert_called_with(expected_data, None)


@pytest.mark.skipif(sys.version_info < (3, 8), reason="AsyncMock is not supported.")
def test_async_save(
    scraper_application: Scraper, async_playwright_select: None, expected_data: List[Dict], test_url: str
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4
    mock_save = mock.AsyncMock()  # type: ignore[attr-defined]
    mock_save.return_value = True
    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="playwright")
    mock_save.assert_called_with(expected_data, None)


def test_format_not_supported(scraper_application: Scraper, async_playwright_select: None, test_url: str) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4
    with pytest.raises(KeyError):
        scraper_application.run(urls=[test_url], pages=2, format="custom", parser="playwright")


def test_failed_to_save(
    scraper_application: Scraper, async_playwright_select: None, expected_data: List[Dict], test_url: str
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()
    mock_save.return_value = False
    scraper_application.save(format="fail_db")(mock_save)
    with pytest.raises(Exception):
        scraper_application.run(urls=[test_url], pages=2, output="failing.fail_db", parser="playwright")


@mock.patch.object(json, "dump")
def test_save(
    mock_dump: mock.MagicMock,
    scraper_application: Scraper,
    async_playwright_select: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4
    scraper_application.run(urls=[test_url], format="json")
    mock_dump.assert_called()
