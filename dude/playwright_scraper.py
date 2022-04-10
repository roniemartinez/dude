import itertools
import logging
from typing import Any, AsyncIterable, Callable, Dict, Iterable, Optional, Sequence, Tuple, Union
from urllib.parse import urljoin

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
        follow_urls: bool = False,
        save_per_page: bool = False,
        ignore_robots_txt: bool = False,
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
        :param follow_urls: Automatically follow URLs.
        :param save_per_page: Flag to save data on every page extraction or not. If not, saves all the data at the end.
        :param ignore_robots_txt: Flag to ignore robots.txt.

        :param headless: Enables headless browser. (default=True)
        :param browser_type: Playwright supported browser types ("chromium", "webkit" or "firefox").
        """
        super(PlaywrightScraper, self).run(
            urls=urls,
            pages=pages,
            proxy=proxy,
            output=output,
            format=format,
            follow_urls=follow_urls,
            save_per_page=save_per_page,
            ignore_robots_txt=ignore_robots_txt,
            **{**kwargs, "headless": headless, "browser_type": browser_type},
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

        self.event_pre_setup(page)

        for rule in self.get_setup_rules(page.url):
            for element in self._query_selector_all(page, rule.selector.to_str(with_type=True)):
                rule.handler(element, page)

        self.event_post_setup(page)

    async def setup_async(self, page: async_api.Page = None) -> None:
        """
        Executes setup handlers

        :param page: Page.
        """
        assert page is not None

        await self.event_pre_setup_async(page)

        for rule in self.get_setup_rules(page.url):
            for element in await page.query_selector_all(rule.selector.to_str(with_type=True)):
                await rule.handler(element, page)

        await self.event_post_setup_async(page)

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

    @staticmethod
    def _get_launch_kwargs(browser_type: str) -> Dict[str, Any]:
        args = []
        if browser_type == "chromium":
            args.append("--disable-notifications")
        return {"args": args, "firefox_user_prefs": {"dom.webnotifications.enabled": False}}

    def _block_url_if_needed(self, route: Union[sync_api.Route, async_api.Route]) -> Any:
        url = route.request.url
        source_url = (
            route.request.headers.get("referer")
            or route.request.headers.get("origin")
            or route.request.headers.get("host")
            or url
        )
        if self.adblock.check_network_urls(
            url=url,
            source_url=source_url,
            request_type=route.request.resource_type,
        ):
            logger.info("URL %s has been blocked.", url)
            return route.abort()
        return route.continue_()

    def run_sync(
        self,
        pages: int,
        proxy: Optional[sync_api.ProxySettings],
        output: Optional[str],
        format: str,
        follow_urls: bool,
        save_per_page: bool,
        headless: bool = True,
        browser_type: str = "chromium",
        **kwargs: Any,
    ) -> None:
        launch_kwargs = self._get_launch_kwargs(browser_type)
        # FIXME: Coverage fails to cover anything within this context manager block
        with sync_playwright() as p:
            browser = p[browser_type].launch(headless=headless, proxy=proxy, **launch_kwargs)
            page = browser.new_page()
            page.route("**/*", self._block_url_if_needed)
            for url in self.iter_urls():
                logger.info("Requesting url %s", url)
                try:
                    page.goto(url)
                except sync_api.Error as e:
                    logger.warning(e)
                    continue
                logger.info("Loaded page %s", page.url)
                if follow_urls:
                    for link in page.query_selector_all("a"):
                        absolute = urljoin(page.url, link.get_attribute("href"))
                        if absolute.rstrip("/") != page.url.rstrip("/"):
                            self.urls.append(absolute)

                self.setup(page=page)

                for i in range(1, pages + 1):
                    current_page = page.url
                    self.collected_data.extend(self.extract_all(page_number=i, page=page))

                    if save_per_page:
                        self._save(format, output, save_per_page)

                    if i == pages or not self.navigate(page=page) or current_page == page.url:
                        break

            browser.close()

    async def run_async(
        self,
        pages: int,
        proxy: Optional[sync_api.ProxySettings],
        output: Optional[str],
        format: str,
        follow_urls: bool,
        save_per_page: bool,
        headless: bool = True,
        browser_type: str = "chromium",
        **kwargs: Any,
    ) -> None:
        launch_kwargs = self._get_launch_kwargs(browser_type)
        async with async_playwright() as p:
            browser = await p[browser_type].launch(headless=headless, proxy=proxy, **launch_kwargs)
            page = await browser.new_page()
            await page.route("**/*", self._block_url_if_needed)
            for url in self.iter_urls():
                logger.info("Requesting url %s", url)
                try:
                    await page.goto(url)
                except async_api.Error as e:
                    logger.warning(e)
                    continue
                logger.info("Loaded page %s", page.url)
                if follow_urls:
                    for link in await page.query_selector_all("a"):
                        absolute = urljoin(page.url, await link.get_attribute("href"))
                        if absolute.rstrip("/") != page.url.rstrip("/"):
                            self.urls.append(absolute)

                await self.setup_async(page=page)

                for i in range(1, pages + 1):
                    current_page = page.url
                    self.collected_data.extend(
                        [data async for data in self.extract_all_async(page_number=i, page=page)]
                    )

                    if save_per_page:
                        await self._save_async(format, output, save_per_page)

                    if i == pages or not await self.navigate_async(page=page) or current_page == page.url:
                        break
            await browser.close()

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
