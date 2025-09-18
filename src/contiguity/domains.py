import logging
from collections.abc import Sequence

from msgspec import Struct

from ._product import BaseProduct
from ._response import BaseResponse, decode_response

logger = logging.getLogger(__name__)


class PartialDomain(Struct):
    domain: str
    status: str
    id: str
    created_at: int
    region: str
    sending_allowed: bool


class DnsRecord(Struct):
    type: str
    name: str
    value: str
    purpose: str


class DomainVerifications(Struct):
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

        self._client.handle_error(response, fail_message="failed to register domain")
        data = decode_response(response.content, type=PartialDomain)
        logger.debug("successfully registered domain %r", domain)
        return data

    def list(self) -> list[PartialDomain]:
        response = self._client.get("/domains")
        self._client.handle_error(response, fail_message="failed to list domains")
        return decode_response(response.content, type=list[PartialDomain])

    def get(self, domain: str, /) -> Domain:
        response = self._client.get(f"/domains/{domain}")
        self._client.handle_error(response, fail_message="failed to get domain")
        return decode_response(response.content, type=Domain)

    def delete(self, domain: str, /) -> DeleteDomainResponse:
        response = self._client.delete(f"/domains/{domain}")
        self._client.handle_error(response, fail_message="failed to delete domain")
        data = decode_response(response.content, type=DeleteDomainResponse)
        logger.debug("successfully deleted domain %r", domain)
        return data
