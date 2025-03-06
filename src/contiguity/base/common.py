from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Generic, TypeVar, Union
from urllib.parse import quote

import msgspec

from .exceptions import InvalidKeyError

TimestampType = Union[int, datetime]
DataType = Union[list["DataType"], dict[str, "DataType"], str, bool, int, float, None]
QueryType = Mapping[str, DataType]

ItemT = TypeVar("ItemT", bound=msgspec.Struct)
DefaultItemT = TypeVar("DefaultItemT")


class Unset:
    pass


UNSET = Unset()


class BaseItem(msgspec.Struct):
    key: str


class QueryResponse(msgspec.Struct, Generic[ItemT]):
    count: int = 0
    last_key: Union[str, None] = None
    items: Sequence[ItemT] = []


class UpdateOperation:
    pass


class Trim(UpdateOperation):
    pass


class Increment(UpdateOperation):
    def __init__(self, value: int = 1, /) -> None:
        self.value = value


class Append(UpdateOperation):
    def __init__(self, value: DataType, /) -> None:
        if isinstance(value, (list, tuple)):
            self.value = value
        else:
            self.value = [value]


class Prepend(Append):
    pass


class Updates:
    @staticmethod
    def trim() -> Trim:
        return Trim()

    @staticmethod
    def increment(value: int = 1, /) -> Increment:
        return Increment(value)

    @staticmethod
    def append(value: DataType, /) -> Append:
        return Append(value)

    @staticmethod
    def prepend(value: DataType, /) -> Prepend:
        return Prepend(value)


class UpdatePayload(msgspec.Struct):
    set: dict[str, DataType] = {}
    increment: dict[str, int] = {}
    append: dict[str, Sequence[DataType]] = {}
    prepend: dict[str, Sequence[DataType]] = {}
    delete: list[str] = []

    @classmethod
    def from_updates_mapping(cls, updates: Mapping[str, "DataType | UpdateOperation"], /) -> "UpdatePayload":
        set = {}
        increment = {}
        append = {}
        prepend = {}
        delete = []
        for attr, value in updates.items():
            if isinstance(value, UpdateOperation):
                if isinstance(value, Trim):
                    delete.append(attr)
                elif isinstance(value, Increment):
                    increment[attr] = value.value
                # Prepend must be checked before Append because it's a subclass of Append.
                elif isinstance(value, Prepend):
                    prepend[attr] = value.value
                elif isinstance(value, Append):
                    append[attr] = value.value
            else:
                set[attr] = value
        return cls(
            set=set,
            increment=increment,
            append=append,
            prepend=prepend,
            delete=delete,
        )


def check_key(key: str, /) -> str:
    if not key:
        raise InvalidKeyError(key)
    return quote(key, safe="")
