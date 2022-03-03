import pytest

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
