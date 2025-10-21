# ruff: noqa: S101, S311
import random
from collections.abc import Generator
from typing import Any

import pytest
from dotenv import load_dotenv
from msgspec import Struct, field

from contiguity.base import Base, InvalidKeyError, ItemConflictError, ItemNotFoundError, QueryResponse
from tests import NON_EXISTENT_ITEM_WARNING, random_string

load_dotenv()


class TestItemModel(Struct):
    __test__ = False
    key: str = "test_key"
    field1: int = random.randint(1, 1000)
    field2: str = random_string()
    field3: int = 1
    field4: int = 0
    field5: list[str] = field(default_factory=lambda: ["foo", "bar"])
    field6: list[int] = field(default_factory=lambda: [1, 2])
    field7: dict[str, str] = field(default_factory=lambda: {"foo": "bar"})


@pytest.fixture
def base() -> Generator[Base[TestItemModel], Any, None]:
    base = Base("test_base_model", item_type=TestItemModel)
    for item in base.query().items:
        base.delete(item.key)
    yield base
    for item in base.query().items:
        base.delete(item.key)


def test_bad_base_name() -> None:
    with pytest.raises(ValueError, match="invalid Base name ''"):
        Base("", item_type=TestItemModel)


def test_bad_key(base: Base[TestItemModel]) -> None:
    with pytest.raises(InvalidKeyError):
        base.get("")
    with pytest.raises(InvalidKeyError):
        base.delete("")
    with pytest.raises(InvalidKeyError):
        base.update({"foo": "bar"}, key="")


def test_get(base: Base[TestItemModel]) -> None:
    item = TestItemModel()
    base.insert(item)
    fetched_item = base.get("test_key")
    assert fetched_item == item


def test_get_nonexistent(base: Base[TestItemModel]) -> None:
    with pytest.warns(DeprecationWarning, match=NON_EXISTENT_ITEM_WARNING):
        assert base.get("nonexistent_key") is None


def test_get_default(base: Base[TestItemModel]) -> None:
    for default_item in (None, "foo", 42, TestItemModel()):
        fetched_item = base.get("nonexistent_key", default=default_item)
        assert fetched_item == default_item


def test_delete(base: Base[TestItemModel]) -> None:
    item = TestItemModel()
    base.insert(item)
    base.delete("test_key")
    with pytest.warns(DeprecationWarning, match=NON_EXISTENT_ITEM_WARNING):
        assert base.get("test_key") is None


def test_insert(base: Base[TestItemModel]) -> None:
    item = TestItemModel()
    inserted_item = base.insert(item)
    assert inserted_item == item


def test_insert_existing(base: Base[TestItemModel]) -> None:
    item = TestItemModel()
    base.insert(item)
    with pytest.raises(ItemConflictError):
        base.insert(item)


def test_put(base: Base[TestItemModel]) -> None:
    items = [TestItemModel(key=f"test_key_{i}") for i in range(3)]
    for _ in range(2):
        response = base.put(*items)
        assert response == items


def test_put_empty(base: Base[TestItemModel]) -> None:
    items = []
    response = base.put(*items)
    assert response == items


def test_put_too_many(base: Base[TestItemModel]) -> None:
    items = [TestItemModel(key=f"test_key_{i}") for i in range(base.PUT_LIMIT + 1)]
    with pytest.raises(ValueError, match=f"cannot put more than {base.PUT_LIMIT} items at a time"):
        base.put(*items)


def test_update(base: Base[TestItemModel]) -> None:
    item = TestItemModel()
    base.insert(item)
    updated_item = base.update(
        {
            "field1": base.util.trim(),
            "field2": "updated_value",
            "field3": base.util.increment(2),
            "field4": base.util.increment(-2),
            "field5": base.util.append("baz"),
            "field6": base.util.prepend([3, 4]),
        },
        key="test_key",
    )
    assert updated_item == TestItemModel(
        key="test_key",
        field1=updated_item.field1,
        field2="updated_value",
        field3=item.field3 + 2,
        field4=item.field4 - 2,
        field5=[*item.field5, "baz"],
        field6=[3, 4, *item.field6],
        field7=item.field7,
    )


def test_update_nonexistent(base: Base[TestItemModel]) -> None:
    with pytest.raises(ItemNotFoundError):
        base.update({"foo": "bar"}, key=random_string())


def test_update_empty(base: Base[TestItemModel]) -> None:
    with pytest.raises(ValueError, match="no updates provided"):
        base.update({}, key="test_key")


def test_query_empty(base: Base[TestItemModel]) -> None:
    items = [TestItemModel(key=f"test_key_{i}", field1=i) for i in range(5)]
    base.put(*items)
    response = base.query()
    assert response == QueryResponse(count=5, last_key=None, items=items)


def test_query(base: Base[TestItemModel]) -> None:
    items = [TestItemModel(key=f"test_key_{i}", field1=i) for i in range(5)]
    base.put(*items)
    response = base.query({"field1?gt": 1})
    assert response == QueryResponse(count=3, last_key=None, items=[item for item in items if item.field1 > 1])
