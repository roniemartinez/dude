import itertools
import logging
from typing import Any, AsyncIterable, Callable, Iterable, Optional, Sequence, Tuple, Union

from playwright.async_api import ProxySettings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from ..base import ScraperAbstract
from ..rule import Selector, SelectorType, rule_grouper, rule_sorter

logger = logging.getLogger(__name__)


class SeleniumScraper(ScraperAbstract):
    """
    Selenium-based scraper
    """

    def run(
        self,
        urls: Sequence[str],
        pages: int = 1,
        proxy: Optional[ProxySettings] = None,
        output: Optional[str] = None,
        format: str = "json",
        headless: bool = True,
        browser_type: str = "safari",
        **kwargs: Any,
    ) -> None:
        """
        Executes Selenium-based scraper.

        :param urls: List of website URLs.
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only used when a navigate handler is defined. # noqa
        :param proxy: Proxy settings. (see https://playwright.dev/python/docs/api/class-apirequest#api-request-new-context-option-proxy)  # noqa
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.

        :param headless: Enables headless browser. (default=True)
        :param browser_type: Selenium supported browser types ("safari", "chromium", "firefox").
        """
        self.update_rule_groups()

        logger.info("Using Selenium...")
        logger.info("Using sync mode...")
        self._run_sync(
            urls=urls,
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
                rule.handler(element)

    async def setup_async(self, element: WebDriver = None) -> None:
        raise Exception("Async is not supported.")  # pragma: no cover

    def navigate(self, driver: WebDriver = None) -> bool:
        """
        Executes navigate handlers

        :param driver: WebDriver.
        """
        assert driver is not None
        for rule in self.get_navigate_rules(driver.current_url):
            for element in self._get_elements(driver, rule.selector):
                rule.handler(element)
                logger.info("Navigated to %s", driver.current_url)
                return True
        return False

    async def navigate_async(self, driver: WebDriver = None) -> bool:
        raise Exception("Async is not supported.")  # pragma: no cover

    def _run_sync(
        self,
        urls: Sequence[str],
        headless: bool,
        browser_type: str,
        pages: int,
        proxy: Optional[ProxySettings],
        output: Optional[str],
        format: str,
    ) -> None:
        driver: WebDriver
        if browser_type == "chromium":
            driver = webdriver.Chrome()
        elif browser_type == "firefox":
            driver = webdriver.Firefox()
        else:
            driver = webdriver.Safari()

        for url in urls:
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

    async def collect_elements_async(
        self, driver: WebDriver = None
    ) -> AsyncIterable[Tuple[str, int, int, int, Any, Callable]]:
        yield "", 0, 0, 0, 0, str  # HACK: mypy does not identify this as AsyncIterable  # pragma: no cover
        raise Exception("Async is not supported.")  # pragma: no cover

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
