from enum import Enum
from http import HTTPStatus

import msgspec
import phonenumbers

from ._client import ApiClient
from ._common import Crumbs


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


class OTPSendResponse(msgspec.Struct):
    message: str
    crumbs: Crumbs
    otp_id: str


class OTPResendResponse(msgspec.Struct):
    message: str
    resent: bool


class OTPVerifyResponse(msgspec.Struct):
    message: str
    verified: bool


class OTP:
    def __init__(self, *, client: ApiClient, debug: bool = False) -> None:
        self._client = client
        self.debug = debug

    def send(
        self,
        to: str,
        /,
        *,
        name: "str | None" = None,
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
        data = msgspec.json.decode(response.content, type=OTPSendResponse)

        if response.status_code != HTTPStatus.OK:
            msg = f"Contiguity couldn't send your OTP. Received: {response.status_code} with reason: '{data.message}'"
            raise ValueError(msg)
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
        data = msgspec.json.decode(response.content, type=OTPResendResponse)

        if response.status_code != HTTPStatus.OK:
            msg = (
                f"Contiguity couldn't resend your OTP. Received: {response.status_code} with reason: '{data.message}'"
            )
            raise ValueError(msg)
        if self.debug:
            print(f"Contiguity resent your OTP ({id}) with status: {data.resent}")

        return data

    def verify(self, otp: "int | str", /, *, otp_id: str) -> OTPVerifyResponse:
        response = self._client.post(
            "/otp/verify",
            json={
                "otp": str(otp),
                "otp_id": otp_id,
            },
        )
        data = msgspec.json.decode(response.content, type=OTPVerifyResponse)

        if response.status_code != HTTPStatus.OK:
            msg = (
                f"Contiguity couldn't verify your OTP. Received: {response.status_code} with reason: '{data.message}'"
            )
            raise ValueError(msg)
        if self.debug:
            print(f"Contiguity verified your OTP ({otp}) with status: {data.verified}")

        return data
