import logging
from collections.abc import Sequence

import phonenumbers

from ._product import BaseProduct
from ._response import BaseResponse, decode_response

logger = logging.getLogger(__name__)


class TextResponse(BaseResponse):
    message_id: str


class Text(BaseProduct):
    def send(
        self,
        *,
        to: str,
        message: str,
        from_: str | None = None,
        attachments: Sequence[str] | None = None,
    ) -> TextResponse:
        try:
            parsed_number = phonenumbers.parse(to, None)
            if not phonenumbers.is_valid_number(parsed_number):
                msg = "formatting failed. Phone number must follow the E.164 format."
                raise ValueError(msg)
        except phonenumbers.NumberParseException as exc:
            msg = "parsing failed. Phone number must follow the E.164 format."
            raise ValueError(msg) from exc

        payload = {
            "to": phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
            "message": message,
            "from": from_,
            "attachments": attachments,
        }

        response = self._client.post(
            "/send/text",
            json={k: v for k, v in payload.items() if v is not None},
        )

        self._client.handle_error(response, fail_message="failed to send text message")
        data = decode_response(response.content, type=TextResponse)
        logger.debug("successfully sent text to %r", to)
        return data
