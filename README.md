# Messagearr
### Add movies to your Radarr library and check their download status through text messages

### 1. Docker Compose
```
version: '3.3'
services:
    messagearr:
        ports:
            - '4545:4545'
        environment:
            - TZ=America/Chicago # OPTIONAL: Default is UTC
            - RADARR_HOST_URL=http://127.0.0.1:7878 # Change to your radarr host
            - RADARR_API_KEY=apikeyhere # Found by navigating to Settings > General
            - SMS_SERVICE=servicename # Currently only supporting Telnyx
        volumes:
            - /local/file/path:/data
        image: packetparker/messagearr:latest
```
### 2. Run the Container
#### Run the container in non-daemon mode, you will get an error stating that there are variables that need to be set within the `config.yaml` file, this file is in the internal path of `/data/config.yaml`. Go into that file and being setting the variables that appear for you within that file. Note that every single entry must have a value, the only optional value is `home_domain` but requires `null` at the very least (this is also the default).

### 3. What Does Every Value in config.yaml Mean?
- #### `quality_profile_id` There is a commented list of profiles that exist within your Radarr server. The list contains the profile id followed by the profile name. This value should be the single integer id of the quality profile that you would like movies to be added under.

- #### `home_domain` Defaults to null meaning 404/405 errors will just return the error to the browser. Replace this will a full URL if you would like those errors to be redirected to your website (e.g. https://pkrm.dev)

- #### `api_number` The number given to you by your SMS service, in international format, and in ' ' (e.g. '+18005282589')

- #### `valid_senders` Comma-space separated list of numbers that are allowed to send commands, this stops random numbers from being allowed to add movies to Radarr. This also must be in international format (e.g. +18005269856, +18005247852, +18002365874). If you have only 1 sender here, that must be put within ' '.

- #### `root_folder_path` The folder path defined in your Radarr server. Find this value by logging into your Radarr server and navigate to Settings > Media Management, at the bottom of this page will be your root folder path (copy the full path!)

- #### The last values will vary dependant on your SMS service, but they are just the authentication values for your service.

### 4. Setup your Domain
#### It is recommended but not technically required to have a domain in order for this to work. This container runs a flask image in order to accept POST requests and must be open to the internet so that incoming messages can be accepted. The process for this is different for every reverse proxy and I recommend that you refer to your proxies documentation for help. Once you have correctly proxied the domain you can test it by navigating to the domain, you should recieve a 404 error or be redirect to `home_domain` if the value has been set.

#### If you do not have a domain you can use a DDNS service or you can open port 4545 (or whatever exposed port you used) on your router.

### 5. Add the Domain
#### Once you have configured your domain or router go to your sms services console and buy a number for SMS messaging. Once you buy the number you need to configure how it handles incoming messages, there you should be able to have the service send a POST request to a webhook for incoming message. You should overwrite or set this value to `http(s)://yourdomain.com/incoming` or `http://yourip:port/incoming`

### 6. Further Help
#### Please open an issue if you need help with any part of setting this up (I know the docs/instructions aren't great). You can also email me at [contact@pkrm.dev](mailto:contact@pkrm.dev)


#### Happy coding!