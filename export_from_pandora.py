import requests
import json
import math

import logging
import argparse


parser = argparse.ArgumentParser(description='Grab my likes from Pandora before I get booted out!')

parser.add_argument('--email', required=True, type=str, help='Your login email address')
parser.add_argument('--password', required=True, type=str, help='Your login password')
parser.add_argument('--output_file', default="my-pandora-likes.csv", type=str, help='File name of CSV file to write to')
parser.add_argument('--batch_size', default=100, type=int, help='Number of likes to pull down in each batch')

args = parser.parse_args()
settings = vars(args)

logger = logging.getLogger("pandabye")
logger.setLevel(logging.INFO)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %I:%M:%S%p')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


logger.info("Getting me a cookie")
url = 'https://www.pandora.com/account/sign-in'
r = requests.get(url)
cookies = r.cookies
logger.info("Got a cookie {0}".format(r.cookies["csrftoken"]))

auth_token = None
webname = None
#batch_size = 100

def login(username, password):
    global auth_token
    global webname
    url = "https://www.pandora.com/api/v1/auth/login"
    body = {
        "existingAuthToken": None,
        "keepLoggedIn": True,
        "username": username,
        "password": password
    }
    headers={
        "Origin": "https://www.pandora.com",
        "Referrer": "https://www.pandora.com/account/sign-in",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "X-CsrfToken": cookies["csrftoken"]
    }
    r = requests.post(
        url,
        json=body,
        headers=headers,
        cookies=cookies
    )
    if(r.status_code != 200):
        logger.exception("Unable to login - %s", r.json())
        raise Exception(r.json())
    #print("Status code: " + str(r.status_code))
    result = r.json()
    logger.debug("Login returned %s", result)
    webname = result["webname"]
    auth_token = result["authToken"]

def get_feedback(webname, page_size=10, start_index=0):
    url = "https://www.pandora.com/api/v1/station/getFeedback"
    body = {
        "pageSize": page_size,
        "startIndex": start_index,
        "webname": webname
    }
    headers = {
        "X-CsrfToken": cookies["csrftoken"],
        "X-AuthToken": auth_token
    }
    r = requests.post(
        url,
        json=body,
        headers=headers,
        cookies=cookies
    )
    if(r.status_code != 200):
        logger.exception("Unable to get feedback %s", r.json())
        raise Exception(r.json())

    return r.json()


logger.info("Logging in with email address {0}".format(settings["email"]))
login(settings["email"], settings["password"])
# get initial count
logger.info("Getting initial page of likes to see how many there are")
initial = get_feedback(webname, page_size=10, start_index=0)
logger.info("Got {0} feedbacks".format(initial["total"]))

logger.info("Downloading feedback in batches of {0}".format(settings["batch_size"]))
total_batches = math.ceil(initial["total"] / settings["batch_size"])

batch_number = 1
all_my_likes = []
while(batch_number <= total_batches):
    logger.info("Requesting batch {batch_number} of {total_batches}".format(batch_number=batch_number, total_batches=total_batches))
    result = get_feedback(webname, settings["batch_size"], (batch_number - 1) * settings["batch_size"])
    for r in result["feedback"]:
        logger.debug("%s", r)
        if(r["isPositive"]):
            all_my_likes.append(r)
    batch_number = batch_number + 1

logger.info("Writing {0} likes to file {1}".format(len(all_my_likes), settings["output_file"]))

import csv
fieldnames = all_my_likes[0].keys()
with open(settings["output_file"], "w") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for l in all_my_likes:
        writer.writerow(l)

logger.info("Export is complete.")
