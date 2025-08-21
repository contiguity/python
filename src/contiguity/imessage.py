from typing import Literal

from ._instant_messaging import InstantMessagingClient

FallbackCause = Literal["imessage_unsupported", "imessage_fails"]


class IMessage(InstantMessagingClient[FallbackCause]):
    @property
    def _api_path(self) -> str:
        return "/imessage"
