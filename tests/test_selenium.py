from typing import Dict, List
from unittest import mock

import pytest
from selenium.webdriver.remote.webelement import WebElement

from dude import Scraper


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
    @scraper_application.select(css=".title", url=r"example\.com")
    def url_dont_match(element: WebElement) -> Dict:
        return {"title": element.text}

    @scraper_application.select(css=".url", group_css=".custom-group")
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
def selenium_setup(scraper_application: Scraper) -> None:
    @scraper_application.select(css=":root", setup=True)
    def check_page(element: WebElement) -> None:
        assert element is not None


@pytest.fixture()
def selenium_navigate(scraper_application: Scraper) -> None:
    @scraper_application.select(css=":root", navigate=True)
    def next_page(element: WebElement) -> bool:
        assert element is not None
        return True


def test_full_flow(
    scraper_application: Scraper,
    selenium_select: None,
    selenium_setup: None,
    selenium_navigate: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 6
    mock_save = mock.MagicMock()
    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="selenium")

    # Pyppeteer prepends "file://" when loading a file
    expected_data = [{**d, "url": "file://" + d["url"]} for d in expected_data]
    mock_save.assert_called_with(expected_data, None)


def test_full_flow_xpath(
    scraper_application: Scraper,
    selenium_xpath: None,
    selenium_setup: None,
    selenium_navigate: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()
    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="selenium")

    # Pyppeteer prepends "file://" when loading a file
    expected_data = [{**d, "url": "file://" + d["url"]} for d in expected_data]
    mock_save.assert_called_with(expected_data, None)


def test_full_flow_text(
    scraper_application: Scraper,
    selenium_text: None,
    selenium_setup: None,
    selenium_navigate: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()
    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="selenium")

    # Pyppeteer prepends "file://" when loading a file
    expected_data = [{**d, "url": "file://" + d["url"]} for d in expected_data]
    mock_save.assert_called_with(expected_data, None)
