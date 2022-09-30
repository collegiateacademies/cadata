import base64, requests, datetime, pprint, json, logging, sys, smtplib
from xml.dom.minidom import Attr
from pathlib import Path
from fpdf import FPDF, HTMLMixin
from email.message import EmailMessage
import __main__

pp = pprint.PrettyPrinter(indent=2)


today_yyyy_mm_dd = datetime.datetime.today().strftime('%Y-%m-%d')


school_info = {
    'LCA' : {
        'short_name': 'LCA',
        'long_name': 'Livingston Collegiate Academy',
        'sr_id': '15',
        'street': '7301 Dwyer Rd',
        'city': 'New Orleans',
        'state': 'LA',
        'zip': '70126',
        'principal': 'Akeem Langham',
        'phone': '504-503-0004',
        'fax': '504-342-0322',
        'attendance_email': 'hello@livingstoncollegiate.org',
        'attendance_letter_recipient': 'cpuliafico@collegiateacademies.org',
    },
    'ASA': {
        'short_name': 'ASA',
        'long_name': 'Abramson Sci Academy',
        'sr_id': '1',
        'street': '5552 Read Blvd',
        'city': 'New Orleans',
        'state': 'LA',
        'zip': '70127',
        'principal': 'Anthony McElligott',
        'fax': '504-324-0171',
        'phone': '504-373-6264',
        'attendance_email': 'frontdesk@sciacademy.org',
        'attendance_letter_recipient': 'kthomas1@collegiateacademies.org',
    },
    'CBR': {
        'short_name': 'CBR',
        'long_name': 'Collegiate Baton Rouge',
        'sr_id': '17',
        'street': '282 Lobdell Blvd',
        'city': 'Baton Rouge',
        'state': 'LA',
        'zip': '70806',
        'principal': 'Samantha Johnson',
        'fax': '225-286-7808',
        'phone': '225-892-6962',
        'attendance_email': 'info@collegiatebr.org',
        'attendance_letter_recipient': 'amiles@collegiateacademies.org',
    },
    'GWC': {
        'short_name': 'GWC',
        'long_name': 'G.W. Carver High School',
        'sr_id': '2',
        'street': '3059 Higgins Blvd',
        'city': 'New Orleans',
        'state': 'LA',
        'zip': '70126',
        'principal': 'Jerel Bryant',
        'fax': '504-754-7980',
        'phone': '504-308-3660',
        'attendance_email': 'info@carvercollegiate.org',
        'attendance_letter_recipient': 'amueller@collegiateacademies.org',
    },
    'RCA': {
        'short_name': 'RCA',
        'long_name': 'Rosenwald Collegiate Academy',
        'sr_id': '18',
        'street': '1801 L B Landry Ave',
        'city': 'New Orleans',
        'state': 'LA',
        'zip': '70114',
        'principal': 'Rhonda Dale',
        'fax': '504-814-9296',
        'phone': '504-503-1400',
        'attendance_email': 'info@rosenwaldcollegiate.org',
        'attendance_letter_recipient': 'sscott1@collegiateacademies.org',
    },
    'OA': {
        'short_name': 'OA',
        'long_name': 'Opportunities Academy',
        'sr_id': '19',
        'street': '2625 Thalia St',
        'city': 'New Orleans',
        'state': 'LA',
        'zip': '70113',
        'principal': 'Sophia Scott',
        'fax': '504-814-1721',
        'phone': '504-503-1421',
        'attendance_email': 'hello@opportunitiesacademy.org',
        'attendance_letter_recipient': 'hello@opportunitiesacademy.org',
    },
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
    level=logging.INFO,
    format="\n[%(levelname)s] %(asctime)s -- %(filename)s on line %(lineno)s\n\tFunction name: %(funcName)s\n\tMessage: %(message)s\n",
    datefmt='%B-%d-%Y %H:%M:%S',
    filename=f"../logs/{Path(__main__.__file__).stem}.log",
    filemode='w'
)

