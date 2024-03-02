import logging
from random import randint
from typing import Any, Optional, Sequence, Type

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
        follow_urls: bool = False,
        save_per_page: bool = False,
        ignore_robots_txt: bool = False,
        user_agent: str = None,
        # extra args
        parser: str = "playwright",
        headless: bool = True,
        browser_type: str = "chromium",
        **kwargs: Any,
    ) -> None:
        """
        Convenience method to handle switching between different types of parser backends.

        :param urls: List of website URLs.
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only used when a navigate handler is defined. # noqa
        :param proxy: Proxy settings.
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.
        :param follow_urls: Automatically follow URLs.
        :param save_per_page: Flag to save data on every page extraction or not. If not, saves all the data at the end.
        :param ignore_robots_txt: Flag to ignore robots.txt.
        :param user_agent: User agent string

        :param parser: Parser backend ["playwright" (default), "bs4", "parsel, "lxml" or "selenium"]
        :param headless: Enables headless browser. (default=True)
        :param browser_type: Playwright supported browser types ("chromium", "chrome", "webkit", or "firefox").
        """

        logger.info("Scraper started...")

        if not self.scraper:
            scraper_class: Type[ScraperBase]
            if parser == "bs4":
                from .optional.beautifulsoup_scraper import BeautifulSoupScraper

                scraper_class = BeautifulSoupScraper
            elif parser == "parsel":
                from .optional.parsel_scraper import ParselScraper

                scraper_class = ParselScraper
            elif parser == "lxml":
                from .optional.lxml_scraper import LxmlScraper

                scraper_class = LxmlScraper
            elif parser == "selenium":
                from .optional.selenium_scraper import SeleniumScraper

                scraper_class = SeleniumScraper
            else:
                scraper_class = PlaywrightScraper

            self.scraper = scraper_class(
                rules=self.rules,
                groups=self.groups,
                save_rules=self.save_rules,
                events=self.events,
                has_async=self.has_async,
                requests=self.requests,
            )

        if not user_agent:
            logger.info(f"no user agents given, selecting automatically!")
            user_agent = self.get_user_agent()

        if not ignore_robots_txt:
            logger.info(
                f"""robots.txt is currently not ignored.
        {"=" * 80}
        Any rules/restrictions set in a website's robots.txt, will be followed by default.
        To ignore robots.txt, add `--ignore-robots-txt` to CLI arguments or  pass `ignore_robots_txt=True` to `run()`
        {"=" * 80}""",
            )

        self.scraper.run(
            urls=urls,
            pages=pages,
            proxy=proxy,
            output=output,
            format=format,
            follow_urls=follow_urls,
            save_per_page=save_per_page or follow_urls,
            ignore_robots_txt=ignore_robots_txt,
            user_agent=user_agent,
            **{"headless": headless, "browser_type": browser_type},
        )

    def get_user_agent(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
            "Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"
            ]
        return user_agents[randint(0, len(user_agents)-1)]
