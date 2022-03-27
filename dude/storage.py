import logging
import sys
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


def save_json(data: List[Dict], output: Optional[str]) -> bool:
    """
    Saves data to JSON.

    :param data: List of scraped data.
    :param output: Optional filename. If not provided, prints the data to stdout.
    :return: Success
    """
    if output is not None:
        _save_json(data, output)
    else:
        import json

        json.dump(data, sys.stdout, indent=2)
    return True


def _save_json(data: List[Dict], output: str) -> None:  # pragma: no cover
    import json

    with open(output, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("%d items saved to %s.", len(data), output)


def save_csv(data: List[Dict], output: Optional[str]) -> bool:
    """
    Saves data to CSV.

    :param data: List of scraped data.
    :param output: Optional filename. If not provided, prints the data to stdout.
    :return: Success
    """
    if output is not None:
        _save_csv(data, output)
    else:
        import json

        # TODO: find a better way to present a table if output is not None
        logger.warning("Printing CSV to terminal is currently not supported. Defaulting to json.")
        json.dump(data, sys.stdout, indent=2)
    return True


def save_yaml(data: List[Dict], output: Optional[str]) -> bool:
    """
    Saves data to YAML.

    :param data: List of scraped data.
    :param output: Optional filename. If not provided, prints the data to stdout.
    :return: Success
    """

    if output is not None:
        _save_yaml(data, output)
    else:
        import yaml

        yaml.safe_dump(data, sys.stdout)
    return True


def _save_csv(data: List[Dict], output: str) -> None:  # pragma: no cover
    import csv

    headers: Set[str] = set()
    rows = []
    for item in data:
        headers.update(item.keys())
        rows.append(item)
    with open(output, "w") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(headers))
        writer.writeheader()
        writer.writerows(rows)
    logger.info("%d items saved to %s.", len(data), output)


def _save_yaml(data: List[Dict], output: str) -> None:  # pragma: no cover
    import yaml

    with open(output, "w") as f:
        yaml.safe_dump(data, f)
    logger.info("%d items saved to %s.", len(data), output)
