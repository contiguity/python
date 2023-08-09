<p align='center'><img src="https://contiguity.co/assets/icon-black.png" height="150px"/></p>
<h1 align='center'>@contiguity/python</h1>

<p align='center'>
    <img display="inline-block" src="https://img.shields.io/pypi/v/contiguity?style=for-the-badge" /> <img display="inline-block" src="https://img.shields.io/badge/Made%20with-Python-green?style=for-the-badge" />
</p>
<p align='center'>Contiguity's official Python SDK.</p>

## Installation 🏗 & Setup 🛠
You can install the SDK using pip
```shell
$ pip install contiguity
```

Then, import & initialize it like this:
```js
import contiguity
client = contiguity.login("your_token_here")
```

You can also initialize it with the optional 'debug' flag:
```js
client = contiguity.login("your_token_here", True)
```

You can get your token from the Contiguity [dashboard](https://contiguity.co/dashboard).

## Sending your first email 📤

As long as you provided Contiguity a valid token, and provide valid inputs, sending emails will be a breeze!

To begin sending an email with an HTML body, you can define a JSON object with all the required fields.

```python
email_object = {
    "to": "example@example.com",
    "from": "Contiguity",
    "subject": "My first email!",
    "html": "<b>I sent an email using Contiguity</b>"
}

client.send.email(email_object)
```

To send an email with a text body, it's very similar. Just switch "html" to "text".
```python
email_object = {
    "to": "example@example.com",
    "from": "Contiguity",
    "subject": "My first email!",
    "text": "I sent an email using Contiguity"
}

client.send.email(email_object)
```

### Optional fields:
- `replyTo` allows you set a reply-to email address. 
- `cc` allows you to CC an email address

You can also fetch a local email template using `client.template.local(file)`:

```python
template = client.template.local('templates/first_email.html')

email_object = {
    "to": "example@example.com",
    "from": "Contiguity",
    "subject": "My first email!",
    "html": template,
}

client.send.email(email_object)
```

## Sending your first text message 💬

As long as you provided Contiguity a valid token, and will provide valid inputs, sending texts will be a breeze!

To begin sending a text message, you can define a JSON object with all the required fields.

```js
text_object = {
    "to": "+15555555555",
    "message": "My first text using Contiguity"
}

client.send.text(text_object)
```

**Note**: _Contiguity expects the recipient phone number to be formatted in E.164. You can attempt to pass numbers in formats like NANP, and the SDK will try its best to convert it. If it fails, it will throw an error!_

## Sending your first OTP 🔑

Contiguity aims to make communications extremely simple and elegant. In doing so, we're providing an OTP API to send one time codes - for free (no additional charge, the text message is still billed / added to quota)

To send your first OTP, first create one:
```python
otp_id = client.otp.send({ 
    'to': "+15555555555", 
    'language': "en", 
    'name': "Contiguity" 
})
```
Contiguity supports 33 languages for OTPs, including `English (en)`, `Afrikaans (af)`, `Arabic (ar)`, `Catalan (ca)`, `Chinese / Mandarin (zh)`, `Cantonese (zh-hk)`, `Croatian (hr)`, `Czech (cs)`, `Danish (da)`, `Dutch (nl)`, `Finnish (fi)`, `French (fr)`, `German (de)`, `Greek (el)`, `Hebrew (he)`, `Hindi (hi)`, `Hungarian (hu)`, `Indonesian (id)`, `Italian (it)`, `Japanese (ja)`, `Korean (ko)`, `Malay (ms)`, `Norwegian (nb)`, `Polish (pl)`, `Portuguese - Brazil (pt-br)`, `Portuguese (pt)`, `Romanian (ro)`, `Russian (ru)`, `Spanish (es)`, `Swedish (sv)`, `Tagalog (tl)`, `Thai (th)`, `Turkish (tr)`, and `Vietnamese (vi)`

_The `name` parameter is optional, it customizes the message to say "Your \[name] code is ..."_

To verify an OTP a user has inputted, simply call `client.otp.verify()`:

```python
verify = client.otp.verify({
    'otp_id': otp_id # you received this when you called client.otp.send(),
    'otp': input # the 6 digits your user inputted.
})
```
It will return a boolean (true/false). The OTP expires 15 minutes after sending it.

Want to resend an OTP? Use `client.otp.resend()`:
```py
resend = client.otp.resend({
    'otp_id': otp_id # you received this when you called client.otp.send(),
})
```
OTP expiry does not renew.

## Verify formatting
Contiguity provides two functions that verify phone number and email formatting, which are:

```py
client.verify.number("number")
```
and
```py
client.verify.email("example@example.com")
```
They return a boolean (true/false)

**Note**: _This occurs locally, and is not part of Contiguity's online verification service._

## Email analytics
If you sent an HTML email, and chose Contiguity to track it, you can fetch an email's status (delivered/read) using:

```py
client.email_analytics.retrieve("email_id")
```

## Quota
If you'd like to retrieve your quota, whether you're on our free tier or Unlimited, you can fetch it using:

```py
client.quota.retrieve()
```

You'll receive an object similar to the `crumbs` the API provides on completion of every request.

## Roadmap 🚦
- Contiguity Identity will be supported
- Adding support for calls
- Adding support for webhooks
- Adding support for online templates
- and way more.

### See complete examples in [examples/](https://github.com/use-contiguity/python/tree/main/examples)