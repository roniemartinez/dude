import itertools
import logging
import re
from typing import Any, Callable, Iterable, Optional, Sequence, Tuple

from dude.base import AbstractScraper
from dude.rule import rule_grouper, rule_sorter
from dude.scraped_data import ScrapedData

logger = logging.getLogger(__name__)


class BeautifulSoupScraper(AbstractScraper):
    def run(
        self,
        urls: Sequence[str],
        pages: int,
        output: Optional[str],
        format: str,
        **kwargs: Any,
    ) -> None:
        import httpx
        from bs4 import BeautifulSoup

        with httpx.Client() as client:
            for url in urls:
                for i in range(1, pages + 1):
                    if url.startswith("file://"):
                        with open(url.removeprefix("file://")) as f:
                            soup = BeautifulSoup(f.read(), "html.parser")
                            self.collected_data.extend(self._soup_extract_all(soup, url, i))
                            if i == pages:
                                break
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

    def setup(self, *kwargs: Any) -> None:
        pass

    async def setup_async(self, *kwargs: Any) -> None:
        pass

    def navigate(self, *kwargs: Any) -> bool:
        pass

    async def navigate_async(self, *kwargs: Any) -> bool:
        pass

    def _soup_collect_elements(self, soup: Any, url: str) -> Iterable[Tuple[str, int, int, int, Any, Callable]]:
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
