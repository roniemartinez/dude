import logging
import sys
from collections import defaultdict

from playwright.sync_api import Page, sync_playwright

from .decorators import NAVIGATE_ACTION_MAP, SELECTOR_MAP, SETUP_ACTION_MAP, select

__all__ = ["run", "select"]


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def collect_elements(page: Page):
    """
    Collects all the elements and returns a generator of element-handler pair.

    :param page: Page object.
    """
    for sel, funcs in SELECTOR_MAP.items():
        for element in page.query_selector_all(sel):
            for func in funcs:
                yield element, func


def extract_all(page: Page):
    """
    Extracts all the data using the registered handler functions.

    :param page: Page object.
    """

    for element, func in collect_elements(page):
        yield func(element)


def setup(page: Page):
    for sel, func in SETUP_ACTION_MAP.items():
        for handle in page.query_selector_all(sel):
            func(handle, page)


def navigate(page: Page):
    if len(NAVIGATE_ACTION_MAP) == 0:
        return False

    for sel, func in NAVIGATE_ACTION_MAP.items():
        for handle in page.query_selector_all(sel):
            func(handle, page)

    logger.info("Navigated to %s", page.url)

    return True


def run(url: str, headless: bool = True, pages: int = 1) -> None:
    """
    Dude, run!

    Runs Playwright and queries all the registered selectors.
    The resulting list of ElementHandle will be passed to the registered handler functions where data extraction
    is defined and performed.

    :param url: Website URL.
    :param headless: Enables headless browser. (default=True)
    :param pages: Number of pages to visit before exiting.
    :return:
    """
    data = defaultdict(list)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(url)
        logger.info("Loaded page %s", page.url)
        setup(page)
        for i in range(1, pages + 1):
            current_page = page.url
            data[current_page].extend(extract_all(page))
            if i == pages or not navigate(page) or current_page == page.url:
                break
        browser.close()

    # TODO: Store the data somewhere
    import json

    print(json.dumps(data, indent=4))
