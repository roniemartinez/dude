import asyncio
import itertools
import json
import logging
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

from dude.rule import Rule, rule_filter
from dude.scraped_data import ScrapedData, scraped_data_grouper, scraped_data_sorter

logger = logging.getLogger(__name__)


def save_json(data: List[Dict], output: Optional[str]) -> bool:
    if output is not None:
        _save_json(data, output)
    else:
        json.dump(data, sys.stdout, indent=2)
    return True


def _save_json(data: List[Dict], output: str) -> None:  # pragma: no cover
    with open(output, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Data saved to %s", output)


class AbstractScraper(ABC):
    def __init__(self) -> None:
        self.rules: List[Rule] = []
        self.collected_data: List[ScrapedData] = []
        self.save_rules: Dict[str, Any] = {"json": save_json}
        self.has_async = False

    @abstractmethod
    def run(self, **kwargs: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def setup(self, **kwargs: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def setup_async(self, **kwargs: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def navigate(self, **kwargs: Any) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def navigate_async(self, **kwargs: Any) -> bool:
        raise NotImplementedError

    def select(
        self,
        selector: str,
        group: str = ":root",
        setup: bool = False,
        navigate: bool = False,
        url: str = "",
        priority: int = 100,
    ) -> Callable:
        """
        Decorator to register a handler function with given selector.

        :param selector: Element selector (CSS, XPath, text, regex)
        :param group: (Optional) Element selector where the matched element should be grouped. Defaults to ":root".
        :param setup: Flag to register a setup handler.
        :param navigate: Flag to register a navigate handler.
        :param url: URL pattern. Run the handler function only when the pattern matches (default None).
        :param priority: Priority, the lowest value will be executed first (default 100).
        """

        def wrapper(func: Callable) -> Callable:
            if asyncio.iscoroutinefunction(func):
                self.has_async = True

            self.rules.append(
                Rule(
                    selector=selector,
                    group=group,
                    url_pattern=url,
                    handler=func,
                    setup=setup,
                    navigate=navigate,
                    priority=priority,
                )
            )
            return func

        return wrapper

    def save(self, format: str) -> Callable:
        def wrapper(func: Callable) -> Callable:
            if asyncio.iscoroutinefunction(func):
                self.has_async = True

            self.save_rules[format] = func
            return func

        return wrapper

    def get_scraping_rules(self) -> Iterable[Rule]:
        return filter(rule_filter(), self.rules)

    def get_setup_rules(self) -> Iterable[Rule]:
        return sorted(filter(rule_filter(setup=True), self.rules), key=lambda r: r.priority)

    def get_navigate_rules(self) -> Iterable[Rule]:
        return sorted(filter(rule_filter(navigate=True), self.rules), key=lambda r: r.priority)

    def get_flattened_data(self) -> List[Dict]:
        items = []
        for _, g in itertools.groupby(sorted(self.collected_data, key=scraped_data_sorter), key=scraped_data_grouper):
            item: Dict = {}
            for d in g:
                for k, v in d._asdict().items():
                    if k == "data":
                        # FIXME: Keys defined in handler functions might duplicate predefined keys
                        item.update(**v)
                    elif k not in item:
                        item[k] = v
            items.append(item)
        return items

    def _save(self, format: str, output: Optional[str] = None) -> None:
        if output:
            extension = Path(output).suffix.lower()[1:]
            format = extension

        data = self.get_flattened_data()
        try:
            if self.save_rules[format](data, output):
                self.collected_data.clear()
            else:
                raise Exception("Failed to save output %s.", {"output": output, "format": format})
        except KeyError:
            self.collected_data.clear()
            raise

    async def _save_async(self, format: str, output: Optional[str] = None) -> None:
        if output:
            extension = Path(output).suffix.lower()[1:]
            format = extension

        data = self.get_flattened_data()
        try:
            handler = self.save_rules[format]
            if asyncio.iscoroutinefunction(handler):
                is_successful = await handler(data, output)
            else:
                is_successful = handler(data, output)
            if is_successful:
                self.collected_data.clear()
            else:
                raise Exception("Failed to save output %s.", {"output": output, "format": format})
        except KeyError:
            self.collected_data.clear()
            raise
