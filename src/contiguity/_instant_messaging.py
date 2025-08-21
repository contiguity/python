from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import TYPE_CHECKING, Generic, Literal, TypeVar

from ._product import BaseProduct
from ._response import BaseResponse, ErrorResponse, decode_response

if TYPE_CHECKING:
    from collections.abc import Sequence

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

        if response.status_code != HTTPStatus.OK:
            data = decode_response(response.content, type=ErrorResponse)
            msg = f"failed to send instant message. {response.status_code} {data.error}"
            raise ValueError(msg)

        data = decode_response(response.content, type=IMSendResponse)
        if self.debug:
            logger.debug(f"successfully sent {self._api_path[1:]} message to {to}")

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

        if response.status_code != HTTPStatus.OK:
            data = decode_response(response.content, type=ErrorResponse)
            msg = f"failed to {action} {self._api_path[1:]} typing indicator. {response.status_code} {data.error}"
            raise ValueError(msg)

        data = decode_response(response.content, type=IMTypingResponse)
        if self.debug:
            logger.debug(f"successfully {action} {self._api_path[1:]} typing indicator for {to}")

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

        if response.status_code != HTTPStatus.OK:
            data = decode_response(response.content, type=ErrorResponse)
            msg = f"failed to {action} {self._api_path[1:]} reaction. {response.status_code} {data.error}"
            raise ValueError(msg)

        data = decode_response(response.content, type=IMReactionResponse)
        if self.debug:
            logger.debug(f"successfully {action} {self._api_path[1:]} reaction for {to}")

        return data

    def add_reaction(self, *, to: str, reaction: str, message: str) -> IMReactionResponse:
        return self._reactions(to=to, action="add", reaction=reaction, message=message)

    def remove_reaction(self, *, to: str, reaction: str, message: str) -> IMReactionResponse:
        return self._reactions(to=to, action="remove", reaction=reaction, message=message)
