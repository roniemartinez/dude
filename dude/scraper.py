import logging
from typing import Any, Optional, Sequence

from playwright import sync_api

from dude.beautifulsoup import BeautifulSoupScraper
from dude.playwright import PlaywrightScraper

logger = logging.getLogger(__name__)


class Scraper(PlaywrightScraper, BeautifulSoupScraper):
    def run(
        self,
        urls: Sequence[str],
        use_bs4: bool = False,
        headless: bool = True,
        browser_type: str = "chromium",
        pages: int = 1,
        proxy: Optional[sync_api.ProxySettings] = None,
        output: Optional[str] = None,
        format: str = "json",
        **kwargs: Any,
    ) -> None:
        """
        Runs Playwright and finds all the registered selectors.

        The resulting list of ElementHandle will be passed to the registered handler functions where data extraction
        is defined and performed.

        :param urls: List of website URLs.
        :param use_bs4: Use BeautifulSoup.  (default=False)
        :param headless: Enables headless browser. (default=True)
        :param browser_type: Playwright supported browser types ("chromium", "webkit" or "firefox").
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only valid when a navigate handler is defined. # noqa
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.
        :param proxy: Proxy settings. (see https://playwright.dev/python/docs/api/class-apirequest#api-request-new-context-option-proxy)  # noqa
        """
        logger.info("Scraper started...")

        if use_bs4:
            BeautifulSoupScraper.run(self, urls, pages, output, format)
        else:
            PlaywrightScraper.run(self, urls, headless, browser_type, pages, proxy, output, format)
