import asyncio
import itertools
import logging
import re
from typing import Any, AsyncIterable, Callable, Iterable, Optional, Sequence, Tuple

from playwright import sync_api

from dude.base import BaseScraper
from dude.rule import rule_grouper, rule_sorter

logger = logging.getLogger(__name__)


class BeautifulSoupScraper(BaseScraper):
    def run(
        self,
        urls: Sequence[str],
        parser: str = "bs4",
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
            loop.run_until_complete(self._run_async(urls=urls, pages=pages, output=output, format=format))
            # FIXME: Tests fail on Python 3.7 when using asyncio.run()
            # asyncio.run(self._run_async(urls, headless, browser_type, pages, proxy, output, format))
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
                            soup = BeautifulSoup(f.read(), "html.parser")
                            self.collected_data.extend(self.extract_all(page_number=i, soup=soup, url=url))
                            if i == pages:
                                break
                    else:
                        try:
                            response = client.get(url)
                            soup = BeautifulSoup(response.text, "html.parser")
                            self.collected_data.extend(self.extract_all(page_number=i, soup=soup, url=url))
                            if i == pages:
                                break
                        except httpx.HTTPStatusError as e:
                            logger.exception(e)
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
                            soup = BeautifulSoup(f.read(), "html.parser")
                            self.collected_data.extend(
                                [data async for data in self.extract_all_async(page_number=i, soup=soup, url=url)]
                            )
                            if i == pages:
                                break
                    else:
                        try:
                            response = await client.get(url)
                            soup = BeautifulSoup(response.text, "html.parser")
                            self.collected_data.extend(
                                [data async for data in self.extract_all_async(page_number=i, soup=soup, url=url)]
                            )
                            if i == pages:
                                break
                        except httpx.HTTPStatusError as e:
                            logger.exception(e)
                            break
        self._save(format, output)

    def setup(self, **kwargs: Any) -> None:
        pass

    async def setup_async(self, **kwargs: Any) -> None:
        pass

    def navigate(self, **kwargs: Any) -> bool:
        return False

    async def navigate_async(self, **kwargs: Any) -> bool:
        return False

    def collect_elements(self, **kwargs: Any) -> Iterable[Tuple[str, int, int, int, Any, Callable]]:
        soup = kwargs["soup"]
        url = kwargs["url"]

        for (url_pattern, group_selector), g in itertools.groupby(
            sorted(self.get_scraping_rules(), key=rule_sorter), key=rule_grouper
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

    async def collect_elements_async(self, **kwargs: Any) -> AsyncIterable[Tuple[str, int, int, int, Any, Callable]]:
        for item in self.collect_elements(**kwargs):
            yield item
