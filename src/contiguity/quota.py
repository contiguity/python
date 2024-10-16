from http import HTTPStatus

from typing_extensions import deprecated

from ._client import ApiClient


class Quota:
    def __init__(self, *, client: ApiClient, debug: bool = False) -> None:
        self._client = client
        self.debug = debug

    @deprecated("quota functionality will be removed in a future release")
    def retrieve(self) -> dict:
        response = self._client.get("/user/get/quota")
        data = response.json()

        if response.status_code != HTTPStatus.OK:
            msg = (
                "Contiguity had an issue finding your quota."
                f" Received {response.status_code} with reason: '{data['message']}'"
            )
            raise ValueError(msg)
        if self.debug:
            print(f"Contiguity successfully found your quota. Data:\n{data}")

        return data
