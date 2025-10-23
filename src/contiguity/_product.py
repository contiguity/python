from ._client import ApiClient


class BaseProduct:
    def __init__(self, *, client: ApiClient) -> None:
        self._client = client
