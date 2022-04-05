import logging
from typing import Iterable, Optional, Tuple

import httpx
from httpx import Request

logger = logging.getLogger(__name__)


async def async_http_get(client: httpx.AsyncClient, request: Request) -> Tuple[Optional[str], str]:
    try:
        response = await client.send(request)
        response.raise_for_status()
        return response.text, str(response.url)
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        logger.warning(e)
        return None, str(request.url)


def http_get(client: httpx.Client, request: Request) -> Tuple[Optional[str], str]:
    try:
        response = client.send(request)
        response.raise_for_status()
        return response.text, str(response.url)
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        logger.warning(e)
        return None, str(request.url)


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

    async def _async_block_httpx_request_if_needed(self, request: Request) -> None:
        self._block_httpx_request_if_needed(request)

    def iter_requests(self) -> Iterable[Request]:
        try:
            while True:
                try:
                    url = next(self.iter_urls())  # type: ignore
                    yield Request(method="GET", url=url)
                    continue
                except StopIteration:
                    pass
                yield self.requests.popleft()  # type: ignore
        except IndexError:
            pass
