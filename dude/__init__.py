from playwright.sync_api import sync_playwright

from .decorators import SELECTOR_MAP, selector

__all__ = ["run", "selector"]


def run(url: str, headless: bool = True) -> None:
    """
    Dude, run!

    Runs Playwright and queries all the registered selectors.
    The resulting list of ElementHandle will be passed to the registered callback functions which should handle data
    extraction.

    :param url:
    :param headless:
    :return:
    """
    data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(url)
        for sel, funcs in SELECTOR_MAP.items():
            for handle in page.query_selector_all(sel):
                data.extend([func(handle) for func in funcs])
        browser.close()

    # TODO: Store the data somewhere
    from pprint import pprint

    pprint(data)
