import logging
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, Literal, TypeVar

from ._product import BaseProduct
from ._response import BaseResponse, decode_response

FallbackCauseT = TypeVar("FallbackCauseT", bound=str)

logger = logging.getLogger(__name__)


class IMSendResponse(BaseResponse):
    message_id: str


class IMTypingResponse(BaseResponse):
    status: str


class IMReactionResponse(IMTypingResponse):
    message: str


class InstantMessagingClient(ABC, BaseProduct, Generic[FallbackCauseT]):
    @property
    @abstractmethod
    def _api_path(self) -> str: ...

    def send(  # noqa: PLR0913
        self,
        *,
        to: str,
        message: str,
        from_: str | None = None,
        attachments: Sequence[str] | None = None,
        fallback_when: Sequence[FallbackCauseT] | None = None,
        fallback_number: str | None = None,
    ) -> IMSendResponse:
        payload = {
            "to": to,
            "message": message,
            "from": from_,
            "attachments": attachments,
            "fallback_when": fallback_when,
            "fallback_number": fallback_number,
        }

        response = self._client.post(
            self._api_path,
            json={k: v for k, v in payload.items() if v is not None},
        )

        self._client.handle_error(response, fail_message="failed to send instant message")
        data = decode_response(response.content, type=IMSendResponse)
        logger.debug("successfully sent %s message to %r", self._api_path[1:], to)
        return data

    def _typing(self, *, to: str, action: Literal["start", "stop"], from_: str | None = None) -> IMTypingResponse:
        payload = {
            "to": to,
            "action": action,
            "from": from_,
        }

        response = self._client.post(
            f"{self._api_path}/typing",
            json={k: v for k, v in payload.items() if v is not None},
        )

        self._client.handle_error(response, fail_message=f"failed to {action} {self._api_path[1:]} typing indicator")
        data = decode_response(response.content, type=IMTypingResponse)
        logger.debug("successfully %s %s typing indicator for %r", action, self._api_path[1:], to)
        return data

    def start_typing(self, *, to: str, from_: str | None = None) -> IMTypingResponse:
        return self._typing(to=to, action="start", from_=from_)

    def stop_typing(self, *, to: str, from_: str | None = None) -> IMTypingResponse:
        return self._typing(to=to, action="stop", from_=from_)

    def _reactions(
        self,
        *,
        to: str,
        action: Literal["add", "remove"],
        reaction: str,
        message: str,
    ) -> IMReactionResponse:
        payload = {
            "to": to,
            "action": action,
            "reaction": reaction,
            "message": message,
        }

        response = self._client.post(
            f"{self._api_path}/reactions",
            json={k: v for k, v in payload.items() if v is not None},
        )

        self._client.handle_error(response, fail_message=f"failed to {action} {self._api_path[1:]} reaction")
        data = decode_response(response.content, type=IMReactionResponse)
        logger.debug("successfully %s %s reaction for %r", action, self._api_path[1:], to)
        return data

    def add_reaction(self, *, to: str, reaction: str, message: str) -> IMReactionResponse:
        return self._reactions(to=to, action="add", reaction=reaction, message=message)

    def remove_reaction(self, *, to: str, reaction: str, message: str) -> IMReactionResponse:
        return self._reactions(to=to, action="remove", reaction=reaction, message=message)
