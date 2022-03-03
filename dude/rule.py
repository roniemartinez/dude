from typing import Callable, NamedTuple, Optional, Tuple


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

    def __bool__(self) -> bool:
        return (self.selector or self.css or self.xpath or self.text or self.regex) is not None

    def __str__(self) -> str:
        return self.selector or self.css or self.xpath or self.text or self.regex or ""


class Rule(NamedTuple):
    group: Selector
    selector: str
    url_pattern: str
    handler: Callable
    setup: bool
    navigate: bool
    priority: int


def rule_sorter(rule: Rule) -> Tuple[str, Selector, str]:
    return rule.url_pattern, rule.group, rule.selector


def rule_grouper(rule: Rule) -> Tuple[str, Selector]:
    return rule.url_pattern, rule.group


def rule_filter(setup: bool = False, navigate: bool = False) -> Callable:
    def wrapper(rule: Rule) -> bool:
        return rule.setup is setup and rule.navigate is navigate

    return wrapper
