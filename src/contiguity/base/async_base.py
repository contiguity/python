import os
from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Any, Generic, Literal, overload
from warnings import warn

import msgspec
from httpx import HTTPStatusError
from httpx import Response as HttpxResponse
from typing_extensions import deprecated

from contiguity._auth import get_data_key, get_project_id
from contiguity._client import AsyncApiClient, ContiguityApiError

from .common import (
    UNSET,
    DataType,
    DefaultItemT,
    ItemT,
    QueryResponse,
    QueryType,
    TimestampType,
    Unset,
    UpdateOperation,
    UpdatePayload,
    Updates,
    check_key,
)
from .exceptions import ItemConflictError, ItemNotFoundError


class AsyncBase(Generic[ItemT]):
    EXPIRES_ATTRIBUTE = "__expires"
    PUT_LIMIT = 30

    @overload
    def __init__(
        self,
        name: str,
        /,
        *,
        item_type: type[ItemT] = Mapping[str, Any],
        data_key: str | None = None,
        project_id: str | None = None,
        host: str | None = None,
        api_version: str = "v1",
    ) -> None: ...

    @overload
    @deprecated("The `project_key` parameter has been renamed to `data_key`.")
    def __init__(
        self,
        name: str,
        /,
        *,
        item_type: type[ItemT] = Mapping[str, Any],
        project_key: str | None = None,
        project_id: str | None = None,
        host: str | None = None,
        api_version: str = "v1",
    ) -> None: ...

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        /,
        *,
        item_type: type[ItemT] = Mapping[str, Any],
        data_key: str | None = None,
        project_key: str | None = None,  # Deprecated.
        project_id: str | None = None,
        host: str | None = None,
        api_version: str = "v1",
    ) -> None:
        if not name:
            msg = f"invalid Base name '{name}'"
            raise ValueError(msg)

        self.name = name
        self.item_type = item_type
        self.data_key = data_key or project_key or get_data_key()
        self.project_id = project_id or get_project_id()
        self.host = host or os.getenv("CONTIGUITY_BASE_HOST") or "api.base.contiguity.co"
        self.api_version = api_version
        self.util = Updates()
        self._client = AsyncApiClient(
            base_url=f"https://{self.host}/{api_version}/{self.project_id}/{self.name}",
            api_key=self.data_key,
            timeout=300,
        )

    @overload
    def _response_as_item_type(
        self,
        response: HttpxResponse,
        /,
        *,
        sequence: Literal[False] = False,
    ) -> ItemT: ...
    @overload
    def _response_as_item_type(
        self,
        response: HttpxResponse,
        /,
        *,
        sequence: Literal[True],
    ) -> Sequence[ItemT]: ...

    def _response_as_item_type(
        self,
        response: HttpxResponse,
        /,
        *,
        sequence: bool = False,
    ) -> ItemT | Sequence[ItemT]:
        try:
            response.raise_for_status()
        except HTTPStatusError as exc:
            raise ContiguityApiError(exc.response.text) from exc
        return msgspec.json.decode(response.content, type=Sequence[self.item_type] if sequence else self.item_type)

    def _insert_expires_attr(
        self,
        item: ItemT | Mapping[str, DataType],
        expire_in: int | None = None,
        expire_at: TimestampType | None = None,
    ) -> dict[str, DataType]:
        if expire_in and expire_at:
            msg = "cannot use both expire_in and expire_at"
            raise ValueError(msg)

        item_dict = msgspec.to_builtins(item) if isinstance(item, msgspec.Struct) else dict(item)

        if not expire_in and not expire_at:
            return item_dict
        if expire_in:
            expire_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expire_in)
        if isinstance(expire_at, datetime):
            expire_at = int(expire_at.replace(microsecond=0).timestamp())
        if not isinstance(expire_at, int):
            msg = "expire_at should be a datetime or int"
            raise TypeError(msg)

        item_dict[self.EXPIRES_ATTRIBUTE] = expire_at
        return item_dict

    @overload
    async def get(self, key: str, /) -> ItemT | None: ...

    @overload
    async def get(self, key: str, /, *, default: ItemT) -> ItemT: ...

    @overload
    async def get(self, key: str, /, *, default: DefaultItemT) -> ItemT | DefaultItemT: ...

    async def get(
        self,
        key: str,
        /,
        *,
        default: ItemT | DefaultItemT | Unset = UNSET,
    ) -> ItemT | DefaultItemT | None:
        key = check_key(key)
        response = await self._client.get(f"/items/{key}")
        if response.status_code == HTTPStatus.NOT_FOUND:
            if not isinstance(default, Unset):
                return default
            msg = (
                "ItemNotFoundError will be raised in the future."
                " To receive None for non-existent keys, set default=None."
            )
            warn(DeprecationWarning(msg), stacklevel=2)
            return None

        return self._response_as_item_type(response, sequence=False)

    async def delete(self, key: str, /) -> None:
        """Delete an item from the Base."""
        key = check_key(key)
        response = await self._client.delete(f"/items/{key}")
        try:
            response.raise_for_status()
        except HTTPStatusError as exc:
            raise ContiguityApiError(exc.response.text) from exc

    async def insert(
        self,
        item: ItemT,
        /,
        *,
        expire_in: int | None = None,
        expire_at: TimestampType | None = None,
    ) -> ItemT:
        item_dict = self._insert_expires_attr(item, expire_in=expire_in, expire_at=expire_at)
        response = await self._client.post("/items", json={"item": item_dict})

        if response.status_code == HTTPStatus.CONFLICT:
            raise ItemConflictError(str(item_dict.get("key")))

        if not (returned_item := self._response_as_item_type(response, sequence=True)):
            msg = "expected a single item, got an empty response"
            raise ContiguityApiError(msg)
        return returned_item[0]

    async def put(
        self,
        *items: ItemT,
        expire_in: int | None = None,
        expire_at: TimestampType | None = None,
    ) -> Sequence[ItemT]:
        """store (put) an item in the database. Overrides an item if key already exists.
        `key` could be provided as function argument or a field in the data dict.
        If `key` is not provided, the server will generate a random 12 chars key.
        """
        if not items:
            return []
        if len(items) > self.PUT_LIMIT:
            msg = f"cannot put more than {self.PUT_LIMIT} items at a time"
            raise ValueError(msg)

        item_dicts = [self._insert_expires_attr(item, expire_in=expire_in, expire_at=expire_at) for item in items]
        response = await self._client.put("/items", json={"items": item_dicts})
        return self._response_as_item_type(response, sequence=True)

    @deprecated("This method will be removed in a future release. You can pass multiple items to `put`.")
    async def put_many(
        self,
        items: Sequence[ItemT],
        /,
        *,
        expire_in: int | None = None,
        expire_at: TimestampType | None = None,
    ) -> Sequence[ItemT]:
        return await self.put(*items, expire_in=expire_in, expire_at=expire_at)

    async def update(
        self,
        updates: Mapping[str, DataType | UpdateOperation],
        /,
        *,
        key: str,
        expire_in: int | None = None,
        expire_at: TimestampType | None = None,
    ) -> ItemT:
        """update an item in the database
        `updates` specifies the attribute names and values to update,add or remove
        `key` is the key of the item to be updated
        """
        key = check_key(key)
        if not updates:
            msg = "no updates provided"
            raise ValueError(msg)

        payload = UpdatePayload.from_updates_mapping(updates)
        payload.set = self._insert_expires_attr(
            payload.set,
            expire_in=expire_in,
            expire_at=expire_at,
        )

        response = await self._client.patch(f"/items/{key}", json={"updates": msgspec.to_builtins(payload)})
        if response.status_code == HTTPStatus.NOT_FOUND:
            raise ItemNotFoundError(key)

        return self._response_as_item_type(response, sequence=False)

    async def query(
        self,
        *queries: QueryType,
        limit: int = 1000,
        last: str | None = None,
    ) -> QueryResponse[ItemT]:
        """fetch items from the database.
        `query` is an optional filter or list of filters. Without filter, it will return the whole db.
        """

        payload = {
            "limit": limit,
            "last_key": last,
        }

        if queries:
            payload["query"] = queries

        response = await self._client.post("/query", json=payload)
        try:
            response.raise_for_status()
        except HTTPStatusError as exc:
            raise ContiguityApiError(exc.response.text) from exc
        return msgspec.json.decode(response.content, type=QueryResponse[self.item_type])

    @deprecated("This method has been renamed to `query` and will be removed in a future release.")
    async def fetch(
        self,
        *queries: QueryType,
        limit: int = 1000,
        last: str | None = None,
    ) -> QueryResponse[ItemT]:
        return await self.query(*queries, limit=limit, last=last)
