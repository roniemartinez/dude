import logging

from .scraper import Scraper

logger = logging.getLogger(__name__)

_scraper = Scraper()
group = _scraper.group
run = _scraper.run
save = _scraper.save
select = _scraper.select
startup = _scraper.startup
shutdown = _scraper.shutdown
pre_setup = _scraper.pre_setup
post_setup = _scraper.post_setup
start_requests = _scraper.start_requests
get_current_url = _scraper.get_current_url
follow_url = _scraper.follow_url
