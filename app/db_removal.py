from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import requests

from initialize_variables import radarr_host_url, headers

# Remove all entries from the database of movies that have already finished downloading
# This helps to stop from entries building up in the database and slowing down everything
sched = BackgroundScheduler(daemon=True)
@sched.scheduled_job('cron', hour='0', minute='0')
def clear_database():
    db = sqlite3.connect('/data/movies.db')
    cursor = db.cursor()
    # First get all of the movie ids in the database
    cursor.execute('''
        SELECT movie_id FROM movies
    ''')
    movie_ids = cursor.fetchall()
    # Get all of the movie_ids that are currently downloading/queued and/or missing
    response = requests.get(f'{radarr_host_url}/api/v3/queue/', headers=headers)
    current_movie_ids = []
    for movie in response.json()['records']:
        current_movie_ids.append(str(movie['movieId']))

    # Loop through the movie_ids in the database, if they are not in the current_movie_ids list,
    # that means they are not currently downloading/queued, so delete them from the database
    for movie_id in movie_ids:
        if movie_id[0] not in current_movie_ids:
            cursor.execute('''
                DELETE FROM movies WHERE movie_id = ?
            ''', (movie_id[0],))
    db.commit()
    db.close()