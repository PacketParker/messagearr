import datetime
import sqlite3
import requests
import humanize

import initialize_variables
from create_message import create_message


def status(from_number):
    # This returns a list of ALL movies being downloaded, but not all of them were
    # requested by the user, so we need to filter out the ones that were not requested
    response = requests.get(f'{initialize_variables.radarr_host_url}/api/v3/queue/', headers=initialize_variables.headers)
    # Get all the movie_ids that were requested by the user
    db = sqlite3.connect(initialize_variables.db_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT movie_id, movie_title FROM movies WHERE from_number = ?
    ''', (from_number,))
    movie_info = cursor.fetchall()
    db.close()

    movies = {} # movie_id: movie_title
    for movie in movie_info:
        movies[movie[0]] = movie[1]

    if len(movies) == 0:
        create_message(from_number, "You have no movies being downloaded at the moment.\n\nIf you previously added a movie, it is likely that it has finished downloading. If you believe this is an error, please contact Parker.")
        return

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
            response = requests.get(f'{initialize_variables.radarr_host_url}/api/v3/movie/{movie_id}', headers=initialize_variables.headers)
            # This means that there is no current download, and no file has been found
            # MOST likely means a download just wasn't found, so alert the user
            data = response.json()
            if data['hasFile'] == False:
                message += f"{movies[movie_id]} - NOT FOUND\n\nThis means a download was not found for the movie(s), if this is a brand new movie that is likely the reason. If the movie has already been released on DVD/Blu-Ray, please contact Parker."

        # Send message with info about download to user, otherwise, the user has
        # no movies being downloaded at the moment so alert them
        if message != "":
            create_message(from_number, message)
            return
        else:
            create_message(from_number, "You have no movies being downloaded at the moment.\n\nIf you previously added a movie, it is likely that it has finished downloading. If you believe this is an error, please contact Parker.")
            return

    # Otherwise, add another part to the message containing movie data
    else:
        message += "\n\nIf movies consistently show as 'WARNING' or 'QUEUED' or any other error over multiple hours, please contact Parker."
        create_message(from_number, message)
        return