import logging
from collections.abc import Sequence
from http import HTTPStatus

import msgspec

from ._product import BaseProduct
from ._response import BaseResponse, ErrorResponse, decode_response

logger = logging.getLogger(__name__)


class PartialDomain(msgspec.Struct):
    domain: str
    status: str
    id: str
    created_at: int
    region: str
    sending_allowed: bool


class DnsRecord(msgspec.Struct):
    type: str
    name: str
    value: str
    purpose: str


class DomainVerifications(msgspec.Struct):
    dkim: str
    mail_from: str
    domain: str


class Domain(PartialDomain):
    records: Sequence[DnsRecord]
    verifications: DomainVerifications


class DeleteDomainResponse(BaseResponse):
    success: bool
    message: str


class Domains(BaseProduct):
    def register(
        self,
        domain: str,
        /,
        *,
        region: str = "us-east-1",
        custom_return_path: str = "contiguity",
    ) -> PartialDomain:
        response = self._client.post(
            f"/domains/{domain}",
            json={
                "region": region,
                "custom_return_path": custom_return_path,
            },
        )

        if response.status_code != HTTPStatus.OK:
            data = decode_response(response.content, type=ErrorResponse)
            msg = f"failed to register domain. {response.status_code} {data.error}"
            raise ValueError(msg)

        data = decode_response(response.content, type=PartialDomain)
        logger.debug("successfully registered domain %r", domain)
        return data

    def list(self) -> list[PartialDomain]:
        response = self._client.get("/domains")

        if response.status_code != HTTPStatus.OK:
            data = decode_response(response.content, type=ErrorResponse)
            msg = f"failed to list domains. {response.status_code} {data.error}"
            raise ValueError(msg)

        return decode_response(response.content, type=list[PartialDomain])

    def get(self, domain: str, /) -> Domain:
        response = self._client.get(f"/domains/{domain}")

        if response.status_code != HTTPStatus.OK:
            data = decode_response(response.content, type=ErrorResponse)
            msg = f"failed to get domain. {response.status_code} {data.error}"
            raise ValueError(msg)

        return decode_response(response.content, type=Domain)

    def delete(self, domain: str, /) -> DeleteDomainResponse:
        response = self._client.delete(f"/domains/{domain}")

        if response.status_code != HTTPStatus.OK:
            data = decode_response(response.content, type=ErrorResponse)
            msg = f"failed to delete domain. {response.status_code} {data.error}"
            raise ValueError(msg)

        data = decode_response(response.content, type=DeleteDomainResponse)
        logger.debug("successfully deleted domain %r", domain)
        return data
