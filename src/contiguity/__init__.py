from ._client import ApiClient
from .analytics import EmailAnalytics
from .base import Base, BaseItem, InvalidKeyError, ItemConflictError, ItemNotFoundError, QueryResponse
from .otp import OTP
from .quota import Quota
from .send import Send
from .template import Template
from .verify import Verify


class Contiguity:
    """
    Create a new instance of the Contiguity class.
    Args:
        token (str): The authentication token.
        debug (bool, optional): A flag indicating whether to enable debug mode. Default is False.
    """

    def __init__(
        self,
        *,
        token: str,
        debug: bool = False,
        base_url: str = "https://api.contiguity.co",
        orwell_base_url: str = "https://orwell.contiguity.co",
    ) -> None:
        if not token:
            raise ValueError("Contiguity requires a token/API key to be provided via contiguity.login('token')")
        self.token = token
        self.debug = debug
        self.base_url = base_url
        self.orwell_base_url = orwell_base_url
        self.client = ApiClient(base_url=self.base_url, api_key=token.strip())
        self.orwell_client = ApiClient(base_url=self.orwell_base_url, api_key=token.strip())

        self.send = Send(client=self.client, debug=self.debug)
        self.verify = Verify()
        self.email_analytics = EmailAnalytics(client=self.orwell_client, debug=self.debug)
        self.quota = Quota(client=self.client, debug=self.debug)
        self.otp = OTP(client=self.client, debug=self.debug)
        self.template = Template()


def login(token: str, /, *, debug: bool = False) -> Contiguity:
    return Contiguity(token=token, debug=debug)


__all__ = (
    "Contiguity",
    "Send",
    "Verify",
    "EmailAnalytics",
    "Quota",
    "OTP",
    "Template",
    "Base",
    "BaseItem",
    "InvalidKeyError",
    "ItemConflictError",
    "ItemNotFoundError",
    "QueryResponse",
    "login",
)
__version__ = "2.0.0"
