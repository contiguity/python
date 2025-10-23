from typing import Literal

from ._instant_messaging import InstantMessagingClient

FallbackCause = Literal["whatsapp_unsupported", "whatsapp_fails"]


class WhatsApp(InstantMessagingClient[FallbackCause]):
    @property
    def _api_path(self) -> str:
        return "/whatsapp"
