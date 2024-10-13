from http import HTTPStatus

from ._client import ApiClient


class EmailAnalytics:
    def __init__(self, *, client: ApiClient, debug: bool = False) -> None:
        self._client = client
        self.debug = debug

    def retrieve(self, id: str):
        if not id:
            msg = "Contiguity Analytics requires an email ID."
            raise ValueError(msg)

        response = self._client.get(f"/email/status/{id}")

        if response.status_code != HTTPStatus.OK:
            msg = f"Contiguity Analytics couldn't find an email with ID {id}"
            raise ValueError(msg)
        if self.debug:
            print(f"Contiguity successfully found your email. Data:\n{response.text}")

        return response.json()
