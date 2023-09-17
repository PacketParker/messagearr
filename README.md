# Messagearr
## Add movies to your Radarr library and check their download status through text messages

## Installation

### 1. Docker Compose
```
version: '3.3'
services:
    messagearr:
        ports:
            - '4545:4545'
        environment:
            - TZ=America/Chicago # OPTIONAL: Default is UTC
            - RADARR_HOST=http://127.0.0.1:7878 # Change to your radarr host
            - RADARR_API_KEY=apikeyhere
            - HOME_DOMAIN=https://pkrm.dev # OPTIONAL: Redirects 405 and 404 errors, defaults to return status code
            - API_NUMBER=+18005632548 # International format
            - VALID_SENDERS=+18005242256, +18002153256 # International format, comma-space separated
            - QUALITY_PROFILE_ID=7
            - ROOT_FOLDER_PATH=/data/media/movies
            - SMS_SERVICE=telnyx
            - SMS_API_KEY=apikeyhere
        volumes:
            - /local/file/path:/data
        image: messagearr
```
### 2. Before Running Compose
#### Before the container will start and work properly a `quality_profile_id` will need to be defined (not in the compose file). First run the container, not in daemon mode, and it will quit with an error stating that the value has not been set. This will create a file in `/data/quality_profile_id.yaml` - within this file there will be comments that list all of the quality profiles defined on your radarr server. Under the `quality_profile_id` value enter one of the integers that corresponds to the quality profile that you want movies to be added under.

### 3. Important Notes

- #### `RADARR_HOST` needs to be entered as a full URL, a host:port configuration will result the container not working.

- #### All phone numbers must be entered in their international format (e.g. +18005263258)

- #### Currently only Telnyx is supported as an SMS client, however, I wanting to support a much larger amount of services. Please submit a pull request if you already have some code (message creation for different services is under `app/create_message.py`).

- #### The `ROOT_FOLDER_PATH` can be found under the UI of your Radarr serve by navigating to Settings > Media Management then scroll to the very bottom of the file. There you will find a file path, this FULL path should be entered as the environment variable value for `ROOT_FOLDER_PATH`.

- #### The `VALID_SENDERS` environment variable defines the list of numbers that have permission to run commands through SMS. This stops random numbers from adding movies to your library.

- #### You must define a volume so that data is persistent across container reboots.

### Please open an issue if you have any trouble when getting started. Also, pull requests that add additional functionality or more SMS services are welcome!

#### Happy coding!