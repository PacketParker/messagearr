import telnyx

from initialize_variables import *

def create_message(number, message):
    if sms_service == 'telnyx':
        telnyx.api_key = telnyx_api_key
        telnyx.Message.create(
            from_=api_number,
            to=number,
            text=message
        )
