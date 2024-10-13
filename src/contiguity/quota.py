from http import HTTPStatus

from ._client import ApiClient


class Quota:
    def __init__(self, *, client: ApiClient, debug: bool = False) -> None:
        self._client = client
        self.debug = debug

    def retrieve(self):
        response = self._client.get("/user/get/quota")
        json_data = response.json()

        if response.status_code != HTTPStatus.OK:
            msg = (
                "Contiguity had an issue finding your quota."
                f" Received {response.status_code} with reason: '{json_data['message']}'"
            )
            raise ValueError(msg)
        if self.debug:
            print(f"Contiguity successfully found your quota. Data:\n{response.text}")

        return json_data
