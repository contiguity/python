import random
import string

NON_EXISTENT_ITEM_WARNING = (
    "ItemNotFoundError will be raised in the future. To receive None for non-existent keys, set default=None."
)


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))  # noqa: S311
