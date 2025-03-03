# ruff: noqa: S101, S311, PLR2004
import random
from collections.abc import Generator
from typing import Any

import pytest
from dotenv import load_dotenv
from pydantic import BaseModel

from contiguity import Collection, InvalidKeyError, ItemConflictError, ItemNotFoundError, QueryResponse
from tests import random_string

load_dotenv()


class TestItemModel(BaseModel):
    key: str = "test_key"
    field1: int = random.randint(1, 1000)
    field2: str = random_string()
    field3: int = 1
    field4: int = 0
    field5: list[str] = ["foo", "bar"]
    field6: list[int] = [1, 2]
    field7: dict[str, str] = {"foo": "bar"}


@pytest.fixture
def db() -> Generator[Collection[TestItemModel], Any, None]:
    db = Collection("test_db_model", item_type=TestItemModel)
    for item in db.query().items:
        db.delete(item.key)
    yield db
    for item in db.query().items:
        db.delete(item.key)


def test_bad_db_name() -> None:
    with pytest.raises(ValueError, match="invalid Collection name ''"):
        Collection("", item_type=TestItemModel)


def test_bad_key(db: Collection[TestItemModel]) -> None:
    with pytest.raises(InvalidKeyError):
        db.get("")
    with pytest.raises(InvalidKeyError):
        db.delete("")
    with pytest.raises(InvalidKeyError):
        db.update({"foo": "bar"}, key="")


def test_get(db: Collection[TestItemModel]) -> None:
    item = TestItemModel()
    db.insert(item)
    fetched_item = db.get("test_key")
    assert fetched_item == item


def test_get_nonexistent(db: Collection[TestItemModel]) -> None:
    with pytest.warns(DeprecationWarning):
        assert db.get("nonexistent_key") is None


def test_get_default(db: Collection[TestItemModel]) -> None:
    for default_item in (None, "foo", 42, TestItemModel()):
        fetched_item = db.get("nonexistent_key", default=default_item)
        assert fetched_item == default_item


def test_delete(db: Collection[TestItemModel]) -> None:
    item = TestItemModel()
    db.insert(item)
    db.delete("test_key")
    with pytest.warns(DeprecationWarning):
        assert db.get("test_key") is None


def test_insert(db: Collection[TestItemModel]) -> None:
    item = TestItemModel()
    inserted_item = db.insert(item)
    assert inserted_item == item


def test_insert_existing(db: Collection[TestItemModel]) -> None:
    item = TestItemModel()
    db.insert(item)
    with pytest.raises(ItemConflictError):
        db.insert(item)


def test_put(db: Collection[TestItemModel]) -> None:
    items = [TestItemModel(key=f"test_key_{i}") for i in range(3)]
    for _ in range(2):
        response = db.put(*items)
        assert response == items


def test_put_empty(db: Collection[TestItemModel]) -> None:
    items = []
    response = db.put(*items)
    assert response == items


def test_put_too_many(db: Collection[TestItemModel]) -> None:
    items = [TestItemModel(key=f"test_key_{i}") for i in range(db.PUT_LIMIT + 1)]
    with pytest.raises(ValueError, match=f"cannot put more than {db.PUT_LIMIT} items at a time"):
        db.put(*items)


def test_update(db: Collection[TestItemModel]) -> None:
    item = TestItemModel()
    db.insert(item)
    updated_item = db.update(
        {
            "field1": db.util.trim(),
            "field2": "updated_value",
            "field3": db.util.increment(2),
            "field4": db.util.increment(-2),
            "field5": db.util.append("baz"),
            "field6": db.util.prepend([3, 4]),
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


def test_update_nonexistent(db: Collection[TestItemModel]) -> None:
    with pytest.raises(ItemNotFoundError):
        db.update({"foo": "bar"}, key=random_string())


def test_update_empty(db: Collection[TestItemModel]) -> None:
    with pytest.raises(ValueError, match="no updates provided"):
        db.update({}, key="test_key")


def test_query_empty(db: Collection[TestItemModel]) -> None:
    items = [TestItemModel(key=f"test_key_{i}", field1=i) for i in range(5)]
    db.put(*items)
    response = db.query()
    assert response == QueryResponse(count=5, last_key=None, items=items)


def test_query(db: Collection[TestItemModel]) -> None:
    items = [TestItemModel(key=f"test_key_{i}", field1=i) for i in range(5)]
    db.put(*items)
    response = db.query({"field1?gt": 1})
    assert response == QueryResponse(count=3, last_key=None, items=[item for item in items if item.field1 > 1])
