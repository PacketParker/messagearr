import os
import yaml
import requests

supported_sms_services = ['telnyx']

sms_service = str(os.environ['SMS_SERVICE']).lower()
radarr_host_url = str(os.environ['RADARR_HOST_URL'])
radarr_api_key = str(os.environ['RADARR_API_KEY'])

headers = {
    'Content-Type': 'application/json',
    'X-Api-Key': radarr_api_key
}

# Open the config.yaml file and see if the config is set
try:
    with open('/data/config.yaml', 'r') as f:
        file = yaml.load(f, Loader=yaml.FullLoader)
        try:
            quality_profile_id = int(file['quality_profile_id'])

            if str(file['home_domain']) != 'null':
                home_domain = str(file['home_domain'])

            api_number = str(file['api_number'])
            val_nums = str(file['valid_senders'])
            root_folder_path = str(file['root_folder_path'])
            if sms_service not in supported_sms_services:
                print(f'{sms_service} is not a supported SMS service. Please choose from the supported list: {supported_sms_services}')
                exit()

            if sms_service == 'telnyx':
                telnyx_api_key = str(file['telnyx_api_key'])

            value_not_set = False
        except:
            print('One or more values are not set or not set correctly within the config.yaml file. Please edit the file or refer to the docs for more information.')
            exit()

except FileNotFoundError:
    # Create the config.yaml file
    with open('/data/config.yaml', 'w') as f:
        value_not_set = True

if value_not_set:
    print('One or more values are not set or not set correctly within the config.yaml file. Please edit the file or refer to the docs for more information.')
    data = requests.get(f'{radarr_host_url}/api/v3/qualityprofile', headers=headers).json()
    # Open config.yaml and write each profile as a comment to the file
    with open('/data/config.yaml', 'w') as f:
        f.write('# Quality Profile ID\'s\n')
        for entry in data:
            f.write(f'# {entry["id"]} - {entry["name"]}\n')

        f.write("quality_profile_id:\n")
        f.write("home_domain: null\n")
        f.write("api_number:\n")
        f.write("valid_senders:\n")
        f.write("root_folder_path:\n")
        if sms_service not in supported_sms_services:
            print(f'{sms_service} is not a supported SMS service. Please choose from the supported list: {supported_sms_services}')
            exit()

        if sms_service == 'telnyx':
            f.write("telnyx_api_key:\n")

        f.write("\n\n# INFORMATION: There should be NO trailing spaced after you enter a value,\n# this will cause errors.\n# There should be one space after the colon though (e.g. quality_profile_id: 1)\n# Check docs for information on each value.")
    exit()

numbers_responses = {
    '1': 1, 'one': 1, '1.': 1,
    '2': 2, 'two': 2, '2.': 2,
    '3': 3, 'three': 3, '3.': 3
}