attendance_letter_blocks_page1 = [
    {
        'name': 'attendance_policy_header',
        'text': "**###school_name### Attendance Policy**",
    },
    {
        'name': 'attendance_policy_explainer',
        'text': "Students can only be successful if they are present and prepared in school every day. Our curriculum is an ambitious one; every day is essential for students to keep pace.  At ###school_name###, excessive absences will not be tolerated.",
    },
    {
        'name': 'attendance_policy_warning',
        'text': "**If a student is absent without excuse for more than 9 days of the semester, the student will not receive credit for any courses they are taking during that semester.**",
    },
    {
        'name': 'attendance_requirements_header',
        'text': '**Attendance Requirements**',
    },
    {
        'name': 'attendance_requirement1',
        'text': 'Students must be present for \"60,120 minutes (equivalent to 167 six-hour school days)\" per year and 30,060 per semester',
        'bullet_level': 1,
    },
    {
        'name': 'attendance_requirement2',
        'text': 'Because our classes are semester based, students must meet attendance requirements per semester',
        'bullet_level': 1,
    },
    {
        'name': 'attendance_requirement3',
        'text': '**Based on our schedule, a student must miss no more than 9 days per semester to earn credit for their courses**',
        'bullet_level': 1,
    },
    {
        'name': 'excuse_policy_header',
        'text': 'Absences will be recorded as excused or unexcused, in accordance with our policies:',
    },
    {
        'name': 'excuse_policy1',
        'text': 'Absences will be considered **excused** if they fall into one of the following categories and documentation is submitted to the school: illness, hospital stay, medical appointments, observation of holidays of the student\'s own faith, visitation with a parent who is a member of the armed forces, death in the immediate family.',
        'bullet_level': 1,
    },
    {
        'name': 'excuse_policy2',
        'text': 'You can submit documentation by:',
        'bullet_level': 1,
    },
    {
        'name': 'excuse_policy2a',
        'text': 'Emailing it to ###attendace_email###',
        'bullet_level': 2,
    },
    {
        'name': 'excuse_policy2b',
        'text': 'Faxing it to ###fax_number###',
        'bullet_level': 2,
    },
    {
        'name': 'excuse_policy2c',
        'text': 'Bringing it to the front office',
        'bullet_level': 2,
    },
    {
        'name': 'excuse_policy3',
        'text': 'Absences will be considered **unexcused** if they do not fall into a category outlined above or if documentation is not provided.',
        'bullet_level': 1,
    },
    {
        'name': 'comms_and_ints_header',
        'text': '**Attendance Communication and Interventions**',
    },
    {
        'name': 'comms_and_ints_explainer',
        'text': 'We believe that it is important for our school staff, families, and students to have open communication around attendance. Our school will take the following steps upon each absence:',
    },
    {
        'name': 'comms_and_ints1',
        'text': '3-4 absences: The school will send a letter to the parent/guardian notifying the parent of the student\'s status and recommending a conference to develop an attendance plan in accordance with LRS 17:233.  The student\'s parent/guardian will be contacted by school staff to schedule a mandatory Attendance Conference to develop an attendance plan for the student.  All notes from the meeting and the details of the attendance plan will be documented.',
        'bullet_level': 1,
    },
    {
        'name': 'comms_and_ints2',
        'text': '5 absences: The student is considered as truant as pursuant to LRS 17:233.  A letter will be sent to the home of the student informing the parent/guardian of violation of compulsory attendance law. Supervisor of Child Welfare and Attendance may file report(s) to Municipal Court for Truancy and/or the NOLA Public Schools Office of Student Support and Attendance.',
        'bullet_level': 1,
    },
    {
        'name': 'comms_and_ints3',
        'text': '6+ absences: A school official or representative may conduct a home visit, review the attendance plan, enforce compulsory attendance law, and make recommendations to improve attendance.',
        'bullet_level': 1,
    },
]

attendance_letter3_blocks_page2 = [
    {
        'name': 'page2_header',
        'text': 'Re: Attendance Warning',
    },
    {
        'name': 'page2_paragraph1',
        'text': '**You are receiving this letter because your child has 3 or more Unexcused Absences and/or Tardies.** Under the law, students are required to attend school regularly and must attend a minimum number of days of school to earn credit and be eligible for promotion to the next grade.  Your child is in danger of not being promoted to the next grade.',
    },
    {
        'name': 'page2_paragraph2',
        'text': 'A representative from the school will contact you via phone to schedule a mandatory attendance conference.  In this conference, your child\'s attendance record will be reviewed and a plan will be put into place that they must follow in order to be eligible for promotion or graduation.',
    },
    {
        'name': 'page2_paragraph3',
        'text': '**If your child does not meet the school\'s attendance requirements, they may not earn credit for their courses and may have to complete the same grade next year.  Failure to adhere to the requirements of your scholar\'s attendance plan will also result in a referral to Municipal Court.**',
    },
    {
        'name': 'page2_paragraph4',
        'text': 'Please review our attendance policy on the reverse of this letter.  You can contact ###school_name### at ###school_phone### to discuss your child\'s attendance and your next steps. We look forward to having your student attend school on a daily basis so we can continue their pathway to college success.',
    }
]

