import json

from contiguity._client import ApiClient


class Quota:
    def __init__(self, *, client: ApiClient, debug: bool = False) -> None:
        self._client = client
        self.debug = debug

    def retrieve(self):
        quota = self._client.get("/user/get/quota")

        json_data = quota.json()

        if quota.status_code != 200:
            raise ValueError(
                f"Contiguity had an issue finding your quota. Received {quota.status_code} with reason: \"{json_data['message']}\""
            )
        if self.debug:
            print(f"Contiguity successfully found your quota. Data:\n\n{json.dumps(json_data)}")

        return json_data
