import re
import requests
import phonenumbers
import json
from htmlmin import minify

class Contiguity:
    """
    Create a new instance of the Contiguity class.
    Args:
        token (str): The authentication token.
        debug (bool, optional): A flag indicating whether to enable debug mode. Default is False.
    """
    def __init__(self, token, debug=False):
        self.token = token.strip()
        self.debug = debug
        self.baseURL = "https://api.contiguity.co"
        self.orwellBaseURL = "https://orwell.contiguity.co"
        self.headers = {"Content-Type": "application/json",
                "Authorization": f"Token {token}"}

    @property
    def send(self):
        """
        Returns an instance of the Send class.
        """
        return Send(self.token, self.baseURL, self.headers, self.debug)

    @property
    def verify(self):
        """
         Returns an instance of the Verify class.
         """
        return Verify(self.token)

    @property
    def email_analytics(self):
        """
         Returns an instance of the EmailAnalytics class.
         """
        return EmailAnalytics(self.token, self.orwellBaseURL, self.headers, self.debug)

    @property
    def quota(self):
        """
         Returns an instance of the Quota class.
         """
        return Quota(self.token, self.baseURL, self.headers,  self.debug)

    @property
    def otp(self):
        """
         Returns an instance of the OTP class.
         """
        return OTP(self.token, self.baseURL, self.headers, self.debug)

    @property
    def template(self):
        """
         Returns an instance of the Template class.
         """
        return Template()