attendance_letter5_blocks_page2 = [
    {
        'name': 'page2_header',
        'text': 'Re: Attendance Warning',
    },
    {
        'name': 'page2_paragraph1',
        'text': '**You are receiving this letter because your child has exceeded the maximum number of Unexcused Absences and/or Tardies allowed by law and is now considered truant.**  Louisiana requires students to attend school for a certain number of days to be promoted to the next grade and earn credit for a course. Under the law, students are required to attend school regularly and must attend a minimum number of days of school to earn credit and be eligible for promotion to the next grade.  Your child is in danger of not being promoted to the next grade because he or she has been absent more than the time allotted by the state.',
    },
    {
        'name': 'page2_paragraph2',
        'text': 'A representative from the school will contact you via phone to schedule a mandatory attendance hearing.  In this hearing, your child\'s attendance record will be reviewed and a plan will be put into place that they must follow in order to be eligible for promotion or graduation.',
    },
    {
        'name': 'page2_paragraph3',
        'text': '**If your child does not meet the school\'s attendance requirements, they may not earn credit for their courses and may have to complete the same grade next year.  Failure to adhere to the requirements of your scholar\'s attendance plan will also result in a referral to Municipal Court.**',
    },
    {
        'name': 'page2_paragraph4',
        'text': 'Please review our attendance policy on the reverse of this letter.  You can contact ###school_name### at ###school_phone### to discuss your child\'s attendance and your next steps. We look forward to having your student attend school on a daily basis so we can continue their pathway to college success.',
    }
]

with open('../creds.json') as file:
    credentials = json.load(file)


def sr_api_pull(search_key: str, parameters: dict = {}, page_limit: str = '') -> list:
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


def convert_yyyy_mm_dd_date(date_string: str) -> datetime.date:
    year = int(date_string[0:4])
    month = int(date_string[5:7])
    day = int(date_string[8:10])

    return datetime.datetime(year, month, day)


def return_term_dates(term_bin_id: str) -> str:
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


def return_this_sr_term(search_term: str, school: str) -> str:
    """Finds the term based on the type of term you look up (semester, quuarter, etc.)"""
    terms = sr_api_pull(
        search_key='term-bins',
        parameters={
            "school_ids": school_info[school]['sr_id'],
            'expand': 'term_bin_type'
        }
    )

    for term in terms:
        start_date = convert_yyyy_mm_dd_date(term['start_date'])
        end_date = convert_yyyy_mm_dd_date(term['end_date'])
        if search_term.lower() in term['long_name'].lower() and start_date <= datetime.datetime.now() <= end_date:
            logging.info(f"Found term {term['long_name']} - {term['term_bin_id']}")
            return term['term_bin_id']

def log_communication(student_id, communication_method_id, communication_type_id, staff_member_id, school_id, contact_person='',comments='', sandbox=False) -> dict:
    """Used to log a communcation in Schoolrunner for any school. Will require
    most parameters that Schoolrunner requires and will also take a comment &
    person contacted just to make the log more useful. These are optional params"""
    payload = {
        'school_id': school_id,
        'student_id': student_id,
        'communication_method_id': communication_method_id,
        'communication_type_id': communication_type_id,
        'staff_member_id': staff_member_id,
        'contact_person': contact_person,
        'date': today_yyyy_mm_dd,
        'comments': comments
    }

    params = {
        'Content-Type': 'application/json'
    }

    headers = {'Authorization': 'Basic ' + base64.b64encode(bytes(f"{credentials['sr_email']}:{credentials['sr_pass']}", "UTF-8")).decode("ascii")}

    logging.info(f'Logging communication for {student_id}')
    
    try:
        if sandbox:
            response = requests.post(f"https://ca.sandbox.schoolrunner.org/api/v1/communications", json=payload, params=params, headers=headers).json()
            logging.info(f"Successful log for {student_id} -- {response}")
            return response
        else:
            response = requests.post(f"https://ca.schoolrunner.org/api/v1/communications", json=payload, params=params, headers=headers).json()
            logging.info(f"Successful log for {student_id} -- {response}")
            return response
    except Exception as error:
        logging.error(f"Unsuccessful log for {student_id} - {error}", exc_info=True)

