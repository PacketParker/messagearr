from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3
import requests
import datetime

import initialize_variables

# Remove all entries from the database of movies that have already finished downloading
# This helps to stop from entries building up in the database and slowing down everything
sched = BackgroundScheduler(daemon=True)
@sched.scheduled_job('cron', hour='0', minute='0')
def clear_database():
    db = sqlite3.connect(initialize_variables.db_path)
    cursor = db.cursor()
    # First get all of the movie ids in the database
    cursor.execute('''
        SELECT movie_id FROM movies
    ''')
    movie_ids = cursor.fetchall()
    # Get all of the movie_ids that are currently downloading/queued and/or missing
    response = requests.get(f'{initialize_variables.radarr_host_url}/api/v3/queue/', headers=initialize_variables.headers)
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

@sched.scheduled_job('interval', seconds=10)
def clear_jellyfin_accounts():
    db = sqlite3.connect(initialize_variables.db_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT user_id, deletion_time FROM jellyfin_accounts
    ''')
    data = cursor.fetchall()
    for user_id, deletion_time in data:
        if datetime.datetime.now() > datetime.datetime.strptime(deletion_time, '%Y-%m-%d %H:%M:%S.%f'):
            requests.delete(f'{initialize_variables.jellyfin_url}/Users/{user_id}', headers=initialize_variables.jellyfin_headers)
            cursor.execute('''
                DELETE FROM jellyfin_accounts WHERE user_id = ?
            ''', (user_id,))
    db.commit()
    db.close()