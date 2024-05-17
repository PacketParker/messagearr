# Messagearr

IMPORTANT: No longer under development. Focus has transfered to the easier to use Discord alternative called <a href="https://github.com/packetparker/cordarr">CordArr</a>
<br>
<br>
Add new movies to your Radarr library through text messages, check on their download status, recieve text notifications for uptime kuma monitors, and allow people to create temporary Jellyfin accounts that automatically delete themselves.

This is a project that was developed exactly for my use case and then open-sourced. So... it might not be exactly what you are looking for, if thats the case, feel free to open an issue on this repo explaining something you would want to see added.

## Hosting Instructions

#### *Note: No matter if you choose Docker or bare metal to run Messagearr, you will need to follow the same "Configuration" instructions.*

#### **Docker**
Use the following docker-compose.yaml file to run the container
```yaml
version: '3.3'
services:
    messagearr:
        ports:
            - '4545:4545'
        volumes:
            - '/loca/file/path:/data'
        image: packetparker/messagearr:latest
```

#### **Bare metal**
Download the latest version of Messagearr, install the requirements from the `requirements.txt` file and run the `wsgi.py` file.

### Configuration

On the first run, Messagearr will exit and print out and error statement, it will also automatically create a `config.ini` file for you, with the necessary fields.

#### *Note: Some fields may not be created on the first run. For example, if you choose to enable the Uptime Kuma notifications, the configuration fields for that feature will only be added after you set the field to true and then re-run Messagearr*

An explanation of the each configuration field can be found below

Field | Description | Requirement
--- | --- | ---
SMS_SERVICE | The service for your messaging API (only twilio/telnyx currently supported) | REQUIRED
RADARR_HOST_URL | URL for your Radarr instance | REQUIRED
RADARR_API_KEY | API key from Radarr (can be created in Settings > General) | REQUIRED
API_NUMBER | Phone number from your messaging service that will be sending/recieving messages | REQUIRED
VALID_SENDERS | Comma separated list of phone numbers (international format) that are authorized to use your Messagearr instance | REQUIRED
ROOT_FOLDER_PATH | Path for the root folder of Radarr (found in Settings > Media Management) | REQUIRED
QUALITY_PROFILE_ID | ID for the quality profile on Radarr (in order to get a list of your quality profiles and their IDs, set the other fields first, then re-run Messagearr, the config.ini file will update with this information) | REQUIRED
ENABLE_KUMA_NOTIFICATIONS | True/False : Whether or not to send Uptime Kuma notifications | REQUIRED
ENABLE_JELLYFIN_TEMP_ACCOUNTS | True/False : Whether or not to enable the Jellyfin temp accounts feature | REQUIRED
HOME_DOMAIN | Home domain to redirect to if a user sends a GET request to a POST only route | OPTIONAL

<br>

If you use Twilio for your messaging service, these fields will also be required
Field | Description | Requirement
--- | --- | ---
TWILIO_ACCOUNT_SID | The account SID for your Twilio account | REQUIRED
TWILIO_AUTH_TOKEN | The auth token for your Twilio account | REQUIRED

<br>

If you use Telnyx for your messaging service, this field will also be required
Field | Description | Requirement
--- | --- | ---
TELNYX_API_KEY | The API key for your Telnyx account | REQUIRED

<br>

If you choose to enable Uptime Kuma notifications, these fields will also be required
Field | Description | Requirement
--- | --- | ---
AUTHORIZATION_HEADER_TOKEN | Token used to authorize requests from Uptime Kuma - follow the "Uptume Kuma Setup" instructions further down this page | REQUIRED
NOTIF_RECIEVERS | Comma separated list of phone numbers (international format) that will recieve text messages from Uptime Kuma | REQUIRED

<br>

If you choose to enable the Jellyfin temp accounts features, these fields will also be required
Field | Description | Requirement
--- | --- | ---
JELLYFIN_URL | The URL of your Jellyfin instance | REQUIRED
JELLYFIN_API_KEY | The API from Jellyfin (can be created in Dashboard > API Keys) | REQUIRED

### Uptime Kuma Setup
If you choose to enable the Uptime Kuma notifications, you will need to configure your Uptime Kuma instance to send webhooks to your Messagearr instance.

1. Navigate to Settings > Notifications and click "Setup Notification"

2. Choose "Webhook" as the Notification Type

3. Friendly Name can be whatever you want

4. Post URL should be the URL that your Messagearr instance will be on with /kuma at the end (e.g. https://messagearr.example.com/kuma)

5. Request Body must be set to "Preset - application/json"

6. Enable the "Addition Headers" toggle, and enter the following in the text box
```json
{
    "Authorization": "uptimekumaauthtoken"
}
```
#### *Note: The 'Authorization' value can be whatever you want, but it MUST be the same as the AUTHORIZATION_HEADER_TOKEN that is set in the `config.ini` file.*
