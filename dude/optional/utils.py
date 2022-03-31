import logging
import platform
from typing import Optional, Tuple

import httpx
from httpx import Request

logger = logging.getLogger(__name__)


def file_url_to_path(url: str) -> str:
    if platform.system() == "Windows":
        path = url[8:].replace("/", "\\")
    else:
        path = url[7:]
    return path


def get_file_content(url: str) -> Optional[str]:
    path = file_url_to_path(url)
    try:
        with open(path) as f:
            content = f.read()
        return content
    except FileNotFoundError as e:
        logger.warning(e)
        return None


async def async_http_get(client: httpx.AsyncClient, url: str) -> Tuple[Optional[str], str]:
    if url.startswith("file://"):
        content = get_file_content(url)
        return content, url
    else:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text, str(response.url)
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger.warning(e)
            return None, url


def http_get(client: httpx.Client, url: str) -> Tuple[Optional[str], str]:
    if url.startswith("file://"):
        content = get_file_content(url)
        return content, url
    else:
        try:
            response = client.get(url)
            response.raise_for_status()
            return response.text, str(response.url)
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger.warning(e)
            return None, url


class HTTPXMixin:
    def _block_httpx_request_if_needed(self, request: Request) -> None:
        url = str(request.url)
        source_url = (
            request.headers.get("referer") or request.headers.get("origin") or request.headers.get("host") or url
        )
        if self.adblock.check_network_urls(  # type: ignore
            url=url,
            source_url=source_url,
            request_type=request.headers.get("sec-fetch-dest") or "other",
        ):
            logger.info("URL %s has been blocked.", url)
            raise httpx.RequestError(message=f"URL {url} has been blocked.", request=request)
