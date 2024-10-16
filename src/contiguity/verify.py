import re

import phonenumbers

EMAIL_REGEX = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class Verify:
    def number(self, number: str) -> bool:
        try:
            return phonenumbers.is_valid_number(phonenumbers.parse(number))
        except phonenumbers.NumberParseException:
            return False

    def email(self, email: str) -> bool:
        return EMAIL_REGEX.match(email) is not None
