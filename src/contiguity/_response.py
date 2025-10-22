from collections.abc import Mapping, Sequence
from http import HTTPStatus
from typing import Generic, TypeVar

import msgspec

T = TypeVar("T", bound=msgspec.Struct | Sequence[msgspec.Struct])
_type = type


class ResponseMetadata(msgspec.Struct):
    id: str
    timestamp: int
    api_version: str
    object: str


class RawResponse(ResponseMetadata, Generic[T]):
    data: T


class BaseResponse(msgspec.Struct):
    metadata: ResponseMetadata


class ErrorResponse(BaseResponse):
    error: str
    status: HTTPStatus


def decode_response(content: bytes, /, *, type: type[T]) -> T:
    raw = msgspec.json.decode(content, type=RawResponse[type])
    metadata = ResponseMetadata(
        id=raw.id,
        timestamp=raw.timestamp,
        api_version=raw.api_version,
        object=raw.object,
    )
    data = msgspec.to_builtins(raw.data)
    if not isinstance(data, Mapping):
        msg = f"expected Mapping instance for 'data' field, got {_type(data)}"
        raise TypeError(msg)
    return msgspec.convert({**data, "metadata": metadata}, type=type)