def send_email(recipient='', text_body='', subject_line='', html_body='', bcc='', cc='', reply_to='', attachment=''):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        try:
            smtp.login(credentials['cadata_email_addr'], credentials['python_gmail_app_password'])
        except Exception as error:
            logging.error(f"Error at SSL login for {recipient} -- {error}", exc_info=True)
            smtp.quit()

        msg = EmailMessage()
        msg['Subject'] = subject_line
        msg['From'] = credentials['cadata_email_addr']
        msg['To'] = recipient
        if cc != '':
            msg['Cc'] = cc
        if bcc != '':
            msg['Bcc'] = bcc
        msg.set_content(text_body)
        if html_body != '':
            msg.add_alternative(html_body, subtype='html')
        if reply_to != '':
            msg['reply-to'] = reply_to
        if attachment != '':
            with open(attachment, 'rb') as content_file:
                content = content_file.read()
                msg.add_attachment(content, maintype='application', subtype='pdf', filename=attachment)

        logging.info(f"\n🤞 Attempting email for to:{recipient} 🤞")
        try:
            smtp.send_message(msg)
            logging.info(f"🍾 Email sent for to:{recipient} 🍾")
            smtp.quit()
        except Exception as error_inside:
            logging.error(f"Error at send for to:{recipient} -- error: {error_inside}", exc_info=True)
            smtp.quit()

def extract_sr_student_attribute(attr_list: list, attr_key: str):
    """Takes the nasy list of student attributes that is attached to students
    and will return the currently active version for the provided key"""
    for attr in attr_list:
        if attr['active'] == '1' and attr['student_attr_type']['attr_key'] == attr_key:
            return attr['display_name']


def today_is_a_school_day(school, school_id):
    params = {
        'school_ids': school_id,
        'max_date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'min_date': datetime.datetime.now().strftime('%Y-%m-%d')
    }

    headers = {'Authorization': 'Basic ' + base64.b64encode(bytes(f"{credentials['sr_email']}:{credentials['sr_pass']}", "UTF-8")).decode("ascii")}
    response = requests.get('https://ca.schoolrunner.org/api/v1/calendar_days?', params=params, headers=headers).json()

    if response['results']['calendar_days'][0]['in_session'] == '0':
        logging.info(f"Today is not a school day at {school.upper()}")
        return False
    else:
        logging.info(f"Today is a school day at {school.upper()}")
        return True

def return_current_sr_term(term_type: str, school: str) -> str:
    terms = sr_api_pull(
        search_key='term-bins',
        parameters={
            'school_ids': school_info[school]['sr_id'],
            'expand': 'term_bin_type'
        }
    )

    for term in terms:
        try:
            start_date = convert_yyyy_mm_dd_date(term['start_date'])
            end_date = convert_yyyy_mm_dd_date(term['end_date'])
            if term_type.lower() in term['long_name'].lower() and start_date <= datetime.datetime.now() <= end_date:
                logging.info(f"Found term {term['long_name']} - {term['term_bin_id']}")
                return term['term_bin_id']
        except AttributeError as attr_error:
            logging.error(f"Error with a term -- it probably doesn\'t have a long name -- {attr_error}", exc_info=True)
        except TypeError as type_error:
            logging.error(f"Error with a termin -- its dates are wonky -- {type_error}", exc_info=True)
        except Exception as error:
            logging.error(f"Error with a term -- {error}", exc_info=True)

def return_term_dates(term_bin_id: str) -> str:
    term_bins = sr_api_pull(
        search_key='term-bins',
        parameters={
            'term_bin_ids': term_bin_id
        }
    )

    return term_bins[0]['start_date'], term_bins[0]['end_date']

def return_term_start_date(term_type: str, school: str) -> str:
    return return_term_dates(return_current_sr_term(term_type, school))[0]

def return_term_end_date(term_type: str, school: str) -> str:
    return return_term_dates(return_current_sr_term(term_type, school))[1]