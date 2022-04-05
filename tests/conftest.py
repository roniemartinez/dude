import platform
import re
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional
from unittest import mock
from urllib.parse import urljoin

import pytest
import respx
from httpx import Response
from respx import Router

from dude import Scraper


class IsInteger:
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, int)

    def __repr__(self) -> str:
        return "IsInteger"


class IsUrl:
    def __init__(self, url: str, full_html_path: str):
        self.url = url
        self.full_html_path = full_html_path

    def __eq__(self, other: Any) -> bool:
        """
        When loading an HTML file from local, Pyppeteer and Selenium prepends "file://" to href.
        On Windows, "file:///<Drive>:" is prepended, e.g. "file:///D:".
        """
        return isinstance(other, str) and (other == self.url or other == urljoin(self.full_html_path, self.url))

    def __repr__(self) -> str:
        return f"IsUrl: {self.url}"


@pytest.fixture()
def test_html_path() -> str:
    return str((Path(__file__).resolve().parent.parent / "examples/dude.html").absolute())


@pytest.fixture()
def base_url() -> str:
    return "https://dwmc.ron.sh"


@pytest.fixture()
def file_url(test_html_path: str) -> str:
    if platform.system() == "Windows":
        return f"file:///{test_html_path}".replace("\\", "/")
    return f"file://{test_html_path}"


@pytest.fixture()
def blocked_url(base_url: str) -> str:
    return urljoin(base_url, "blockme.css")


@pytest.fixture
def mock_httpx(test_html_path: str, base_url: str) -> Generator[Router, None, None]:
    with respx.mock(base_url=base_url, assert_all_called=False) as r, open(test_html_path) as f:
        content = f.read()
        r.get("/").mock(return_value=Response(200, content=content))
        r.post("/").mock(return_value=Response(200, content=content))
        r.put("/").mock(return_value=Response(200, content=content))
        r.patch("/").mock(return_value=Response(200, content=content))
        r.get(re.compile(".*")).mock(return_value=Response(404))
        yield r


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
def expected_data(base_url: str) -> List[Dict]:
    is_integer = IsInteger()
    return [
        {
            "_page_number": 1,
            "_page_url": base_url,
            "_group_id": is_integer,
            "_group_index": 0,
            "_element_index": 0,
            "url": "url-1.html",
            "title": "Title 1",
        },
        {
            "_page_number": 1,
            "_page_url": base_url,
            "_group_id": is_integer,
            "_group_index": 1,
            "_element_index": 0,
            "url": "url-2.html",
            "title": "Title 2",
        },
        {
            "_page_number": 1,
            "_page_url": base_url,
            "_group_id": is_integer,
            "_group_index": 2,
            "_element_index": 0,
            "url": "url-3.html",
            "title": "Title 3",
        },
    ]


@pytest.fixture()
def expected_browser_data(file_url: str) -> List[Dict]:
    is_integer = IsInteger()
    return [
        {
            "_page_number": 1,
            "_page_url": file_url,
            "_group_id": is_integer,
            "_group_index": 0,
            "_element_index": 0,
            "url": IsUrl("url-1.html", file_url),
            "title": "Title 1",
        },
        {
            "_page_number": 1,
            "_page_url": file_url,
            "_group_id": is_integer,
            "_group_index": 1,
            "_element_index": 0,
            "url": IsUrl("url-2.html", file_url),
            "title": "Title 2",
        },
        {
            "_page_number": 1,
            "_page_url": file_url,
            "_group_id": is_integer,
            "_group_index": 2,
            "_element_index": 0,
            "url": IsUrl("url-3.html", file_url),
            "title": "Title 3",
        },
    ]
