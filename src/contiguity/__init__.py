from ._client import ApiClient
from .domains import Domains
from .email import Email
from .imessage import IMessage
from .leases import Leases
from .otp import OTP
from .text import Text
from .whatsapp import WhatsApp


class Contiguity:
    """
    Create a new instance of the Contiguity class.

    Args:
        token (str): The authentication token.
    """

    def __init__(
        self,
        *,
        token: str,
        base_url: str = "https://api.contiguity.com",
    ) -> None:
        if not token:
            msg = "token cannot be empty"
            raise ValueError(msg)
        self.token = token
        self.base_url = base_url
        self.client = ApiClient(base_url=self.base_url, api_key=token.strip())

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
