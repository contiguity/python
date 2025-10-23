import logging
from typing import Literal

from msgspec import Struct

from ._instant_messaging import InstantMessagingClient
from ._response import decode_response

FallbackCause = Literal["imessage_unsupported", "imessage_fails"]

logger = logging.getLogger(__name__)


class ReadResponse(Struct):
    status: str  # possible values?
    """Status of the read receipt."""
    message: str
    """Confirmation message."""


class MessageDelivery(Struct):
    status: Literal["delivered", "failed", "delayed"]
    delayed: bool
    timestamp: int
    """When the message was delivered."""


class MessageRisk(Struct):
    auto_reported_as_spam: bool
    """Whether the message was automatically labeled as spam by Apple."""
    marked_as_spam: bool
    """Whether the message was marked as spam by the user."""


class HistoryMessage(Struct):
    to: str
    from_: int
    message: str
    """Message content."""
    timestamp: int
    """When the message was sent."""
    read: int
    """When the message was read."""
    delivery: MessageDelivery
    risk: MessageRisk
    attachments: list[str]
    """URLs of the attachments."""


class HistoryReaction(Struct):
    reaction: str
    on: str
    """Message content."""
    timestamp: int
    action: str  # possible values?
    from_: str


class HistoryChat(Struct):
    filtered: bool
    """Whether the conversation was filtered by Apple."""
    chat_marked_as_spam: bool
    """Whether the chat was automatically labeled as spam by Apple."""
    limit: int
    """Message return limit."""
    total: int
    """Total number of messages in the conversation."""
    count: int
    """Number of messages returned."""


class History(Struct):
    conversation: list[HistoryMessage]
    reactions: list[HistoryReaction]
    chat: HistoryChat


class IMessage(InstantMessagingClient[FallbackCause]):
    @property
    def _api_path(self) -> str:
        return "/imessage"

    def mark_read(self, *, to: str, from_: str) -> ReadResponse:
        payload = {
            "to": to,
            "from": from_,
        }

        response = self._client.post(
            f"{self._api_path}/read",
            json={k: v for k, v in payload.items() if v is not None},
        )

        self._client.handle_error(response, fail_message="failed to send instant message")
        data = decode_response(response.content, type=ReadResponse)
        logger.debug("successfully sent %s read receipt to %r", self._api_path[1:], to)
        return data

    def get_history(self, *, to: str, from_: str, limit: int = 20) -> History:
        response = self._client.post(
            f"/history/{self._api_path}/{to}/{from_}/{limit}",
        )

        self._client.handle_error(response, fail_message="failed to get message history")
        return decode_response(response.content, type=History)
