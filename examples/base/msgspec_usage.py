from msgspec import Struct

from contiguity.base import Base


# Create a Pydantic model for the item.
class MyItem(Struct):
    key: str  # Make sure to include the key field.
    name: str
    age: int
    interests: list[str] = []


# Create a Base instance.
# Static type checking will work with the Pydantic model.
db = Base("members", item_type=MyItem)

# Put an item with a specific key.
put_result = db.put(
    MyItem(
        key="foo",
        name="John Doe",
        age=30,
        interests=["Python", "JavaScript"],
    ),
)
print("Put result:", put_result)

# Put multiple items.
put_result = db.put(
    MyItem(key="bar", name="Jane Doe", age=28),
    MyItem(key="baz", name="Alice", age=25),
)
print("Put many result:", put_result)

# Insert an item with a specific key.
insert_result = db.insert(
    MyItem(
        key="xyz",
        name="Arthur",
        age=33,
        interests=["Anime", "Music"],
    ),
)
print("Insert result:", insert_result)

# Insert an item with a specific key that expires in 1 hour.
expiring_insert_result = db.insert(MyItem(key="abc", name="David", age=20), expire_in=3600)
print("Insert with expiry result:", expiring_insert_result)

# Get an item using a key.
get_result = db.get("foo")
print("Get result:", get_result)

# Update an item.
update_result = db.update({"age": db.util.increment(2), "name": "Mr. Doe"}, key="foo")
print("Update result:", update_result)

# Query items.
query_result = db.query({"age?gt": 25}, limit=10)
print("Query result:", query_result)

# Delete an item.
db.delete("bar")

# Delete all items.
for item in db.query().items:
    db.delete(str(item.key))
