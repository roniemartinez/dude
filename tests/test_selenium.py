from typing import Any, Dict, List, Optional
from unittest import mock

import browsers
import pytest
import respx
from braveblock import Adblocker
from httpx import Response
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from dude import Scraper
from dude.optional.selenium_scraper import SeleniumScraper
from dude.optional.utils import get_chromedriver_latest_release


@pytest.fixture()
def scraper_application_with_selenium_parser() -> Scraper:
    scraper = SeleniumScraper()
    scraper.adblock = Adblocker(rules=["https://dude.ron.sh/blockme.css"])
    return Scraper(scraper=scraper)


@pytest.fixture()
def selenium_select(scraper_application: Scraper) -> None:
    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title")
    def title(element: WebElement) -> Dict:
        return {"title": element.text}

    @scraper_application.select(css=".title", group_css=".custom-group")
    def empty(element: WebElement) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title", url_match="example.com")
    def url_dont_match(element: WebElement) -> Dict:
        return {"title": element.text}

    @scraper_application.select(css=".url", group_css=".custom-group")
    def url(element: WebElement) -> Dict:
        return {"url": element.get_attribute("href")}


@pytest.fixture()
def selenium_select_with_parser(scraper_application_with_selenium_parser: Scraper) -> None:
    @scraper_application_with_selenium_parser.group(css=".custom-group")
    @scraper_application_with_selenium_parser.select(css=".title")
    def title(element: WebElement) -> Dict:
        return {"title": element.text}

    @scraper_application_with_selenium_parser.select(css=".title", group_css=".custom-group")
    def empty(element: WebElement) -> Dict:
        return {}

    @scraper_application_with_selenium_parser.group(css=".custom-group")
    @scraper_application_with_selenium_parser.select(css=".title", url_match="example.com")
    def url_dont_match(element: WebElement) -> Dict:
        return {"title": element.text}

    @scraper_application_with_selenium_parser.select(css=".url", group_css=".custom-group")
    def url(element: WebElement) -> Dict:
        return {"url": element.get_attribute("href")}


@pytest.fixture()
def selenium_xpath(scraper_application: Scraper) -> None:
    @scraper_application.select(
        xpath='.//p[contains(@class, "title")]', group_xpath='.//div[contains(@class, "custom-group")]'
    )
    def title(element: WebElement) -> Dict:
        return {"title": element.text}

    @scraper_application.select(
        xpath='.//a[contains(@class, "url")]', group_xpath='.//div[contains(@class, "custom-group")]'
    )
    def url(element: WebElement) -> Dict:
        return {"url": element.get_attribute("href")}


@pytest.fixture()
def selenium_text(scraper_application: Scraper) -> None:
    @scraper_application.select(text="Title", group_css=".custom-group")
    def title(element: WebElement) -> Dict:
        return {"title": element.text}

    @scraper_application.select(xpath='.//a[contains(@class, "url")]', group_css=".custom-group")
    def url(element: WebElement) -> Dict:
        return {"url": element.get_attribute("href")}


@pytest.fixture()
def selenium_regex(scraper_application: Scraper) -> None:
    @scraper_application.select(regex=".*", group_css=".custom-group")
    def title(element: WebElement) -> Dict:
        return {}


@pytest.fixture()
def selenium_setup(scraper_application: Scraper) -> None:
    @scraper_application.select(css=":root", setup=True)
    def check_page(element: WebElement, driver: WebDriver) -> None:
        assert element is not None


@pytest.fixture()
def selenium_navigate(scraper_application: Scraper) -> None:
    @scraper_application.select(css=":root", navigate=True)
    def next_page(element: WebElement, driver: WebDriver) -> bool:
        assert element is not None
        return True


@pytest.fixture()
def async_selenium_select(scraper_application: Scraper) -> None:
    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title")
    async def title(element: WebElement) -> Dict:
        return {"title": element.text}

    @scraper_application.select(css=".title", group_css=".custom-group")
    async def empty(element: WebElement) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title", url_match="example.com")
    async def url_dont_match(element: WebElement) -> Dict:
        return {"title": element.text}

    @scraper_application.select(css=".url", group_css=".custom-group")
    async def url(element: WebElement) -> Dict:
        return {"url": element.get_attribute("href")}


@pytest.fixture()
def async_selenium_xpath(scraper_application: Scraper) -> None:
    @scraper_application.select(
        xpath='.//p[contains(@class, "title")]', group_xpath='.//div[contains(@class, "custom-group")]'
    )
    async def title(element: WebElement) -> Dict:
        return {"title": element.text}

    @scraper_application.select(
        xpath='.//a[contains(@class, "url")]', group_xpath='.//div[contains(@class, "custom-group")]'
    )
    async def url(element: WebElement) -> Dict:
        return {"url": element.get_attribute("href")}


@pytest.fixture()
def async_selenium_text(scraper_application: Scraper) -> None:
    @scraper_application.select(text="Title", group_css=".custom-group")
    async def title(element: WebElement) -> Dict:
        return {"title": element.text}

    @scraper_application.select(xpath='.//a[contains(@class, "url")]', group_css=".custom-group")
    async def url(element: WebElement) -> Dict:
        return {"url": element.get_attribute("href")}


@pytest.fixture()
def async_selenium_setup(scraper_application: Scraper) -> None:
    @scraper_application.select(css=":root", setup=True)
    async def check_page(element: WebElement, driver: WebDriver) -> None:
        assert element is not None


@pytest.fixture()
def async_selenium_navigate(scraper_application: Scraper) -> None:
    @scraper_application.select(css=":root", navigate=True)
    async def next_page(element: WebElement, driver: WebDriver) -> bool:
        assert element is not None
        return True


