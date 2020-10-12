import itertools
import threading
import requests
import logging
import json
import time

logging.basicConfig(filename='non_existing_usernames.log', level=logging.INFO)

ltrs = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q",
        "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

bulk_list = []
bulk_size = 4  # Changed depending on how many requests you want at once.

ranges = [range(0, len(ltrs)) for x in range(0, 4)]
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    "User-Agent": "Mozilla/5.0"
}


def fetch_user(username):
    data = '{"usernames": ["%s"], "excludeBannedUsers": false}' % username
    # User API url. See all: https://users.roblox.com/docs
    url = 'https://users.roblox.com/v1/usernames/users'
    urlHandler = requests.post(url, headers=headers, data=data)
    if urlHandler.status_code == 200:
        root_doc = urlHandler.json()
        if root_doc['data']:
            print("uid: ", root_doc['data'][0]['id'], ", Username: ", username)
        else:
            logging.info('Username: %s does not exist yet.' % username)
        return
    elif urlHandler.status_code == 400:
        print("Filtering system has blocked the following username: ",
              urlHandler.status_code, " for user: ", username)
    else:
        print('REQUEST FAILED FOR: %s RETRYING...' % username)
        # Retry finding user if request fails. This is normal with larger bulk requests.
        return fetch_user(username)  # Recursion.


for v1, v2, v3, v4 in itertools.product(*ranges):
    username = ''.join('%s%s%s%s') % (ltrs[v1], ltrs[v2], ltrs[v3], ltrs[v4])
    bulk_list.append(username)
    if len(bulk_list) == bulk_size:
        threads = [threading.Thread(target=fetch_user, args=(
            user_data,)) for user_data in bulk_list]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        bulk_list = []
