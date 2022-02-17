import re
from collections import defaultdict
from typing import Optional

# TODO: Implement a better way to store:
#  - Selectors, groups, url patterns and handler functions
#  - Setup selector and handler
#  - Navigate selector and handler
#
# TODO: There could be multiple setup and navigate actions.
#  Add navigate priority value as there can only be one successful navigation.
#  When the priority fails, try the next one.
#  Priority values can also be applied to setup and scraping handlers.
SELECTOR_MAP = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
SETUP_ACTION_MAP = {}
NAVIGATE_ACTION_MAP = {}


def select(selector: str, group: str = ":root", setup: bool = False, navigate: bool = False, url: Optional[str] = None):
    """
    Decorator to register a handler function with given selector.

    :param selector: Element selector (CSS, XPath, text, regex)
    :param group: (Optional) Element selector where the matched element should be grouped. Defaults to ":root".
    :param setup: Flag to register a setup handler.
    :param navigate: Flag to register a navigate handler.
    :param url: URL pattern. Run the handler function only when the pattern matches (default None)
    :return: Returns the same function, technically.
    """

    def _selector(func):
        if setup:
            SETUP_ACTION_MAP[selector] = func
        elif navigate:
            NAVIGATE_ACTION_MAP[selector] = func
        else:
            url_pattern = url
            if url_pattern is not None:
                url_pattern = re.compile(url_pattern, re.IGNORECASE)
            SELECTOR_MAP[url_pattern][group][selector].append(func)
        return func

    return _selector
