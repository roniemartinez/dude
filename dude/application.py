import logging
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional, Pattern

from playwright.sync_api import Page, ProxySettings, sync_playwright

SUPPORTED_FORMATS = ("json", "csv", "yaml", "yml")

logger = logging.getLogger(__name__)


def flatten(data):
    import itertools

    def key(x):
        return x["group_index"], x["element_index"]

    for page_url, group in data.items():
        for group_id, items in group.items():
            for k, g in itertools.groupby(sorted(items, key=key), lambda x: (x["group_index"], x["element_index"])):
                yield {"page_url": page_url, "group_id": group_id, **{k: v for item in g for k, v in item.items()}}


class Application:
    def __init__(self):
        # TODO: Implement a better way to store:
        #  - Selectors, groups, url patterns and its handler functions
        #  - Setup selectors and its handler functions
        #  - Navigate selectors and its handler functions

        # TODO: There could be multiple setup and navigate actions.
        #  Add navigate priority value as there can only be one successful navigation.
        #  When the priority fails, try the next one.
        #  Priority values can also be applied to setup and scraping handlers.
        self.selector_map = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        self.setup_action_map = {}
        self.navigate_action_map = {}

        self.collected_data = defaultdict(lambda: defaultdict(list))

    def select(
        self,
        selector: str,
        group: str = ":root",
        setup: bool = False,
        navigate: bool = False,
        url: Optional[str] = None,
    ):
        """
        Decorator to register a handler function with given selector.

        :param selector: Element selector (CSS, XPath, text, regex)
        :param group: (Optional) Element selector where the matched element should be grouped. Defaults to ":root".
        :param setup: Flag to register a setup handler.
        :param navigate: Flag to register a navigate handler.
        :param url: URL pattern. Run the handler function only when the pattern matches (default None)
        :return: Returns the same function, technically.
        """

        def wrapper(func):
            if setup:
                self.setup_action_map[selector] = func
            elif navigate:
                self.navigate_action_map[selector] = func
            else:
                url_pattern = url
                if url_pattern is not None:
                    url_pattern = re.compile(url_pattern, re.IGNORECASE)
                self.selector_map[url_pattern][group][selector].append(func)
            return func

        return wrapper

    def run(
        self,
        url: str,
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

        :param url: Website URL.
        :param headless: Enables headless browser. (default=True)
        :param browser_type: Playwright supported browser types ("chromium", "webkit" or "firefox").
        :param pages: Maximum number of pages to crawl before exiting (default=1). This is only valid when a navigate handler is defined. # noqa
        :param output: Output file. If not provided, prints in the terminal.
        :param format: Output file format. If not provided, uses the extension of the output file or defaults to JSON.
        :param proxy: Proxy settings. (see https://playwright.dev/python/docs/api/class-apirequest#api-request-new-context-option-proxy)  # noqa
        """
        logger.info("Scraper started...")

        with sync_playwright() as p:
            browser = p[browser_type].launch(headless=headless, proxy=proxy)
            page = browser.new_page()
            page.goto(url)
            logger.info("Loaded page %s", page.url)
            self.setup(page)
            for i in range(1, pages + 1):
                current_page = page.url
                for group, data in self._extract_all(page):
                    self.collected_data[current_page][group].append(data)
                if i == pages or not self.navigate(page) or current_page == page.url:
                    break
            browser.close()

        self._process_output(format, output)

    def setup(self, page: Page):
        for sel, func in self.setup_action_map.items():
            for handle in page.query_selector_all(sel):
                func(handle, page)

    def navigate(self, page: Page):
        if len(self.navigate_action_map) == 0:
            return False

        for sel, func in self.navigate_action_map.items():
            for handle in page.query_selector_all(sel):
                func(handle, page)

        logger.info("Navigated to %s", page.url)

    def _collect_elements(self, page: Page):
        """
        Collects all the elements and returns a generator of element-handler pair.

        :param page: Page object.
        """
        url_pattern: Pattern
        for url_pattern, groups in self.selector_map.items():
            if url_pattern is not None and not url_pattern.search(page.url):
                continue

            for group_selector, selectors in groups.items():
                for group_index, group in enumerate(page.query_selector_all(group_selector)):
                    for selector, funcs in selectors.items():
                        for element_index, element in enumerate(group.query_selector_all(selector)):
                            for func in funcs:
                                yield group_index, id(group), element_index, element, func

    def _extract_all(self, page: Page):
        """
        Extracts all the data using the registered handler functions.

        :param page: Page object.
        """

        for group_index, group_id, element_index, element, func in self._collect_elements(page):
            yield group_id, {
                "group_index": group_index,
                "element_index": element_index,
                **func(element),
            }

        return True

    def _process_output(self, format, output):
        if output:
            extension = Path(output).suffix.lower()[1:]
            if extension in SUPPORTED_FORMATS:
                format = extension

        if format == "csv":
            self._process_csv(output)
        elif format in ("yaml", "yml"):
            self._process_yml(output)
        else:
            self._process_json(output)

    def _process_json(self, output):
        import json

        if output is not None:
            with open(output, "w") as f:
                json.dump(list(flatten(self.collected_data)), f, indent=2)

            logger.info("Data saved to %s", output)
        else:
            json.dump(list(flatten(self.collected_data)), sys.stdout, indent=2)

    def _process_yml(self, output):
        import yaml

        if output is not None:
            with open(output, "w") as f:
                yaml.safe_dump(list(flatten(self.collected_data)), f)

            logger.info("Data saved to %s", output)

        else:
            yaml.safe_dump(list(flatten(self.collected_data)), sys.stdout)

    def _process_csv(self, output):
        if output is not None:
            import csv

            headers = set()
            rows = []
            for data in flatten(self.collected_data):
                headers.update(data.keys())
                rows.append(data)

            with open(output, "w") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)

            logger.info("Data saved to %s", output)
        else:
            # TODO: find a better way to present a table if output is not None
            logger.warning("Printing CSV to terminal is currently not supported. Defaulting to json.")
            self._process_json(output)
