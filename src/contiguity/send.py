from http import HTTPStatus
from typing import overload

import msgspec
import phonenumbers

from ._client import ApiClient
from ._common import Crumbs


class TextResponse(msgspec.Struct):
    message: str
    crumbs: Crumbs


class EmailResponse(msgspec.Struct):
    message: str
    crumbs: Crumbs


class Send:
    def __init__(self, *, client: ApiClient, debug: bool = False) -> None:
        self._client = client
        self.debug = debug

    def text(self, to: str, message: str) -> TextResponse:
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
                msg = "Contiguity requires phone numbers to follow the E.164 format. Formatting failed."
                raise ValueError(msg)
        except phonenumbers.NumberParseException as exc:
            msg = "Contiguity requires phone numbers to follow the E.164 format. Parsing failed."
            raise ValueError(msg) from exc

        response = self._client.post(
            "/send/text",
            json={
                "to": phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
                "message": message,
            },
        )
        data = msgspec.json.decode(response.content, type=TextResponse)

        if response.status_code != HTTPStatus.OK:
            msg = (
                "Contiguity couldn't send your message."
                f" Received: {response.status_code} with reason: '{data.message}'"
            )
            raise ValueError(msg)
        if self.debug:
            print(f"Contiguity successfully sent your text to {to}. Crumbs:\n{data.crumbs}")

        return data

    @overload
    def email(
        self,
        *,
        to: str,
        from_: str,
        subject: str,
        text: str,
        reply_to: str = "",
        cc: str = "",
    ) -> EmailResponse: ...

    @overload
    def email(
        self,
        *,
        to: str,
        from_: str,
        subject: str,
        html: str,
        reply_to: str = "",
        cc: str = "",
    ) -> EmailResponse: ...

    def email(  # noqa: PLR0913
        self,
        *,
        to: str,
        from_: str,
        subject: str,
        reply_to: str = "",
        cc: str = "",
        text: "str | None" = None,
        html: "str | None" = None,
    ) -> EmailResponse:
        """
        Send an email.
        Args:
            to (str): The recipient's email address.
            from (str): The sender's name. The email address is selected automatically.
                Configure at contiguity.co/dashboard
            subject (str): The email subject.
            text (str, optional): The plain text email body.
                Provide one body, or HTML will be prioritized if both are present.
            html (str, optional): The HTML email body. Provide one body.
            reply_to (str, optional): The reply-to email address.
            cc (str, optional): The CC email addresses.
        Returns:
            dict: The response object.
        Raises:
            ValueError: Raises an error if required fields are missing or sending the email fails.
        """
        email_payload = {
            "to": to,
            "from": from_,
            "subject": subject,
            "body": html or text,
            "contentType": "html" if html else "text",
        }

        if reply_to:
            email_payload["replyTo"] = reply_to

        if cc:
            email_payload["cc"] = cc

        response = self._client.post("/send/email", json=email_payload)
        data = msgspec.json.decode(response.content, type=EmailResponse)

        if response.status_code != HTTPStatus.OK:
            msg = (
                f"Contiguity couldn't send your email. Received: {response.status_code} with reason: '{data.message}'"
            )
            raise ValueError(msg)
        if self.debug:
            print(f"Contiguity successfully sent your email to {to}. Crumbs:\n{data.crumbs}")

        return data
