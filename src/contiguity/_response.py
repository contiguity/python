from http import HTTPStatus

from msgspec import Struct


class ResponseMetadata(Struct):
    id: str
    timestamp: int
    api_version: str
    object: str


class BaseResponse(Struct):
    metadata: ResponseMetadata


class ErrorResponse(BaseResponse):
    error: str
    status: HTTPStatus
