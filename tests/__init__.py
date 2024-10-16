import random
import string


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))  # noqa: S311
