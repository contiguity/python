from ._auth import get_contiguity_token
from ._client import ApiClient
from .domains import Domains
from .email import Email
from .imessage import IMessage
from .leases import Leases
from .otp import OTP
from .text import Text
from .whatsapp import WhatsApp


class Contiguity:
    """The Contiguity client."""

    def __init__(
        self,
        *,
        token: str | None = None,
        base_url: str = "https://api.contiguity.com",
    ) -> None:
        self.token = token or get_contiguity_token()
        self.base_url = base_url
        self.client = ApiClient(base_url=self.base_url, api_key=self.token.strip())

        self.text = Text(client=self.client)
        self.email = Email(client=self.client)
        self.otp = OTP(client=self.client)
        self.imessage = IMessage(client=self.client)
        self.whatsapp = WhatsApp(client=self.client)
        self.leases = Leases(client=self.client)
        self.domains = Domains(client=self.client)


__all__ = (
    "OTP",
    "Contiguity",
    "Domains",
    "Email",
    "IMessage",
    "Leases",
    "Text",
    "WhatsApp",
)
__version__ = "3.0.0"
