import logging
from collections.abc import Mapping, Sequence
from typing import overload

from ._product import BaseProduct
from ._response import BaseResponse, decode_response

logger = logging.getLogger(__name__)


class EmailResponse(BaseResponse):
    email_id: str


class Email(BaseProduct):
    @overload
    def send(
        self,
        *,
        to: str,
        from_: str,
        subject: str,
        body_text: str,
        reply_to: str | None = None,
        cc: str | Sequence[str] | None = None,
        bcc: str | Sequence[str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> EmailResponse: ...

    @overload
    def send(
        self,
        *,
        to: str,
        from_: str,
        subject: str,
        body_html: str,
        reply_to: str | None = None,
        cc: str | Sequence[str] | None = None,
        bcc: str | Sequence[str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> EmailResponse: ...

    def send(  # noqa: PLR0913
        self,
        *,
        to: str,
        from_: str,
        subject: str,
        body_text: str | None = None,
        body_html: str | None = None,
        reply_to: str | None = None,
        cc: str | Sequence[str] | None = None,
        bcc: str | Sequence[str] | None = None,
        headers: Mapping[str, str] | None = None,
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
        if not body_text and not body_html:
            msg = "either text or html body must be provided"
            raise ValueError(msg)

        email_payload = {
            "to": to,
            "from": from_,
            "subject": subject,
            "body": {
                "text": body_text,
                "html": body_html,
            },
            "reply_to": reply_to,
            "cc": cc,
            "bcc": bcc,
            "headers": headers,
        }

        response = self._client.post(
            "/send/email",
            json={k: v for k, v in email_payload.items() if v},
        )

        self._client.handle_error(response, fail_message="failed to send email")
        data = decode_response(response.content, type=EmailResponse)
        logger.debug("successfully sent email to %r", to)
        return data
