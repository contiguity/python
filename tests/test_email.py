import pytest

from contiguity import Contiguity
from contiguity.email import Email
from tests import get_test_email

pytest.skip("tests are WIP", allow_module_level=True)


@pytest.fixture
def email() -> Email:
    return Contiguity().email


def test_email_with_text_body(email: Email) -> None:
    """Test sending an email with plain text body."""
    result = email.send(
        to=get_test_email(),
        from_="Test Sender",
        subject="Test Email with Text Body",
        body_text="This is a test email body sent from pytest.",
    )

    assert result.email_id
    assert result.metadata


def test_email_with_html_body(email: Email) -> None:
    """Test sending an email with HTML body."""
    result = email.send(
        to=get_test_email(),
        from_="Test Sender",
        subject="Test Email with HTML Body",
        body_html="<h1>This is a test email</h1><p>Sent from pytest.</p>",
    )

    assert result.email_id
    assert result.metadata


def test_email_with_optional_fields(email: Email) -> None:
    """Test sending an email with optional fields."""
    result = email.send(
        to=get_test_email(),
        from_="Test Sender",
        subject="Test Email with Optional Fields",
        body_text="This is a test email with optional fields.",
        reply_to=get_test_email(reply_to=True),
        cc=[get_test_email(cc=True)],
        headers={"X-Test-Header": "pytest"},
    )

    assert result.email_id
    assert result.metadata
