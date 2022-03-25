import platform
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from unittest import mock

import pytest

from dude import Scraper


class IsInteger:
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, int)

    def __repr__(self) -> str:
        return "IsInteger"


class IsUrl:
    def __init__(self, url: str):
        self.url = url

    def __eq__(self, other: Any) -> bool:
        """
        When loading an HTML file from local, Pyppeteer and Selenium prepends "file://" to href.
        On Windows, "file:///<Drive>:" is prepended, e.g. "file:///D:".
        """
        return isinstance(other, str) and (
            other == self.url or (other.startswith("file://") and other.endswith(self.url))
        )

    def __repr__(self) -> str:
        return f"IsUrl: {self.url}"


@pytest.fixture()
def test_html_path() -> str:
    return str((Path(__file__).resolve().parent.parent / "examples/dude.html").absolute())


@pytest.fixture()
def side_effect_func(test_html_path: str) -> Callable:
    def side_effect(url: str) -> mock.MagicMock:
        mock_response = mock.MagicMock()
        if url == "https://dude.ron.sh":
            with open(test_html_path) as f:
                mock_response.text = f.read()
        else:
            mock_response.text = ""
        return mock_response

    return side_effect


@pytest.fixture()
def test_url(test_html_path: str) -> str:
    if platform.system() == "Windows":
        return f"file:///{test_html_path}".replace("\\", "/")
    return f"file://{test_html_path}"


@pytest.fixture()
def mock_database() -> mock.MagicMock:
    return mock.MagicMock()


@pytest.fixture()
def mock_database_per_page() -> mock.MagicMock:
    return mock.MagicMock()


@pytest.fixture()
def scraper_application() -> Scraper:
    return Scraper()


@pytest.fixture()
def scraper_save(
    scraper_application: Scraper, mock_database: mock.MagicMock, mock_database_per_page: mock.MagicMock
) -> None:
    @scraper_application.save("custom")
    def save_to_database(data: Any, output: Optional[str]) -> bool:
        mock_database.save(data)
        return True

    @scraper_application.save("custom", is_per_page=True)
    def save_to_database_per_page(data: Any, output: Optional[str]) -> bool:
        mock_database_per_page.save(data)
        return True


@pytest.fixture()
def expected_data(test_url: str) -> List[Dict]:
    is_integer = IsInteger()
    return [
        {
            "_page_number": 1,
            "_page_url": test_url,
            "_group_id": is_integer,
            "_group_index": 0,
            "_element_index": 0,
            "url": IsUrl(url="url-1.html"),
            "title": "Title 1",
        },
        {
            "_page_number": 1,
            "_page_url": test_url,
            "_group_id": is_integer,
            "_group_index": 1,
            "_element_index": 0,
            "url": IsUrl(url="url-2.html"),
            "title": "Title 2",
        },
        {
            "_page_number": 1,
            "_page_url": test_url,
            "_group_id": is_integer,
            "_group_index": 2,
            "_element_index": 0,
            "url": IsUrl(url="url-3.html"),
            "title": "Title 3",
        },
    ]
