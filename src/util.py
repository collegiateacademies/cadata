import base64, requests, datetime, pprint, json, csv, logging, sys
from pathlib import Path

pp = pprint.PrettyPrinter(indent=2)

# ANSI Escape Codes

# Colors
black = "\u001b[30m"
red = "\u001b[31m"
green = "\u001b[32m"
yellow = "\u001b[33m"
blue = "\u001b[34m"
magenta = "\u001b[35m"
cyan = "\u001b[36m"
white = "\u001b[37m"
reset = "\u001b[0m"

# Text Decorations
bold = "\u001b[1m"
underline = "\u001b[4m"

sys.path.append("..")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%B-%d-%Y %H:%M:%S',
    filename=f"../logs/{Path(__file__).stem}.log",
    filemode='w'
)

with open('../creds.json') as file:
    credentials = json.load(file)

def sr_api_pull(search_key, parameters={}, page_limit=''):
    items = []
    headers = {'Authorization': 'Basic ' + base64.b64encode(bytes(f"{credentials['sr_email']}:{credentials['sr_pass']}", "UTF-8")).decode("ascii")}
    page_params = {key: value for (key, value) in parameters.items() if key != 'expand'}
    logging.info(f"🤞 Finding number of pages for {' '.join(search_key.split('-'))} 🤞")
    response = requests.get(f"https://ca.schoolrunner.org/api/v1/{search_key}?", params=page_params,headers=headers).json()
    logging.info(f"There are {response['meta']['total_pages']} page(s) of {' '.join(search_key.split('-'))}.")
    if page_limit == '':
        for page in range(response['meta']['total_pages']):
            logging.info(f"Pulling page {page + 1} of {response['meta']['total_pages']} page(s)")
            this_response = requests.get(f"https://ca.schoolrunner.org/api/v1/{search_key}?page={page + 1}", params=parameters, headers=headers).json()
            for item in this_response['results'][search_key.replace('-', '_')]:
                items.append(item)
        logging.info(f"🎉 Done pulling {' '.join(search_key.split('-'))}! 🎉")
    else:
        for page in range(page_limit):
            logging.info(f"Pulling page {yellow}{page + 1} of {page_limit} pages [limited]")
            this_response = requests.get(f"https://ca.schoolrunner.org/api/v1/{search_key}?page={page + 1}",params=parameters, headers=headers).json()
            for item in this_response['results'][search_key.replace('-', '_')]:
                items.append(item)
        logging.info(f"🎉 Done pulling {' '.join(search_key.split('-'))}! 🎉\n")
    
    with open(f"../logs/json/{search_key}output_{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.json", "w") as file:
        json.dump(items, file, indent=4)

    return items