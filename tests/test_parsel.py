import sys
from typing import Any, Dict, List
from unittest import mock

import httpx
import parsel
import pytest

from dude import Scraper


@pytest.fixture()
def parsel_select(scraper_application: Scraper) -> None:
    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title::text")
    def title(element: parsel.Selector) -> Dict:
        return {"title": element.get()}

    @scraper_application.select(css=".title::text", group_css=".custom-group")
    def empty(element: parsel.Selector) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title::text", url=r"example\.com")
    def url_dont_match(element: parsel.Selector) -> Dict:
        return {"title": element.get()}

    @scraper_application.select(css=".url::attr(href)", group_css=".custom-group")
    def url(element: parsel.Selector) -> Dict:
        return {"url": element.get()}


@pytest.fixture()
def async_parsel_select(scraper_application: Scraper) -> None:
    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title::text")
    async def title(element: parsel.Selector) -> Dict:
        return {"title": element.get()}

    @scraper_application.select(css=".title::text", group_css=".custom-group")
    async def empty(element: parsel.Selector) -> Dict:
        return {}

    @scraper_application.group(css=".custom-group")
    @scraper_application.select(css=".title::text", url=r"example\.com")
    async def url_dont_match(element: parsel.Selector) -> Dict:
        return {"title": element.get()}

    @scraper_application.select(css=".url::attr(href)", group_css=".custom-group")
    async def url(element: parsel.Selector) -> Dict:
        return {"url": element.get()}


def test_full_flow_parsel(
    scraper_application: Scraper,
    parsel_select: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()
    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="parsel")
    mock_save.assert_called_with(expected_data, None)


@mock.patch.object(httpx, "Client")
def test_full_flow_parsel_httpx(
    mock_client: mock.MagicMock,
    scraper_application: Scraper,
    parsel_select: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()

    with open(test_url[7:]) as f:
        mock_client.return_value.__enter__.return_value.get.return_value.text = f.read()

    test_url = "https://dude.ron.sh"
    expected_data = [{**d, "_page_url": test_url} for d in expected_data]

    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="parsel")
    mock_save.assert_called_with(expected_data, None)


@mock.patch.object(httpx, "Client")
def test_parsel_httpx_exception(
    mock_client: mock.MagicMock,
    scraper_application: Scraper,
    parsel_select: None,
    expected_data: List[Dict],
) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()

    response = mock_client.return_value.__enter__.return_value.get.return_value
    response.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="Mock exception",
        request=mock.MagicMock(),
        response=mock.MagicMock(),
    )

    test_url = "https://dude.ron.sh"

    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="parsel")
    mock_save.assert_called_with([], None)


def test_full_flow_parsel_async(
    scraper_application: Scraper,
    async_parsel_select: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()
    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="parsel")
    mock_save.assert_called_with(expected_data, None)


@pytest.mark.skipif(sys.version_info < (3, 8), reason="AsyncMock is not supported.")
@mock.patch.object(httpx, "AsyncClient")
def test_full_flow_parsel_httpx_async(
    mock_client: Any,  # mock.AsyncMock
    scraper_application: Scraper,
    async_parsel_select: None,
    expected_data: List[Dict],
    test_url: str,
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()

    with open(test_url[7:]) as f:
        response = mock_client.return_value.__aenter__.return_value.get.return_value
        response.raise_for_status = mock.MagicMock()
        response.text = f.read()

    test_url = "https://dude.ron.sh"
    expected_data = [{**d, "_page_url": test_url} for d in expected_data]

    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="parsel")
    mock_save.assert_called_with(expected_data, None)


@pytest.mark.skipif(sys.version_info < (3, 8), reason="AsyncMock is not supported.")
@mock.patch.object(httpx, "AsyncClient")
def test_parsel_httpx_exception_async(
    mock_client: Any,  # mock.AsyncMock
    scraper_application: Scraper,
    async_parsel_select: None,
    expected_data: List[Dict],
) -> None:
    assert scraper_application.has_async is True
    assert len(scraper_application.rules) == 4
    mock_save = mock.MagicMock()

    response = mock_client.return_value.__aenter__.return_value.get.return_value
    response.raise_for_status = mock.MagicMock(
        side_effect=httpx.HTTPStatusError(
            message="Mock exception",
            request=mock.MagicMock(),
            response=mock.MagicMock(),
        )
    )

    test_url = "https://dude.ron.sh"

    scraper_application.save(format="custom")(mock_save)
    scraper_application.run(urls=[test_url], pages=2, format="custom", parser="parsel")
    mock_save.assert_called_with([], None)
