import flask
import datetime
import requests
import sqlite3
import humanize

from create_message import create_message
from initialize_variables import *


"""
Define variables to be used later on
"""
app = flask.Flask(__name__)

db = sqlite3.connect('/data/movies.db')
cursor = db.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies(
        from_number TEXT,
        movie_id TEXT,
        movie_title TEXT
    )
''')
db.commit()
db.close()

temp_movie_ids = {}
"""
{
    'from_number': {
        'ids': ['tmdb_id_one', 'tmdb_id_two', 'tmdb_id_three'],
        'time': 'time of request'
    }
}
"""
valid_senders = []

for number in val_nums.split(', '):
    valid_senders.append(number)

if notif_receivers_nums:
    notif_receivers = []

    for number in notif_receivers_nums.split(', '):
        notif_receivers.append(number)


"""
POST request route to accept incoming notifications from UptimeKuma
regarding the status of certain services. Messages are sent to the
'notif_receivers' list whenever a service goes down or comes back up.
"""
@app.route('/kuma', methods=['POST'])
def api():
    # Make sure the request is coming from UptimeKuma (Configured to use this authorization token)
    if flask.request.headers.get('Authorization') == authorization_header_token:
        data = flask.request.get_json()

        if data['heartbeat']['status'] == 0:
            message = f"❌ {data['monitor']['name']} is down!"

        elif data['heartbeat']['status'] == 1:
            message = f"✅ {data['monitor']['name']} is up!"

        for number in notif_receivers:
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
    if sms_service == 'telnyx':
        from_number = flask.request.get_json()['data']['payload']['from']['phone_number']
        message = str(flask.request.get_json()['data']['payload']['text'])

    if sms_service == 'twilio':
        from_number = flask.request.form['From']
        message = str(flask.request.form['Body'])

    # Make sure the number is a valid_sender, this stops random people from
    # adding movies to the library
    if from_number not in valid_senders:
        return 'OK'
    # If the message starts with /request, that means the user is trying to add a movie
    if message.startswith('/request'):
        # If the user has already run the /request command, delete the entry
        # from the temp_movie_ids dict so that they can run the command again
        if from_number in temp_movie_ids.keys():
            del temp_movie_ids[from_number]
        # If the user did not include a movie title, alert them to do so
        # Just check to make sure that the length of the message is greater than 9
        if len(message) <= 9:
            create_message(from_number, "Please include the movie title after the /request command.\nEX: /request The Dark Knight")
            return 'OK'

        incoming_message = message.split(' ', 1)[1]
        movie_request = incoming_message.replace(' ', '%20')
        # Send a request to the radarr API to get the movie info
        response = requests.get(f'{radarr_host_url}/api/v3/movie/lookup?term={movie_request}', headers=headers)
        # If there are no results, alert the user
        if len(response.json()) == 0:
            create_message(from_number, "There were no results for that movie. Please make sure you typed the title correctly.")
            return 'OK'
        # If the movie is already added to the library, return a message saying so.
        if response.json()[0]['added'] != '0001-01-01T05:51:00Z':
            create_message(from_number, "This movie is already added to the server.\n\nIf you believe this is an error, please contact Parker.")
            return 'OK'
        # Define an empty message variable, we then loop through the first 3 results from the API
        # If there are less than 3 results, we loop through the amount of results there are
        message = ""
        for i in range(min(3, len(response.json()))):
            message += f"{i+1}. {response.json()[i]['folder']}\n\n"
            if from_number not in temp_movie_ids.keys():
                temp_movie_ids[from_number] = {
                    'ids': [],
                    'time': datetime.datetime.now()
                }
            temp_movie_ids[from_number]['ids'].append(response.json()[i]['tmdbId'])

        message += "Reply with the number associated with the movie you want to download. EX: 1\n\nIf the movie you want is not on the list, make sure you typed the title exactly as it is spelt, or ask Parker to manually add the movie."

        create_message(from_number, message)
        return 'OK'
    # Elif the user responded with a variation of 1, 2, or 3
    # This means they are replying to the previous prompt, so now we need to
    # add their movie choice to radarr for download
    elif message.strip() in numbers_responses.keys():
        # If there is no entry for the user in the temp_movie_ids dict, that means
        # they have not yet run the /request command, so alert them to do so.
        if from_number not in temp_movie_ids.keys():
            create_message(from_number, "There is no current request that you can decide on. It might be that your /request command timed out due since you took too long to response. Please try again. If this issue persists, please contact Parker.")
            return 'OK'
        # If the time is greater than 5 minutes, delete the entry from the dict, and alert
        # the user that their request timed out
        if (datetime.datetime.now() - temp_movie_ids[from_number]['time']).total_seconds() / 60 > 5:
            del temp_movie_ids[from_number]
            create_message(from_number, "You waited too long and therefore your request has timed out.\n\nPlease try again by re-running the /request command. If this issue persists, please contact Parker.")
            return 'OK'

        # Otherwise, all checks have been completed, so alert the user of the
        # start of the process
        create_message(from_number, "Just a moment while I add your movie to the library...")
        movie_number = numbers_responses[message.strip()]
        try:
            tmdb_id = temp_movie_ids[from_number]['ids'][movie_number - 1]
        except IndexError:
            create_message(from_number, "You did not enter a valid number. Please re-send the /request command and try again. If you believe this is an error, please contact Parker.")
            del temp_movie_ids[from_number]
            return 'OK'

        data = requests.get(f'{radarr_host_url}/api/v3/movie/lookup/tmdb?tmdbId={tmdb_id}', headers=headers)

        data = data.json()
        movie_title = data['title']
        # Change the qualityProfileId, monitored, and rootFolderPath values
        data['qualityProfileId'] = quality_profile_id
        data['monitored'] = True
        data['rootFolderPath'] = root_folder_path
        # Pass this data into a pass request to the radarr API, this will add the movie to the library
        response = requests.post(f'{radarr_host_url}/api/v3/movie', headers=headers, json=data)
        data = response.json()
        movie_id = data['id']
        # Send message to user alerting them that the movie was added to the library
        create_message(from_number, f"🎉 {data['title']} has been added to the library!\n\nTo check up on the status of your movie(s) send /status - please wait at least 5 minutes before running this command in order to get an accurate time.")
        # Finally, as to not slow up the sending of the message, send this request
        # Send a POST request to the radarr API to search for the movie in the indexers
        requests.post(f'{radarr_host_url}/api/v3/command', headers=headers, json={'name': 'MoviesSearch', 'movieIds': [int(movie_id)]})

        # Add the movie_id to the database so that users can check up on the status of their movie
        db = sqlite3.connect('/data/movies.db')
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO movies(from_number, movie_id, movie_title)
            VALUES(?, ?, ?)
        ''', (from_number, movie_id, movie_title))
        db.commit()
        db.close()

        # Delete the entry from the temp_movie_ids dict
        del temp_movie_ids[from_number]
        return 'OK'

    elif message.strip() == '/status':
        # This returns a list of ALL movies being downloaded, but not all of them were
        # requested by the user, so we need to filter out the ones that were not requested
        response = requests.get(f'{radarr_host_url}/api/v3/queue/', headers=headers)
        # Get all the movie_ids that were requested by the user
        db = sqlite3.connect('/data/movies.db')
        cursor = db.cursor()
        cursor.execute('''
            SELECT movie_id, movie_title FROM movies WHERE from_number = ?
        ''', (from_number,))
        movie_info = cursor.fetchall()
        db.close()
        # Turn the movie_id, movie_title into key value pairs
        movies = {}
        for movie in movie_info:
            movies[movie[0]] = movie[1]

        # If the user has no movies in the database, alert them to run the /request command
        if len(movies) == 0:
            create_message(from_number, "You have no movies being downloaded at the moment.\n\nIf you previously added a movie, it is likely that it has finished downloading. If you believe this is an error, please contact Parker.")
            return 'OK'

        message = ""
        # Loop through the response from the radarr API and filter out the movies that were not requested by the user
        for movie in response.json()['records']:
            movie_id = str(movie['movieId'])
            if movie_id in movies.keys():
                if movie['status'] == 'downloading':
                    # Humanize the time_left value
                    try:
                        time_left = humanize.precisedelta(datetime.datetime.strptime(movie['timeleft'], '%H:%M:%S') - datetime.datetime.strptime('00:00:00', '%H:%M:%S'), minimum_unit='seconds')
                    except ValueError:
                        # Sometimes movie downloads take a long time and include days in the time_left value
                        # This is formated as 1.00:00:00
                        time_left = humanize.precisedelta(datetime.datetime.strptime(movie['timeleft'], '%d.%H:%M:%S') - datetime.datetime.strptime('00:00:00', '%H:%M:%S'), minimum_unit='seconds')
                    except KeyError:
                        time_left = 'Unknown'

                    message += f"📥 {movies[movie_id]} - {time_left}\n"
                else:
                    message += f"{movies[movie_id]} - {str(movie['status']).upper()}\n"

        # If the message is empty, that means the user has no movies being downloaded
        # Or, no download was found for the movie they requested
        if message == "":
            # For all movie IDs within the database
            for movie_id in movies.keys():
                response = requests.get(f'{radarr_host_url}/api/v3/movie/{movie_id}', headers=headers)
                # This means that there is no current download, and no file has been found
                # MOST likely means a download just wasn't found, so alert the user
                data = response.json()
                if data['hasFile'] == False:
                    message += f"{movies[movie_id]} - NOT FOUND\n\nThis means a download was not found for the movie(s), if this is a brand new movie that is likely the reason. If the movie has already been released on DVD/Blu-Ray, please contact Parker."

            # If the message is still empty, that means the user has no movies being downloaded
            if message != "":
                create_message(from_number, message)
                return 'OK'
            else:
                create_message(from_number, "You have no movies being downloaded at the moment.\n\nIf you previously added a movie, it is likely that it has finished downloading. If you believe this is an error, please contact Parker.")
                return 'OK'
        # Otherwise, add another part to the message containing movie data
        else:
            message += "\n\nIf movies consistently show as 'WARNING' or 'QUEUED' or any other error over multiple hours, please contact Parker."
            create_message(from_number, message)
            return 'OK'
    # No valid commands were found, so just return
    else:
        return 'OK'


# Handle 405 errors - when a user attempts a GET request on a POST only route
@app.errorhandler(405)
def method_not_allowed(e):
    if home_domain != 'None':
        return flask.redirect(home_domain)
    return 'Method Not Allowed'

@app.errorhandler(404)
def page_not_found(e):
    if home_domain != 'None':
        return flask.redirect(home_domain)
    return 'Page Not Found'
