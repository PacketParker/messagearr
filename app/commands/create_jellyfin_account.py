import datetime
import requests
import random
import string
import sqlite3

import initialize_variables
from create_message import create_message


def create_jellyfin_account(from_number):
    # Otherwise, all checks have been completed
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    password = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

    deletion_time = datetime.datetime.now() + datetime.timedelta(hours=4)
    # Create new Jellyfin account
    request_1 = requests.post(f'{initialize_variables.jellyfin_url}/Users/New', headers=initialize_variables.jellyfin_headers, json={'Name': username, 'Password': password})
    if request_1.status_code != 200:
        create_message(from_number, "Error creating Jellyfin account. Please try again. If the error persists, contact Parker.")
        return

    user_id = request_1.json()['Id']
    # Get account policy and make edits
    request_2 = requests.get(f'{initialize_variables.jellyfin_url}/Users/{user_id}', headers=initialize_variables.jellyfin_headers)
    if request_2.status_code != 200:
        create_message(from_number, "Error creating Jellyfin account. Please try again. If the error persists, contact Parker.")
        return

    policy = request_2.json()['Policy']
    policy['SyncPlayAccess'] = 'JoinGroups'
    policy['EnableContentDownloading'] = False
    policy['InvalidLoginAttemptCount'] = 3
    policy['MaxActiveSessions'] = 1
    # Update user with new policy
    request_3 = requests.post(f'{initialize_variables.jellyfin_url}/Users/{user_id}/Policy', headers=initialize_variables.jellyfin_headers, json=policy)
    if request_3.status_code != 204:
        create_message(from_number, "Error creating Jellyfin account. Please try again. If the error persists, contact Parker.")
        return

    # Add information to the database
    db = sqlite3.connect(initialize_variables.db_path)
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO jellyfin_accounts (user_id, deletion_time)
        VALUES(?, ?)
    ''', (user_id, deletion_time))
    db.commit()
    db.close()

    create_message(from_number, f"Username: {username}\nPassword: {password}\n\nYour account will expire in 4 hours.")
    return
