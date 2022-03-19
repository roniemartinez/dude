import asyncio
import itertools
import logging
from typing import Any, AsyncIterable, Callable, Iterable, Optional, Sequence, Tuple
from urllib.parse import urljoin

import httpx
import lxml.html
from httpx._types import ProxiesTypes
from lxml.etree import _Element

from ..base import ScraperAbstract
from ..rule import Selector, SelectorType, rule_grouper, rule_sorter

logger = logging.getLogger(__name__)


class LxmlScraper(ScraperAbstract):
    """
    Scraper using lxml parser backend and HTTPX for requests
    """

    def run(
        self,
        urls: Sequence[str],
        pages: int = 1,
        proxy: ProxiesTypes = None,
        output: Optional[str] = None,
        format: str = "json",
        follow_urls: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Executes lxml-based scraper.

        :param urls: List of website URLs.
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only used when a navigate handler is defined. # noqa
        :param proxy: Proxy settings. (see https://www.python-httpx.org/advanced/#http-proxying)  # noqa
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.
        :param follow_urls: Automatically follow URLs.
        """
        self.update_rule_groups()
        self.urls.clear()
        self.urls.extend(urls)

        logger.info("Using lxml...")
        if self.has_async:
            logger.info("Using async mode...")
            loop = asyncio.get_event_loop()
            # FIXME: Tests fail on Python 3.7 when using asyncio.run()
            loop.run_until_complete(
                self._run_async(pages=pages, proxy=proxy, output=output, format=format, follow_urls=follow_urls)
            )
        else:
            logger.info("Using sync mode...")
            self._run_sync(pages=pages, proxy=proxy, output=output, format=format, follow_urls=follow_urls)

    def _run_sync(
        self,
        pages: int,
        proxy: Optional[ProxiesTypes],
        output: Optional[str],
        format: str,
        follow_urls: bool,
    ) -> None:
        with httpx.Client(proxies=proxy) as client:
            for url in self.iter_urls():
                logger.info("Requesting url %s", url)
                for i in range(1, pages + 1):
                    if url.startswith("file://"):
                        path = self.file_url_to_path(url)
                        with open(path) as f:
                            content = f.read()
                    else:
                        try:
                            response = client.get(url)
                            response.raise_for_status()
                            content = response.text
                        except httpx.HTTPStatusError as e:
                            logger.warning(e)
                            break

                    tree = lxml.html.fromstring(html=content, base_url=url)
                    if follow_urls:
                        self.urls.extend([urljoin(url, link[2]) for link in tree.iterlinks()])
                    self.setup()  # does not do anything yet
                    self.collected_data.extend(self.extract_all(page_number=i, tree=tree, url=url))
                    if i == pages or not self.navigate():
                        break
        self._save(format, output)

    async def _run_async(
        self,
        pages: int,
        proxy: Optional[ProxiesTypes],
        output: Optional[str],
        format: str,
        follow_urls: bool,
    ) -> None:
        async with httpx.AsyncClient(proxies=proxy) as client:
            for url in self.iter_urls():
                logger.info("Requesting url %s", url)
                for i in range(1, pages + 1):
                    if url.startswith("file://"):
                        path = self.file_url_to_path(url)
                        with open(path) as f:
                            content = f.read()
                    else:
                        try:
                            response = await client.get(url)
                            response.raise_for_status()
                            content = response.text
                        except httpx.HTTPStatusError as e:
                            logger.warning(e)
                            break

                    tree = lxml.html.fromstring(html=content, base_url=url)
                    if follow_urls:
                        self.urls.extend([urljoin(url, link[2]) for link in tree.iterlinks()])
                    await self.setup_async()  # does not do anything yet
                    self.collected_data.extend(
                        [data async for data in self.extract_all_async(page_number=i, tree=tree, url=url)]
                    )
                    if i == pages or not await self.navigate_async():
                        break
        self._save(format, output)

    def setup(self) -> None:
        pass

    async def setup_async(self) -> None:
        pass

    def navigate(self) -> bool:
        return False

    async def navigate_async(self) -> bool:
        return False

    def collect_elements(
        self, tree: _Element = None, url: str = None
    ) -> Iterable[Tuple[str, int, int, int, Any, Callable]]:
        assert tree is not None
        assert url is not None

        for group_selector, g in itertools.groupby(
            sorted(self.get_scraping_rules(url), key=rule_sorter), key=rule_grouper
        ):
            rules = list(sorted(g, key=lambda r: r.priority))

            for group_index, group in enumerate(self._get_elements(tree, group_selector)):
                for rule in rules:
                    for element_index, element in enumerate(self._get_elements(group, rule.selector)):
                        yield url, group_index, id(group), element_index, element, rule.handler

    @staticmethod
    def _get_elements(tree: _Element, selector: Selector) -> Iterable[_Element]:
        selector_str = selector.to_str()
        selector_type = selector.selector_type()
        if selector_type in (SelectorType.CSS, SelectorType.ANY):  # assume CSS
            yield from tree.cssselect(selector_str)
        elif selector_type == SelectorType.XPATH:
            yield from tree.xpath(selector_str)
        elif selector_type == SelectorType.TEXT:
            escaped_selector = selector_str.replace('"', '\\"')
            yield from tree.xpath(f".//*[contains(text(), '{escaped_selector}')]")
        elif selector_type == SelectorType.REGEX:
            yield from tree.xpath(
                f".//*[re:test(text(), '{selector_str}', 'i')]",
                namespaces={"re": "http://exslt.org/regular-expressions"},
            )

    async def collect_elements_async(self, **kwargs: Any) -> AsyncIterable[Tuple[str, int, int, int, Any, Callable]]:
        for item in self.collect_elements(**kwargs):
            yield item
