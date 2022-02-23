import logging
from typing import Any, Optional, Sequence

from playwright import sync_api

from dude.base import BaseCollector
from dude.beautifulsoup import BeautifulSoupScraper
from dude.playwright import PlaywrightScraper

logger = logging.getLogger(__name__)


class Scraper(BaseCollector):
    """
    Convenience class to easily use the available decorators.
    """

    def run(
        self,
        urls: Sequence[str],
        parser: str = "playwright",
        headless: bool = True,
        browser_type: str = "chromium",
        pages: int = 1,
        proxy: Optional[sync_api.ProxySettings] = None,
        output: Optional[str] = None,
        format: str = "json",
        **kwargs: Any,
    ) -> None:
        logger.info("Scraper started...")

        if not self.scraper:
            if parser == "bs4":
                self.scraper = BeautifulSoupScraper(
                    rules=self.rules,
                    save_rules=self.save_rules,
                    has_async=self.has_async,
                )
            else:
                self.scraper = PlaywrightScraper(
                    rules=self.rules,
                    save_rules=self.save_rules,
                    has_async=self.has_async,
                )

        self.scraper.run(urls, parser, headless, browser_type, pages, proxy, output, format, **kwargs)
