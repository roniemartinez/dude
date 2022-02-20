import json
import sys
from typing import Dict, List, Optional
from unittest import mock

import pytest
from playwright.async_api import ElementHandle, Page

from dude import Scraper

async_app = Scraper()


@async_app.select(selector=".title")
async def title(element: ElementHandle) -> Dict:
    return {"item": await element.text_content()}


@async_app.select(selector=".title", url=r"example\.com")
async def url_dont_match(element: ElementHandle) -> Dict:
    return {"item": await element.text_content()}


@async_app.select(selector="text=Next Page", navigate=True)
async def next_page(element: ElementHandle, page: Page) -> None:
    async with page.expect_navigation():
        await element.click()


@async_app.save("json")
async def save_json(data: List[Dict], output: Optional[str]) -> bool:
    json.dump(data, sys.stdout, indent=2)
    return True


"""
Actual tests below.
"""


def test_simple(expected_data: List[Dict], test_url: str) -> None:
    mock_save = mock.MagicMock()
    async_app.save(format="custom")(mock_save)
    async_app.run(urls=[test_url], pages=2, format="custom")
    mock_save.assert_called_with(expected_data, None)


def test_navigate(expected_data: List[Dict], test_url: str) -> None:
    mock_save = mock.MagicMock()
    async_app.save(format="custom")(mock_save)
    async_app.run(urls=[test_url], pages=2, format="custom")
    mock_save.assert_called_with(expected_data, None)


def test_format_not_supported(expected_data: List[Dict], test_url: str) -> None:
    with pytest.raises(KeyError):
        async_app.run(urls=[test_url], pages=2, format="unknown")


def test_fail_to_save(expected_data: List[Dict], test_url: str) -> None:
    mock_save = mock.MagicMock()
    mock_save.return_value = False
    async_app.save(format="fail_db")(mock_save)
    with pytest.raises(Exception):
        async_app.run(urls=[test_url], pages=2, output="failing.fail_db")


@mock.patch.object(json, "dump")
def test_save(mock_dump: mock.MagicMock, expected_data: List[Dict], test_url: str) -> None:
    async_app.run(urls=[test_url], format="json")
    mock_dump.assert_called()
