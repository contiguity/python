import pytest

from contiguity import Contiguity
from contiguity.otp import OTP, OTPLanguage
from tests import get_test_phone


@pytest.fixture
def otp_client() -> OTP:
    return Contiguity().otp


def test_send_otp_basic(otp: OTP) -> None:
    """Test sending a basic OTP."""
    result = otp.send(get_test_phone())

    assert result.otp_id
    assert result.metadata


def test_send_otp_with_name(otp: OTP) -> None:
    """Test sending an OTP with a custom name."""
    result = otp.send(get_test_phone(), name="PyTest App")

    assert result.otp_id
    assert result.metadata


def test_send_otp_with_language(otp: OTP) -> None:
    """Test sending an OTP with a different language."""
    result = otp.send(get_test_phone(), language=OTPLanguage.SPANISH)

    assert result.otp_id
    assert result.metadata
