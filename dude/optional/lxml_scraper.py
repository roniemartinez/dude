import asyncio
import itertools
import logging
from typing import Any, AsyncIterable, Callable, Iterable, Optional, Sequence, Tuple

import httpx
from httpx._types import ProxiesTypes
from lxml import etree
from lxml.etree import _Element

from ..base import ScraperAbstract
from ..rule import Selector, SelectorType, rule_grouper, rule_sorter

logger = logging.getLogger(__name__)


class LxmlScraper(ScraperAbstract):
    """
    Scraper using lxml parser and HTTPX for requests
    """

    def run(
        self,
        urls: Sequence[str],
        pages: int = 1,
        proxy: ProxiesTypes = None,
        output: Optional[str] = None,
        format: str = "json",
        **kwargs: Any,
    ) -> None:
        """
        Executes lxml-based scraper.

        :param urls: List of website URLs.
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only used when a navigate handler is defined. # noqa
        :param proxy: Proxy settings. (see https://www.python-httpx.org/advanced/#http-proxying)  # noqa
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.
        """
        self.update_rule_groups()

        logger.info("Using lxml...")
        if self.has_async:
            logger.info("Using async mode...")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._run_async(urls=urls, pages=pages, proxy=proxy, output=output, format=format))
            # FIXME: Tests fail on Python 3.7 when using asyncio.run()
            # asyncio.run(self._run_async((urls=urls, pages=pages, proxy=proxy, output=output, format=format))
        else:
            logger.info("Using sync mode...")
            self._run_sync(urls=urls, pages=pages, proxy=proxy, output=output, format=format)

    def _run_sync(
        self,
        urls: Sequence[str],
        pages: int,
        proxy: Optional[ProxiesTypes],
        output: Optional[str],
        format: str,
    ) -> None:
        with httpx.Client(proxies=proxy) as client:
            for url in urls:
                for i in range(1, pages + 1):
                    if url.startswith("file://"):
                        with open(url[7:]) as f:
                            content = f.read()
                    else:
                        try:
                            response = client.get(url)
                            response.raise_for_status()
                            content = response.text
                        except httpx.HTTPStatusError as e:
                            logger.exception(e)
                            break

                    tree = etree.HTML(text=content)
                    self.setup()  # does not do anything yet
                    self.collected_data.extend(self.extract_all(page_number=i, tree=tree, url=url))
                    if i == pages or not self.navigate():
                        break
        self._save(format, output)

    async def _run_async(
        self,
        urls: Sequence[str],
        pages: int,
        proxy: Optional[ProxiesTypes],
        output: Optional[str],
        format: str,
    ) -> None:
        async with httpx.AsyncClient(proxies=proxy) as client:
            for url in urls:
                for i in range(1, pages + 1):
                    if url.startswith("file://"):
                        with open(url[7:]) as f:
                            content = f.read()
                    else:
                        try:
                            response = await client.get(url)
                            response.raise_for_status()
                            content = response.text
                        except httpx.HTTPStatusError as e:
                            logger.exception(e)
                            break

                    tree = etree.HTML(text=content)
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
