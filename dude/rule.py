from typing import Callable, NamedTuple, Tuple


class Rule(NamedTuple):
    group: str
    selector: str
    url_pattern: str
    handler: Callable
    setup: bool
    navigate: bool
    priority: int


def rule_sorter(rule: Rule) -> Tuple[str, str, str]:
    return rule.url_pattern, rule.group, rule.selector


def rule_grouper(rule: Rule) -> Tuple[str, str]:
    return rule.url_pattern, rule.group


def rule_filter(setup: bool = False, navigate: bool = False) -> Callable:
    def wrapper(rule: Rule) -> bool:
        return rule.setup is setup and rule.navigate is navigate

    return wrapper
