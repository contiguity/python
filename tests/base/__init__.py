# ruff: noqa: S311
import random
from collections.abc import Mapping
from typing import Callable, TypedDict, TypeVar

import msgspec

from contiguity.base.common import DataType
from tests import random_string

DictItemType = Mapping[str, DataType]
T = TypeVar("T", DictItemType, dict)


class ItemStruct(msgspec.Struct):
    key: str = "test_key"
    field1: int = random.randint(1, 1000)
    field2: str = random_string()
    field3: int = 1
    field4: int = 0
    field5: list[str] = msgspec.field(default_factory=lambda: ["foo", "bar"])
    field6: list[int] = msgspec.field(default_factory=lambda: [1, 2])
    field7: dict[str, str] = msgspec.field(default_factory=lambda: {"foo": "bar"})


class ItemTypedDict(TypedDict):
    key: str
    field1: int
    field2: str
    field3: int
    field4: int
    field5: list[str]
    field6: list[int]
    field7: dict[str, str]


def create_test_item_typed_dict(  # noqa: PLR0913
    key: str = "test_key",
    field1: int = random.randint(1, 1000),
    field2: str = random_string(),
    field3: int = 1,
    field4: int = 0,
    field5: "list[str] | None" = None,
    field6: "list[int] | None" = None,
    field7: "dict[str, str] | None" = None,
) -> ItemTypedDict:
    return ItemTypedDict(
        key=key,
        field1=field1,
        field2=field2,
        field3=field3,
        field4=field4,
        field5=field5 or ["foo", "bar"],
        field6=field6 or [1, 2],
        field7=field7 or {"foo": "bar"},
    )


# Yes, this is a factory function to create an item factory function.
def test_item_factory_factory(type: type[T], /) -> Callable[..., T]:
    def test_item_factory(**kwargs: DataType) -> T:
        kwargs.setdefault("key", "test_key")
        kwargs.setdefault("field1", random.randint(1, 1000))
        kwargs.setdefault("field2", random_string())
        kwargs.setdefault("field3", 1)
        kwargs.setdefault("field4", 0)
        kwargs.setdefault("field5", ["foo", "bar"])
        kwargs.setdefault("field6", [1, 2])
        kwargs.setdefault("field7", {"foo": "bar"})
        return type(**kwargs)

    return test_item_factory


create_test_item_dict = test_item_factory_factory(dict)
create_test_item_dict_typed = test_item_factory_factory(DictItemType)
