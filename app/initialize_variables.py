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

        f.write("quality_profile_id: ")
        f.write("\n")
        f.write("home_domain: null # Optional: 404/405 errors redirect to this domain, leaving as\n# null means the webserver will just return the error to the browser\n")
        f.write("api_number:  # International format\n")
        f.write("valid_senders:  # International format, comma-space separated (eg. +18005263256, +18005428741\n")
        f.write("root_folder_path:  # Path to the root folder where movies are downloaded to\n")
        if sms_service not in supported_sms_services:
            print(f'{sms_service} is not a supported SMS service. Please choose from the supported list: {supported_sms_services}')
            exit()

        if sms_service == 'telnyx':
            f.write("telnyx_api_key: \n")
    exit()

numbers_responses = {
    '1': 1, 'one': 1, '1.': 1,
    '2': 2, 'two': 2, '2.': 2,
    '3': 3, 'three': 3, '3.': 3
}