import pytest

from contiguity import Contiguity
from contiguity.imessage import IMessage
from tests import get_test_phone

pytest.skip("tests are WIP", allow_module_level=True)


@pytest.fixture
def imessage() -> IMessage:
    return Contiguity().imessage


def test_send_imessage_basic(imessage: IMessage) -> None:
    """Test sending a basic iMessage."""
    result = imessage.send(
        to=get_test_phone(),
        message="Hello via iMessage from pytest!",
    )

    assert result.message_id
    assert result.metadata


def test_send_imessage_with_attachments(imessage: IMessage) -> None:
    """Test sending an iMessage with attachments."""
    result = imessage.send(
        to=get_test_phone(),
        message="Check out this attachment!",
        attachments=["https://example.com/image1.jpg"],
    )

    assert result.message_id
    assert result.metadata


def test_start_typing(imessage: IMessage) -> None:
    """Test starting typing indicator."""
    result = imessage.start_typing(to=get_test_phone())

    assert result.status


def test_stop_typing(imessage: IMessage) -> None:
    """Test stopping typing indicator."""
    result = imessage.stop_typing(to=get_test_phone())

    assert result.status


def test_add_reaction(imessage: IMessage) -> None:
    """Test adding a reaction to a message."""
    result = imessage.add_reaction(
        to=get_test_phone(),
        reaction="❤️",
        message="test_message_id",
    )

    assert result.status
    assert result.message


def test_remove_reaction(imessage: IMessage) -> None:
    """Test removing a reaction from a message."""
    result = imessage.remove_reaction(
        to=get_test_phone(),
        reaction="❤️",
        message="test_message_id",
    )

    assert result.status


def test_mark_read(imessage: IMessage) -> None:
    """Test marking a message as read."""
    result = imessage.mark_read(
        to=get_test_phone(),
        from_="+14155552670",
    )

    assert result.status
    assert result.message
