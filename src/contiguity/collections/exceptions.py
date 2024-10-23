from contiguity._client import ApiError


class ItemConflictError(ApiError):
    def __init__(self, key: str, *args: object) -> None:
        super().__init__(f"item with key '{key}' already exists", *args)


class ItemNotFoundError(ApiError):
    def __init__(self, key: str, *args: object) -> None:
        super().__init__(f"key '{key}' not found", *args)


class InvalidKeyError(ValueError):
    def __init__(self, key: str, *args: object) -> None:
        super().__init__(f"invalid key '{key}'", *args)
