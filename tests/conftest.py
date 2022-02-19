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
            "item": "Item 1",
        },
        {
            "page_number": 1,
            "page_url": test_url,
            "group_id": is_integer,
            "group_index": 0,
            "element_index": 1,
            "item": "Item 2",
        },
        {
            "page_number": 1,
            "page_url": test_url,
            "group_id": is_integer,
            "group_index": 0,
            "element_index": 2,
            "item": "Item 3",
        },
    ]
