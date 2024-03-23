import datetime
import requests
import sqlite3

import initialize_variables
from create_message import create_message


def number_response_request(from_number, message):
    if from_number not in initialize_variables.temp_movie_ids.keys():
        create_message(from_number, "There is no current request that you can decide on. It might be that your /request command timed out due since you took too long to response. Please try again. If this issue persists, please contact Parker.")
        return

    # If its been 5 minutes since prompt was sent, alert user of timed out request
    if (datetime.datetime.now() - initialize_variables.temp_movie_ids[from_number]['time']).total_seconds() / 60 > 5:
        del initialize_variables.temp_movie_ids[from_number]
        create_message(from_number, "You waited too long and therefore your request has timed out.\n\nPlease try again by re-running the /request command. If this issue persists, please contact Parker.")
        return

    # Otherwise, all checks have been completed
    create_message(from_number, "Just a moment while I add your movie to the library...")
    movie_number = initialize_variables.numbers_responses[message.strip()]
    try:
        tmdb_id = initialize_variables.temp_movie_ids[from_number]['ids'][movie_number - 1]
    except IndexError:
        create_message(from_number, "You did not enter a valid number. Please re-send the /request command and try again. If you believe this is an error, please contact Parker.")
        del initialize_variables.temp_movie_ids[from_number]
        return

    data = requests.get(f'{initialize_variables.radarr_host_url}/api/v3/movie/lookup/tmdb?tmdbId={tmdb_id}', headers=initialize_variables.headers)

    data = data.json()
    movie_title = data['title']
    # Change the qualityProfileId, monitored, and rootFolderPath values
    data['qualityProfileId'] = initialize_variables.quality_profile_id
    data['monitored'] = True
    data['rootFolderPath'] = initialize_variables.root_folder_path
    # Send data to Radarr API
    response = requests.post(f'{initialize_variables.radarr_host_url}/api/v3/movie', headers=initialize_variables.headers, json=data)
    data = response.json()
    movie_id = data['id']
    # Send message to user alerting them that the movie was added to the library
    create_message(from_number, f"🎉 {data['title']} has been added to the library!\n\nTo check up on the status of your movie(s) send /status - please wait at least 5 minutes before running this command in order to get an accurate time.")

    # After everything is completed, send Radarr a request to search indexers for new movie
    requests.post(f'{initialize_variables.radarr_host_url}/api/v3/command', headers=initialize_variables.headers, json={'name': 'MoviesSearch', 'movieIds': [int(movie_id)]})

    # Add the movie_id to the database so that users can check up on the status of their movie
    db = sqlite3.connect(initialize_variables.db_path)
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO movies(from_number, movie_id, movie_title)
        VALUES(?, ?, ?)
    ''', (from_number, movie_id, movie_title))
    db.commit()
    db.close()

    del initialize_variables.temp_movie_ids[from_number]
    return