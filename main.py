import itertools
import threading
import requests
import logging

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


def filtered_user(username):
    url = 'https://users.roblox.com/v1/users/search?keyword=%s&limit=10' % username
    urlHandler = requests.get(url, headers=headers)
    if urlHandler.status_code == 200:
        # Either an exception username or it simply does not exist yet.
        print("Username: %s does not exist yet and has been logged to file. Exceptions do exist though." % username)
        logging.info(
            "Username: %s does not exist yet. NOTE: There are exceptions! Roblox's API does NOT always find certain taken usernames." % username)
    elif urlHandler.status_code == 400:
        # Bad username. Filtered by Roblox.
        print(
            "Username query has been filtered by ROBLOX's filtering system: %s" % username)
    elif urlHandler.status_code == 429:
        # Too many requests.
        print("API reported: %s Too many requests for username: %s" %
              (urlHandler.status_code, username))
    else:
        # Unexpected error.
        print("FILTERING Response failed with code: %s RETRYING..." %
              urlHandler.status_code)
        return filtered_user(username)


def fetch_user(username):
    data = '{"usernames": ["%s"], "excludeBannedUsers": false}' % username
    # User API url. See all: https://users.roblox.com/docs
    URL = 'https://users.roblox.com/v1/usernames/users'
    urlHandler = requests.post(URL, headers=headers, data=data)
    if urlHandler.status_code == 200:
        root_doc = urlHandler.json()
        if root_doc['data']:
            print("uid: %s, Username: %s" %
                  (root_doc['data'][0]['id'], username))
        else:
            # Is this username filtered by ROBLOX or genuinely not taken? (NOTE! Some taken username exceptions DO exist, ex. "a0uq")
            print("--------------------------------------------")
            filtered_user(username)
        return
    elif urlHandler.status_code == 400:
        print('%s error code.' % urlHandler.status_code)
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
