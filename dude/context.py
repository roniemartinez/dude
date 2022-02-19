import logging
import sys
from typing import Dict, List, Optional

from .scraper import Scraper

logger = logging.getLogger(__name__)

_scraper = Scraper()
run = _scraper.run
save = _scraper.save
select = _scraper.select


"""
These storage options are not included to the Scraper object.
"""


@save("csv")
def save_csv(data: List[Dict], output: Optional[str]) -> bool:
    """
    Saves data to YAML.

    :param data: List of scraped data.
    :param output: Optional filename. If not provided, prints the data to stdout.
    :return: Success
    """
    if output is not None:
        import csv

        headers = set()
        rows = []
        for item in data:
            headers.update(item.keys())
            rows.append(item)

        with open(output, "w") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        logger.info("Data saved to %s", output)
    else:
        import json

        # TODO: find a better way to present a table if output is not None
        logger.warning("Printing CSV to terminal is currently not supported. Defaulting to json.")
        json.dump(data, sys.stdout, indent=2)
    return True


@save("yaml")
@save("yml")
def save_yaml(data: List[Dict], output: Optional[str]) -> bool:
    """
    Saves data to YAML.

    :param data: List of scraped data.
    :param output: Optional filename. If not provided, prints the data to stdout.
    :return: Success
    """
    import yaml

    if output is not None:
        with open(output, "w") as f:
            yaml.safe_dump(data, f)

        logger.info("Data saved to %s", output)
    else:
        yaml.safe_dump(data, sys.stdout)
    return True
