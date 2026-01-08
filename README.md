<p align="center"><img src="https://contiguity.co/assets/icon-black.png" height="150px"/></p>
<h1 align="center">@contiguity/python</h1>
<p align="center">
    <img display="inline-block" src="https://img.shields.io/pypi/v/contiguity?style=for-the-badge" />
    <img display="inline-block" src="https://img.shields.io/badge/Made%20with-Python-green?style=for-the-badge" />
</p>
<p align="center">Contiguity's official Python SDK.</p>

## Documentation 📖

[Full documentation](https://docs.contiguity.com/sdk/python)

## Installation & setup 🛠

You can install the SDK using pip

```shell
pip install contiguity
```

Then, import & initialize it like this:

```python
from contiguity import Contiguity

client = Contiguity(token="your_token_here")
```

> [!TIP]
> It is recommended to set the `CONTIGUITY_TOKEN` environment variable instead of hardcoding your token. The SDK will automatically read this variable if no token is provided during initialization.

You can get your token from the [Contiguity console](https://console.contiguity.com/).

## Sending your first email 📤

As long as you provided Contiguity a valid token, and provide valid inputs, sending emails will be a breeze!

To send an email with an HTML body:

```python
client.email.send(
    to="example@example.com",
    from_="Contiguity",
    subject="My first email!",
    body_html="<b>I sent an email using Contiguity</b>",
)
```

To send an email with a text body:

```python
client.email.send(
    to="example@example.com",
    from_="Contiguity",
    subject="My first email!",
    body_text="I sent an email using Contiguity",
)
```

### Optional fields

- `reply_to` allows you to set a reply-to email address.
- `cc` allows you to CC email addresses.
- `bcc` allows you to BCC email addresses.
- `headers` allows you to set custom email headers.

## Sending your first text message 💬

As long as you provided Contiguity a valid token, and will provide valid inputs, sending texts will be a breeze!

```python
client.text.send(to="+15555555555", message="My first text using Contiguity")
```

**Note**: _Contiguity expects the recipient phone number to be formatted in E.164. You can attempt to pass numbers in formats like NANP, and the SDK will try its best to convert it. If it fails, it will throw an error!_

## Sending your first OTP 🔑

Contiguity aims to make communications extremely simple and elegant. In doing so, we're providing an OTP API to send one time codes - for free (no additional charge, the text message is still billed/added to quota)

To send your first OTP, first create one:

```python
from contiguity.otp import OTPLanguage

response = client.otp.send("+15555555555", language=OTPLanguage.ENGLISH, name="Contiguity")
otp_id = response.otp_id
```

Contiguity supports 33 languages for OTPs, see the [OTPLanguage enum](src/contiguity/otp.py) for the full list.

_The `name` parameter is optional, it customizes the message to say "Your \[name] code is ..."_

To verify an OTP a user has inputted, simply call `client.otp.verify()`:

```python
response = client.otp.verify(otp_id, otp=user_input)
is_verified = response.verified  # True or False
```

The OTP expires 15 minutes after sending it.

Want to resend an OTP? Use `client.otp.resend()`:

```python
response = client.otp.resend(otp_id)
```

OTP expiry does not renew.

## More examples 📚

The SDK also supports sending iMessages, WhatsApp messages, managing email domains, and leasing phone numbers.

See more examples in the [examples](examples/) folder.

## Roadmap 🚦

- Contiguity Identity will be supported
- Adding support for calls
- Adding support for webhooks
- and much more!

## License ⚖️

[MIT License](LICENSE.txt)
