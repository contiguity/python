from __future__ import annotations

from http import HTTPStatus
from typing import overload

import msgspec

from ._product import BaseProduct
from ._response import BaseResponse, ErrorResponse


class EmailResponse(BaseResponse):
    message: str


class Email(BaseProduct):
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
            msg = f"failed to send email. {response.status_code} {data.error}"
            raise ValueError(msg)

        data = msgspec.json.decode(response.content, type=EmailResponse)
        if self.debug:
            print(f"successfully sent email to {to}")

        return data
