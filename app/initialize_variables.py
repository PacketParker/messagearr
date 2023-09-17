import os
import yaml
import requests

supported_sms_services = ['telnyx']


radarr_host = os.environ['RADARR_HOST']
radarr_api_key = os.environ['RADARR_API_KEY']
try:
    home_domain = os.environ['HOME_DOMAIN']
except:
    home_domain = None
api_number = os.environ['API_NUMBER']
val_nums = os.environ['VALID_SENDERS']
root_folder_path = os.environ['ROOT_FOLDER_PATH']
sms_service = os.environ['SMS_SERVICE']
if sms_service not in supported_sms_services:
    print(f'{sms_service} is not a supported SMS service. Please choose from the supported list: {supported_sms_services}')
    exit()
sms_api_key = os.environ['SMS_API_KEY']

headers = {
    'Content-Type': 'application/json',
    'X-Api-Key': radarr_api_key
}

numbers_responses = {
    '1': 1, 'one': 1, '1.': 1,
    '2': 2, 'two': 2, '2.': 2,
    '3': 3, 'three': 3, '3.': 3
}

# Open the quality_profile_id.yaml file and see if the quality_profile_id is set
try:
    with open('/data/quality_profile_id.yaml', 'r') as f:
        file = yaml.load(f, Loader=yaml.FullLoader)
        try:
            quality_profile_id = int(file['quality_profile_id'])
        except:
            print('quality_profile_id is not set or is invalid. Please edit the quality_profile_id.yaml file and add the quality_profile_id from one of the integer values listed within the file')
            exit()
except FileNotFoundError:
    # Create the quality_profile_id.yaml file
    with open('/data/quality_profile_id.yaml', 'w') as f:
        quality_profile_id = None

if not quality_profile_id:
    print('No quality_profile_id found. Please edit the quality_profile_id.yaml file and add the quality_profile_id from one of the integer values listed within the file')
    data = requests.get(f'{radarr_host}/api/v3/qualityprofile', headers=headers).json()
    # Open quality_profile_id.yaml and write each profile as a comment to the file
    with open('/data/quality_profile_id.yaml', 'w') as f:
        f.write('# Quality Profile ID\'s\n')
        for entry in data:
            f.write(f'# {entry["id"]} - {entry["name"]}\n')

        f.write("quality_profile_id: ")
    exit()