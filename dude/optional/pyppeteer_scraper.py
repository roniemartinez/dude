import asyncio
import itertools
import logging
from typing import Any, AsyncIterable, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Union
from urllib.parse import urljoin

from pyppeteer import launch
from pyppeteer.element_handle import ElementHandle
from pyppeteer.errors import PageError
from pyppeteer.network_manager import Request
from pyppeteer.page import Page

from ..base import ScraperAbstract
from ..rule import Selector, SelectorType, rule_grouper, rule_sorter
from ..scraped_data import ScrapedData

logger = logging.getLogger(__name__)


class PyppeteerScraper(ScraperAbstract):
    """
    Pyppeteer-based scraper
    """

    supports_sync = False

    def run(
        self,
        urls: Sequence[str],
        pages: int = 1,
        proxy: Optional[Dict] = None,
        output: Optional[str] = None,
        format: str = "json",
        follow_urls: bool = False,
        save_per_page: bool = False,
        ignore_robots_txt: bool = False,
        headless: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Executes Pyppeteer-based scraper.

        :param urls: List of website URLs.
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only used when a navigate handler is defined. # noqa
        :param proxy: Proxy settings.
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.
        :param follow_urls: Automatically follow URLs.
        :param save_per_page: Flag to save data on every page extraction or not. If not, saves all the data at the end.
        :param ignore_robots_txt: Flag to ignore robots.txt.

        :param headless: Enables headless browser. (default=True)
        """
        super(PyppeteerScraper, self).run(
            urls=urls,
            pages=pages,
            proxy=proxy,
            output=output,
            format=format,
            follow_urls=follow_urls,
            save_per_page=save_per_page,
            ignore_robots_txt=ignore_robots_txt,
            headless=headless,
            **kwargs,
        )

    def setup(self, page: Page = None) -> None:
        raise Exception("Sync is not supported.")  # pragma: no cover

    async def setup_async(self, page: Page = None) -> None:
        """
        Executes setup handlers

        :param page: Page.
        """
        assert page is not None

        await self.event_pre_setup_async(page)

        for rule in self.get_setup_rules(page.url):
            for element in await self._get_elements(page, rule.selector):
                await rule.handler(element, page)

        await self.event_post_setup_async(page)

    def navigate(self, page: Page = None) -> bool:
        raise Exception("Sync is not supported.")  # pragma: no cover

    async def navigate_async(self, page: Page = None) -> bool:
        """
        Executes navigate handlers

        :param page: Page.
        """
        assert page is not None
        for rule in self.get_navigate_rules(page.url):
            for element in await self._get_elements(page, rule.selector):
                await rule.handler(element, page)
                logger.info("Navigated to %s", page.url)
                return True
        return False

    async def _block_url_if_needed(self, request: Request) -> Any:
        url = request.url
        source_url = (
            request.headers.get("referer") or request.headers.get("origin") or request.headers.get("host") or url
        )
        if self.adblock.check_network_urls(
            url=url,
            source_url=source_url,
            request_type=request.resourceType,
        ):
            logger.info("URL %s has been blocked.", url)
            return await request.abort()
        else:
            return await request.continue_()

    def run_sync(
        self,
        pages: int,
        proxy: Optional[Dict],
        output: Optional[str],
        format: str,
        follow_urls: bool,
        save_per_page: bool,
        headless: bool = True,
        **kwargs: Any,
    ) -> None:
        raise NotImplementedError  # pragma: no cover

    async def run_async(
        self,
        pages: int,
        proxy: Optional[Dict],
        output: Optional[str],
        format: str,
        follow_urls: bool,
        save_per_page: bool,
        headless: bool = True,
        **kwargs: Any,
    ) -> None:
        launch_args: Dict[str, Any] = {"headless": headless, "args": ["--disable-notifications"]}
        if proxy:
            launch_args["args"] = [f"--proxy-server={proxy['server']}"]

        browser = await launch(options=launch_args)
        page = await browser.newPage()

        if proxy and proxy["username"] and proxy["password"]:
            await page.authenticate(credentials={"username": proxy["username"], "password": proxy["password"]})

        await page.setRequestInterception(True)
        page.on("request", lambda res: asyncio.ensure_future(self._block_url_if_needed(res)))

        for url in self.iter_urls():
            logger.info("Requesting url %s", url)
            try:
                await page.goto(url)
            except PageError as e:
                logger.warning(e)
                continue
            logger.info("Loaded page %s", page.url)
            if follow_urls:
                for element in await page.querySelectorAll("a"):
                    handle = await element.getProperty("href")
                    href = await handle.jsonValue()
                    if isinstance(href, str):
                        absolute = urljoin(page.url, href)
                        if absolute.rstrip("/") != page.url.rstrip("/"):
                            self.urls.append(absolute)

            await self.setup_async(page=page)

            for i in range(1, pages + 1):
                current_page = page.url
                self.collected_data.extend([data async for data in self.extract_all_async(page_number=i, page=page)])

                if save_per_page:
                    await self._save_async(format, output, save_per_page)

                if i == pages or not await self.navigate_async(page=page) or current_page == page.url:
                    break

        await browser.close()

    def collect_elements(self, page: Page = None) -> Iterable[Tuple[str, int, int, int, Any, Callable]]:
        raise Exception("Sync is not supported.")  # pragma: no cover

    async def extract_all_async(self, page_number: int, **kwargs: Any) -> AsyncIterable[ScrapedData]:
        """
        Extracts all the data using the registered handler functions.

        Modified version for Pyppeteer
        """
        page = kwargs["page"]

        collected_elements = [element async for element in self.collect_elements_async(**kwargs)]

        for page_url, group_index, group_id, element_index, element, handler in collected_elements:
            data = await handler(element, page)

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

    async def collect_elements_async(
        self, page: Page = None
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
            for group_index, group in enumerate(await self._get_elements(page, group_selector)):
                for rule in rules:
                    for element_index, element in enumerate(await self._get_elements(group, rule.selector)):
                        yield page_url, group_index, id(group), element_index, element, rule.handler

    @staticmethod
    async def _get_elements(parent: Union[ElementHandle, Page], selector: Selector) -> List[ElementHandle]:
        selector_str = selector.to_str()
        selector_type = selector.selector_type()
        if selector_type in (SelectorType.CSS, SelectorType.ANY):  # assume CSS
            return await parent.querySelectorAll(selector_str)
        elif selector_type == SelectorType.XPATH:
            return await parent.xpath(selector_str)
        elif selector_type == SelectorType.TEXT:
            escaped_selector = selector_str.replace('"', '\\"')
            return await parent.xpath(f".//*[contains(text(), '{escaped_selector}')]")
        else:
            raise Exception("Regex selector is not supported.")
