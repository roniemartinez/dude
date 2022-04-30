import asyncio
import collections
import itertools
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import (
    Any,
    AsyncIterable,
    Callable,
    Coroutine,
    DefaultDict,
    Deque,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)
from urllib.error import URLError
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

from braveblock import Adblocker

from .rule import Rule, Selector, rule_filter
from .scraped_data import ScrapedData, scraped_data_grouper, scraped_data_sorter
from .storage import save_csv, save_json, save_yaml

logger = logging.getLogger(__name__)


class ScraperBase(ABC):
    """
    Base Scraper class.

    This registers all the selector and saving rules.
    """

    supports_sync = True
    current_url = ""

    def __init__(
        self,
        rules: List[Rule] = None,
        groups: Dict[Callable, Selector] = None,
        save_rules: Dict[Tuple[str, bool], Any] = None,
        events: Optional[DefaultDict] = None,
        has_async: bool = False,
        requests: Optional[Deque] = None,  # only valid for BeautifulSoup4, lxml and Parsel backends
        scraper: Optional["ScraperAbstract"] = None,
    ) -> None:
        self.rules: List[Rule] = rules or []
        self.groups: Dict[Callable, Selector] = groups or {}
        if save_rules is None:
            save_rules = {}
        self.save_rules: Dict[Tuple[str, bool], Any] = {
            ("json", False): save_json,
            ("csv", False): save_csv,
            ("yml", False): save_yaml,
            ("yaml", False): save_yaml,
            **save_rules,
        }
        self.events: DefaultDict = events or collections.defaultdict(list)
        self.has_async = has_async
        self.scraper = scraper
        self.adblock = Adblocker()
        self.urls: Deque = collections.deque()  # allows dynamically appending new URLs for crawling
        self.requests: Deque = requests or collections.deque()  # allows dynamically appending new requests for crawling
        self.allowed_domains: Set[str] = set()
        self.ignore_robots_txt: bool = False

    @abstractmethod
    def run(
        self,
        urls: Sequence[str],
        pages: int,
        proxy: Optional[Any],
        output: Optional[str],
        format: str,
        follow_urls: bool = False,
        save_per_page: bool = False,
        ignore_robots_txt: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Abstract method for executing the scraper.

        :param urls: List of website URLs.
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only used when a navigate handler is defined. # noqa
        :param proxy: Proxy settings.
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.
        :param follow_urls: Automatically follow URLs.
        :param save_per_page: Flag to save data on every page extraction or not. If not, saves all the data at the end.
        :param ignore_robots_txt: Flag to ignore robots.txt.
        """
        self.initialize_scraper(urls)
        self.ignore_robots_txt = ignore_robots_txt

        logger.info("Using %s...", self.__class__.__name__)

        if self.has_async or not self.supports_sync:
            logger.info("Using async mode...")
            loop = asyncio.get_event_loop()
            # FIXME: Tests fail on Python 3.7 when using asyncio.run()
            loop.run_until_complete(
                self.run_async(  # type: ignore
                    pages=pages,
                    proxy=proxy,
                    output=output,
                    format=format,
                    follow_urls=follow_urls,
                    save_per_page=save_per_page,
                    **kwargs,
                )
            )
            if not save_per_page:
                loop.run_until_complete(self._save_async(format, output, save_per_page))  # type: ignore
        else:
            logger.info("Using sync mode...")
            self.run_sync(  # type: ignore
                pages=pages,
                proxy=proxy,
                output=output,
                format=format,
                follow_urls=follow_urls,
                save_per_page=save_per_page,
                **kwargs,
            )
            if not save_per_page:
                self._save(format, output, save_per_page)  # type: ignore

        self.event_shutdown()

    def select(
        self,
        selector: str = None,
        group: str = None,
        setup: bool = False,
        navigate: bool = False,
        url_match: Union[str, Callable] = "*",
        priority: int = 100,
        css: str = None,
        xpath: str = None,
        text: str = None,
        regex: str = None,
        group_css: str = None,
        group_xpath: str = None,
        group_text: str = None,
        group_regex: str = None,
    ) -> Callable:
        """
        Decorator to register a handler function to a given selector.

        :param selector: Element selector (CSS, XPath, text, regex).
        :param group: (Optional) Element selector where the matched element should be grouped. Defaults to ":root".
        :param setup: Flag to register a setup handler.
        :param navigate: Flag to register a navigate handler.
        :param url_match: URL pattern matcher. Run the handler function only when the pattern matches (defaults to *) or when custom function/lambda returns True. # noqa
        :param priority: Priority, the lowest value will be executed first (default 100).
        :param css: CSS selector.
        :param xpath: XPath selector.
        :param text: Text selector.
        :param regex: Regular expression selector
        :param group_css: Group CSS selector.
        :param group_xpath: Group XPath selector.
        :param group_text: Group Text selector.
        :param group_regex: Group Regular expression selector
        """

        def wrapper(func: Callable) -> Union[Callable, Coroutine]:
            sel = Selector(selector=selector, css=css, xpath=xpath, text=text, regex=regex)
            assert sel, "Any of selector, css, xpath, text and regex params should be present."

            if asyncio.iscoroutinefunction(func):
                self.has_async = True

            rule = Rule(
                selector=sel,
                group=Selector(selector=group, css=group_css, xpath=group_xpath, text=group_text, regex=group_regex),
                url_matcher=url_match,
                handler=func,
                setup=setup,
                navigate=navigate,
                priority=priority,
            )
            rules = self.scraper.rules if self.scraper else self.rules
            rules.append(rule)
            return func

        return wrapper

    def group(
        self,
        selector: str = None,
        css: str = None,
        xpath: str = None,
        text: str = None,
        regex: str = None,
    ) -> Callable:
        """
        Decorator to register a handler function to a given group.

        :param selector: Element selector (any of CSS, XPath, text, regex).
        :param css: CSS selector.
        :param xpath: XPath selector.
        :param text: Text selector.
        :param regex: Regular expression selector
        """

        def wrapper(func: Callable) -> Union[Callable, Coroutine]:
            if not (selector or css or xpath or text or regex):
                raise Exception("Any of selector, css, xpath, text or regex selectors must be present")

            if asyncio.iscoroutinefunction(func):
                self.has_async = True

            group = Selector(selector=selector, css=css, xpath=xpath, text=text, regex=regex)
            if not self.scraper:
                if func in self.groups:
                    logger.warning(
                        "Group '%s' already exists for function '%s'. Skipping '%s'...",
                        self.groups[func],
                        func.__name__,
                        group,
                    )
                else:
                    self.groups[func] = group
            else:
                if func in self.scraper.groups:
                    logger.warning(
                        "Group '%s' already exists for function '%s'. Skipping '%s'...",
                        self.scraper.groups[func],
                        func.__name__,
                        group,
                    )
                else:
                    self.scraper.groups[func] = group
            return func

        return wrapper

    def save(self, format: str, is_per_page: bool = False) -> Callable:
        """
        Decorator to register a save function to a format.

        :param format: Format (json, csv, or any custom string).
        :param is_per_page: Flag to identify if func will be called after each page.
        """

        def wrapper(func: Callable) -> Callable:
            if asyncio.iscoroutinefunction(func):
                self.has_async = True

            save_rules = self.scraper.save_rules if self.scraper else self.save_rules
            save_rules[format, is_per_page] = func
            return func

        return wrapper

    def startup(self) -> Callable:
        """
        Decorator to register a function to startup events.

        Startup events are executed before any actual scraping happens to, for example, setup databases, etc.
        """

        def wrapper(func: Callable) -> Callable:
            if asyncio.iscoroutinefunction(func):
                self.has_async = True

            events = self.scraper.events if self.scraper else self.events
            events["startup"].append(func)
            return func

        return wrapper

    def pre_setup(self) -> Callable:
        """
        Decorator to register a function to pre-setup events.

        Pre-setup events are executed after a page is loaded (or HTTP response in case of HTTPX) and
        before running the setup functions.
        """

        def wrapper(func: Callable) -> Callable:
            if asyncio.iscoroutinefunction(func):
                self.has_async = True

            events = self.scraper.events if self.scraper else self.events
            events["pre-setup"].append(func)
            return func

        return wrapper

    def post_setup(self) -> Callable:
        """
        Decorator to register a function to post-setup events.

        Post-setup events are executed after running the setup functions and before the actual web-scraping happens.
        This is useful when "page clean-ups" are done in the setup functions.
        """

        def wrapper(func: Callable) -> Callable:
            if asyncio.iscoroutinefunction(func):
                self.has_async = True

            events = self.scraper.events if self.scraper else self.events
            events["post-setup"].append(func)
            return func

        return wrapper

    def shutdown(self) -> Callable:
        """
        Decorator to register a function to the shutdown events.

        Shutdown events are executed before terminating the application for cleaning up or closing resources like
        files and database sessions.
        """

        def wrapper(func: Callable) -> Callable:
            if asyncio.iscoroutinefunction(func):
                self.has_async = True

            events = self.scraper.events if self.scraper else self.events
            events["shutdown"].append(func)
            return func

        return wrapper

    def start_requests(self) -> Callable:
        """
        Decorator to register custom Request objects.
        """
        from httpx import Request

        def wrapper(func: Callable) -> Callable:
            requests = self.scraper.requests if self.scraper else self.requests
            for request in func():
                assert isinstance(request, Request)
                requests.append(request)
            return func

        return wrapper

    def get_current_url(self) -> str:
        return self.scraper.current_url if self.scraper else self.current_url

    def follow_url(self, url: str) -> None:
        self.scraper.urls.append(url) if self.scraper else self.urls.append(url)

    def iter_urls(self) -> Iterator[str]:
        try:
            while True:
                url = self.urls.popleft()
                if urlparse(url).netloc not in self.allowed_domains:
                    logger.info("URL %s is not in allowed domains.", url)
                    continue
                can_fetch, crawl_delay = self.can_fetch_and_crawl_delay(url)
                if not can_fetch:
                    logger.info("Not allowed to crawl %s", url)
                    continue
                time.sleep(crawl_delay)
                self.current_url = url
                yield url
        except IndexError:
            pass

    def can_fetch_and_crawl_delay(self, url: str) -> Tuple[bool, int]:
        if self.ignore_robots_txt:
            return True, 0
        user_agent = "dude"  # TODO: https://github.com/roniemartinez/dude/issues/63
        # TODO: Store content so as to prevent re-fetching
        robots_url = urljoin(url, "/robots.txt")
        parser = RobotFileParser(url=robots_url)
        try:
            parser.read()
        except URLError:
            parser.parse([""])
        crawl_delay = parser.crawl_delay(user_agent) or 0
        can_fetch = parser.can_fetch(user_agent, url)
        return can_fetch, int(crawl_delay)

    def _update_rule_groups(self) -> Iterable[Rule]:
        for rule in self.rules:
            if rule.group:
                yield rule
            elif rule.handler in self.groups:
                yield rule._replace(group=self.groups[rule.handler])
            else:
                yield rule._replace(group=Selector(selector=":root"))

    def initialize_scraper(self, urls: Sequence[str]) -> None:
        self.rules = [rule for rule in self._update_rule_groups()]
        self.urls = collections.deque(urls)
        self.allowed_domains = {urlparse(url).netloc for url in urls}
        self.event_startup()

    def event_startup(self) -> None:
        """
        Run all startup events
        """
        self.run_event("startup")

    def event_shutdown(self) -> None:
        """
        Run all shutdown events
        """
        self.run_event("shutdown")

    def run_event(self, event_name: str) -> None:
        loop = None
        if self.has_async:
            loop = asyncio.get_event_loop()

        for func in self.events[event_name]:
            if asyncio.iscoroutinefunction(func):
                assert loop is not None
                loop.run_until_complete(func())
            else:
                func()


class ScraperAbstract(ScraperBase):
    def __init__(
        self,
        rules: List[Rule] = None,
        groups: Dict[Callable, Selector] = None,
        save_rules: Dict[Tuple[str, bool], Any] = None,
        events: Optional[DefaultDict] = None,
        has_async: bool = False,
        requests: Optional[Deque] = None,
    ) -> None:
        super(ScraperAbstract, self).__init__(rules, groups, save_rules, events, has_async, requests)
        self.collected_data: List[ScrapedData] = []

    @abstractmethod
    async def run_async(
        self,
        pages: int,
        proxy: Optional[Any],
        output: Optional[str],
        format: str,
        follow_urls: bool,
        save_per_page: bool,
        **kwargs: Any,
    ) -> None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def run_sync(
        self,
        pages: int,
        proxy: Optional[Any],
        output: Optional[str],
        format: str,
        follow_urls: bool,
        save_per_page: bool,
        **kwargs: Any,
    ) -> None:
        raise NotImplementedError  # pragma: no cover

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

    def event_pre_setup(self, *args: Any) -> None:
        """
        Run all pre-setup events.
        """
        for func in self.events["pre-setup"]:
            func(*args)

    def event_post_setup(self, *args: Any) -> None:
        """
        Run all post-setup events.
        """
        for func in self.events["post-setup"]:
            func(*args)

    async def event_pre_setup_async(self, *args: Any) -> None:
        """
        Run all pre-setup events.
        """
        for func in self.events["pre-setup"]:
            await func(*args)

    async def event_post_setup_async(self, *args: Any) -> None:
        """
        Run all post-setup events.
        """
        for func in self.events["post-setup"]:
            await func(*args)

    def extract_all(self, page_number: int, **kwargs: Any) -> Iterable[ScrapedData]:
        """
        Extracts all the data using the registered handler functions.
        """
        collected_elements = list(self.collect_elements(**kwargs))

        for page_url, group_index, group_id, element_index, element, handler in collected_elements:
            data = handler(element)

            if not data:
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

            if not data:
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

    def get_scraping_rules(self, url: str) -> Iterable[Rule]:
        return filter(rule_filter(url), self.rules)

    def get_setup_rules(self, url: str) -> Iterable[Rule]:
        return sorted(filter(rule_filter(url, setup=True), self.rules), key=lambda r: r.priority)

    def get_navigate_rules(self, url: str) -> Iterable[Rule]:
        return sorted(filter(rule_filter(url, navigate=True), self.rules), key=lambda r: r.priority)

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

    def _save(self, format: str, output: Optional[str] = None, save_per_page: bool = False) -> None:
        if output:
            extension = Path(output).suffix.lower()[1:]
            format = extension
        try:
            handler = self.save_rules[format, save_per_page]
            data = self.get_flattened_data()
            if not len(data):
                logger.info(
                    "No data was scraped. Skipped saving %s.",
                    dict(format=format, output=format, save_per_page=save_per_page),
                )
                return
            if handler(data, output):
                self.collected_data.clear()
            else:
                raise Exception("Failed to save output %s.", {"output": output, "format": format})
        except KeyError:
            raise

    async def _save_async(self, format: str, output: Optional[str] = None, save_per_page: bool = False) -> None:
        if output:
            extension = Path(output).suffix.lower()[1:]
            format = extension
        try:
            handler = self.save_rules[format, save_per_page]
            data = self.get_flattened_data()
            if not len(data):
                logger.info(
                    "No data was scraped. Skipped saving %s.",
                    dict(format=format, output=format, save_per_page=save_per_page),
                )
                return
            if asyncio.iscoroutinefunction(handler):
                is_successful = await handler(data, output)
            else:
                is_successful = handler(data, output)
            if is_successful:
                self.collected_data.clear()
            else:
                raise Exception("Failed to save output %s.", {"output": output, "format": format})
        except KeyError:
            raise
