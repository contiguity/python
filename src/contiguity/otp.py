import logging
from enum import Enum

import phonenumbers

from ._product import BaseProduct
from ._response import BaseResponse, decode_response

logger = logging.getLogger(__name__)


class OTPLanguage(str, Enum):
    ENGLISH = "en"
    AFRIKAANS = "af"
    ARABIC = "ar"
    CATALAN = "ca"
    CHINESE = "zh"
    "Chinese (Mandarin)"
    CANTONESE = "zh-hk"
    "Chinese (Cantonese)"
    CROATIAN = "hr"
    CZECH = "cs"
    DANISH = "da"
    DUTCH = "nl"
    FINNISH = "fi"
    FRENCH = "fr"
    GERMAN = "de"
    GREEK = "el"
    HEBREW = "he"
    HINDI = "hi"
    HUNGARIAN = "hu"
    INDONESIAN = "id"
    ITALIAN = "it"
    JAPANESE = "ja"
    KOREAN = "ko"
    MALAY = "ms"
    NORWEGIAN = "nb"
    POLISH = "pl"
    PORTUGUESE = "pt"
    PORTUGUESE_BRAZIL = "pt-br"
    ROMANIAN = "ro"
    RUSSIAN = "ru"
    SPANISH = "es"
    SWEDISH = "sv"
    TAGALOG = "tl"
    THAI = "th"
    TURKISH = "tr"
    VIETNAMESE = "vi"


class OTPSendResponse(BaseResponse):
    otp_id: str


class OTPResendResponse(BaseResponse):
    resent: bool


class OTPVerifyResponse(BaseResponse):
    verified: bool


class OTP(BaseProduct):
    def send(
        self,
        to: str,
        /,
        *,
        name: str | None = None,
        language: OTPLanguage = OTPLanguage.ENGLISH,
    ) -> OTPSendResponse:
        e164 = phonenumbers.format_number(phonenumbers.parse(to), phonenumbers.PhoneNumberFormat.E164)

        response = self._client.post(
            "/otp/new",
            json={
                "to": e164,
                "language": language,
                "name": name,
            },
        )

        self._client.handle_error(response, fail_message="failed to send OTP")
        data = decode_response(response.content, type=OTPSendResponse)
        logger.debug("successfully sent OTP %r to %r", data.otp_id, to)
        return data

    def resend(self, otp_id: str, /) -> OTPResendResponse:
        response = self._client.post(
            "/otp/resend",
            json={
                "otp_id": otp_id,
            },
        )

        self._client.handle_error(response, fail_message="failed to resend OTP")
        data = decode_response(response.content, type=OTPResendResponse)
        logger.debug("successfully resent OTP %r with status: %r", otp_id, data.resent)
        return data

    def verify(self, otp: int | str, /, *, otp_id: str) -> OTPVerifyResponse:
        response = self._client.post(
            "/otp/verify",
            json={
                "otp": str(otp),
                "otp_id": otp_id,
            },
        )

        self._client.handle_error(response, fail_message="failed to verify OTP")
        data = decode_response(response.content, type=OTPVerifyResponse)
        logger.debug("successfully verified OTP %r with status: %r", otp_id, data.verified)
        return data
