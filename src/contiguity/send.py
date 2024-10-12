from __future__ import annotations

import json
from typing import overload

import phonenumbers
from htmlmin import minify

from contiguity._client import ApiClient


class Send:
    def __init__(self, *, client: ApiClient, debug: bool = False) -> None:
        self._client = client
        self.debug = debug

    def text(self, to: str, message: str):
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
                raise ValueError("Contiguity requires phone numbers to follow the E.164 format. Formatting failed.")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError("Contiguity requires phone numbers to follow the E.164 format. Parsing failed.")

        text_handler = self._client.post(
            "/send/text",
            json={
                "to": phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
                "message": message,
            },
        )
        text_handler_response = text_handler.json()

        if text_handler.status_code != 200:
            raise ValueError(
                f"Contiguity couldn't send your message. Received: {text_handler.status_code} with reason: \"{text_handler_response['message']}\""
            )
        if self.debug:
            print(f"Contiguity successfully sent your text to {to}. Crumbs:\n\n{json.dumps(text_handler_response)}")

        return text_handler_response

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
    ): ...

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
    ): ...

    def email(
        self,
        *,
        to: str,
        from_: str,
        subject: str,
        reply_to: str = "",
        cc: str = "",
        text: str | None = None,
        html: str | None = None,
    ):
        """
        Send an email.
        Args:
            obj (dict): The object containing the email details.
                obj['to'] (str): The recipient's email address.
                obj['from'] (str): The sender's name. The email address is selected automatically. Configure at contiguity.co/dashboard
                obj['subject'] (str): The email subject.
                obj['text'] (str, optional): The plain text email body. Provide one body, or HTML will be prioritized if both are present.
                obj['html'] (str, optional): The HTML email body. Provide one body.
                obj['replyTo'] (str, optional): The reply-to email address.
                obj['cc'] (str, optional): The CC email addresses.
        Returns:
            dict: The response object.
        Raises:
            ValueError: Raises an error if required fields are missing or sending the email fails.
        """
        email_payload = {
            "to": to,
            "from": from_,
            "subject": subject,
            "body": minify(html) if html else text,
            "contentType": "html" if html else "text",
        }

        if reply_to:
            email_payload["replyTo"] = reply_to

        if cc:
            email_payload["cc"] = cc

        email_handler = self._client.post("/send/email", json=email_payload)

        email_handler_response = email_handler.json()

        if email_handler.status_code != 200:
            raise ValueError(
                f"Contiguity couldn't send your email. Received: {email_handler.status_code} with reason: \"{email_handler_response['message']}\""
            )
        if self.debug:
            print(f"Contiguity successfully sent your email to {to}. Crumbs:\n\n{json.dumps(email_handler_response)}")

        return email_handler_response
