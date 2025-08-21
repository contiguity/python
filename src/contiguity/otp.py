from __future__ import annotations

from enum import Enum
from http import HTTPStatus

import msgspec
import phonenumbers

from ._product import BaseProduct
from ._response import BaseResponse, ErrorResponse


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

        if response.status_code != HTTPStatus.OK:
            data = msgspec.json.decode(response.content, type=ErrorResponse)
            msg = f"Contiguity couldn't send your OTP. Received: {response.status_code} with reason: '{data.error}'"
            raise ValueError(msg)

        data = msgspec.json.decode(response.content, type=OTPSendResponse)
        if self.debug:
            print(f"Contiguity successfully sent your OTP to {to} with OTP ID {data.otp_id}")

        return data

    def resend(self, otp_id: str, /) -> OTPResendResponse:
        response = self._client.post(
            "/otp/resend",
            json={
                "otp_id": otp_id,
            },
        )

        if response.status_code != HTTPStatus.OK:
            data = msgspec.json.decode(response.content, type=ErrorResponse)
            msg = f"Contiguity couldn't resend your OTP. Received: {response.status_code} with reason: '{data.error}'"
            raise ValueError(msg)

        data = msgspec.json.decode(response.content, type=OTPResendResponse)
        if self.debug:
            print(f"Contiguity resent your OTP ({id}) with status: {data.resent}")

        return data

    def verify(self, otp: int | str, /, *, otp_id: str) -> OTPVerifyResponse:
        response = self._client.post(
            "/otp/verify",
            json={
                "otp": str(otp),
                "otp_id": otp_id,
            },
        )

        if response.status_code != HTTPStatus.OK:
            data = msgspec.json.decode(response.content, type=ErrorResponse)
            msg = f"Contiguity couldn't verify your OTP. Received: {response.status_code} with reason: '{data.error}'"
            raise ValueError(msg)

        data = msgspec.json.decode(response.content, type=OTPVerifyResponse)
        if self.debug:
            print(f"Contiguity verified your OTP ({otp}) with status: {data.verified}")

        return data
