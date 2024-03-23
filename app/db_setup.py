import os
import sqlite3
import initialize_variables

"""
This function is run before the application starts - creates database and sets connection string
"""
def setup_db():
    IN_DOCKER = os.environ.get('IN_DOCKER', False)
    if IN_DOCKER:
        db = sqlite3.connect('/data/movies.db')
        initialize_variables.db_path =  '/data/movies.db'
    else:
        db = sqlite3.connect('movies.db')
        initialize_variables.db_path = 'movies.db'

    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies(
            from_number TEXT,
            movie_id TEXT,
            movie_title TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jellyfin_accounts(
            user_id TEXT,
            deletion_time DATETIME
        )
    ''')
    db.commit()
    db.close()
