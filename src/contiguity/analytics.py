from http import HTTPStatus

from typing_extensions import deprecated

from ._client import ApiClient


class EmailAnalytics:
    def __init__(self, *, client: ApiClient, debug: bool = False) -> None:
        self._client = client
        self.debug = debug

    @deprecated("email analytics will be removed in a future release")
    def retrieve(self, id: str) -> dict:
        if not id:
            msg = "Contiguity Analytics requires an email ID."
            raise ValueError(msg)

        response = self._client.get(f"/email/status/{id}")
        data = response.json()

        if response.status_code != HTTPStatus.OK:
            msg = f"Contiguity Analytics couldn't find an email with ID {id}"
            raise ValueError(msg)
        if self.debug:
            print(f"Contiguity successfully found your email. Data:\n{data}")

        return data
