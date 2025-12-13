import random
import string

from dotenv import load_dotenv

from contiguity._auth import _get_env_var

load_dotenv()

NON_EXISTENT_ITEM_WARNING = (
    "ItemNotFoundError will be raised in the future. To receive None for non-existent keys, set default=None."
)


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def get_test_email(*, reply_to: bool = False, cc: bool = False) -> str:
    if reply_to:
        return _get_env_var("TEST_REPLY_TO_EMAIL", "test reply-to email address")
    if cc:
        return _get_env_var("TEST_CC_EMAIL", "test cc email address")
    return _get_env_var("TEST_EMAIL", "test email address")


def get_test_phone() -> str:
    return _get_env_var("TEST_PHONE_NUMBER", "test phone number")
