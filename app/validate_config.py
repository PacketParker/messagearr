import configparser
import os
from simple_chalk import chalk
import validators
import requests
import initialize_variables

def write_to_config(config):
    IN_DOCKER = os.environ.get('IN_DOCKER', False)
    if IN_DOCKER:
        with open('/data/config.ini', 'w') as configfile:
            config.write(configfile)
    else:
        with open('config.ini', 'w') as configfile:
            config.write(configfile)


def validate_config(file_contents):
    config = configparser.ConfigParser()
    config.read_string(file_contents)

    # Check SMS service
    if config['REQUIRED']['SMS_SERVICE'].lower() not in initialize_variables.supported_sms_services:
        print(chalk.red(f'Invalid or empty SMS_SERVICE option passed. Please choose from the supported list: {initialize_variables.supported_sms_services}'))
        exit()
    initialize_variables.sms_service = config['REQUIRED']['SMS_SERVICE'].lower()

    # Check API key is Telnyx is selected
    if config['REQUIRED']['SMS_SERVICE'].lower() == 'telnyx':
        try:
            if not config['REQUIRED']['TELNYX_API_KEY']:
                print(chalk.red('Empty TELNYX_API_KEY option passed. Please enter the API key for your Telnyx account.'))
                exit()
        except KeyError:
            config['REQUIRED']['TELNYX_API_KEY'] = ''
            write_to_config(config)
            print(chalk.red('Empty TELNYX_API_KEY option passed. Please enter the API key for your Telnyx account.'))
        initialize_variables.telnyx_api_key = config['REQUIRED']['TELNYX_API_KEY']

    # Check account SID and auth token is Twilio is selected
    if config['REQUIRED']['SMS_SERVICE'].lower() == 'twilio':
        try:
            if not config['REQUIRED']['TWILIO_ACCOUNT_SID'] or not config['REQUIRED']['TWILIO_AUTH_TOKEN']:
                print(chalk.red('Empty TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN option passed. Please enter the account SID and auth token for your Twilio account.'))
                exit()
        except KeyError:
            config['REQUIRED']['TWILIO_ACCOUNT_SID'] = ''
            config['REQUIRED']['TWILIO_AUTH_TOKEN'] = ''
            write_to_config(config)
            print(chalk.red('Empty TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN option passed. Please enter the account SID and auth token for your Twilio account.'))
        initialize_variables.twilio_account_sid = config['REQUIRED']['TWILIO_ACCOUNT_SID']
        initialize_variables.twilio_auth_token = config['REQUIRED']['TWILIO_AUTH_TOKEN']

    # Check API_NUMBER
    if not config['REQUIRED']['API_NUMBER']:
        print(chalk.red('Empty API_NUMBER option passed. Please enter an internationally formatted phone number with no spaces.'))
        exit()
    if len(config['REQUIRED']['API_NUMBER']) < 12 or len(config['REQUIRED']['API_NUMBER']) > 13 or not config['REQUIRED']['API_NUMBER'].startswith('+'):
        print(chalk.red('API_NUMBER must be a valid international phone number with no spaces (e.g. +15459087689)'))
        exit()
    initialize_variables.api_number = config['REQUIRED']['API_NUMBER']

    # Check VALID_SENDERS
    if not config['REQUIRED']['VALID_SENDERS']:
        print(chalk.red('Empty VALID_SENDERS option passed. Please enter a command separated list of internationally formatted phone numbers (e.g. +15359087689, +15256573847)'))
        exit()

    for sender in config['REQUIRED']['VALID_SENDERS'].split(', '):
        if len(sender) < 12 or len(sender) > 13 or not sender.startswith('+'):
            print(chalk.red('At least one number within VALID_SENDER is malformed. Please enter a command separated list of internationally formatted phone numbers (e.g. +15359087689, +15256573847)'))
            exit()
        else:
            initialize_variables.valid_senders.append(sender)

    # Check RADARR_HOST_URL
    if not validators.url(config['REQUIRED']['RADARR_HOST_URL']):
        print(chalk.red('Invalid or empty URL passed to RADARR_HOST_URL. Pass a valid URL (e.g. http://localhost:7878)'))
        exit()
    initialize_variables.radarr_host_url = config['REQUIRED']['RADARR_HOST_URL']

    # Check RADARR_API_KEY
    if not config['REQUIRED']['RADARR_API_KEY']:
        print(chalk.red('Empty RADARR_API_KEY passed. Obtain an API key from your Radarr instance and paste it in this option.'))
        exit()

    initialize_variables.headers = {
        'Content-Type': 'application/json',
        'X-Api-Key': config['REQUIRED']['RADARR_API_KEY']
    }

    # Make sure connection to Radarr API can be established
    try:
        requests.get(config['REQUIRED']['RADARR_HOST_URL'], headers=initialize_variables.headers)
    except requests.exceptions.ConnectionError:
        print(chalk.red('Could not connect to Radarr API. Please check your RADARR_HOST_URL and RADARR_API_KEY'))
        exit()

    # Check ROOT_FOLDER_PATH
    if not config['REQUIRED']['ROOT_FOLDER_PATH']:
        print(chalk.red('Empty ROOT_FOLDER_PATH option passed. Please enter a path to a folder within your Radarr instance.'))
        exit()
    initialize_variables.root_folder_path = config['REQUIRED']['ROOT_FOLDER_PATH']

    # Check QUALITY_PROFILE_ID
    data = requests.get(f'{config["REQUIRED"]["RADARR_HOST_URL"]}/api/v3/qualityprofile', headers=initialize_variables.headers).json()
    all_ids = []
    for entry in data:
        all_ids.append(str(entry['id']))

    if not config['REQUIRED']['QUALITY_PROFILE_ID'] or config['REQUIRED']['QUALITY_PROFILE_ID'] not in all_ids:
        config['AVAILABLE_QUALITY_IDS'] = {}
        for entry in data:
            config['AVAILABLE_QUALITY_IDS'][str(entry['id'])] = entry['name']

        print(chalk.red('Empty or invalid QUALITY_PROFILE_ID passed. Pass one of the valid IDs which are now listed within the config.ini file.'))
        write_to_config(config)
        exit()
    initialize_variables.quality_profile_id = config['REQUIRED']['QUALITY_PROFILE_ID']

    # Check ENABLE_KUMA_NOTIFICATIONS
    if not config['REQUIRED']['ENABLE_KUMA_NOTIFICATIONS'] or config['REQUIRED']['ENABLE_KUMA_NOTIFICATIONS'].lower() not in ['true', 'false']:
        print(chalk.red('ENABLE_KUMA_NOTIFICATIONS must be a boolean value (true/false)'))
        exit()

    if config['REQUIRED']['ENABLE_KUMA_NOTIFICATIONS'].lower() == 'true':
        # Check existence
        try:
            if not config['KUMA_NOTIFICATIONS']['AUTHORIZATION_HEADER_TOKEN']:
                print(chalk.red('Empty AUTHORIZATION_HEADER_TOKEN passed. Make sure to set your authorization header in Uptime Kuma and copy the key here.'))
                exit()
        except KeyError:
            config['KUMA_NOTIFICATIONS']['AUTHORIZATION_HEADER_TOKEN'] = ''
            write_to_config(config)
            print(chalk.red('Empty AUTHORIZATION_HEADER_TOKEN passed. Make sure to set your authorization header in Uptime Kuma and copy the key here.'))
            exit()
        initialize_variables.authorization_header_tokens = config['KUMA_NOTIFICATIONS']['AUTHORIZATION_HEADER_TOKEN']
        # Check existence
        try:
            if not config['KUMA_NOTIFICATIONS']['NOTIF_RECIEVERS']:
                print(chalk.red('Empty NOTIF_RECIEVERS passed. This should be a comma separated list of the numbers of people who should recieve uptime notifications - formatted the same way as VALID_SENDERS.'))
                exit()
        except KeyError:
            config['KUMA_NOTIFICATIONS']['NOTIF_RECIEVERS'] = ''
            write_to_config(config)
            print(chalk.red('Empty NOTIF_RECIEVERS passed. This should be a comma separated list of the numbers of people who should recieve uptime notifications - formatted the same way as VALID_SENDERS.'))
            exit()

        # Check validity of NOTIF_RECIEVERS
        for sender in config['KUMA_NOTIFICATIONS']['NOTIF_RECIEVERS'].split(', '):
            if len(sender) < 12 or len(sender) > 13 or not sender.startswith('+'):
                print(chalk.red('At least one number within NOTIF_RECIEVERS is malformed. Please enter a command separated list of internationally formatted phone numbers (e.g. +15359087689, +15256573847)'))
                exit()
            else:
                initialize_variables.notifs_recievers.append(sender)

    # Check ENABLE_JELLYFIN_TEMP_ACCOUNTS
    if not config['REQUIRED']['ENABLE_JELLYFIN_TEMP_ACCOUNTS'] or config['REQUIRED']['ENABLE_JELLYFIN_TEMP_ACCOUNTS'].lower() not in ['true', 'false']:
        print(chalk.red('ENABLE_JELLYFIN_TEMP_ACCOUNTS must be a boolean value (true/false)'))
        exit()
    initialize_variables.enable_jellyfin_temp_accounts = config['REQUIRED']['ENABLE_JELLYFIN_TEMP_ACCOUNTS'].lower()

    if config['REQUIRED']['ENABLE_JELLYFIN_TEMP_ACCOUNTS'].lower() == 'true':
        # Check existence
        try:
            if not config['JELLYFIN_ACCOUNTS']['JELLYFIN_URL']:
                print(chalk.red('Empty URL passed to JELLYFIN_URL. Pass a valid URL (e.g. http://localhost:8096)'))
                exit()
        except KeyError:
            config['JELLYFIN_ACCOUNTS']['JELLYFIN_URL'] = ''
            write_to_config(config)
            print(chalk.red('Empty URL passed to JELLYFIN_URL. Pass a valid URL (e.g. http://localhost:8096)'))
            exit()
        # Check URL validity
        if not validators.url(config['JELLYFIN_ACCOUNTS']['JELLYFIN_URL']):
            print(chalk.red('Invalid URL passed to JELLYFIN_URL. Pass a valid URL (e.g. http://localhost:8096)'))
            exit()
        initialize_variables.jellyfin_url = config['JELLYFIN_ACCOUNTS']['JELLYFIN_URL']

        # Check existence
        try:
            if not config['JELLYFIN_ACCOUNTS']['JELLYFIN_API_KEY']:
                print(chalk.red('Empty JELLYFIN_API_KEY passed. Create a Jellyfin API key in your Jellyfin dashboard and pass it here.'))
                exit()
        except KeyError:
            config['JELLYFIN_ACCOUNTS']['JELLYFIN_API_KEY'] = ''
            write_to_config(config)
            print(chalk.red('Empty JELLYFIN_API_KEY passed. Create a Jellyfin API key in your Jellyfin dashboard and pass it here.'))
            exit()

        # Make sure connection to Jellyfin API can be established
        initialize_variables.jellyfin_headers = {
            'Content-Type': 'application/json',
            'Authorization': f"MediaBrowser Client=\"other\", device=\"Messagearr\", DeviceId=\"totally-unique-device-id\", Version=\"0.0.0\", Token=\"{config['JELLYFIN_ACCOUNTS']['JELLYFIN_API_KEY']}\""
        }

        response = requests.get(f"{config['JELLYFIN_ACCOUNTS']['JELLYFIN_URL']}/Users", headers=initialize_variables.jellyfin_headers)
        if response.status_code != 200:
            print(chalk.red('Could not connect to Jellyfin API. Please check your JELLYFIN_URL and JELLYFIN_API_KEY'))
            exit()

    # Validate home domain if it is set
    if config['OPTIONAL']['HOME_DOMAIN']:
        if not validators.url(config['OPTIONAL']['HOME_DOMAIN']):
            print(chalk.red('Invalid HOME_DOMAIN passed. Please enter a valid url (e.g. https://example.com)'))
            exit()
        else:
            initialize_variables.home_domain = config['OPTIONAL']['HOME_DOMAIN']

