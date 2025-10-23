from typing import Literal

from msgspec import Struct

from ._product import BaseProduct
from ._response import decode_response

Carrier = Literal["T-Mobile", "AT&T", "Verizon", "Twilio", "Contiguity", "International Partner"]
LeaseStatus = Literal["active", "expired", "terminated"]


class NumberFormats(Struct):
    e164: str
    formatted: str


class NumberLocation(Struct):
    country: str
    region: str
    city: str


class NumberCapabilities(Struct):
    intl_sms: bool
    channels: list[Literal["sms", "mms", "rcs", "imessage", "whatsapp"]]


class NumberHealth(Struct):
    reputation: float
    previous_owners: int


class AdditionalNumberData(Struct):
    requirements: list[
        Literal["imessage_entitlement_required", "whatsapp_entitlement_required", "enterprise_plan_required"]
    ]
    e911_capable: bool


class NumberPricing(Struct):
    currency: str
    upfront_fee: float
    monthly_rate: float


class NumberBillingPeriod(Struct):
    start: int
    end: int | None


class NumberBilling(Struct):
    method: Literal["monthly", "service_contract", "goodwill"]
    period: NumberBillingPeriod


class NumberDetails(Struct):
    id: str
    """Phone number in E.164 format"""
    status: Literal["available", "g-available", "leased", "unavailable"]
    number: NumberFormats
    location: NumberLocation
    carrier: Carrier
    capabilities: NumberCapabilities
    health: NumberHealth
    data: AdditionalNumberData
    created_at: int
    pricing: NumberPricing
    lease_id: str | None
    lease_status: LeaseStatus | None
    billing: NumberBilling | None


class TerminateLeaseResponse(Struct):
    lease_id: str
    number_id: str
    status: LeaseStatus
    terminated_at: int


class Leases(BaseProduct):
    def get_available_numbers(self) -> list[NumberDetails]:
        response = self._client.get("/leases")
        self._client.handle_error(response, fail_message="failed to get available numbers")
        return decode_response(response.content, type=list[NumberDetails])

    def get_leased_numbers(self) -> list[NumberDetails]:
        response = self._client.get("/leased")
        self._client.handle_error(response, fail_message="failed to get leased numbers")
        return decode_response(response.content, type=list[NumberDetails])

    def get_number_details(self, number: str, /) -> NumberDetails:
        response = self._client.get(f"/lease/{number}")
        self._client.handle_error(response, fail_message="failed to get number details")
        return decode_response(response.content, type=NumberDetails)

    def lease_number(
        self,
        number: NumberDetails | str,
        /,
        *,
        billing_method: Literal["monthly", "service_contract"],
    ) -> NumberDetails:
        number = number.id if isinstance(number, NumberDetails) else number
        response = self._client.post(
            f"/lease/{number}",
            json={"billing_method": billing_method},
        )
        self._client.handle_error(response, fail_message="failed to lease number")
        return decode_response(response.content, type=NumberDetails)

    def terminate_lease(self, number: NumberDetails | str, /) -> TerminateLeaseResponse:
        number = number.id if isinstance(number, NumberDetails) else number
        response = self._client.delete(f"/leased/{number}")
        self._client.handle_error(response, fail_message="failed to terminate lease")
        return decode_response(response.content, type=TerminateLeaseResponse)
