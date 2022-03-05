import json
import sys
from typing import Dict, List
from unittest import mock

import pytest

from dude import Scraper


def test_full_flow(
    scraper_application: Scraper,
    async_playwright_select: None,
    async_playwright_setup: None,
    async_playwright_navigate: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 6
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
