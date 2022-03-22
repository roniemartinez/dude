import logging

from .scraper import Scraper
from .storage import save_csv, save_yaml

logger = logging.getLogger(__name__)

_scraper = Scraper()
group = _scraper.group
run = _scraper.run
save = _scraper.save
select = _scraper.select
startup = _scraper.startup
pre_setup = _scraper.pre_setup
post_setup = _scraper.post_setup


"""
These storage options are not included by default to the Scraper class.
"""

save("csv")(save_csv)
save("yaml")(save_yaml)
save("yml")(save_yaml)
