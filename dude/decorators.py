from collections import defaultdict

SELECTOR_MAP = defaultdict(list)


def selector(sel: str):
    def _selector(func):
        SELECTOR_MAP[sel].append(func)
        return func

    return _selector
