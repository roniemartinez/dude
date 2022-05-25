import logging
import sys
from pathlib import Path
from typing import Any

from .context import (  # noqa: F401
    follow_url,
    get_current_url,
    group,
    post_setup,
    pre_setup,
    run,
    save,
    select,
    shutdown,
    start_requests,
    startup,
)
from .scraper import Scraper  # noqa: F401

EXTRA_EXPORTS = []
try:
    from httpx import Request  # noqa: F401

    EXTRA_EXPORTS.append("Request")
except ImportError:  # pragma: no cover
    pass

__all__ = [
    "Scraper",
    "group",
    "run",
    "save",
    "select",
    "startup",
    "shutdown",
    "pre_setup",
    "post_setup",
    "start_requests",
    "get_current_url",
    "follow_url",
] + EXTRA_EXPORTS


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def cli() -> None:  # pragma: no cover
    import argparse
    import importlib.util

    parser = argparse.ArgumentParser(description="dude uncomplicated data extraction")
    parser.add_argument("-V", "--version", dest="version", action="store_true", required=False, help="show version")
    subparsers = parser.add_subparsers(title="subcommands")
    scrape = subparsers.add_parser("scrape", description="Run the dude scraper.", help="Run the dude scraper.")
    # required parameters
    required = scrape.add_argument_group("required arguments")
    required.add_argument(
        "paths",
        metavar="PATH",
        nargs="+",
        type=str,
        help="Path to python file/s containing the handler functions.",
    )
    required.add_argument(
        "--url",
        metavar="URL",
        dest="urls",
        action="append",
        type=str,
        required=False,
        default=[],
        help='Website URL to scrape. Accepts one or more url (e.g. "dude scrape --url <url1> --url <url2> ...")',
    )
    # optional parameters
    optional = scrape.add_argument_group("optional arguments")
    parser_group = optional.add_mutually_exclusive_group()
    parser_group.add_argument(
        "--playwright",
        dest="playwright",
        default=False,
        action="store_true",
        help="Use Playwright.",
    )
    parser_group.add_argument(
        "--bs4",
        dest="bs4",
        default=False,
        action="store_true",
        help="Use BeautifulSoup4.",
    )
    parser_group.add_argument(
        "--parsel",
        dest="parsel",
        default=False,
        action="store_true",
        help="Use Parsel.",
    )
    parser_group.add_argument(
        "--lxml",
        dest="lxml",
        default=False,
        action="store_true",
        help="Use lxml.",
    )
    parser_group.add_argument(
        "--pyppeteer",
        dest="pyppeteer",
        default=False,
        action="store_true",
        help="Use Pyppeteer.",
    )
    parser_group.add_argument(
        "--selenium",
        dest="selenium",
        default=False,
        action="store_true",
        help="Use Selenium.",
    )
    optional.add_argument(
        "--headed",
        dest="headed",
        default=False,
        action="store_true",
        help="Run headed browser.",
    )
    optional.add_argument(
        "--browser",
        dest="browser",
        default="chromium",
        choices=(
            "chromium",
            "firefox",
            "webkit",  # Applies only to Playwright
        ),
        help="Browser type to use.",
    )
    optional.add_argument(
        "--pages",
        dest="pages",
        default=1,
        type=int,
        help="Maximum number of pages to crawl before exiting (default=1). This is only valid when a navigate handler is defined.",  # noqa
    )
    optional.add_argument(
        "--output",
        dest="output",
        type=str,
        help="Output file. If not provided, prints into the terminal.",
    )
    optional.add_argument(
        "--format",
        dest="format",
        default="json",
        type=str,
        help='Output file format. If not provided, uses the extension of the output file or defaults to "json". '
        'Supports "json", "yaml/yml", and "csv" but can be extended using the @save() decorator.',
    )
    optional.add_argument(
        "--proxy-server",
        dest="proxy_server",
        type=str,
        help="Proxy server.",
    )
    optional.add_argument(
        "--proxy-user",
        dest="proxy_user",
        type=str,
        help="Proxy username.",
    )
    optional.add_argument(
        "--proxy-pass",
        dest="proxy_pass",
        type=str,
        help="Proxy password.",
    )
    optional.add_argument(
        "--follow-urls",
        dest="follow_urls",
        default=False,
        action="store_true",
        help="Automatically follow URLs.",
    )
    optional.add_argument(
        "--save-per-page",
        dest="save_per_page",
        default=False,
        action="store_true",
        help="Flag to save data on every page extraction or not. If not, saves all the data at the end."
        "If --follow-urls is set to true, this variable will be automatically set to true.",
    )
    optional.add_argument(
        "--ignore-robots-txt",
        dest="ignore_robots_txt",
        default=False,
        action="store_true",
        help="Flag to ignore robots.txt.",
    )
    arguments = parser.parse_args()

    if arguments.version:
        import pkg_resources

        version = pkg_resources.get_distribution("pydude").version
        print("dude", version)
        return

    if (arguments.proxy_user or arguments.proxy_pass) and not arguments.proxy_server:
        parser.error("--proxy-user or --proxy-pass requires --proxy-server.")

    for path in arguments.paths:
        module_name = Path(path).stem
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

    parser_type = "playwright"
    if arguments.bs4:
        parser_type = "bs4"
    elif arguments.parsel:
        parser_type = "parsel"
    elif arguments.lxml:
        parser_type = "lxml"
    elif arguments.pyppeteer:
        parser_type = "pyppeteer"
    elif arguments.selenium:
        parser_type = "selenium"

    proxy: Any = None
    if arguments.proxy_server:
        if parser_type in ("playwright", "pyppeteer"):
            proxy = {
                "server": arguments.proxy_server,
                "username": arguments.proxy_user or "",
                "password": arguments.proxy_pass or "",
            }
        elif parser_type in ("bs4", "parsel", "lxml"):
            user_info = ""
            if arguments.proxy_user and arguments.proxy_pass:
                user_info = f"{arguments.proxy_user}:{arguments.proxy_pass}@"

            proxy = f"http://{user_info}{arguments.proxy_server}"

    run(
        urls=arguments.urls,
        parser=parser_type,
        headless=not arguments.headed,
        browser_type=arguments.browser,
        pages=arguments.pages,
        proxy=proxy,
        output=arguments.output,
        format=arguments.format,
        follow_urls=arguments.follow_urls,
        save_per_page=arguments.save_per_page,
        ignore_robots_txt=arguments.ignore_robots_txt,
    )
