import phonenumbers

from contiguity._client import ApiClient


class OTP:
    def __init__(self, *, client: ApiClient, debug: bool = False) -> None:
        self._client = client
        self.debug = debug

    def send(self, to, /, *, language, name=""):
        e164 = phonenumbers.format_number(phonenumbers.parse(to), phonenumbers.PhoneNumberFormat.E164)

        otp_handler = self._client.post(
            "/otp/new",
            json={
                "to": e164,
                "language": language,
                "name": name,
            },
        )

        otp_handler_response = otp_handler.json()

        if otp_handler.status_code != 200:
            raise ValueError(
                f"Contiguity couldn't send your OTP. Received: {otp_handler.status_code} with reason: \"{otp_handler_response['message']}\""
            )
        if self.debug:
            print(f"Contiguity successfully sent your OTP to {to} with OTP ID {otp_handler_response['otp_id']}")

        return otp_handler_response["otp_id"]

    def verify(self, otp, id):
        otp_handler = self._client.post(
            "/otp/verify",
            json={
                "otp": otp,
                "otp_id": id,
            },
        )

        otp_handler_response = otp_handler.json()

        if otp_handler.status_code != 200:
            raise ValueError(
                f"Contiguity couldn't verify your OTP. Received: {otp_handler.status_code} with reason: \"{otp_handler_response['message']}\""
            )
        if self.debug:
            print(
                f"Contiguity 'verified' your OTP ({otp}) with boolean verified status: {otp_handler_response['verified']}"
            )

        return otp_handler_response["verified"]

    def resend(self, id, /):
        otp_handler = self._client.post(
            "/otp/resend",
            json={
                "otp_id": id,
            },
        )

        otp_handler_response = otp_handler.json()

        if otp_handler.status_code != 200:
            raise ValueError(
                f"Contiguity couldn't resend your OTP. Received: {otp_handler.status_code} with reason: \"{otp_handler_response['message']}\""
            )
        if self.debug:
            print(
                f"Contiguity resent your OTP ({id}) with boolean resent status: {otp_handler_response['verified']}"
            )

        return otp_handler_response["verified"]
