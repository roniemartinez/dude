import asyncio
import itertools
import logging
import re
from typing import Any, AsyncIterable, Callable, Iterable, Optional, Sequence, Tuple

from playwright import async_api, sync_api
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

from dude.base import AbstractScraper
from dude.rule import rule_grouper, rule_sorter
from dude.scraped_data import ScrapedData

logger = logging.getLogger(__name__)


class PlaywrightScraper(AbstractScraper):
    def run(
        self,
        urls: Sequence[str],
        headless: bool = True,
        browser_type: str = "chromium",
        pages: int = 1,
        proxy: Optional[sync_api.ProxySettings] = None,
        output: Optional[str] = None,
        format: str = "json",
        **kwargs: Any,
    ) -> None:
        if self.has_async:
            logger.info("Using async mode...")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._run_async(urls, headless, browser_type, pages, proxy, output, format))
            # FIXME: Tests fail on Python 3.7 when using asyncio.run()
            # asyncio.run(self._run_async(urls, headless, browser_type, pages, proxy, output, format))
        else:
            logger.info("Using sync mode...")
            self._run_sync(urls, headless, browser_type, pages, proxy, output, format)

    def setup(self, page: sync_api.Page, **kwargs: Any) -> None:
        for rule in self.get_setup_rules():
            for element in page.query_selector_all(rule.selector):
                rule.handler(element, page)

    async def setup_async(self, page: async_api.Page, **kwargs: Any) -> None:
        for rule in self.get_setup_rules():
            for element in await page.query_selector_all(rule.selector):
                await rule.handler(element, page)

    def navigate(self, page: sync_api.Page, **kwargs: Any) -> bool:
        for rule in self.get_navigate_rules():
            for element in page.query_selector_all(rule.selector):
                rule.handler(element, page)
                logger.info("Navigated to %s", page.url)
                return True
        return False

    async def navigate_async(self, page: async_api.Page, **kwargs: Any) -> bool:
        for rule in self.get_navigate_rules():
            for element in await page.query_selector_all(rule.selector):
                await rule.handler(element, page)
                logger.info("Navigated to %s", page.url)
                return True
        return False

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
                self.setup(page)

                for i in range(1, pages + 1):
                    current_page = page.url
                    self.collected_data.extend(self._extract_all(page, i))
                    # TODO: Add option to save data per page
                    if i == pages or not self.navigate(page) or current_page == page.url:
                        break
            browser.close()
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
                await self.setup_async(page)

                for i in range(1, pages + 1):
                    current_page = page.url
                    self.collected_data.extend([data async for data in self._extract_all_async(page, i)])
                    # TODO: Add option to save data per page
                    if i == pages or not await self.navigate_async(page) or current_page == page.url:
                        break
            await browser.close()
        await self._save_async(format, output)

    def _collect_elements(
        self, page: sync_api.Page
    ) -> Iterable[Tuple[str, int, int, int, sync_api.ElementHandle, Callable]]:
        """
        Collects all the elements and returns a generator of element-handler pair.

        :param page: Page object.
        """
        page_url = page.url
        for (url_pattern, group_selector), g in itertools.groupby(
            sorted(self.get_scraping_rules(), key=rule_sorter), key=rule_grouper
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
            sorted(self.get_scraping_rules(), key=rule_sorter), key=rule_grouper
        ):
            if not re.search(url_pattern, page_url):
                continue

            rules = list(sorted(g, key=lambda r: r.priority))

            for group_index, group in enumerate(await page.query_selector_all(group_selector)):
                for rule in rules:
                    for element_index, element in enumerate(await group.query_selector_all(rule.selector)):
                        yield page_url, group_index, id(group), element_index, element, rule.handler

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
