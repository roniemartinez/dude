import logging
import sys
from collections import defaultdict

from playwright.sync_api import Page, ProxySettings, sync_playwright

from .decorators import NAVIGATE_ACTION_MAP, SELECTOR_MAP, SETUP_ACTION_MAP, select

__all__ = ["cli", "run", "select"]


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def collect_elements(page: Page):
    """
    Collects all the elements and returns a generator of element-handler pair.

    :param page: Page object.
    """
    for group_selector, selectors in SELECTOR_MAP.items():
        for group_index, group in enumerate(page.query_selector_all(group_selector)):
            for selector, funcs in selectors.items():
                for element_index, element in enumerate(group.query_selector_all(selector)):
                    for func in funcs:
                        yield group_index, id(group), element_index, element, func


def extract_all(page: Page):
    """
    Extracts all the data using the registered handler functions.

    :param page: Page object.
    """

    for group_index, group_id, element_index, element, func in collect_elements(page):
        yield group_id, {
            "group": group_index,
            "element": element_index,
            **func(element),
        }


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


def run(
    url: str,
    headless: bool = True,
    pages: int = 1,
    browser_type: str = "chromium",
    proxy: ProxySettings = None,
) -> None:
    """
    Dude, run!

    Runs Playwright and queries all the registered selectors.
    The resulting list of ElementHandle will be passed to the registered handler functions where data extraction
    is defined and performed.

    :param url: Website URL.
    :param headless: Enables headless browser. (default=True)
    :param pages: Number of pages to visit before exiting.
    :param browser_type: Playwright supported browser types ("chromium", "webkit" or "firefox").
    :param proxy: Proxy settings. (see https://playwright.dev/python/docs/api/class-apirequest#api-request-new-context-option-proxy)
    """
    collected_data = defaultdict(lambda: defaultdict(list))
    with sync_playwright() as p:
        browser = p[browser_type].launch(headless=headless, proxy=proxy)
        page = browser.new_page()
        page.goto(url)
        logger.info("Loaded page %s", page.url)
        setup(page)
        for i in range(1, pages + 1):
            current_page = page.url
            for group, data in extract_all(page):
                collected_data[current_page][group].append(data)
            if i == pages or not navigate(page) or current_page == page.url:
                break
        browser.close()

    # TODO: Store the data somewhere
    import json

    print(json.dumps(collected_data, indent=4))


def cli():
    import argparse
    import importlib.util
    from pathlib import Path

    parser = argparse.ArgumentParser(description="dude uncomplicated data extraction")
    subparsers = parser.add_subparsers(title="subcommands")
    scrape = subparsers.add_parser("scrape", description="Run the dude scraper.", help="Run the dude scraper.")
    # required parameters
    required = scrape.add_argument_group("required arguments")
    required.add_argument(
        "paths",
        metavar="PATH",
        nargs="+",
        type=str,
        help="Path to python file/s containing the handler functions.",
    )
    required.add_argument(
        "--url",
        dest="url",
        type=str,
        required=True,
        help="URL to scrape.",
    )
    # optional parameters
    optional = scrape.add_argument_group("optional arguments")
    optional.add_argument(
        "--headed",
        dest="headed",
        default=False,
        action="store_true",
        help="Run headed browser.",
    )
    optional.add_argument(
        "--browser",
        dest="browser",
        default="chromium",
        choices=["chromium", "webkit", "firefox"],
        help="Browser type to use.",
    )
    optional.add_argument(
        "--proxy-server",
        dest="proxy_server",
        type=str,
        help="Proxy server.",
    )
    optional.add_argument(
        "--proxy-user",
        dest="proxy_user",
        type=str,
        help="Proxy username.",
    )
    optional.add_argument(
        "--proxy-pass",
        dest="proxy_pass",
        type=str,
        help="Proxy password.",
    )
    arguments = parser.parse_args()
    if (arguments.proxy_user or arguments.proxy_pass) and not arguments.proxy_server:
        parser.error("--proxy-user or --proxy-pass requires --proxy-server.")

    for path in arguments.paths:
        module_name = Path(path).stem
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

    proxy = None
    if arguments.proxy_server:
        proxy = ProxySettings(
            server=arguments.proxy_server,
            username=arguments.proxy_user or "",
            password=arguments.proxy_pass or "",
        )

    run(url=arguments.url, headless=not arguments.headed, browser_type=arguments.browser, proxy=proxy)
