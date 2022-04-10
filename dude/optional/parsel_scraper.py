import itertools
import logging
from typing import Any, AsyncIterable, Callable, Iterable, Optional, Sequence, Tuple
from urllib.parse import urljoin

import httpx
from httpx._types import ProxiesTypes
from parsel import Selector as ParselSelector

from ..base import ScraperAbstract
from ..rule import Selector, SelectorType, rule_grouper, rule_sorter
from .utils import HTTPXMixin, async_http_get, http_get

logger = logging.getLogger(__name__)


class ParselScraper(ScraperAbstract, HTTPXMixin):
    """
    Scraper using Parsel parser backend and HTTPX for requests
    """

    def run(
        self,
        urls: Sequence[str],
        pages: int = 1,
        proxy: ProxiesTypes = None,
        output: Optional[str] = None,
        format: str = "json",
        follow_urls: bool = False,
        save_per_page: bool = False,
        ignore_robots_txt: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Executes Parsel-based scraper.

        :param urls: List of website URLs.
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only used when a navigate handler is defined. # noqa
        :param proxy: Proxy settings. (see https://www.python-httpx.org/advanced/#http-proxying)  # noqa
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.
        :param follow_urls: Automatically follow URLs.
        :param save_per_page: Flag to save data on every page extraction or not. If not, saves all the data at the end.
        :param ignore_robots_txt: Flag to ignore robots.txt.
        """
        super(ParselScraper, self).run(
            urls=urls,
            pages=pages,
            proxy=proxy,
            output=output,
            format=format,
            follow_urls=follow_urls,
            save_per_page=save_per_page,
            ignore_robots_txt=ignore_robots_txt,
            **kwargs,
        )

    def run_sync(
        self,
        pages: int,
        proxy: Optional[ProxiesTypes],
        output: Optional[str],
        format: str,
        follow_urls: bool,
        save_per_page: bool,
        **kwargs: Any,
    ) -> None:
        with httpx.Client(proxies=proxy, event_hooks={"request": [self._block_httpx_request_if_needed]}) as client:
            for request in self.iter_requests():
                logger.info("Requesting url %s - %s", request.method, request.url)
                for i in range(1, pages + 1):
                    content, url = http_get(client, request)
                    if not content:
                        break

                    selector = ParselSelector(content, base_url=url)
                    if follow_urls:
                        for link in selector.root.iterlinks():
                            absolute = urljoin(url, link[2])
                            if absolute.rstrip("/") != url.rstrip("/"):
                                self.urls.append(absolute)

                    self.setup(selector)

                    self.collected_data.extend(self.extract_all(page_number=i, selector=selector, url=url))

                    if save_per_page:
                        self._save(format, output, save_per_page)

                    if i == pages or not self.navigate():
                        break

    async def run_async(
        self,
        pages: int,
        proxy: Optional[ProxiesTypes],
        output: Optional[str],
        format: str,
        follow_urls: bool,
        save_per_page: bool,
        **kwargs: Any,
    ) -> None:
        async with httpx.AsyncClient(
            proxies=proxy, event_hooks={"request": [self._async_block_httpx_request_if_needed]}
        ) as client:
            for request in self.iter_requests():
                logger.info("Requesting url %s - %s", request.method, request.url)
                for i in range(1, pages + 1):
                    content, url = await async_http_get(client, request)
                    if not content:
                        break

                    selector = ParselSelector(content, base_url=url)
                    if follow_urls:
                        for link in selector.root.iterlinks():
                            absolute = urljoin(url, link[2])
                            if absolute.rstrip("/") != url.rstrip("/"):
                                self.urls.append(absolute)

                    await self.setup_async(selector)

                    self.collected_data.extend(
                        [data async for data in self.extract_all_async(page_number=i, selector=selector, url=url)]
                    )

                    if save_per_page:
                        await self._save_async(format, output, save_per_page)

                    if i == pages or not await self.navigate_async():
                        break

    def setup(self, selector: ParselSelector = None) -> None:
        """
        This will only call the pre-setup and post-setup events if extra actions are needed to the selector object.
        :param selector: Selector object
        """
        assert selector is not None
        self.event_pre_setup(selector)
        self.event_post_setup(selector)

    async def setup_async(self, selector: ParselSelector = None) -> None:
        """
        This will only call the pre-setup and post-setup events if extra actions are needed to the selector object.
        :param selector: Selector object
        """
        assert selector is not None
        await self.event_pre_setup_async(selector)
        await self.event_post_setup_async(selector)

    def navigate(self) -> bool:
        return False

    async def navigate_async(self) -> bool:
        return False

    def collect_elements(
        self, selector: ParselSelector = None, url: str = None
    ) -> Iterable[Tuple[str, int, int, int, Any, Callable]]:
        assert selector is not None
        assert url is not None

        for group_selector, g in itertools.groupby(
            sorted(self.get_scraping_rules(url), key=rule_sorter), key=rule_grouper
        ):
            rules = list(sorted(g, key=lambda r: r.priority))

            for group_index, group in enumerate(self._get_elements(selector, group_selector)):
                for rule in rules:
                    for element_index, element in enumerate(self._get_elements(group, rule.selector)):
                        yield url, group_index, id(group), element_index, element, rule.handler

    @staticmethod
    def _get_elements(parsel_selector: ParselSelector, selector: Selector) -> Iterable[ParselSelector]:
        selector_str = selector.to_str()
        selector_type = selector.selector_type()
        if selector_type in (SelectorType.CSS, SelectorType.ANY):  # assume CSS
            yield from parsel_selector.css(selector_str)
        elif selector_type == SelectorType.XPATH:
            yield from parsel_selector.xpath(selector_str)
        elif selector_type == SelectorType.TEXT:
            yield from parsel_selector.xpath(".//*[contains(text(), $string)]/text()", string=selector_str)
        elif selector_type == SelectorType.REGEX:
            yield from parsel_selector.re(selector_str)

    async def collect_elements_async(self, **kwargs: Any) -> AsyncIterable[Tuple[str, int, int, int, Any, Callable]]:
        for item in self.collect_elements(**kwargs):
            yield item
