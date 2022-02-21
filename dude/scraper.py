import asyncio
import itertools
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, AsyncIterable, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from playwright import async_api, sync_api
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

from dude.rule import Rule, rule_filter, rule_grouper, rule_sorter
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


class Scraper:
    def __init__(self) -> None:
        self.rules: List[Rule] = []
        self.collected_data: List[ScrapedData] = []
        self.save_rules: Dict[str, Any] = {"json": save_json}
        self.has_async = False

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

    def run(
        self,
        urls: Sequence[str],
        use_bs4: bool = False,
        headless: bool = True,
        browser_type: str = "chromium",
        pages: int = 1,
        proxy: Optional[sync_api.ProxySettings] = None,
        output: Optional[str] = None,
        format: str = "json",
    ) -> None:
        """
        Runs Playwright and finds all the registered selectors.

        The resulting list of ElementHandle will be passed to the registered handler functions where data extraction
        is defined and performed.

        :param urls: List of website URLs.
        :param use_bs4: Use BeautifulSoup.  (default=False)
        :param headless: Enables headless browser. (default=True)
        :param browser_type: Playwright supported browser types ("chromium", "webkit" or "firefox").
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only valid when a navigate handler is defined. # noqa
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.
        :param proxy: Proxy settings. (see https://playwright.dev/python/docs/api/class-apirequest#api-request-new-context-option-proxy)  # noqa
        """
        logger.info("Scraper started...")

        if use_bs4:
            self._run_soup(urls, pages, output, format)

        # FIXME: Too many duplicated code just to support both sync and async
        elif self.has_async:
            logger.info("Using async mode...")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._run_async(urls, headless, browser_type, pages, proxy, output, format))
            # FIXME: Tests fail on Python 3.7 when using asyncio.run()
            # asyncio.run(self._run_async(urls, headless, browser_type, pages, proxy, output, format))
        else:
            logger.info("Using sync mode...")
            self._run_sync(urls, headless, browser_type, pages, proxy, output, format)

    def _run_sync(
        self,
        urls: Sequence[str],
        headless: bool,
        browser_type: str,
        pages: int,
        proxy: Optional[sync_api.ProxySettings],
        output: Optional[str],
        format: str,
    ) -> None:
        with sync_playwright() as p:
            browser = p[browser_type].launch(headless=headless, proxy=proxy)
            page = browser.new_page()
            for url in urls:
                page.goto(url)
                logger.info("Loaded page %s", page.url)
                self._setup(page)

                for i in range(1, pages + 1):
                    current_page = page.url
                    self.collected_data.extend(self._extract_all(page, i))
                    # TODO: Add option to save data per page
                    if i == pages or not self._navigate(page) or current_page == page.url:
                        break
            browser.close()
        self._save(format, output)

    def _run_soup(
        self,
        urls: Sequence[str],
        pages: int,
        output: Optional[str],
        format: str,
    ) -> None:
        import httpx
        from bs4 import BeautifulSoup

        client = httpx.Client()
        for url in urls:
            for i in range(1, pages + 1):
                if url.startswith("file://"):
                    with open(url.removeprefix("file://")) as f:
                        soup = BeautifulSoup(f.read(), "html.parser")
                        self.collected_data.extend(self._soup_extract_all(soup, url, i))
                else:
                    try:
                        response = client.get(url)
                        soup = BeautifulSoup(response.text, "html.parser")
                        self.collected_data.extend(self._soup_extract_all(soup, url, i))
                        if i == pages:
                            break
                    except httpx.HTTPStatusError as e:
                        logger.exception(e)
                        break
        self._save(format, output)

    async def _run_async(
        self,
        urls: Sequence[str],
        headless: bool,
        browser_type: str,
        pages: int,
        proxy: Optional[sync_api.ProxySettings],
        output: Optional[str],
        format: str,
    ) -> None:
        async with async_playwright() as p:
            browser = await p[browser_type].launch(headless=headless, proxy=proxy)
            page = await browser.new_page()
            for url in urls:
                await page.goto(url)
                logger.info("Loaded page %s", page.url)
                await self._setup_async(page)

                for i in range(1, pages + 1):
                    current_page = page.url
                    self.collected_data.extend([data async for data in self._extract_all_async(page, i)])
                    # TODO: Add option to save data per page
                    if i == pages or not await self._navigate_async(page) or current_page == page.url:
                        break
            await browser.close()
        await self._save_async(format, output)

    def _setup(self, page: sync_api.Page) -> None:
        for rule in self._get_setup_rules():
            for element in page.query_selector_all(rule.selector):
                rule.handler(element, page)

    async def _setup_async(self, page: async_api.Page) -> None:
        for rule in self._get_setup_rules():
            for element in await page.query_selector_all(rule.selector):
                await rule.handler(element, page)

    def _navigate(self, page: sync_api.Page) -> bool:
        for rule in self._get_navigate_rules():
            for element in page.query_selector_all(rule.selector):
                rule.handler(element, page)
                logger.info("Navigated to %s", page.url)
                return True
        return False

    async def _navigate_async(self, page: async_api.Page) -> bool:
        for rule in self._get_navigate_rules():
            for element in await page.query_selector_all(rule.selector):
                await rule.handler(element, page)
                logger.info("Navigated to %s", page.url)
                return True
        return False

    def _get_scraping_rules(self) -> Iterable[Rule]:
        return filter(rule_filter(), self.rules)

    def _get_setup_rules(self) -> Iterable[Rule]:
        return sorted(filter(rule_filter(setup=True), self.rules), key=lambda r: r.priority)

    def _get_navigate_rules(self) -> Iterable[Rule]:
        return sorted(filter(rule_filter(navigate=True), self.rules), key=lambda r: r.priority)

    def _collect_elements(
        self, page: sync_api.Page
    ) -> Iterable[Tuple[str, int, int, int, sync_api.ElementHandle, Callable]]:
        """
        Collects all the elements and returns a generator of element-handler pair.

        :param page: Page object.
        """
        page_url = page.url
        for (url_pattern, group_selector), g in itertools.groupby(
            sorted(self._get_scraping_rules(), key=rule_sorter), key=rule_grouper
        ):
            if not re.search(url_pattern, page_url):
                continue

            rules = list(sorted(g, key=lambda r: r.priority))

            for group_index, group in enumerate(page.query_selector_all(group_selector)):
                for rule in rules:
                    for element_index, element in enumerate(group.query_selector_all(rule.selector)):
                        yield page_url, group_index, id(group), element_index, element, rule.handler

    async def _collect_elements_async(
        self, page: async_api.Page
    ) -> AsyncIterable[Tuple[str, int, int, int, async_api.ElementHandle, Callable]]:
        """
        Collects all the elements and returns a generator of element-handler pair.

        :param page: Page object.
        """
        page_url = page.url
        for (url_pattern, group_selector), g in itertools.groupby(
            sorted(self._get_scraping_rules(), key=rule_sorter), key=rule_grouper
        ):
            if not re.search(url_pattern, page_url):
                continue

            rules = list(sorted(g, key=lambda r: r.priority))

            for group_index, group in enumerate(await page.query_selector_all(group_selector)):
                for rule in rules:
                    for element_index, element in enumerate(await group.query_selector_all(rule.selector)):
                        yield page_url, group_index, id(group), element_index, element, rule.handler

    def _soup_collect_elements(self, soup: Any, url: str) -> Iterable[Tuple[str, int, int, int, Any, Callable]]:
        for (url_pattern, group_selector), g in itertools.groupby(
            sorted(self._get_scraping_rules(), key=rule_sorter), key=rule_grouper
        ):
            if not re.search(url_pattern, url):
                continue

            rules = list(sorted(g, key=lambda r: r.priority))

            for group_index, group in enumerate(soup.select(group_selector)):
                for rule in rules:
                    for element_index, element in enumerate(group.select(rule.selector)):
                        if not element:
                            continue
                        yield url, group_index, id(group), element_index, element, rule.handler

    def _extract_all(self, page: sync_api.Page, page_number: int) -> Iterable[ScrapedData]:
        """
        Extracts all the data using the registered handler functions.

        :param page: Page object.
        """
        collected_elements = list(self._collect_elements(page))

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

    def _soup_extract_all(self, soup: Any, url: str, page_number: int) -> Iterable[ScrapedData]:
        """
        Extracts all the data using the registered handler functions.

        """
        collected_elements = list(self._soup_collect_elements(soup, url))

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

    async def _extract_all_async(self, page: async_api.Page, page_number: int) -> AsyncIterable[ScrapedData]:
        """
        Extracts all the data using the registered handler functions.

        :param page: Page object.
        """

        collected_elements = [element async for element in self._collect_elements_async(page)]

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

    def _get_flattened_data(self) -> List[Dict]:
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

        data = self._get_flattened_data()
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

        data = self._get_flattened_data()
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
