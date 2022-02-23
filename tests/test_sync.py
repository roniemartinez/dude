import json
from typing import Dict, List
from unittest import mock

import pytest
import yaml
from playwright.sync_api import ElementHandle, Page

from dude import Scraper, context, run, scraper, select

app = Scraper()


@select(selector=".title")
@app.select(selector=".title")
def title(element: ElementHandle) -> Dict:
    return {"item": element.text_content()}


@select(selector=".title", url=r"example\.com")
@app.select(selector=".title", url=r"example\.com")
def url_dont_match(element: ElementHandle) -> Dict:
    return {"item": element.text_content()}


@app.select(selector="text=Next Page", navigate=True)
def next_page(element: ElementHandle, page: Page) -> None:
    with page.expect_navigation():
        element.click()


"""
Actual tests below.
"""


def test_simple(expected_data: List[Dict], test_url: str) -> None:
    mock_save = mock.MagicMock()
    app.save(format="custom")(mock_save)
    app.run(urls=[test_url], pages=2, format="custom")
    mock_save.assert_called_with(expected_data, None)


def test_navigate(expected_data: List[Dict], test_url: str) -> None:
    mock_save = mock.MagicMock()
    app.save(format="custom")(mock_save)
    app.run(urls=[test_url], pages=2, format="custom")
    mock_save.assert_called_with(expected_data, None)


def test_format_not_supported(expected_data: List[Dict], test_url: str) -> None:
    with pytest.raises(KeyError):
        run(urls=[test_url], pages=2, format="custom")


def test_fail_to_save(expected_data: List[Dict], test_url: str) -> None:
    mock_save = mock.MagicMock()
    mock_save.return_value = False
    app.save(format="fail_db")(mock_save)
    with pytest.raises(Exception):
        app.run(urls=[test_url], pages=2, output="failing.fail_db")


@pytest.mark.parametrize("format", ("json", "csv"))
@mock.patch.object(json, "dump")
def test_save(mock_dump: mock.MagicMock, expected_data: List[Dict], test_url: str, format: str) -> None:
    run(urls=[test_url], format=format)
    mock_dump.assert_called()


@mock.patch.object(yaml, "safe_dump")
def test_save_yaml(mock_safe_dump: mock.MagicMock, expected_data: List[Dict], test_url: str) -> None:
    run(urls=[test_url], format="yaml")
    mock_safe_dump.assert_called()


@mock.patch.object(scraper, "_save_json")
def test_save_json_file(mock_save: mock.MagicMock, expected_data: List[Dict], test_url: str) -> None:
    run(urls=[test_url], output="output.json")
    mock_save.assert_called_with(expected_data, "output.json")


@mock.patch.object(context, "_save_csv")
def test_save_csv_file(mock_save: mock.MagicMock, expected_data: List[Dict], test_url: str) -> None:
    run(urls=[test_url], output="output.csv")
    mock_save.assert_called_with(expected_data, "output.csv")


@mock.patch.object(context, "_save_yaml")
def test_save_yaml_file(mock_save: mock.MagicMock, expected_data: List[Dict], test_url: str) -> None:
    run(urls=[test_url], output="output.yaml")
    mock_save.assert_called_with(expected_data, "output.yaml")
    assert False
