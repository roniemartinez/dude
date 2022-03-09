import asyncio
import itertools
import logging
from typing import Any, AsyncIterable, Callable, Iterable, Optional, Sequence, Tuple, Union

from playwright import async_api, sync_api
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

from .base import ScraperAbstract
from .rule import rule_grouper, rule_sorter

logger = logging.getLogger(__name__)


class PlaywrightScraper(ScraperAbstract):
    """
    Playwright-based scraper
    """

    def run(
        self,
        urls: Sequence[str],
        pages: int = 1,
        proxy: Optional[sync_api.ProxySettings] = None,
        output: Optional[str] = None,
        format: str = "json",
        headless: bool = True,
        browser_type: str = "chromium",
        **kwargs: Any,
    ) -> None:
        """
        Executes Playwright-based scraper.

        :param urls: List of website URLs.
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only used when a navigate handler is defined. # noqa
        :param proxy: Proxy settings. (see https://playwright.dev/python/docs/api/class-apirequest#api-request-new-context-option-proxy)  # noqa
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.

        :param headless: Enables headless browser. (default=True)
        :param browser_type: Playwright supported browser types ("chromium", "webkit" or "firefox").
        """
        self.update_rule_groups()

        logger.info("Using Playwright...")
        if self.has_async:
            logger.info("Using async mode...")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                self._run_async(
                    urls=urls,
                    headless=headless,
                    browser_type=browser_type,
                    pages=pages,
                    proxy=proxy,
                    output=output,
                    format=format,
                )
            )
            # FIXME: Tests fail on Python 3.7 when using asyncio.run()
            # asyncio.run(
            #     self._run_async(
            #         urls=urls,
            #         headless=headless,
            #         browser_type=browser_type,
            #         pages=pages,
            #         proxy=proxy,
            #         output=output,
            #         format=format,
            #     )
            # )
        else:
            logger.info("Using sync mode...")
            self._run_sync(
                urls=urls,
                headless=headless,
                browser_type=browser_type,
                pages=pages,
                proxy=proxy,
                output=output,
                format=format,
            )

    @staticmethod
    def _query_selector_all(
        page_or_element: Union[sync_api.Page, sync_api.ElementHandle], selector: str
    ) -> Iterable[sync_api.ElementHandle]:
        """
        Temporary fix for coverage not counting page.query_selector_all() when used in a for loop.
        """
        yield from page_or_element.query_selector_all(selector)

    def setup(self, page: sync_api.Page = None) -> None:
        """
        Executes setup handlers

        :param page: Page.
        """
        assert page is not None
        for rule in self.get_setup_rules(page.url):
            for element in self._query_selector_all(page, rule.selector.to_str(with_type=True)):
                rule.handler(element, page)

    async def setup_async(self, page: async_api.Page = None) -> None:
        """
        Executes setup handlers

        :param page: Page.
        """
        assert page is not None
        for rule in self.get_setup_rules(page.url):
            for element in await page.query_selector_all(rule.selector.to_str(with_type=True)):
                await rule.handler(element, page)

    def navigate(self, page: sync_api.Page = None) -> bool:
        """
        Executes navigate handlers

        :param page: Page.
        """
        assert page is not None
        for rule in self.get_navigate_rules(page.url):
            for element in self._query_selector_all(page, rule.selector.to_str(with_type=True)):
                rule.handler(element, page)
                logger.info("Navigated to %s", page.url)
                return True
        return False

    async def navigate_async(self, page: async_api.Page = None) -> bool:
        """
        Executes navigate handlers

        :param page: Page.
        """
        assert page is not None
        for rule in self.get_navigate_rules(page.url):
            for element in await page.query_selector_all(rule.selector.to_str(with_type=True)):
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
        # FIXME: Coverage fails to cover anything within this context manager block
        with sync_playwright() as p:
            browser = p[browser_type].launch(headless=headless, proxy=proxy)
            page = browser.new_page()
            self._scrape_sync(page, urls, pages)
            browser.close()
        self._save(format, output)

    def _scrape_sync(self, page: sync_api.Page, urls: Sequence[str], pages: int) -> None:
        for _ in (page.goto(url) for url in urls):
            logger.info("Loaded page %s", page.url)
            self.setup(page=page)

            for i in range(1, pages + 1):
                current_page = page.url
                self.collected_data.extend(self.extract_all(page_number=i, page=page))
                # TODO: Add option to save data per page
                if i == pages or not self.navigate(page=page) or current_page == page.url:
                    break

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
                await self.setup_async(page=page)

                for i in range(1, pages + 1):
                    current_page = page.url
                    self.collected_data.extend(
                        [data async for data in self.extract_all_async(page_number=i, page=page)]
                    )
                    # TODO: Add option to save data per page
                    if i == pages or not await self.navigate_async(page=page) or current_page == page.url:
                        break
            await browser.close()
        await self._save_async(format, output)

    def collect_elements(self, page: sync_api.Page = None) -> Iterable[Tuple[str, int, int, int, Any, Callable]]:
        """
        Collects all the elements and returns a generator of element-handler pair.
        """
        assert page is not None
        page_url = page.url
        for group_selector, g in itertools.groupby(
            sorted(self.get_scraping_rules(page_url), key=rule_sorter), key=rule_grouper
        ):
            rules = list(sorted(g, key=lambda r: r.priority))

            for group_index, group in enumerate(page.query_selector_all(group_selector.to_str(with_type=True))):
                for rule in rules:
                    for element_index, element in enumerate(
                        self._query_selector_all(group, rule.selector.to_str(with_type=True))
                    ):
                        yield page_url, group_index, id(group), element_index, element, rule.handler

    async def collect_elements_async(
        self, page: async_api.Page = None
    ) -> AsyncIterable[Tuple[str, int, int, int, Any, Callable]]:
        """
        Collects all the elements and returns a generator of element-handler pair.
        """
        assert page is not None
        page_url = page.url
        for group_selector, g in itertools.groupby(
            sorted(self.get_scraping_rules(page_url), key=rule_sorter), key=rule_grouper
        ):
            rules = list(sorted(g, key=lambda r: r.priority))
            for group_index, group in enumerate(await page.query_selector_all(group_selector.to_str(with_type=True))):
                for rule in rules:
                    for element_index, element in enumerate(
                        await group.query_selector_all(rule.selector.to_str(with_type=True))
                    ):
                        yield page_url, group_index, id(group), element_index, element, rule.handler
