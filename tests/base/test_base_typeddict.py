import random
from collections.abc import Generator
from typing import Any, TypedDict

import pytest

from contiguity.base import Base, InvalidKeyError, ItemConflictError, ItemNotFoundError, QueryResponse
from tests import NON_EXISTENT_ITEM_WARNING, random_string


class TestItemDict(TypedDict):
    key: str
    field1: int
    field2: str
    field3: int
    field4: int
    field5: list[str]
    field6: list[int]
    field7: dict[str, str]


def create_test_item(  # noqa: PLR0913
    key: str = "test_key",
    field1: int = random.randint(1, 1000),
    field2: str = random_string(),
    field3: int = 1,
    field4: int = 0,
    field5: list[str] | None = None,
    field6: list[int] | None = None,
    field7: dict[str, str] | None = None,
) -> TestItemDict:
    return TestItemDict(
        key=key,
        field1=field1,
        field2=field2,
        field3=field3,
        field4=field4,
        field5=field5 or ["foo", "bar"],
        field6=field6 or [1, 2],
        field7=field7 or {"foo": "bar"},
    )


@pytest.fixture
def base() -> Generator[Base[TestItemDict], Any, None]:
    base = Base("test_base_typeddict", item_type=TestItemDict)
    for item in base.query().items:
        base.delete(item["key"])
    yield base
    for item in base.query().items:
        base.delete(item["key"])


def test_bad_base_name() -> None:
    with pytest.raises(ValueError, match="invalid Base name ''"):
        Base("", item_type=TestItemDict)


def test_bad_key(base: Base[TestItemDict]) -> None:
    with pytest.raises(InvalidKeyError):
        base.get("")
    with pytest.raises(InvalidKeyError):
        base.delete("")
    with pytest.raises(InvalidKeyError):
        base.update({"foo": "bar"}, key="")


def test_get(base: Base[TestItemDict]) -> None:
    item = create_test_item()
    base.insert(item)
    fetched_item = base.get("test_key")
    assert fetched_item == item


def test_get_nonexistent(base: Base[TestItemDict]) -> None:
    with pytest.warns(DeprecationWarning, match=NON_EXISTENT_ITEM_WARNING):
        assert base.get("nonexistent_key") is None


def test_get_default(base: Base[TestItemDict]) -> None:
    for default_item in (None, "foo", 42, create_test_item()):
        fetched_item = base.get("nonexistent_key", default=default_item)
        assert fetched_item == default_item


def test_delete(base: Base[TestItemDict]) -> None:
    item = create_test_item()
    base.insert(item)
    base.delete("test_key")
    with pytest.warns(DeprecationWarning, match=NON_EXISTENT_ITEM_WARNING):
        assert base.get("test_key") is None


def test_insert(base: Base[TestItemDict]) -> None:
    item = create_test_item()
    inserted_item = base.insert(item)
    assert inserted_item == item


def test_insert_existing(base: Base[TestItemDict]) -> None:
    item = create_test_item()
    base.insert(item)
    with pytest.raises(ItemConflictError):
        base.insert(item)


def test_put(base: Base[TestItemDict]) -> None:
    items = [create_test_item(f"test_key_{i}") for i in range(3)]
    for _ in range(2):
        response = base.put(*items)
        assert response == items


def test_put_empty(base: Base[TestItemDict]) -> None:
    items = []
    response = base.put(*items)
    assert response == items


def test_put_too_many(base: Base[TestItemDict]) -> None:
    items = [create_test_item(key=f"test_key_{i}") for i in range(base.PUT_LIMIT + 1)]
    with pytest.raises(ValueError, match=f"cannot put more than {base.PUT_LIMIT} items at a time"):
        base.put(*items)


def test_update(base: Base[TestItemDict]) -> None:
    item = create_test_item()
    base.insert(item)
    updated_item = base.update(
        {
            # Trim will not pass type validation when using TypedDict
            # because TypedDict does not support default values.
            "field2": "updated_value",
            "field3": base.util.increment(2),
            "field4": base.util.increment(-2),
            "field5": base.util.append("baz"),
            "field6": base.util.prepend([3, 4]),
        },
        key="test_key",
    )
    assert updated_item == TestItemDict(
        key="test_key",
        field1=item["field1"],
        field2="updated_value",
        field3=item["field3"] + 2,
        field4=item["field4"] - 2,
        field5=[*item["field5"], "baz"],
        field6=[3, 4, *item["field6"]],
        field7=item["field7"],
    )


def test_update_nonexistent(base: Base[TestItemDict]) -> None:
    with pytest.raises(ItemNotFoundError):
        base.update({"foo": "bar"}, key=random_string())


def test_update_empty(base: Base[TestItemDict]) -> None:
    with pytest.raises(ValueError, match="no updates provided"):
        base.update({}, key="test_key")


def test_query_empty(base: Base[TestItemDict]) -> None:
    items = [create_test_item(key=f"test_key_{i}", field1=i) for i in range(5)]
    base.put(*items)
    response = base.query()
    assert response == QueryResponse(count=5, last_key=None, items=items)


def test_query(base: Base[TestItemDict]) -> None:
    items = [create_test_item(key=f"test_key_{i}", field1=i) for i in range(5)]
    base.put(*items)
    response = base.query({"field1?gt": 1})
    assert response == QueryResponse(count=3, last_key=None, items=[item for item in items if item["field1"] > 1])
