from collections.abc import AsyncGenerator
from typing import Any

import pytest
from dotenv import load_dotenv

from contiguity import AsyncBase, InvalidKeyError, ItemConflictError, ItemNotFoundError, QueryResponse
from tests import random_string
from tests.base import create_test_item_dict as create_test_item

load_dotenv()


@pytest.fixture
async def base() -> AsyncGenerator[AsyncBase, Any]:
    base = AsyncBase("test_base_dict_untyped")
    for item in (await base.query()).items:
        await base.delete(str(item["key"]))
    yield base
    for item in (await base.query()).items:
        await base.delete(str(item["key"]))


def test_bad_base_name() -> None:
    with pytest.raises(ValueError, match="invalid Base name ''"):
        AsyncBase("")


async def test_bad_key(base: AsyncBase) -> None:
    with pytest.raises(InvalidKeyError):
        await base.get("")
    with pytest.raises(InvalidKeyError):
        await base.delete("")
    with pytest.raises(InvalidKeyError):
        await base.update({"foo": "bar"}, key="")


async def test_get(base: AsyncBase) -> None:
    item = create_test_item()
    await base.insert(item)
    fetched_item = await base.get("test_key")
    assert fetched_item == item


async def test_get_nonexistent(base: AsyncBase) -> None:
    with pytest.warns(DeprecationWarning):
        assert await base.get("nonexistent_key") is None


async def test_get_default(base: AsyncBase) -> None:
    for default_item in (None, "foo", 42, create_test_item()):
        fetched_item = await base.get("nonexistent_key", default=default_item)
        assert fetched_item == default_item


async def test_delete(base: AsyncBase) -> None:
    item = create_test_item()
    await base.insert(item)
    await base.delete("test_key")
    with pytest.warns(DeprecationWarning):
        assert await base.get("test_key") is None


async def test_insert(base: AsyncBase) -> None:
    item = create_test_item()
    inserted_item = await base.insert(item)
    assert inserted_item == item


async def test_insert_existing(base: AsyncBase) -> None:
    item = create_test_item()
    await base.insert(item)
    with pytest.raises(ItemConflictError):
        await base.insert(item)


async def test_put(base: AsyncBase) -> None:
    items = [create_test_item(key=f"test_key_{i}") for i in range(3)]
    for _ in range(2):
        response = await base.put(*items)
        assert response == items


async def test_put_empty(base: AsyncBase) -> None:
    items = []
    response = await base.put(*items)
    assert response == items


async def test_put_too_many(base: AsyncBase) -> None:
    items = [create_test_item(key=f"test_key_{i}") for i in range(base.PUT_LIMIT + 1)]
    with pytest.raises(ValueError, match=f"cannot put more than {base.PUT_LIMIT} items at a time"):
        await base.put(*items)


async def test_update(base: AsyncBase) -> None:
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
    await base.insert(item)
    updated_item = await base.update(
        {
            "field1": "updated_value",
            "field2": base.util.trim(),
            "field3": base.util.increment(2),
            "field4": base.util.increment(-2),
            "field5": base.util.append("baz"),
            "field6": base.util.prepend([3, 4]),
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


async def test_update_nonexistent(base: AsyncBase) -> None:
    with pytest.raises(ItemNotFoundError):
        await base.update({"foo": "bar"}, key=random_string())


async def test_update_empty(base: AsyncBase) -> None:
    with pytest.raises(ValueError, match="no updates provided"):
        await base.update({}, key="test_key")


async def test_query_empty(base: AsyncBase) -> None:
    items = [create_test_item(key=f"test_key_{i}", field1=i) for i in range(5)]
    await base.put(*items)
    response = await base.query()
    assert response == QueryResponse(count=5, last_key=None, items=items)


async def test_query(base: AsyncBase) -> None:
    items = [create_test_item(key=f"test_key_{i}", field1=i) for i in range(5)]
    await base.put(*items)
    response = await base.query({"field1?gt": 1})
    assert response == QueryResponse(count=3, last_key=None, items=[item for item in items if item["field1"] > 1])
