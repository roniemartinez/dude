import logging
from typing import Any, Optional, Sequence

from .base import ScraperBase
from .playwright_scraper import PlaywrightScraper

logger = logging.getLogger(__name__)


class Scraper(ScraperBase):
    """
    Convenience class to easily use the available decorators.
    """

    def run(
        self,
        urls: Sequence[str],
        pages: int = 1,
        proxy: Optional[Any] = None,
        output: Optional[str] = None,
        format: str = "json",
        # extra args
        parser: str = "playwright",
        headless: bool = True,
        browser_type: str = "chromium",
    ) -> None:
        """
        Convenience method to handle switching between different types of parsers.

        :param urls: List of website URLs.
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only used when a navigate handler is defined. # noqa
        :param proxy: Proxy settings.
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.

        :param parser: Parser type ["playwright" (default), "bs4", "parsel, "lxml", "pyppeteer" or "selenium"]
        :param headless: Enables headless browser. (default=True)
        :param browser_type: Playwright supported browser types ("chromium", "chrome", "webkit", or "firefox").
        """

        logger.info("Scraper started...")

        if not self.scraper:
            if parser == "bs4":
                from .optional.beautifulsoup_scraper import BeautifulSoupScraper

                self.scraper = BeautifulSoupScraper(
                    rules=self.rules,
                    groups=self.groups,
                    save_rules=self.save_rules,
                    has_async=self.has_async,
                )
            elif parser == "parsel":
                from .optional.parsel_scraper import ParselScraper

                self.scraper = ParselScraper(
                    rules=self.rules,
                    groups=self.groups,
                    save_rules=self.save_rules,
                    has_async=self.has_async,
                )
            elif parser == "lxml":
                from .optional.lxml_scraper import LxmlScraper

                self.scraper = LxmlScraper(
                    rules=self.rules,
                    groups=self.groups,
                    save_rules=self.save_rules,
                    has_async=self.has_async,
                )
            elif parser == "pyppeteer":
                from .optional.pyppeteer_scraper import PyppeteerScraper

                self.scraper = PyppeteerScraper(
                    rules=self.rules,
                    groups=self.groups,
                    save_rules=self.save_rules,
                    has_async=self.has_async,
                )
            elif parser == "selenium":
                from .optional.selenium_scraper import SeleniumScraper

                self.scraper = SeleniumScraper(
                    rules=self.rules,
                    groups=self.groups,
                    save_rules=self.save_rules,
                    has_async=self.has_async,
                )
            else:
                self.scraper = PlaywrightScraper(
                    rules=self.rules,
                    groups=self.groups,
                    save_rules=self.save_rules,
                    has_async=self.has_async,
                )

        self.scraper.run(
            urls=urls,
            pages=pages,
            proxy=proxy,
            output=output,
            format=format,
            **{"headless": headless, "browser_type": browser_type},
        )
