import pytest

from contiguity.verify import Verify


@pytest.fixture
def verify() -> Verify:
    return Verify()


def test_verify_valid_number(verify: Verify) -> None:
    """Test verifying a valid phone number."""
    assert verify.number("+14155552671") is True
    assert verify.number("+44 20 7946 0958") is True
    assert verify.number("+49 30 901820") is True


def test_verify_invalid_number(verify: Verify) -> None:
    """Test verifying invalid phone numbers."""
    assert verify.number("invalid") is False
    assert verify.number("1234") is False
    assert verify.number("") is False
    assert verify.number("abc123") is False


def test_verify_malformed_number(verify: Verify) -> None:
    """Test verifying malformed phone numbers."""
    assert verify.number("+1-415-555-2671-extra") is False


def test_verify_valid_email(verify: Verify) -> None:
    """Test verifying valid email addresses."""
    assert verify.email("test@example.com") is True
    assert verify.email("user.name@example.co.uk") is True
    assert verify.email("user+tag@example.com") is True
    assert verify.email("123@domain.org") is True


def test_verify_invalid_email(verify: Verify) -> None:
    """Test verifying invalid email addresses."""
    assert verify.email("invalid") is False
    assert verify.email("@example.com") is False
    assert verify.email("user@") is False
    assert verify.email("user @example.com") is False
    assert verify.email("user@domain") is False
    assert verify.email("") is False
    assert verify.email("user@.com") is False


def test_verify_edge_case_emails(verify: Verify) -> None:
    """Test verifying edge case email addresses."""
    assert verify.email("user@@example.com") is False
    assert verify.email("user@.") is False
    assert verify.email("@") is False
