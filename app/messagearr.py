import flask
import datetime

from create_message import create_message
from commands.request import request
from commands.status import status
from commands.number_response_request import number_response_request
from commands.movie_show_response_newaccount import movie_show_response_newaccount
import initialize_variables

app = flask.Flask(__name__)


"""
POST request route to accept incoming notifications from UptimeKuma
regarding the status of certain services. Messages are sent to the
'notif_receivers' list whenever a service goes down or comes back up.
"""
@app.route('/kuma', methods=['POST'])
def kuma():
    # Make sure the request is coming from UptimeKuma (Configured to use this authorization token)
    if flask.request.headers.get('Authorization') == initialize_variables.authorization_header_tokens:
        data = flask.request.get_json()

        if data['heartbeat']['status'] == 0:
            message = f"❌ {data['monitor']['name']} is down!"

        elif data['heartbeat']['status'] == 1:
            message = f"✅ {data['monitor']['name']} is up!"

        for number in initialize_variables.notifs_recievers:
            create_message(number, message)

        return 'OK'
    # If the request does not contain the correct authorization token, return 401
    else:
        return 'Unauthorized', 401


"""
POST request route to accept incoming message from the SMS API,
then process the incoming message in order to see if it is a valid command
and then run the command if it is valid.
"""
@app.route('/incoming', methods=['POST'])
def incoming():
    # Get the data and define the from_number (number that sent the message)
    if initialize_variables.sms_service == 'telnyx':
        from_number = flask.request.get_json()['data']['payload']['from']['phone_number']
        message = str(flask.request.get_json()['data']['payload']['text'])

    if initialize_variables.sms_service == 'twilio':
        from_number = flask.request.form['From']
        message = str(flask.request.form['Body'])

    # Make sure the number is a valid_sender, this stops random people from
    # adding movies to the library
    if from_number not in initialize_variables.valid_senders:
        return 'OK'

    if message.startswith('/request'):
        request(from_number, message)
        return 'OK'

    # If a user responded with a number, they are responding to
    # the 'request' command prompt
    elif message.strip() in initialize_variables.numbers_responses.keys():
        number_response_request(from_number, message)
        return 'OK'

    elif message.startswith('/status'):
        status(from_number)
        return 'OK'

    elif message.startswith('/newaccount'):
        if initialize_variables.enable_jellyfin_temp_accounts.lower() == 'true':
            # If number is already in the temp dict, delete it so that they can redo the request
            if from_number in initialize_variables.temp_new_account_requests.keys():
                del initialize_variables.temp_new_account_requests[from_number]

            create_message(from_number, "Will you be watching a TV show or a movie?\n\nRespond with 'show' for TV show, 'movie' for movies")
            initialize_variables.temp_new_account_requests[from_number] = datetime.datetime.now()
        return 'OK'

    # User must be responding to above prompt
    elif message.strip().lower() in ['show', 'movie']:
        if initialize_variables.enable_jellyfin_temp_accounts.lower() == 'true':
            movie_show_response_newaccount(from_number, message)
        return 'OK'

    # No valid commands were found, so just return
    else:
        return 'OK'


# Handle 405 errors - when a user attempts a GET request on a POST only route
@app.errorhandler(405)
def method_not_allowed(e):
    if initialize_variables.home_domain != 'None':
        return flask.redirect(initialize_variables.home_domain)
    return 'Method Not Allowed'

@app.errorhandler(404)
def page_not_found(e):
    if initialize_variables.home_domain != 'None':
        return flask.redirect(initialize_variables.home_domain)
    return 'Page Not Found'