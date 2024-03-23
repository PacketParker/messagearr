supported_sms_services = ['telnyx', 'twilio']

numbers_responses = {
    '1': 1, 'one': 1, '1.': 1,
    '2': 2, 'two': 2, '2.': 2,
    '3': 3, 'three': 3, '3.': 3
}

def init():
    global sms_service
    sms_service = ''
    global telnyx_api_key
    telnyx_api_key = ''
    global twilio_account_sid
    twilio_account_sid = ''
    global twilio_auth_token
    twilio_auth_token = ''
    global api_number
    api_number = ''
    global valid_senders
    valid_senders = []
    global radarr_host_url
    radarr_host_url = ''
    global headers
    headers = ''
    global root_folder_path
    root_folder_path = ''
    global quality_profile_id
    quality_profile_id = ''
    global authorization_header_tokens
    authorization_header_tokens= ''
    global notifs_recievers
    notifs_recievers = []
    global enable_jellyfin_temp_accounts
    enable_jellyfin_temp_accounts = ''
    global jellyfin_url
    jellyfin_url = ''
    global jellyfin_headers
    jellyfin_headers = ''
    global home_domain
    home_domain = ''
    global db_path
    db_path = ''

    global temp_movie_ids
    temp_movie_ids = {}
    """
    {
        'from_number': {
            'ids': ['tmdb_id_one', 'tmdb_id_two', 'tmdb_id_three'],
            'time': 'time of request'
        }
    }
    """
    global temp_new_account_requests
    temp_new_account_requests = {}
    """
    {
        'from_number': 'time'
    }
    """