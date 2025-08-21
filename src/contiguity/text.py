from http import HTTPStatus

import msgspec
import phonenumbers

from ._product import BaseProduct
from ._response import BaseResponse, ErrorResponse


class TextResponse(BaseResponse):
    message_id: str


class Text(BaseProduct):
    def send(self, *, to: str, message: str) -> TextResponse:
        """
        Send a text message.
        Args:
            to (str): The recipient's phone number.
            message (str): The message to send.
        Returns:
            dict: The response object.
        Raises:
            ValueError: Raises an error if required fields are missing or sending the message fails.
        """
        try:
            parsed_number = phonenumbers.parse(to, None)
            if not phonenumbers.is_valid_number(parsed_number):
                msg = "formatting failed. Phone number must follow the E.164 format."
                raise ValueError(msg)
        except phonenumbers.NumberParseException as exc:
            msg = "parsing failed. Phone number must follow the E.164 format."
            raise ValueError(msg) from exc

        response = self._client.post(
            "/send/text",
            json={
                "to": phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
                "message": message,
            },
        )

        if response.status_code != HTTPStatus.OK:
            msg = f"failed to send message. {response.status_code} {data.error}"
            raise ValueError(msg)

        data = msgspec.json.decode(response.content, type=TextResponse)
        if self.debug:
            print(f"successfully sent text to {to}")

        return data
