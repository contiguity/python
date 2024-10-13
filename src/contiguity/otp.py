from http import HTTPStatus

import phonenumbers

from ._client import ApiClient


class OTP:
    def __init__(self, *, client: ApiClient, debug: bool = False) -> None:
        self._client = client
        self.debug = debug

    def send(self, to: str, /, *, language, name: str = ""):
        e164 = phonenumbers.format_number(phonenumbers.parse(to), phonenumbers.PhoneNumberFormat.E164)

        response = self._client.post(
            "/otp/new",
            json={
                "to": e164,
                "language": language,
                "name": name,
            },
        )
        json_data = response.json()

        if response.status_code != HTTPStatus.OK:
            msg = (
                "Contiguity couldn't send your OTP."
                f" Received: {response.status_code} with reason: '{json_data['message']}'"
            )
            raise ValueError(msg)
        if self.debug:
            print(f"Contiguity successfully sent your OTP to {to} with OTP ID {json_data['otp_id']}")

        return json_data["otp_id"]

    def verify(self, otp, id):
        response = self._client.post(
            "/otp/verify",
            json={
                "otp": otp,
                "otp_id": id,
            },
        )
        json_data = response.json()

        if response.status_code != HTTPStatus.OK:
            msg = (
                "Contiguity couldn't verify your OTP."
                f" Received: {response.status_code} with reason: '{json_data['message']}'"
            )
            raise ValueError(msg)
        if self.debug:
            print(f"Contiguity verified your OTP ({otp}) with status: {json_data['verified']}")

        return json_data["verified"]

    def resend(self, id, /):
        response = self._client.post(
            "/otp/resend",
            json={
                "otp_id": id,
            },
        )
        json_data = response.json()

        if response.status_code != HTTPStatus.OK:
            msg = (
                "Contiguity couldn't resend your OTP."
                f" Received: {response.status_code} with reason: '{json_data['message']}'"
            )
            raise ValueError(msg)
        if self.debug:
            print(f"Contiguity resent your OTP ({id}) with status: {json_data['verified']}")

        return json_data["verified"]
