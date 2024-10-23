# ruff: noqa: S101, S311, PLR2004
from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

import pytest
from dotenv import load_dotenv
from typing_extensions import TypedDict

from contiguity import AsyncCollection, InvalidKeyError, ItemConflictError, ItemNotFoundError, QueryResponse
from tests import random_string

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

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
async def db() -> AsyncGenerator[AsyncCollection[TestItemDict], Any]:
    db = AsyncCollection("test_db_typeddict", item_type=TestItemDict)
    for item in (await db.query()).items:
        await db.delete(item["key"])
    yield db
    for item in (await db.query()).items:
        await db.delete(item["key"])


def test_bad_db_name() -> None:
    with pytest.raises(ValueError, match="invalid Collection name ''"):
        AsyncCollection("", item_type=TestItemDict)


async def test_bad_key(db: AsyncCollection[TestItemDict]) -> None:
    with pytest.raises(InvalidKeyError):
        await db.get("")
    with pytest.raises(InvalidKeyError):
        await db.delete("")
    with pytest.raises(InvalidKeyError):
        await db.update({"foo": "bar"}, key="")


async def test_get(db: AsyncCollection[TestItemDict]) -> None:
    item = create_test_item()
    await db.insert(item)
    fetched_item = await db.get("test_key")
    assert fetched_item == item


async def test_get_nonexistent(db: AsyncCollection[TestItemDict]) -> None:
    with pytest.warns(DeprecationWarning):
        assert await db.get("nonexistent_key") is None


async def test_get_default(db: AsyncCollection[TestItemDict]) -> None:
    for default_item in (None, "foo", 42, create_test_item()):
        fetched_item = await db.get("nonexistent_key", default=default_item)
        assert fetched_item == default_item


async def test_delete(db: AsyncCollection[TestItemDict]) -> None:
    item = create_test_item()
    await db.insert(item)
    await db.delete("test_key")
    with pytest.warns(DeprecationWarning):
        assert await db.get("test_key") is None


async def test_insert(db: AsyncCollection[TestItemDict]) -> None:
    item = create_test_item()
    inserted_item = await db.insert(item)
    assert inserted_item == item


async def test_insert_existing(db: AsyncCollection[TestItemDict]) -> None:
    item = create_test_item()
    await db.insert(item)
    with pytest.raises(ItemConflictError):
        await db.insert(item)


async def test_put(db: AsyncCollection[TestItemDict]) -> None:
    items = [create_test_item(f"test_key_{i}") for i in range(3)]
    for _ in range(2):
        response = await db.put(*items)
        assert response == items


async def test_put_empty(db: AsyncCollection[TestItemDict]) -> None:
    items = []
    response = await db.put(*items)
    assert response == items


async def test_put_too_many(db: AsyncCollection[TestItemDict]) -> None:
    items = [create_test_item(key=f"test_key_{i}") for i in range(db.PUT_LIMIT + 1)]
    with pytest.raises(ValueError, match=f"cannot put more than {db.PUT_LIMIT} items at a time"):
        await db.put(*items)


async def test_update(db: AsyncCollection[TestItemDict]) -> None:
    item = create_test_item()
    await db.insert(item)
    updated_item = await db.update(
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


async def test_update_nonexistent(db: AsyncCollection[TestItemDict]) -> None:
    with pytest.raises(ItemNotFoundError):
        await db.update({"foo": "bar"}, key=random_string())


async def test_update_empty(db: AsyncCollection[TestItemDict]) -> None:
    with pytest.raises(ValueError, match="no updates provided"):
        await db.update({}, key="test_key")


async def test_query_empty(db: AsyncCollection[TestItemDict]) -> None:
    items = [create_test_item(key=f"test_key_{i}", field1=i) for i in range(5)]
    await db.put(*items)
    response = await db.query()
    assert response == QueryResponse(count=5, last_key=None, items=items)


async def test_query(db: AsyncCollection[TestItemDict]) -> None:
    items = [create_test_item(key=f"test_key_{i}", field1=i) for i in range(5)]
    await db.put(*items)
    response = await db.query({"field1?gt": 1})
    assert response == QueryResponse(count=3, last_key=None, items=[item for item in items if item["field1"] > 1])
