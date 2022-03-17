import asyncio
import itertools
import logging
import os
from typing import Any, AsyncIterable, Callable, Iterable, Optional, Sequence, Tuple, Union

from braveblock import Adblocker
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from seleniumwire.request import Request
from seleniumwire.webdriver import Chrome, Firefox
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.utils import ChromeType

from ..base import ScraperAbstract
from ..rule import Selector, SelectorType, rule_grouper, rule_sorter

logger = logging.getLogger(__name__)


class SeleniumScraper(ScraperAbstract):
    """
    Selenium-based scraper
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(SeleniumScraper, self).__init__(*args, **kwargs)
        self.adblock = Adblocker()

    def run(
        self,
        urls: Sequence[str],
        pages: int = 1,
        proxy: Optional[Any] = None,
        output: Optional[str] = None,
        format: str = "json",
        follow_urls: bool = False,
        headless: bool = True,
        browser_type: str = "chromium",
        **kwargs: Any,
    ) -> None:
        """
        Executes Selenium-based scraper.

        :param urls: List of website URLs.
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only used when a navigate handler is defined. # noqa
        :param proxy: Proxy settings.
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.
        :param follow_urls: Automatically follow URLs.

        :param headless: Enables headless browser. (default=True)
        :param browser_type: Selenium supported browser types ("chromium", "firefox").
        """
        self.update_rule_groups()
        self.urls.clear()
        self.urls.extend(urls)

        logger.info("Using Selenium...")
        if self.has_async:
            logger.info("Using async mode...")
            loop = asyncio.get_event_loop()
            # FIXME: Tests fail on Python 3.7 when using asyncio.run()
            loop.run_until_complete(
                self._run_async(
                    headless=headless,
                    browser_type=browser_type,
                    pages=pages,
                    proxy=proxy,
                    output=output,
                    format=format,
                )
            )
        else:
            logger.info("Using sync mode...")
            self._run_sync(
                headless=headless,
                browser_type=browser_type,
                pages=pages,
                proxy=proxy,
                output=output,
                format=format,
            )

    def setup(self, driver: WebDriver = None) -> None:
        """
        Executes setup handlers

        :param driver: Web Driver.
        """
        assert driver is not None
        for rule in self.get_setup_rules(driver.current_url):
            for element in self._get_elements(driver, rule.selector):
                rule.handler(element, driver)

    async def setup_async(self, driver: WebDriver = None) -> None:
        """
        Executes setup handlers

        :param driver: Web Driver.
        """
        assert driver is not None
        for rule in self.get_setup_rules(driver.current_url):
            for element in self._get_elements(driver, rule.selector):
                if asyncio.iscoroutinefunction(rule.handler):
                    await rule.handler(element, driver)
                else:
                    rule.handler(element, driver)

    def navigate(self, driver: WebDriver = None) -> bool:
        """
        Executes navigate handlers

        :param driver: WebDriver.
        """
        assert driver is not None
        for rule in self.get_navigate_rules(driver.current_url):
            for element in self._get_elements(driver, rule.selector):
                rule.handler(element, driver)
                logger.info("Navigated to %s", driver.current_url)
                return True
        return False

    async def navigate_async(self, driver: WebDriver = None) -> bool:
        """
        Executes navigate handlers

        :param driver: WebDriver.
        """
        assert driver is not None
        for rule in self.get_navigate_rules(driver.current_url):
            for element in self._get_elements(driver, rule.selector):
                if asyncio.iscoroutinefunction(rule.handler):
                    await rule.handler(element, driver)
                else:
                    rule.handler(element, driver)
                logger.info("Navigated to %s", driver.current_url)
                return True
        return False

    def _run_sync(
        self,
        headless: bool,
        browser_type: str,
        pages: int,
        proxy: Optional[Any],
        output: Optional[str],
        format: str,
    ) -> None:
        driver = self._get_driver(browser_type, headless)

        for url in self.urls:
            driver.get(url)
            logger.info("Loaded page %s", driver.current_url)
            self.setup(driver=driver)

            for i in range(1, pages + 1):
                current_page = driver.current_url
                self.collected_data.extend(self.extract_all(page_number=i, driver=driver))
                # TODO: Add option to save data per page
                if i == pages or not self.navigate(driver=driver) or current_page == driver.current_url:
                    break

        driver.close()
        self._save(format, output)

    async def _run_async(
        self,
        headless: bool,
        browser_type: str,
        pages: int,
        proxy: Optional[Any],
        output: Optional[str],
        format: str,
    ) -> None:
        driver = self._get_driver(browser_type, headless)

        for url in self.urls:
            driver.get(url)
            logger.info("Loaded page %s", driver.current_url)
            await self.setup_async(driver=driver)

            for i in range(1, pages + 1):
                current_page = driver.current_url
                self.collected_data.extend(
                    [data async for data in self.extract_all_async(page_number=i, driver=driver)]
                )
                # TODO: Add option to save data per page
                if i == pages or not await self.navigate_async(driver=driver) or current_page == driver.current_url:
                    break

        driver.close()
        await self._save_async(format, output)

    def _block_url_if_needed(self, request: Request) -> None:
        url = request.url
        source_url = (
            request.headers.get("referer") or request.headers.get("origin") or request.headers.get("host") or url
        )
        if self.adblock.check_network_urls(
            url=url,
            source_url=source_url,
            request_type=request.headers.get("sec-fetch-dest") or "other",
        ):
            logger.info("URL %s has been blocked.", url)
            request.abort()

    def _get_driver(self, browser_type: str, headless: bool) -> WebDriver:
        # TODO: Add more drivers: https://github.com/SergeyPirogov/webdriver_manager#webdriver-manager-for-python
        if browser_type == "firefox":
            executable_path = GeckoDriverManager().install()
            firefox_options = FirefoxOptions()
            firefox_options.headless = headless
            firefox_options.set_preference("dom.webnotifications.enabled", False)
            driver = Firefox(service=FirefoxService(executable_path=executable_path), options=firefox_options)
        else:
            chrome_options = ChromeOptions()
            chrome_options.headless = headless
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-notifications")
            executable_path = ChromeDriverManager(
                chrome_type=ChromeType.CHROMIUM, version=os.getenv("CHROMEDRIVER_VERSION", "latest")
            ).install()
            driver = Chrome(service=ChromeService(executable_path=executable_path), options=chrome_options)

        driver.implicitly_wait(10)
        driver.request_interceptor = self._block_url_if_needed

        return driver

    def collect_elements(self, driver: WebDriver = None) -> Iterable[Tuple[str, int, int, int, Any, Callable]]:
        """
        Collects all the elements and returns a generator of element-handler pair.
        """
        assert driver is not None
        page_url = driver.current_url
        for group_selector, g in itertools.groupby(
            sorted(self.get_scraping_rules(page_url), key=rule_sorter), key=rule_grouper
        ):
            rules = list(sorted(g, key=lambda r: r.priority))

            for group_index, group in enumerate(self._get_elements(driver, group_selector)):
                for rule in rules:
                    for element_index, element in enumerate(self._get_elements(group, rule.selector)):
                        yield page_url, group_index, id(group), element_index, element, rule.handler

    async def collect_elements_async(self, **kwargs: Any) -> AsyncIterable[Tuple[str, int, int, int, Any, Callable]]:
        for item in self.collect_elements(**kwargs):
            yield item

    @staticmethod
    def _get_elements(parent: Union[WebDriver, WebElement], selector: Selector) -> Iterable[WebElement]:
        selector_str = selector.to_str()
        selector_type = selector.selector_type()
        if selector_type in (SelectorType.CSS, SelectorType.ANY):  # assume CSS
            yield from parent.find_elements(by=By.CSS_SELECTOR, value=selector_str)
        elif selector_type == SelectorType.XPATH:
            yield from parent.find_elements(by=By.XPATH, value=selector_str)
        elif selector_type == SelectorType.TEXT:
            escaped_selector = selector_str.replace('"', '\\"')
            yield from parent.find_elements(by=By.XPATH, value=f".//*[contains(text(), '{escaped_selector}')]")
        elif selector_type == SelectorType.REGEX:
            raise Exception("Regex selector is not supported.")
