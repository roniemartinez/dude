import itertools
import logging
import re
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence

from playwright.sync_api import Page, ProxySettings, sync_playwright

from dude.rule import Rule, rule_filter, rule_grouper, rule_sorter
from dude.scraped_data import ScrapedData, scraped_data_grouper, scraped_data_sorter

logger = logging.getLogger(__name__)


def save_json(data, output):
    import json

    if output is not None:
        with open(output, "w") as f:
            json.dump(data, f, indent=2)

        logger.info("Data saved to %s", output)
    else:
        json.dump(data, sys.stdout, indent=2)
    return True


class Scraper:
    def __init__(self):
        self.rules: List[Rule] = []
        self.collected_data: List[ScrapedData] = []
        self.save_rules: Dict[str, Callable[[List[Dict], str], bool]] = {"json": save_json}

    def select(
        self,
        selector: str,
        group: str = ":root",
        setup: bool = False,
        navigate: bool = False,
        url: Optional[str] = None,
        priority: int = 100,
    ):
        """
        Decorator to register a handler function with given selector.

        :param selector: Element selector (CSS, XPath, text, regex)
        :param group: (Optional) Element selector where the matched element should be grouped. Defaults to ":root".
        :param setup: Flag to register a setup handler.
        :param navigate: Flag to register a navigate handler.
        :param url: URL pattern. Run the handler function only when the pattern matches (default None).
        :param priority: Priority, the lowest value will be executed first (default 100).
        """

        def wrapper(func):
            url_pattern = url
            if url_pattern is not None:
                url_pattern = re.compile(url_pattern, re.IGNORECASE)
            self.rules.append(
                Rule(
                    selector=selector,
                    group=group,
                    url_pattern=url_pattern,
                    handler=func,
                    setup=setup,
                    navigate=navigate,
                    priority=priority,
                )
            )
            return func

        return wrapper

    def save(self, format: str):
        def wrapper(func):
            self.save_rules[format] = func
            return func

        return wrapper

    def run(
        self,
        urls: Sequence[str],
        headless: bool = True,
        browser_type: str = "chromium",
        pages: int = 1,
        proxy: ProxySettings = None,
        output: Optional[str] = None,
        format: str = "json",
    ) -> None:
        """
        Runs Playwright and finds all the registered selectors.

        The resulting list of ElementHandle will be passed to the registered handler functions where data extraction
        is defined and performed.

        :param urls: List of website URLs.
        :param headless: Enables headless browser. (default=True)
        :param browser_type: Playwright supported browser types ("chromium", "webkit" or "firefox").
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only valid when a navigate handler is defined. # noqa
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to json.
        :param proxy: Proxy settings. (see https://playwright.dev/python/docs/api/class-apirequest#api-request-new-context-option-proxy)  # noqa
        """
        logger.info("Scraper started...")

        with sync_playwright() as p:
            browser = p[browser_type].launch(headless=headless, proxy=proxy)
            page = browser.new_page()
            for url in urls:
                page.goto(url)
                logger.info("Loaded page %s", page.url)
                self.setup(page)

                for i in range(1, pages + 1):
                    current_page = page.url
                    self.collected_data.extend(self._extract_all(page, i))
                    # TODO: Add option to save data per page
                    if i == pages or not self.navigate(page) or current_page == page.url:
                        break
            browser.close()

        self._save(format, output)

    def setup(self, page: Page):
        for rule in self._get_setup_rules():
            for handle in page.query_selector_all(rule.selector):
                rule.handler(handle, page)

    def navigate(self, page: Page):

        for rule in self._get_navigate_rules():
            for handle in page.query_selector_all(rule.selector):
                rule.handler(handle, page)
                logger.info("Navigated to %s", page.url)
                return True

        return False

    def _get_scraping_rules(self):
        return filter(rule_filter(), self.rules)

    def _get_setup_rules(self):
        return sorted(filter(rule_filter(setup=True), self.rules), key=lambda r: r.priority)

    def _get_navigate_rules(self):
        return sorted(filter(rule_filter(navigate=True), self.rules), key=lambda r: r.priority)

    def _collect_elements(self, page: Page):
        """
        Collects all the elements and returns a generator of element-handler pair.

        :param page: Page object.
        """
        page_url = page.url
        for (url_pattern, group_selector), g in itertools.groupby(
            sorted(self._get_scraping_rules(), key=rule_sorter), key=rule_grouper
        ):
            if url_pattern is not None and not url_pattern.search(page_url):
                continue

            rules = list(sorted(g, key=lambda r: r.priority))

            for group_index, group in enumerate(page.query_selector_all(group_selector)):
                for rule in rules:
                    for element_index, element in enumerate(group.query_selector_all(rule.selector)):
                        yield page_url, group_index, id(group), element_index, element, rule.handler

    def _extract_all(self, page: Page, page_number: int):
        """
        Extracts all the data using the registered handler functions.

        :param page: Page object.
        """
        collected_elements = list(self._collect_elements(page))

        for page_url, group_index, group_id, element_index, element, handler in collected_elements:
            data = ScrapedData(
                page_number=page_number,
                page_url=page_url,
                group_id=group_id,
                group_index=group_index,
                element_index=element_index,
                data=handler(element),
            )
            yield data

    def _get_flattened_data(self):
        items = []
        for _, g in itertools.groupby(sorted(self.collected_data, key=scraped_data_sorter), key=scraped_data_grouper):
            item = {}
            for d in g:
                for k, v in d._asdict().items():
                    if k == "data":
                        # FIXME: Keys defined in handler functions might duplicate predefined keys
                        item.update(**v)
                    elif k not in item:
                        item[k] = v
            items.append(item)
        return items

    def _save(self, format: str, output: Optional[str] = None):
        if output:
            extension = Path(output).suffix.lower()[1:]
            format = extension

        data = self._get_flattened_data()
        if self.save_rules[format](data, output):
            self.collected_data.clear()
        else:
            raise Exception("Failed to save output %s.", {"output": output, "format": format})
