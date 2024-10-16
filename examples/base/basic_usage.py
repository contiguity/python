# ruff: noqa: T201
from contiguity import Base

# Create a Base instance.
db = Base("my-base")

# Put an item with a specific key.
put_result = db.put({"key": "foo", "value": "Hello world!"})
print("Put result:", put_result)

# Put multiple items.
put_result = db.put({"key": "bar", "value": "Bar"}, {"key": "baz", "value": "Baz"})
print("Put many result:", put_result)

# Insert an item with a specific key.
insert_result = db.insert({"key": "john-doe", "name": "John Doe", "age": 30})
print("Insert result:", insert_result)

# Insert an item with a specific key that expires in 1 hour.
expiring_insert_result = db.insert({"key": "jane-doe", "name": "Jane Doe", "age": 28}, expire_in=3600)
print("Insert with expiry result:", expiring_insert_result)

# Get an item using a key.
get_result = db.get("foo")
print("Get result:", get_result)

# Update an item.
update_result = db.update({"age": db.util.increment(2), "name": "Mr. Doe"}, key="john-doe")
print("Update result:", update_result)

# Query items.
query_result = db.query({"age?gt": 25}, limit=10)
print("Query result:", query_result)

# Delete an item.
db.delete("jane-doe-py")

# Delete all items.
for item in db.query().items:
    db.delete(str(item["key"]))
