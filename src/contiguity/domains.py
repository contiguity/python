import msgspec
from contiguity._response import BaseResponse, ErrorResponse


class DnsRecord(msgspec.Struct):
    ...


class DomainVerifications(msgspec.Struct):
    # TODO: change to bools?
    dkim: str
    mail_from: str
    domain: str


class Domain(msgspec.Struct):
    domain: str
    status: str
    id: str
    created_at: int
    records: list[DnsRecord]
    region: str
    sending_allowed: bool
    verifications: DomainVerifications


class Domains:
    def register(self, domain: str, /, region: str = "us-east-1", custom_return_path: str = "contiguity"):
        raise NotImplementedError

    def list(self):
        raise NotImplementedError

    def get(self, domain: str, /):
        raise NotImplementedError

    def delete(self, domain: str, /):
        raise NotImplementedError