@pytest.fixture()
def scraper_with_parser_save(scraper_application_with_selenium_parser: Scraper, mock_database: mock.MagicMock) -> None:
    @scraper_application_with_selenium_parser.save("custom")
    def save_to_database(data: Any, output: Optional[str]) -> bool:
        mock_database.save(data)
        return True


@pytest.mark.parametrize(
    "browser_type",
    (
        "chromium",
        "firefox",
    ),
)
def test_full_flow(
    scraper_application: Scraper,
    selenium_select: None,
    selenium_setup: None,
    selenium_navigate: None,
    expected_browser_data: List[Dict],
    file_url: str,
    browser_type: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
    mock_database_per_page: mock.MagicMock,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 6

    scraper_application.run(
        urls=[file_url], pages=2, format="custom", parser="selenium", browser_type=browser_type, follow_urls=True
    )

    mock_database_per_page.save.assert_called_with(expected_browser_data)
    mock_database.save.assert_not_called()


def test_full_flow_without_setup_and_navigate(
    scraper_application: Scraper,
    selenium_select: None,
    expected_browser_data: List[Dict],
    file_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[file_url], pages=2, format="custom", parser="selenium")

    mock_database.save.assert_called_with(expected_browser_data)


def test_full_flow_xpath(
    scraper_application: Scraper,
    selenium_xpath: None,
    selenium_setup: None,
    selenium_navigate: None,
    expected_browser_data: List[Dict],
    file_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[file_url], pages=2, format="custom", parser="selenium")

    mock_database.save.assert_called_with(expected_browser_data)


def test_full_flow_text(
    scraper_application: Scraper,
    selenium_text: None,
    selenium_setup: None,
    selenium_navigate: None,
    expected_browser_data: List[Dict],
    file_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[file_url], pages=2, format="custom", parser="selenium")

    mock_database.save.assert_called_with(expected_browser_data)


@pytest.mark.parametrize(
    "browser_type",
    (
        "chromium",
        "firefox",
    ),
)
def test_full_flow_async(
    scraper_application: Scraper,
    async_selenium_select: None,
    async_selenium_setup: None,
    async_selenium_navigate: None,
    expected_browser_data: List[Dict],
    file_url: str,
    browser_type: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
    mock_database_per_page: mock.MagicMock,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 6

    scraper_application.run(
        urls=[file_url], pages=2, format="custom", parser="selenium", browser_type=browser_type, follow_urls=True
    )

    mock_database_per_page.save.assert_called_with(expected_browser_data)
    mock_database.save.assert_not_called()


def test_full_flow_async_with_sync_setup_and_navigate(
    scraper_application: Scraper,
    async_selenium_select: None,
    selenium_setup: None,
    selenium_navigate: None,
    expected_browser_data: List[Dict],
    file_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 6

    scraper_application.run(urls=[file_url], pages=2, format="custom", parser="selenium")

    mock_database.save.assert_called_with(expected_browser_data)


def test_full_flow_async_without_setup_and_navigate(
    scraper_application: Scraper,
    async_selenium_select: None,
    expected_browser_data: List[Dict],
    file_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[file_url], pages=2, format="custom", parser="selenium")

    mock_database.save.assert_called_with(expected_browser_data)


def test_full_flow_xpath_async(
    scraper_application: Scraper,
    async_selenium_xpath: None,
    async_selenium_setup: None,
    async_selenium_navigate: None,
    expected_browser_data: List[Dict],
    file_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[file_url], pages=2, format="custom", parser="selenium")

    mock_database.save.assert_called_with(expected_browser_data)


def test_full_flow_text_async(
    scraper_application: Scraper,
    async_selenium_text: None,
    async_selenium_setup: None,
    async_selenium_navigate: None,
    expected_browser_data: List[Dict],
    file_url: str,
    scraper_save: None,
    mock_database: mock.MagicMock,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4

    scraper_application.run(urls=[file_url], pages=2, format="custom", parser="selenium")

    mock_database.save.assert_called_with(expected_browser_data)


def test_unsupported_regex(
    scraper_application: Scraper,
    selenium_regex: None,
    expected_browser_data: List[Dict],
    file_url: str,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 1
    mock_save = mock.MagicMock()
    scraper_application.save(format="custom")(mock_save)
    with pytest.raises(Exception):
        scraper_application.run(urls=[file_url], pages=2, format="custom", parser="selenium")


def test_scraper_with_parser(
    scraper_application_with_selenium_parser: Scraper,
    selenium_select_with_parser: None,
    expected_browser_data: List[Dict],
    file_url: str,
    scraper_with_parser_save: None,
    mock_database: mock.MagicMock,
) -> None:
    assert scraper_application_with_selenium_parser.has_async is False
    assert scraper_application_with_selenium_parser.scraper is not None
    assert len(scraper_application_with_selenium_parser.scraper.rules) == 4

    scraper_application_with_selenium_parser.run(urls=[file_url], pages=2, format="custom", parser="selenium")

    mock_database.save.assert_called_with(expected_browser_data)


@pytest.mark.parametrize(
    ("response", "expected_version"),
    (
        (Response(200, content="102.0.5005.61"), "102.0.5005.61"),
        (Response(404), "latest"),
    ),
)
@respx.mock(base_url="https://chromedriver.storage.googleapis.com")
@mock.patch.object(browsers, "get", return_value={"version": "102.0.5005.0"})
def test_get_chromedriver_latest_release(
    mock_browser: mock.MagicMock, respx_mock: respx.Router, response: Response, expected_version: str
) -> None:
    respx_mock.get("/LATEST_RELEASE_102.0.5005").mock(return_value=response)

    version = get_chromedriver_latest_release()
    assert version == expected_version

    mock_browser.assert_called()
