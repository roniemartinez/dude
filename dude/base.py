import asyncio
import itertools
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, AsyncIterable, Callable, Coroutine, Dict, Iterable, List, Optional, Sequence, Tuple, Union

from playwright import sync_api

from .rule import Rule, rule_filter
from .scraped_data import ScrapedData, scraped_data_grouper, scraped_data_sorter
from .storage import save_json

logger = logging.getLogger(__name__)


class ScraperBase(ABC):
    """
    Base Scraper class.

    This registers all the selector and saving rules.
    """

    def __init__(
        self,
        rules: List[Rule] = None,
        save_rules: Dict[str, Any] = None,
        has_async: bool = False,
        scraper: Optional["ScraperAbstract"] = None,
    ) -> None:
        self.rules: List[Rule] = rules or []
        self.save_rules: Dict[str, Any] = save_rules or {"json": save_json}
        self.has_async = has_async
        self.scraper = scraper

    @abstractmethod
    def run(
        self,
        urls: Sequence[str],
        pages: int,
        proxy: Optional[sync_api.ProxySettings],
        output: Optional[str],
        format: str,
    ) -> None:
        """
        Abstract method for executing the scraper.

        :param urls: List of website URLs.
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only used when a navigate handler is defined. # noqa
        :param proxy: Proxy settings. (see https://playwright.dev/python/docs/api/class-apirequest#api-request-new-context-option-proxy)  # noqa
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.
        """
        raise NotImplementedError  # pragma: no cover

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
        Decorator to register a handler function to a given selector.

        :param selector: Element selector (CSS, XPath, text, regex)
        :param group: (Optional) Element selector where the matched element should be grouped. Defaults to ":root".
        :param setup: Flag to register a setup handler.
        :param navigate: Flag to register a navigate handler.
        :param url: URL pattern. Run the handler function only when the pattern matches (default None).
        :param priority: Priority, the lowest value will be executed first (default 100).
        """

        def wrapper(func: Callable) -> Union[Callable, Coroutine]:
            if asyncio.iscoroutinefunction(func):
                self.has_async = True

            rule = Rule(
                selector=selector,
                group=group,
                url_pattern=url,
                handler=func,
                setup=setup,
                navigate=navigate,
                priority=priority,
            )
            if not self.scraper:
                self.rules.append(rule)
            else:
                self.scraper.rules.append(rule)
            return func

        return wrapper

    def save(self, format: str) -> Callable:
        """
        Decorator to register a save function to a format.

        :param format: Format (json, csv, or any custom string).
        """

        def wrapper(func: Callable) -> Callable:
            if asyncio.iscoroutinefunction(func):
                self.has_async = True

            if not self.scraper:
                self.save_rules[format] = func
            else:
                self.scraper.save_rules[format] = func
            return func

        return wrapper


class ScraperAbstract(ScraperBase):
    def __init__(self, rules: List[Rule] = None, save_rules: Dict[str, Any] = None, has_async: bool = False) -> None:
        super(ScraperAbstract, self).__init__(rules, save_rules, has_async)
        self.collected_data: List[ScrapedData] = []

    @abstractmethod
    def setup(self) -> None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def setup_async(self) -> None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def navigate(self) -> bool:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def navigate_async(self) -> bool:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def collect_elements(self) -> Iterable[Tuple[str, int, int, int, Any, Callable]]:
        """
        Collects all the elements and returns a generator of element-handler pair.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def collect_elements_async(self) -> AsyncIterable[Tuple[str, int, int, int, Any, Callable]]:
        """
        Collects all the elements and returns a generator of element-handler pair.
        """

        yield "", 0, 0, 0, 0, str  # HACK: mypy does not identify this as AsyncIterable  # pragma: no cover
        raise NotImplementedError  # pragma: no cover

    def extract_all(self, page_number: int, **kwargs: Any) -> Iterable[ScrapedData]:
        """
        Extracts all the data using the registered handler functions.
        """
        collected_elements = list(self.collect_elements(**kwargs))

        for page_url, group_index, group_id, element_index, element, handler in collected_elements:
            data = handler(element)
            if not len(data):
                continue
            scraped_data = ScrapedData(
                page_number=page_number,
                page_url=page_url,
                group_id=group_id,
                group_index=group_index,
                element_index=element_index,
                data=data,
            )
            yield scraped_data

    async def extract_all_async(self, page_number: int, **kwargs: Any) -> AsyncIterable[ScrapedData]:
        """
        Extracts all the data using the registered handler functions.
        """

        collected_elements = [element async for element in self.collect_elements_async(**kwargs)]

        for page_url, group_index, group_id, element_index, element, handler in collected_elements:
            data = await handler(element)

            if not len(data):
                continue

            scraped_data = ScrapedData(
                page_number=page_number,
                page_url=page_url,
                group_id=group_id,
                group_index=group_index,
                element_index=element_index,
                data=data,
            )
            yield scraped_data

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
                        item[f"_{k}"] = v
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
