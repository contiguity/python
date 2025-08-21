from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, overload

import msgspec

from ._response import BaseResponse, ErrorResponse

if TYPE_CHECKING:
    from ._client import ApiClient


class EmailResponse(BaseResponse):
    message: str


class Email:
    def __init__(self, *, client: ApiClient, debug: bool = False) -> None:
        self._client = client
        self.debug = debug

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
        text: str | None = None,
        html: str | None = None,
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

        if response.status_code != HTTPStatus.OK:
            data = msgspec.json.decode(response.content, type=ErrorResponse)
            msg = f"Contiguity couldn't send your email. Received: {response.status_code} with reason: '{data.error}'"
            raise ValueError(msg)

        data = msgspec.json.decode(response.content, type=EmailResponse)
        if self.debug:
            print(f"Contiguity successfully sent your email to {to}")

        return data
