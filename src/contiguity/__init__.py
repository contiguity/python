from ._client import ApiClient
from .email import Email
from .otp import OTP
from .text import Text


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
        base_url: str = "https://api.contiguity.com",
        debug: bool = False,
    ) -> None:
        if not token:
            msg = "Contiguity requires a token/API key to be provided via contiguity.login('token')"
            raise ValueError(msg)
        self.token = token
        self.base_url = base_url
        self.debug = debug
        self.client = ApiClient(base_url=self.base_url, api_key=token.strip())

        self.text = Text(client=self.client, debug=self.debug)
        self.email = Email(client=self.client, debug=self.debug)
        self.otp = OTP(client=self.client, debug=self.debug)


__all__ = (
    "OTP",
    "Contiguity",
    "Email",
    "Text",
)
__version__ = "3.0.0"
