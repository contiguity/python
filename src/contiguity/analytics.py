import json

from ._client import ApiClient


class EmailAnalytics:
    def __init__(self, *, client: ApiClient, debug: bool = False) -> None:
        self._client = client
        self.debug = debug

    def retrieve(self, id: str):
        if not id:
            raise ValueError("Contiguity Analytics requires an email ID.")

        status = self._client.get(f"/email/status/{id}")

        json_data = status.json()

        if status.status_code != 200:
            raise ValueError(f"Contiguity Analytics couldn't find an email with ID {id}")
        if self.debug:
            print(f"Contiguity successfully found your email. Data:\n\n{json.dumps(json_data)}")

        return json_data
