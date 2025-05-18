from twilio.rest import Client
from stock_secrets import *

def send_SMS_message(message: str, to: str):
    client = Client(twilio_account_ssid, twilio_auth_token)

    message = client.messages.create(
        body=message,
        from_=twilio_from_phone_number,
        to=to
    )