from collections import defaultdict

from playwright.sync_api import Page, sync_playwright

from .decorators import NAVIGATE_ACTION_MAP, SELECTOR_MAP, SETUP_ACTION_MAP, selector

__all__ = ["run", "selector"]


def extract_all(page: Page):
    for sel, funcs in SELECTOR_MAP.items():
        for handle in page.query_selector_all(sel):
            for func in funcs:
                yield func(handle)


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
    return True


def run(url: str, headless: bool = True, pages: int = 1) -> None:
    """
    Dude, run!

    Runs Playwright and queries all the registered selectors.
    The resulting list of ElementHandle will be passed to the registered callback functions which should handle data
    extraction.

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
        setup(page)
        for _ in range(pages):
            current_page = page.url
            data[current_page].extend(extract_all(page))
            if not navigate(page) or current_page == page.url:
                break
        browser.close()

    # TODO: Store the data somewhere
    import json

    print(json.dumps(data, indent=4))
