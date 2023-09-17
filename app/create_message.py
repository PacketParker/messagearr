import telnyx
from initialize_variables import sms_service, sms_api_key, api_number

def create_message(number, message):
    if sms_service == 'telnyx':
        telnyx.api_key = sms_api_key
        telnyx.Message.create(
            from_=api_number,
            to=number,
            text=message
        )