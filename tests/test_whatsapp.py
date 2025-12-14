import pytest

from contiguity import Contiguity
from contiguity.whatsapp import WhatsApp
from tests import get_test_phone

pytest.skip("tests are WIP", allow_module_level=True)


@pytest.fixture
def whatsapp() -> WhatsApp:
    return Contiguity().whatsapp


def test_send_whatsapp_basic(whatsapp: WhatsApp) -> None:
    """Test sending a basic WhatsApp message."""
    whatsapp.send(
        to=get_test_phone(),
        message="Hello via WhatsApp!",
    )


def test_send_whatsapp_with_attachments(whatsapp: WhatsApp) -> None:
    """Test sending a WhatsApp message with attachments."""
    whatsapp.send(
        to=get_test_phone(),
        message="Check out these attachments!",
        attachments=["https://example.com/image1.jpg"],
    )


def test_start_typing(whatsapp: WhatsApp) -> None:
    """Test starting typing indicator."""
    whatsapp.start_typing(to=get_test_phone())


def test_stop_typing(whatsapp: WhatsApp) -> None:
    """Test stopping typing indicator."""
    whatsapp.stop_typing(to=get_test_phone())


def test_add_reaction(whatsapp: WhatsApp) -> None:
    """Test adding a reaction to a message."""
    whatsapp.add_reaction(
        to=get_test_phone(),
        reaction="❤️",
        message="msg_123",
    )


def test_remove_reaction(whatsapp: WhatsApp) -> None:
    """Test removing a reaction from a message."""
    whatsapp.remove_reaction(
        to=get_test_phone(),
        reaction="❤️",
        message="msg_123",
    )
