import telnyx
from twilio.rest import Client

import initialize_variables

def create_message(number, message):
    if initialize_variables.sms_service == 'telnyx':
        telnyx.api_key = initialize_variables.telnyx_api_key
        telnyx.Message.create(
            from_=initialize_variables.api_number,
            to=number,
            text=message
        )

    if initialize_variables.sms_service == 'twilio':
        client = Client(initialize_variables.twilio_account_sid, initialize_variables.twilio_auth_token)
        client.messages.create(
            body=message,
            from_=initialize_variables.api_number,
            to=number
        )
