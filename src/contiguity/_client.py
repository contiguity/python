from __future__ import annotations

from httpx import AsyncClient as HttpxAsyncClient
from httpx import Client as HttpxClient

from ._auth import get_contiguity_token


class ApiError(Exception):
    pass


class ApiClient(HttpxClient):
    def __init__(
        self: ApiClient,
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


class AsyncApiClient(HttpxAsyncClient):
    def __init__(
        self: AsyncApiClient,
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
