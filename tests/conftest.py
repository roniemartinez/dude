from pathlib import Path
from typing import Any, Dict, List

import pytest


class IsInteger:
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, int)

    def __repr__(self) -> str:
        return "IsInteger"


@pytest.fixture()
def test_url() -> str:
    return f"file://{(Path(__file__).resolve().parent / 'dude.html').absolute()}"


@pytest.fixture()
def expected_data(test_url: str) -> List[Dict]:
    is_integer = IsInteger()
    return [
        {
            "page_number": 1,
            "page_url": test_url,
            "group_id": is_integer,
            "group_index": 0,
            "element_index": 0,
            "feature": "Simple Flask-inspired design - build a scraper with one decorator.",
        },
        {
            "page_number": 1,
            "page_url": test_url,
            "group_id": is_integer,
            "group_index": 0,
            "element_index": 1,
            "feature": "Uses Playwright's API - run your scraper in Chrome, Firefox and Webkit and leverage "
            "Playwright's powerful\n        selector engine.\n    ",
        },
        {
            "page_number": 1,
            "page_url": test_url,
            "group_id": is_integer,
            "group_index": 0,
            "element_index": 2,
            "feature": "Data grouping - group related scraping data.",
        },
        {
            "page_number": 1,
            "page_url": test_url,
            "group_id": is_integer,
            "group_index": 0,
            "element_index": 3,
            "feature": "URL pattern matching - run functions on specific URLs.",
        },
        {
            "page_number": 1,
            "page_url": test_url,
            "group_id": is_integer,
            "group_index": 0,
            "element_index": 4,
            "feature": "Priority - reorder functions based on priority.",
        },
        {
            "page_number": 1,
            "page_url": test_url,
            "group_id": is_integer,
            "group_index": 0,
            "element_index": 5,
            "feature": "Setup function - enable setup steps (clicking dialogs or login).",
        },
        {
            "page_number": 1,
            "page_url": test_url,
            "group_id": is_integer,
            "group_index": 0,
            "element_index": 6,
            "feature": "Navigate function - enable navigation steps to move to other pages.",
        },
        {
            "page_number": 1,
            "page_url": test_url,
            "group_id": is_integer,
            "group_index": 0,
            "element_index": 7,
            "feature": "Custom storage - option to save data to other formats or database.",
        },
    ]
