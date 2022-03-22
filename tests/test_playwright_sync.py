import json
from typing import Any, Dict, List, Optional
from unittest import mock

import pytest
import yaml
from playwright import sync_api

from dude import Scraper, storage
from dude.storage import save_csv, save_json, save_yaml


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
def playwright_startup(scraper_application: Scraper, mock_database: mock.MagicMock) -> None:
    @scraper_application.startup()
    def setup_database() -> None:
        mock_database.setup()


@pytest.fixture()
def playwright_pre_setup(scraper_application: Scraper) -> None:
    @scraper_application.pre_setup()
    def pre_setup(page: sync_api.Page) -> None:
        assert page is not None


@pytest.fixture()
def playwright_post_setup(scraper_application: Scraper) -> None:
    @scraper_application.post_setup()
    def post_setup(page: sync_api.Page) -> None:
        assert page is not None


@pytest.fixture()
def playwright_save(scraper_application: Scraper, mock_database: mock.MagicMock) -> None:
    @scraper_application.save("custom")
    def save_to_database(data: Any, output: Optional[str]) -> bool:
        mock_database.save(data)
        return True


@pytest.mark.parametrize(
    "browser_type",
    (
        "chromium",
        "firefox",
        "webkit",
    ),
)
def test_full_flow(
    scraper_application: Scraper,
    playwright_select: None,
    playwright_setup: None,
    playwright_navigate: None,
    playwright_startup: None,
    playwright_pre_setup: None,
    playwright_post_setup: None,
    playwright_save: None,
    expected_data: List[Dict],
    test_url: str,
    mock_database: mock.MagicMock,
    browser_type: str,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 6

    scraper_application.run(
        urls=[test_url], pages=2, format="custom", parser="playwright", browser_type=browser_type, follow_urls=True
    )

    mock_database.setup.assert_called_once()
    mock_database.save.assert_called_with(expected_data)


def test_full_flow_xpath(
    scraper_application: Scraper,
    playwright_xpath: None,
    playwright_setup: None,
    playwright_navigate: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()
    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="playwright")
    mock_save.assert_called_with(expected_data, None)


def test_custom_save(
    scraper_application: Scraper, playwright_select: None, expected_data: List[Dict], test_url: str
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()
    mock_save.return_value = True
    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="playwright")
    mock_save.assert_called_with(expected_data, None)


def test_scraper_with_parser(
    scraper_application_with_parser: Scraper,
    playwright_select_with_parser: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application_with_parser.has_async is False
    assert scraper_application_with_parser.scraper is not None
    assert len(scraper_application_with_parser.scraper.rules) == 4
    mock_save = mock.MagicMock()
    mock_save.return_value = True
    scraper_application_with_parser.save(format="custom")(mock_save)
    scraper_application_with_parser.run(urls=[test_url], pages=2, format="custom", parser="playwright")
    mock_save.assert_called_with(expected_data, None)


def test_format_not_supported(scraper_application: Scraper, playwright_select: None, test_url: str) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    with pytest.raises(KeyError):
        scraper_application.run(urls=[test_url], pages=2, format="custom", parser="playwright")


def test_failed_to_save(
    scraper_application: Scraper, playwright_select: None, expected_data: List[Dict], test_url: str
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()
    mock_save.return_value = False
    scraper_application.save(format="fail_db")(mock_save)
    with pytest.raises(Exception):
        scraper_application.run(urls=[test_url], pages=2, output="failing.fail_db", parser="playwright")


@mock.patch.object(json, "dump")
def test_save_json(
    mock_dump: mock.MagicMock,
    scraper_application: Scraper,
    playwright_select: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    scraper_application.save(format="json")(save_json)
    scraper_application.run(urls=[test_url], format="json")
    mock_dump.assert_called()


@mock.patch.object(json, "dump")
def test_save_csv(
    mock_dump: mock.MagicMock,
    scraper_application: Scraper,
    playwright_select: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    scraper_application.save(format="csv")(save_csv)
    scraper_application.run(urls=[test_url], format="csv")
    mock_dump.assert_called()


@mock.patch.object(yaml, "safe_dump")
def test_save_yaml(
    mock_safe_dump: mock.MagicMock,
    scraper_application: Scraper,
    playwright_select: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    scraper_application.save(format="yaml")(save_yaml)
    scraper_application.run(urls=[test_url], format="yaml")
    mock_safe_dump.assert_called()


@mock.patch.object(storage, "_save_json")
def test_save_json_file(
    mock_save: mock.MagicMock,
    scraper_application: Scraper,
    playwright_select: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    scraper_application.run(urls=[test_url], output="output.json")
    mock_save.assert_called_with(expected_data, "output.json")


@mock.patch.object(storage, "_save_csv")
def test_save_csv_file(
    mock_save: mock.MagicMock,
    scraper_application: Scraper,
    playwright_select: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    scraper_application.save(format="csv")(save_csv)
    scraper_application.run(urls=[test_url], output="output.csv")
    mock_save.assert_called_with(expected_data, "output.csv")


@mock.patch.object(storage, "_save_yaml")
def test_save_yaml_file(
    mock_save: mock.MagicMock,
    scraper_application: Scraper,
    playwright_select: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    scraper_application.save(format="yaml")(save_yaml)
    scraper_application.run(urls=[test_url], output="output.yaml")
    mock_save.assert_called_with(expected_data, "output.yaml")


def test_playwright_invalid_group(scraper_application: Scraper) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 0
    with pytest.raises(Exception):

        @scraper_application.group()
        @scraper_application.select(css=".title")
        def title(element: Any) -> Dict:
            return {}