class Send:
    """
    Send class for Contiguity.
    """

    def __init__(self, token, baseURL, headers, debug=False):
        self.token = token
        self.baseURL = baseURL
        self.debug = debug
        self.headers = headers

    def text(self, obj):
        """
        Send a text message.
        Args:
            obj (dict): The object containing the message details.
                obj['to'] (str): The recipient's phone number.
                obj['message'] (str): The message to send.
        Returns:
            dict: The response object.
        Raises:
            ValueError: Raises an error if required fields are missing or sending the message fails.
        """
        if 'to' not in obj:
            raise ValueError("Contiguity requires a recipient to be specified.")
        if 'message' not in obj:
            raise ValueError("Contiguity requires a message to be provided.")
        if not self.token:
            raise ValueError("Contiguity requires a token/API key to be provided via contiguity.login('token')")

        try:
            parsed_number = phonenumbers.parse(obj['to'], None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("Contiguity requires phone numbers to follow the E.164 format. Formatting failed.")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError("Contiguity requires phone numbers to follow the E.164 format. Parsing failed.")

        text_handler = requests.post(
            f"{self.baseURL}/send/text",
            json={
                'to': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
                'message': obj['message'],
            },
            headers= self.headers
        )
        text_handler_response = text_handler.json()

        if text_handler.status_code != 200:
            raise ValueError(
                f"Contiguity couldn't send your message. Received: {text_handler.status_code} with reason: \"{text_handler_response['message']}\"")
        if self.debug:
            print(
                f"Contiguity successfully sent your text to {obj['to']}. Crumbs:\n\n{json.dumps(text_handler_response)}")

        return text_handler_response

    def email(self, obj):
        """
        Send an email.
        Args:
            obj (dict): The object containing the email details.
                obj['to'] (str): The recipient's email address.
                obj['from'] (str): The sender's name. The email address is selected automatically. Configure at contiguity.co/dashboard
                obj['subject'] (str): The email subject.
                obj['text'] (str, optional): The plain text email body. Provide one body, or HTML will be prioritized if both are present.
                obj['html'] (str, optional): The HTML email body. Provide one body.
                obj['replyTo'] (str, optional): The reply-to email address.
                obj['cc'] (str, optional): The CC email addresses.
        Returns:
            dict: The response object.
        Raises:
            ValueError: Raises an error if required fields are missing or sending the email fails.
        """
        if 'to' not in obj:
            raise ValueError("Contiguity requires a recipient to be specified.")
        if 'from' not in obj:
            raise ValueError("Contiguity requires a sender to be specified.")
        if 'subject' not in obj:
            raise ValueError("Contiguity requires a subject to be specified.")
        if 'text' not in obj and 'html' not in obj:
            raise ValueError("Contiguity requires an email body (text or HTML) to be provided.")
        if not self.token:
            raise ValueError("Contiguity requires a token/API key to be provided via contiguity.login('token')")

        email_payload = {
            'to': obj['to'],
            'from': obj['from'],
            'subject': obj['subject'],
            'body': minify(obj['html']) if 'html' in obj else obj['text'],
            'contentType': 'html' if 'html' in obj else 'text',
        }

        if 'replyTo' in obj:
            email_payload['replyTo'] = obj['replyTo']

        if 'cc' in obj:
            email_payload['cc'] = obj['cc']

        email_handler = requests.post(
            f"{self.baseURL}/send/email",
            json=email_payload,
            headers= self.headers
        )

        email_handler_response = email_handler.json()

        if email_handler.status_code != 200:
            raise ValueError(
                f"Contiguity couldn't send your email. Received: {email_handler.status_code} with reason: \"{email_handler_response['message']}\"")
        if self.debug:
            print(
                f"Contiguity successfully sent your email to {obj['to']}. Crumbs:\n\n{json.dumps(email_handler_response)}")

        return email_handler_response


class Verify:
    def __init__(self, token):
        self.token = token

    def number(self, number):
        try:
            validity = phonenumbers.is_valid_number(phonenumbers.parse(number))
            return validity
        except Exception as e:
            return False

    def email(self, email):
        email_pattern = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
        return bool(email_pattern.match(email))


class EmailAnalytics:
    def __init__(self, token, orwellBaseURL, headers,  debug=False):
        self.token = token
        self.orwellBaseURL = orwellBaseURL
        self.debug = debug
        self.headers = headers

    def retrieve(self, id):
        if not self.token:
            raise ValueError("Contiguity requires a token/API key to be provided via contiguity.login('token')")
        if not id:
            raise ValueError("Contiguity Analytics requires an email ID.")

        status = requests.get(
            f"{self.orwellBaseURL}/email/status/{id}",
            headers= self.headers
        )

        json_data = status.json()

        if status.status_code != 200:
            raise ValueError(f"Contiguity Analytics couldn't find an email with ID {id}")
        if self.debug:
            print(f"Contiguity successfully found your email. Data:\n\n{json.dumps(json_data)}")

        return json_data


class Quota:
    def __init__(self, token, baseURL, headers,  debug=False):
        self.token = token
        self.baseURL = baseURL
        self.debug = debug
        self.headers = headers

    def retrieve(self):
        if not self.token:
            raise ValueError("Contiguity requires a token/API key to be provided via contiguity.login('token')")

        quota = requests.get(
            f"{self.baseURL}/user/get/quota",
            headers= self.headers
        )

        json_data = quota.json()

        if quota.status_code != 200:
            raise ValueError(
                f"Contiguity had an issue finding your quota. Received {quota.status_code} with reason: \"{json_data['message']}\"")
        if self.debug:
            print(f"Contiguity successfully found your quota. Data:\n\n{json.dumps(json_data)}")

        return json_data


class OTP:
    def __init__(self, token, baseURL, headers, debug=False):
        self.token = token
        self.baseURL = baseURL
        self.debug = debug
        self.headers = headers

    def send(self, obj):
        if not self.token:
            raise ValueError("Contiguity requires a token/API key to be provided via contiguity.login('token')")
        if "to" not in obj:
            raise ValueError("Contiguity requires a recipient to be specified.")
        if "language" not in obj:
            raise ValueError("Contiguity requires a language to be specified.")

        e164 = phonenumbers.format_number(phonenumbers.parse(obj["to"]), phonenumbers.PhoneNumberFormat.E164)

        otp_handler = requests.post(
            f"{self.baseURL}/otp/new",
            json={
                "to": e164,
                "language": obj["language"],
                "name": obj.get("name"),
            },
            headers= self.headers
        )

        otp_handler_response = otp_handler.json()

        if otp_handler.status_code != 200:
            raise ValueError(
                f"Contiguity couldn't send your OTP. Received: {otp_handler.status_code} with reason: \"{otp_handler_response['message']}\"")
        if self.debug:
            print(f"Contiguity successfully sent your OTP to {obj['to']} with OTP ID {otp_handler_response['otp_id']}")

        return otp_handler_response["otp_id"]

    def verify(self, obj):
        if not self.token:
            raise ValueError("Contiguity requires a token/API key to be provided via contiguity.login('token')")
        if "otp_id" not in obj:
            raise ValueError("Contiguity requires an OTP ID to be specified.")
        if "otp" not in obj:
            raise ValueError("Contiguity requires an OTP (user input) to be specified.")

        otp_handler = requests.post(
            f"{self.baseURL}/otp/verify",
            json={
                "otp": obj["otp"],
                "otp_id": obj["otp_id"],
            },
            headers= self.headers
        )

        otp_handler_response = otp_handler.json()

        if otp_handler.status_code != 200:
            raise ValueError(
                f"Contiguity couldn't verify your OTP. Received: {otp_handler.status_code} with reason: \"{otp_handler_response['message']}\"")
        if self.debug:
            print(
                f"Contiguity 'verified' your OTP ({obj['otp']}) with boolean verified status: {otp_handler_response['verified']}")

        return otp_handler_response["verified"]

    def resend(self, obj):
        if not self.token:
            raise ValueError("Contiguity requires a token/API key to be provided via contiguity.login('token')")
        if "otp_id" not in obj:
            raise ValueError("Contiguity requires an OTP ID to be specified.")

        otp_handler = requests.post(
            f"{self.baseURL}/otp/resend",
            json={
                "otp_id": obj["otp_id"],
            },
            headers= self.headers
        )

        otp_handler_response = otp_handler.json()

        if otp_handler.status_code != 200:
            raise ValueError(
                f"Contiguity couldn't resend your OTP. Received: {otp_handler.status_code} with reason: \"{otp_handler_response['message']}\"")
        if self.debug:
            print(
                f"Contiguity resent your OTP ({obj['otp']}) with boolean resent status: {otp_handler_response['verified']}")

        return otp_handler_response["verified"]


class Template:
    def local(self, file):
        try:
            with open(file, "r") as f:
                file_content = f.read()
                mini = minify(file_content, minify_js=True, minify_css=True)
                return mini
        except IOError:
            raise ValueError("Getting contents from files is not supported in the current environment.")

    async def online(self, file_name):
        # Coming soon
        pass