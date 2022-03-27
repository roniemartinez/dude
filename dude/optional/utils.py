import logging
import platform
from typing import Optional, Tuple

import httpx

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
        except httpx.HTTPStatusError as e:
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
        except httpx.HTTPStatusError as e:
            logger.warning(e)
            return None, url
