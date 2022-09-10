import base64, requests, datetime, pprint, json, csv, logging, sys, string, inspect
from pathlib import Path


pp = pprint.PrettyPrinter(indent=2)


today_yyyy_mm_dd = datetime.datetime.today().strftime('%Y-%m-%d')


school_codes = {
    'LCA' : '15'
}


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
    format="[%(levelname)s] %(asctime)s -- %(filename)s on line %(lineno)s\n\tFunction name: %(funcName)s\n\tMessage: %(message)s\n",
    datefmt='%B-%d-%Y %H:%M:%S',
    filename=f"../logs/{Path(__file__).stem}.log",
    filemode='w'
)


with open('../creds.json') as file:
    credentials = json.load(file)


def sr_api_pull(search_key, parameters={}, page_limit='') -> list:
    """A blank function for returning an endpoint for Schoolrunner. Logs its progress in the logs folder and logs its outputs as a json file."""
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


def convert_yyyy_mm_dd_date(date_string: string) -> datetime.date:
    year = int(date_string[0:4])
    month = int(date_string[5:7])
    day = int(date_string[8:10])

    return datetime.datetime(year, month, day)


def return_term_dates(term_bin_id: string) -> string:
    """Returns the start and end dates of a given term in Schoolrunner."""
    term_bins = sr_api_pull(
        search_key='term-bins',
        parameters={
            'term_bin_ids': term_bin_id,
            'expand': 'school_id'
        }
    )
    logging.info(f"{term_bins[0]['long_name']} (Term ID {term_bins[0]['term_bin_id']}) starts on {term_bins[0]['start_date']} and ends on {term_bins[0]['end_date']}")
    return term_bins[0]['start_date'], term_bins[0]['end_date']


def return_this_sr_term(search_term: string, school: string) -> string:
    """Finds the term based on the type of term you look up (semester, quuarter, etc.)"""
    terms = sr_api_pull(
        search_key='term-bins',
        parameters={
            "school_ids": school_codes[school],
            'expand': 'term_bin_type'
        }
    )

    for term in terms:
        start_date = convert_yyyy_mm_dd_date(term['start_date'])
        end_date = convert_yyyy_mm_dd_date(term['end_date'])
        if search_term.lower() in term['long_name'].lower() and start_date <= datetime.datetime.now() <= end_date:
            logging.info(f"Found term {term['long_name']} - {term['term_bin_id']}")
            return term['term_bin_id']