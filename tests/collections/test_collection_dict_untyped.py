# ruff: noqa: S101, S311, PLR2004
import random
from collections.abc import Generator
from typing import Any

import pytest
from dotenv import load_dotenv
from pydantic import JsonValue

from contiguity import Collection, InvalidKeyError, ItemConflictError, ItemNotFoundError, QueryResponse
from tests import random_string

load_dotenv()


def create_test_item(**kwargs: JsonValue) -> dict:
    kwargs.setdefault("key", "test_key")
    kwargs.setdefault("field1", random.randint(1, 1000))
    kwargs.setdefault("field2", random_string())
    kwargs.setdefault("field3", 1)
    kwargs.setdefault("field4", 0)
    kwargs.setdefault("field5", ["foo", "bar"])
    kwargs.setdefault("field6", [1, 2])
    kwargs.setdefault("field7", {"foo": "bar"})
    return kwargs


@pytest.fixture
def db() -> Generator[Collection, Any, None]:
    db = Collection("test_db_dict_untyped")
    for item in db.query().items:
        db.delete(str(item["key"]))
    yield db
    for item in db.query().items:
        db.delete(str(item["key"]))


def test_bad_db_name() -> None:
    with pytest.raises(ValueError, match="invalid Collection name ''"):
        Collection("")


def test_bad_key(db: Collection) -> None:
    with pytest.raises(InvalidKeyError):
        db.get("")
    with pytest.raises(InvalidKeyError):
        db.delete("")
    with pytest.raises(InvalidKeyError):
        db.update({"foo": "bar"}, key="")


def test_get(db: Collection) -> None:
    item = create_test_item()
    db.insert(item)
    fetched_item = db.get("test_key")
    assert fetched_item == item


def test_get_nonexistent(db: Collection) -> None:
    with pytest.warns(DeprecationWarning):
        assert db.get("nonexistent_key") is None


def test_get_default(db: Collection) -> None:
    for default_item in (None, "foo", 42, create_test_item()):
        fetched_item = db.get("nonexistent_key", default=default_item)
        assert fetched_item == default_item


def test_delete(db: Collection) -> None:
    item = create_test_item()
    db.insert(item)
    db.delete("test_key")
    with pytest.warns(DeprecationWarning):
        assert db.get("test_key") is None


def test_insert(db: Collection) -> None:
    item = create_test_item()
    inserted_item = db.insert(item)
    assert inserted_item == item


def test_insert_existing(db: Collection) -> None:
    item = create_test_item()
    db.insert(item)
    with pytest.raises(ItemConflictError):
        db.insert(item)


def test_put(db: Collection) -> None:
    items = [create_test_item(key=f"test_key_{i}") for i in range(3)]
    for _ in range(2):
        response = db.put(*items)
        assert response == items


def test_put_empty(db: Collection) -> None:
    items = []
    response = db.put(*items)
    assert response == items


def test_put_too_many(db: Collection) -> None:
    items = [create_test_item(key=f"test_key_{i}") for i in range(db.PUT_LIMIT + 1)]
    with pytest.raises(ValueError, match=f"cannot put more than {db.PUT_LIMIT} items at a time"):
        db.put(*items)


def test_update(db: Collection) -> None:
    item = {
        "key": "test_key",
        "field1": random_string(),
        "field2": random_string(),
        "field3": 1,
        "field4": 0,
        "field5": ["foo", "bar"],
        "field6": [1, 2],
        "field7": {"foo": "bar"},
    }
    db.insert(item)
    updated_item = db.update(
        {
            "field1": "updated_value",
            "field2": db.util.trim(),
            "field3": db.util.increment(2),
            "field4": db.util.increment(-2),
            "field5": db.util.append("baz"),
            "field6": db.util.prepend([3, 4]),
        },
        key="test_key",
    )
    assert updated_item == {
        "key": "test_key",
        "field1": "updated_value",
        "field3": item["field3"] + 2,
        "field4": item["field4"] - 2,
        "field5": [*item["field5"], "baz"],
        "field6": [3, 4, *item["field6"]],
        "field7": item["field7"],
    }


def test_update_nonexistent(db: Collection) -> None:
    with pytest.raises(ItemNotFoundError):
        db.update({"foo": "bar"}, key=random_string())


def test_update_empty(db: Collection) -> None:
    with pytest.raises(ValueError, match="no updates provided"):
        db.update({}, key="test_key")


def test_query_empty(db: Collection) -> None:
    items = [create_test_item(key=f"test_key_{i}", field1=i) for i in range(5)]
    db.put(*items)
    response = db.query()
    assert response == QueryResponse(count=5, last_key=None, items=items)


def test_query(db: Collection) -> None:
    items = [create_test_item(key=f"test_key_{i}", field1=i) for i in range(5)]
    db.put(*items)
    response = db.query({"field1?gt": 1})
    assert response == QueryResponse(count=3, last_key=None, items=[item for item in items if item["field1"] > 1])
