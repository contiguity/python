import pytest

from contiguity import Contiguity
from contiguity.text import Text
from tests import get_test_phone

pytest.skip("tests are WIP", allow_module_level=True)


@pytest.fixture
def text() -> Text:
    return Contiguity().text


def test_send_text_basic(text: Text) -> None:
    """Test sending a basic text message."""
    result = text.send(
        to=get_test_phone(),
        message="Hello, this is a test message from pytest!",
    )

    assert result.message_id
    assert result.metadata


def test_send_text_with_from(text: Text) -> None:
    """Test sending a text message with from field."""
    result = text.send(
        to=get_test_phone(),
        message="Hello from a specific sender!",
        from_="+14155552670",
    )

    assert result.message_id
    assert result.metadata


def test_send_text_with_attachments(text: Text) -> None:
    """Test sending a text message with attachments."""
    result = text.send(
        to=get_test_phone(),
        message="Check out these attachments!",
        attachments=["https://example.com/image1.jpg"],
    )

    assert result.message_id
    assert result.metadata


def test_send_text_invalid_number_format(text: Text) -> None:
    """Test that invalid phone number format raises ValueError."""
    with pytest.raises(ValueError, match="parsing failed"):
        text.send(
            to="invalid_number",
            message="This should fail",
        )


def test_send_text_invalid_number_validation(text: Text) -> None:
    """Test that invalid phone number validation raises ValueError."""
    with pytest.raises(ValueError, match="formatting failed"):
        text.send(
            to="+1234",
            message="This should fail",
        )
