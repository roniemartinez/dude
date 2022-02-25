import asyncio
import itertools
import logging
import re
from typing import Any, AsyncIterable, Callable, Iterable, Optional, Sequence, Tuple

from bs4 import BeautifulSoup
from playwright import sync_api

from .base import ScraperAbstract
from .rule import rule_grouper, rule_sorter

logger = logging.getLogger(__name__)


class BeautifulSoupScraper(ScraperAbstract):
    """
    Scraper using BeautifulSoup4 parser and HTTPX for requests
    """

    def run(
        self,
        urls: Sequence[str],
        pages: int = 1,
        proxy: Optional[sync_api.ProxySettings] = None,
        output: Optional[str] = None,
        format: str = "json",
        **kwargs: Any,
    ) -> None:
        """
        Executes BeautifulSoup4-based scraper.

        :param urls: List of website URLs.
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only used when a navigate handler is defined. # noqa
        :param proxy: Proxy settings. (see https://playwright.dev/python/docs/api/class-apirequest#api-request-new-context-option-proxy)  # noqa
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.
        """
        logger.info("Using BeautifulSoup4...")
        if self.has_async:
            logger.info("Using async mode...")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._run_async(urls=urls, pages=pages, output=output, format=format))
            # FIXME: Tests fail on Python 3.7 when using asyncio.run()
            # asyncio.run(self._run_async((urls=urls, pages=pages, output=output, format=format))
        else:
            logger.info("Using sync mode...")
            self._run_sync(urls=urls, pages=pages, output=output, format=format)

    def _run_sync(
        self,
        urls: Sequence[str],
        pages: int,
        output: Optional[str],
        format: str,
    ) -> None:
        import httpx
        from bs4 import BeautifulSoup

        with httpx.Client() as client:
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

                    soup = BeautifulSoup(content, "html.parser")
                    self.setup()  # does not do anything yet
                    self.collected_data.extend(self.extract_all(page_number=i, soup=soup, url=url))
                    if i == pages or not self.navigate():
                        break
        self._save(format, output)

    async def _run_async(
        self,
        urls: Sequence[str],
        pages: int,
        output: Optional[str],
        format: str,
    ) -> None:
        import httpx
        from bs4 import BeautifulSoup

        async with httpx.AsyncClient() as client:
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

                    soup = BeautifulSoup(content, "html.parser")
                    await self.setup_async()  # does not do anything yet
                    self.collected_data.extend(
                        [data async for data in self.extract_all_async(page_number=i, soup=soup, url=url)]
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
        self, soup: BeautifulSoup = None, url: str = None
    ) -> Iterable[Tuple[str, int, int, int, Any, Callable]]:
        assert soup is not None
        assert url is not None

        for (url_pattern, group_selector), g in itertools.groupby(
            sorted(self.get_scraping_rules(), key=rule_sorter), key=rule_grouper
        ):
            if not re.search(url_pattern, url):
                continue

            rules = list(sorted(g, key=lambda r: r.priority))

            for group_index, group in enumerate(soup.select(group_selector)):
                for rule in rules:
                    for element_index, element in enumerate(group.select(rule.selector)):
                        yield url, group_index, id(group), element_index, element, rule.handler

    async def collect_elements_async(self, **kwargs: Any) -> AsyncIterable[Tuple[str, int, int, int, Any, Callable]]:
        for item in self.collect_elements(**kwargs):
            yield item
