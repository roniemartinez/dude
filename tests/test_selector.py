from typing import Dict

import pytest
from playwright import sync_api

from dude import Scraper
from dude.rule import Selector


@pytest.mark.parametrize(
    ("group", "selector_str", "selector_str_with_type"),
    (
        (Selector(selector="test"), "test", "test"),
        (Selector(css="test"), "test", "css=test"),
        (Selector(xpath="test"), "test", "xpath=test"),
        (Selector(text="test"), "test", "text=test"),
        (Selector(regex="test"), "test", "text=/test/i"),
    ),
)
def test_to_str(group: Selector, selector_str: str, selector_str_with_type: str) -> None:
    assert group.to_str(with_type=False) == selector_str
    assert group.to_str(with_type=True) == selector_str_with_type


def test_invalid_to_str() -> None:
    group = Selector()
    with pytest.raises(AssertionError):
        group.to_str()


def test_no_selector(scraper_application: Scraper) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 0

    with pytest.raises(AssertionError):

        @scraper_application.select()
        def invalid(element: sync_api.ElementHandle) -> Dict:
            return {}


def test_different_selector_types(scraper_application: Scraper) -> None:
    assert scraper_application.has_async is False
    assert len(scraper_application.rules) == 0

    @scraper_application.select(selector="test", group="group")
    @scraper_application.select(css="test", group_css="group")
    @scraper_application.select(xpath="test", group_xpath="group")
    @scraper_application.select(text="test", group_text="group")
    @scraper_application.select(regex="test", group_regex="group")
    def handler(element: sync_api.ElementHandle) -> Dict:
        return {}

    assert len(scraper_application.rules) == 5
