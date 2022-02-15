from collections import defaultdict

SELECTOR_MAP = defaultdict(list)

# TODO: There could be multiple setup and navigate actions
SETUP_ACTION_MAP = {}
# TODO: Add navigate priority value as there can only be one successful navigation.
#  When the priority fails, try the next one.
NAVIGATE_ACTION_MAP = {}


def select(selector: str, setup: bool = False, navigate: bool = False):
    """
    Decorator to register a handler function with given selector.

    :param selector: Element selector (CSS, XPath, text, regex)
    :param setup: Flag to register a setup handler.
    :param navigate: Flag to register a navigate handler.
    :return: Returns the same function, technically.
    """

    def _selector(func):
        if setup:
            SETUP_ACTION_MAP[selector] = func
        elif navigate:
            NAVIGATE_ACTION_MAP[selector] = func
        else:
            SELECTOR_MAP[selector].append(func)
        return func

    return _selector
