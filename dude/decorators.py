from collections import defaultdict

SELECTOR_MAP = defaultdict(list)

# TODO: There could be multiple setup and navigate actions
SETUP_ACTION_MAP = {}
# TODO: Add navigate priority value as there can only be one successful navigation.
#  When the priority fails, try the next one.
NAVIGATE_ACTION_MAP = {}


def selector(sel: str, setup: bool = False, navigate: bool = False):
    def _selector(func):
        if setup:
            SETUP_ACTION_MAP[sel] = func
            return func
        if navigate:
            NAVIGATE_ACTION_MAP[sel] = func
            return func
        SELECTOR_MAP[sel].append(func)
        return func

    return _selector
