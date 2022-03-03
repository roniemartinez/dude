import logging
import sys
from pathlib import Path

from playwright.sync_api import ProxySettings

from .context import group, run, save, select  # noqa: F401
from .scraper import Scraper  # noqa: F401

__al__ = ["Scraper", "group", "run", "save", "select"]


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
        required=True,
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
        choices=("chromium", "webkit", "firefox"),
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

    proxy = None
    if arguments.proxy_server:
        proxy = ProxySettings(  # type: ignore
            server=arguments.proxy_server,
            username=arguments.proxy_user or "",
            password=arguments.proxy_pass or "",
        )

    parser_type = "playwright"
    if arguments.bs4:
        parser_type = "bs4"

    run(
        urls=arguments.urls,
        parser=parser_type,
        headless=not arguments.headed,
        browser_type=arguments.browser,
        pages=arguments.pages,
        proxy=proxy,
        output=arguments.output,
        format=arguments.format,
    )
