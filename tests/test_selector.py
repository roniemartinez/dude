from typing import Dict

import pytest
from playwright import sync_api

from dude import Scraper
from dude.rule import Selector, SelectorType


@pytest.mark.parametrize(
    ("selector", "selector_str", "selector_str_with_type", "expected_type"),
    (
        pytest.param(Selector(selector="test"), "test", "test", SelectorType.ANY, id="any"),
        pytest.param(Selector(css="test"), "test", "css=test", SelectorType.CSS, id="css"),
        pytest.param(Selector(xpath="test"), "test", "xpath=test", SelectorType.XPATH, id="xpath"),
        pytest.param(Selector(text="test"), "test", "text=test", SelectorType.TEXT, id="text"),
        pytest.param(Selector(regex="test"), "test", "text=/test/i", SelectorType.REGEX, id="regex"),
    ),
)
def test_to_str(
    selector: Selector, selector_str: str, selector_str_with_type: str, expected_type: SelectorType
) -> None:
    assert selector.to_str(with_type=False) == selector_str
    assert selector.to_str(with_type=True) == selector_str_with_type
    assert selector.selector_type() == expected_type


def test_invalid_to_str() -> None:
    selector = Selector()
    with pytest.raises(AssertionError):
        selector.to_str()
    with pytest.raises(Exception):
        selector.selector_type()


def test_comparison() -> None:
    selector1 = Selector(css="test")
    selector2 = Selector(xpath="test")
    assert selector1 < selector2


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
