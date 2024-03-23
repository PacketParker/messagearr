import requests
import datetime

import initialize_variables
from create_message import create_message


def request(from_number, message):
    # If the user has already run the /request command, delete the entry
    # from the temp_movie_ids dict so that they can run the command again
    if from_number in initialize_variables.temp_movie_ids.keys():
        del initialize_variables.temp_movie_ids[from_number]

    # If the user did not include a movie title, alert them to do so
    if len(message) <= 9:
        create_message(from_number, "Please include the movie title after the /request command.\nEX: /request The Dark Knight")
        return

    incoming_message = message.split(' ', 1)[1]
    movie_request = incoming_message.replace(' ', '%20')
    if movie_request.endswith("%20"):
        movie_request = movie_request[:-3]

    # Send a request to the radarr API to get the movie info
    response = requests.get(f'{initialize_variables.radarr_host_url}/api/v3/movie/lookup?term={movie_request}', headers=initialize_variables.headers)

    if len(response.json()) == 0:
        create_message(from_number, "There were no results for that movie. Please make sure you typed the title correctly.")
        return
    # If the movie is already added to the library, return a message saying so.
    if response.json()[0]['added'] != '0001-01-01T05:51:00Z':
        create_message(from_number, "This movie is already added to the server.\n\nIf you believe this is an error, please contact Parker.")
        return

    # Add top 3 results to a message
    message = ""
    for i in range(min(3, len(response.json()))):
        message += f"{i+1}. {response.json()[i]['folder']}\n\n"
        if from_number not in initialize_variables.temp_movie_ids.keys():
            initialize_variables.temp_movie_ids[from_number] = {
                'ids': [],
                'time': datetime.datetime.now()
            }
        initialize_variables.temp_movie_ids[from_number]['ids'].append(response.json()[i]['tmdbId'])

    message += "Reply with the number associated with the movie you want to download. EX: 1\n\nIf the movie you want is not on the list, make sure you typed the title exactly as it is spelt, or ask Parker to manually add the movie."

    create_message(from_number, message)
    return