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
YOUR_ROBLOX_COOKIE = "Your .ROBLOSECURITY cookie goes here."
# If you log out this will change. Stay logged in to keep this cookie.
# There are plenty of tutorials on how to get your .ROBLOSECURITY cookie. Copy paste it into YOUR_ROBLOX_COOKIE field.
# An example of what YOUR_ROBLOX_COOKIE should look like: "_|WARNING: -DO-NOT-SHARE-THIS.--... numbers ..."
cookies = {'.ROBLOSECURITY': YOUR_ROBLOX_COOKIE}


def can_register_user(username):
    url = "https://auth.roblox.com/v1/usernames/validate?context=UsernameChange&username=%s" % username
    urlHandler = requests.get(url, headers=headers, cookies=cookies)
    if urlHandler.status_code == 200:
        root_doc = urlHandler.json()
        if root_doc and root_doc['code'] == 0:
            print("Found an available username: %s" % username)
            logging.info("Username: %s available!" % username)
        elif root_doc and root_doc['code'] == 1:
            print("Username is already in use: %s" % username)
        else:
            print("Filtering does not allow creation for the username: %s" % username)
            logging.info(
                "Username: %s does not exist but can't be made since it's inappropriate for Roblox!" % username)
    else:
        print("Your cookie is most likely invalid. Change it in the code!")
        return can_register_user(username)  # Recursion.


for v1, v2, v3, v4 in itertools.product(*ranges):
    username = ''.join('%s%s%s%s') % (ltrs[v1], ltrs[v2], ltrs[v3], ltrs[v4])
    bulk_list.append(username)
    if len(bulk_list) == bulk_size:
        threads = [threading.Thread(target=can_register_user, args=(
            user_data,)) for user_data in bulk_list]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        bulk_list = []
