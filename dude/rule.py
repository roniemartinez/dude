import fnmatch
from enum import Enum, auto
from typing import Callable, NamedTuple, Optional, Tuple


class SelectorType(Enum):
    ANY = auto()
    CSS = auto()
    XPATH = auto()
    TEXT = auto()
    REGEX = auto()


class Selector(NamedTuple):
    selector: Optional[str] = None
    css: Optional[str] = None
    xpath: Optional[str] = None
    text: Optional[str] = None
    regex: Optional[str] = None

    def to_str(self, with_type: bool = False) -> str:
        if not with_type or self.selector:
            selector = self.selector or self.css or self.xpath or self.text or self.regex
            assert selector is not None
            return selector
        if self.css:
            return f"css={self.css}"
        elif self.xpath:
            return f"xpath={self.xpath}"
        elif self.text:
            return f"text={self.text}"
        return f"text=/{self.regex}/i"  # NOTE: Playwright support only

    def selector_type(self) -> SelectorType:
        if self.selector:
            return SelectorType.ANY
        elif self.css:
            return SelectorType.CSS
        elif self.xpath:
            return SelectorType.XPATH
        elif self.text:
            return SelectorType.TEXT
        elif self.regex:
            return SelectorType.REGEX
        raise Exception("No selector specified.")

    def __bool__(self) -> bool:
        return (self.selector or self.css or self.xpath or self.text or self.regex) is not None

    def __str__(self) -> str:
        return self.selector or self.css or self.xpath or self.text or self.regex or ""

    def __repr__(self) -> str:
        return self.to_str(with_type=True)  # pragma: no cover

    def __lt__(self, other: "Selector") -> bool:  # type: ignore
        return self.to_str(with_type=True) < other.to_str(with_type=True)


class Rule(NamedTuple):
    group: Selector
    selector: Selector
    url_pattern: str
    handler: Callable
    setup: bool
    navigate: bool
    priority: int


def rule_sorter(rule: Rule) -> Tuple[Selector, Selector]:
    return rule.group, rule.selector


def rule_grouper(rule: Rule) -> Selector:
    return rule.group


def rule_filter(url: str, setup: bool = False, navigate: bool = False) -> Callable:
    def wrapper(rule: Rule) -> bool:
        return fnmatch.fnmatch(url, rule.url_pattern) and rule.setup is setup and rule.navigate is navigate

    return wrapper