"""
This method is called before starting the application - to make and validate the configuration
"""
def make_config():
    # Attempt to open and validate the configuration file
    try:
        with open('config.ini', 'r') as config:
            file_contents = config.read()
            validate_config(file_contents)

    except FileNotFoundError:
        try:
            with open('/data/config.ini', 'r') as config:
                file_contents = config.read()
                validate_config(file_contents)

        except FileNotFoundError:
            # Create the config.ini file
            config = configparser.ConfigParser()
            config['REQUIRED'] = {
                'SMS_SERVICE': '',
                'API_NUMBER': '',
                'VALID_SENDERS': '',
                'RADARR_HOST_URL': 'http://',
                'RADARR_API_KEY': '',
                'ROOT_FOLDER_PATH': '',
                'QUALITY_PROFILE_ID': '',
                'ENABLE_KUMA_NOTIFICATIONS': '',
                'ENABLE_JELLYFIN_TEMP_ACCOUNTS': ''
            }

            config['OPTIONAL'] = {
                'HOME_DOMAIN': ''
            }

            config['KUMA_NOTIFICATIONS'] = {
                'AUTHORIZATION_HEADER_TOKEN': '',
                'NOTIF_RECIEVERS': ''
            }

            config['JELLYFIN_ACCOUNTS'] = {
                'JELLYFIN_URL': '',
                'JELLYFIN_API_KEY': ''
            }

            IN_DOCKER = os.environ.get('IN_DOCKER', False)
            if IN_DOCKER:
                with open('/data/config.ini', 'w') as configfile:
                    config.write(configfile)

            else:
                with open('config.ini', 'w') as configfile:
                    config.write(configfile)