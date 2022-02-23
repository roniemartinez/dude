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
    return f"file://{(Path(__file__).resolve().parent.parent / 'examples/dude.html').absolute()}"


@pytest.fixture()
def expected_data(test_url: str) -> List[Dict]:
    is_integer = IsInteger()
    return [
        {
            "page_number_": 1,
            "page_url_": test_url,
            "group_id_": is_integer,
            "group_index_": 0,
            "element_index_": 0,
            "item": "Title 1",
        },
        {
            "page_number_": 1,
            "page_url_": test_url,
            "group_id_": is_integer,
            "group_index_": 0,
            "element_index_": 1,
            "item": "Title 2",
        },
        {
            "page_number_": 1,
            "page_url_": test_url,
            "group_id_": is_integer,
            "group_index_": 0,
            "element_index_": 2,
            "item": "Title 3",
        },
    ]
