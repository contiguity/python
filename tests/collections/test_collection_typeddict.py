# ruff: noqa: S101, S311, PLR2004
from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

import pytest
from dotenv import load_dotenv
from typing_extensions import TypedDict

from contiguity import Collection, InvalidKeyError, ItemConflictError, ItemNotFoundError, QueryResponse
from tests import random_string

if TYPE_CHECKING:
    from collections.abc import Generator

load_dotenv()


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
def db() -> Generator[Collection[TestItemDict], Any, None]:
    db = Collection("test_db_typeddict", item_type=TestItemDict)
    for item in db.query().items:
        db.delete(item["key"])
    yield db
    for item in db.query().items:
        db.delete(item["key"])


def test_bad_db_name() -> None:
    with pytest.raises(ValueError, match="invalid Collection name ''"):
        Collection("", item_type=TestItemDict)


def test_bad_key(db: Collection[TestItemDict]) -> None:
    with pytest.raises(InvalidKeyError):
        db.get("")
    with pytest.raises(InvalidKeyError):
        db.delete("")
    with pytest.raises(InvalidKeyError):
        db.update({"foo": "bar"}, key="")


def test_get(db: Collection[TestItemDict]) -> None:
    item = create_test_item()
    db.insert(item)
    fetched_item = db.get("test_key")
    assert fetched_item == item


def test_get_nonexistent(db: Collection[TestItemDict]) -> None:
    with pytest.warns(DeprecationWarning):
        assert db.get("nonexistent_key") is None


def test_get_default(db: Collection[TestItemDict]) -> None:
    for default_item in (None, "foo", 42, create_test_item()):
        fetched_item = db.get("nonexistent_key", default=default_item)
        assert fetched_item == default_item


def test_delete(db: Collection[TestItemDict]) -> None:
    item = create_test_item()
    db.insert(item)
    db.delete("test_key")
    with pytest.warns(DeprecationWarning):
        assert db.get("test_key") is None


def test_insert(db: Collection[TestItemDict]) -> None:
    item = create_test_item()
    inserted_item = db.insert(item)
    assert inserted_item == item


def test_insert_existing(db: Collection[TestItemDict]) -> None:
    item = create_test_item()
    db.insert(item)
    with pytest.raises(ItemConflictError):
        db.insert(item)


def test_put(db: Collection[TestItemDict]) -> None:
    items = [create_test_item(f"test_key_{i}") for i in range(3)]
    for _ in range(2):
        response = db.put(*items)
        assert response == items


def test_put_empty(db: Collection[TestItemDict]) -> None:
    items = []
    response = db.put(*items)
    assert response == items


def test_put_too_many(db: Collection[TestItemDict]) -> None:
    items = [create_test_item(key=f"test_key_{i}") for i in range(db.PUT_LIMIT + 1)]
    with pytest.raises(ValueError, match=f"cannot put more than {db.PUT_LIMIT} items at a time"):
        db.put(*items)


def test_update(db: Collection[TestItemDict]) -> None:
    item = create_test_item()
    db.insert(item)
    updated_item = db.update(
        {
            # Trim will not pass type validation when using TypedDict
            # because TypedDict does not support default values.
            "field2": "updated_value",
            "field3": db.util.increment(2),
            "field4": db.util.increment(-2),
            "field5": db.util.append("baz"),
            "field6": db.util.prepend([3, 4]),
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


def test_update_nonexistent(db: Collection[TestItemDict]) -> None:
    with pytest.raises(ItemNotFoundError):
        db.update({"foo": "bar"}, key=random_string())


def test_update_empty(db: Collection[TestItemDict]) -> None:
    with pytest.raises(ValueError, match="no updates provided"):
        db.update({}, key="test_key")


def test_query_empty(db: Collection[TestItemDict]) -> None:
    items = [create_test_item(key=f"test_key_{i}", field1=i) for i in range(5)]
    db.put(*items)
    response = db.query()
    assert response == QueryResponse(count=5, last_key=None, items=items)


def test_query(db: Collection[TestItemDict]) -> None:
    items = [create_test_item(key=f"test_key_{i}", field1=i) for i in range(5)]
    db.put(*items)
    response = db.query({"field1?gt": 1})
    assert response == QueryResponse(count=3, last_key=None, items=[item for item in items if item["field1"] > 1])
