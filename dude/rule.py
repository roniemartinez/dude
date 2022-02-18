from typing import Callable, NamedTuple, Optional, Pattern, Tuple


class Rule(NamedTuple):
    group: str
    selector: str
    url_pattern: Optional[Pattern]
    handler: Callable
    setup: bool
    navigate: bool


def rule_sorter(rule: Rule) -> Tuple[Optional[Pattern], str, str]:
    return rule.url_pattern, rule.group, rule.selector


def rule_grouper(rule: Rule) -> Tuple[Optional[Pattern], str]:
    return rule.url_pattern, rule.group


def rule_filter(setup: bool = False, navigate: bool = False) -> Callable:
    def wrapper(rule: Rule) -> bool:
        return rule.setup is setup and rule.navigate is navigate

    return wrapper
