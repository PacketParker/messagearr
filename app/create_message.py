import telnyx
from twilio.rest import Client

from initialize_variables import *

def create_message(number, message):
    if sms_service == 'telnyx':
        telnyx.api_key = telnyx_api_key
        telnyx.Message.create(
            from_=api_number,
            to=number,
            text=message
        )

    if sms_service == 'twilio':
        client = Client(twilio_account_sid, twilio_auth_token)
        client.messages.create(
            body=message,
            from_=api_number,
            to=number
        )
