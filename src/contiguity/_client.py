from http import HTTPStatus

from httpx import AsyncClient as HttpxAsyncClient
from httpx import Client as HttpxClient
from httpx import Response

from ._auth import get_contiguity_token
from ._response import ErrorResponse, decode_response


class ContiguityApiError(Exception):
    pass


class BaseApiClient:
    def handle_error(self, response: Response, /, *, fail_message: str = "api request failed") -> None:
        if not HTTPStatus.OK <= response.status_code < HTTPStatus.MULTIPLE_CHOICES:
            data = decode_response(response.content, type=ErrorResponse)
            msg = f"{fail_message}. {response.status_code} {data.error}"
            raise ContiguityApiError(msg)


class ApiClient(HttpxClient, BaseApiClient):
    def __init__(
        self: "ApiClient",
        *,
        base_url: str = "https://api.contiguity.com",
        api_key: str | None = None,
        timeout: int = 5,
    ) -> None:
        if not api_key:
            api_key = get_contiguity_token()
        super().__init__(
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token {api_key}",
            },
            timeout=timeout,
            base_url=base_url,
        )


class AsyncApiClient(HttpxAsyncClient, BaseApiClient):
    def __init__(
        self: "AsyncApiClient",
        *,
        base_url: str = "https://api.contiguity.com",
        api_key: str | None = None,
        timeout: int = 5,
    ) -> None:
        if not api_key:
            api_key = get_contiguity_token()
        super().__init__(
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Token {api_key}",
            },
            timeout=timeout,
            base_url=base_url,
        )
