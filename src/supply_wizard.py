import logging, json, sys, smtplib
from email.message import EmailMessage
from pprint import pformat
from todoist_api_python.api import TodoistAPI

sys.path.append("..")

with open('../creds.json') as file:
    credentials = json.load(file)

# LCA Todoist Operations Team
collaborators = {
    'Diamond Davis': '39208790',
    'Caitlin Puliafico': '39208786',
    'Topher McKee': '39208760',
    'Thaise Ashford': '39208781',
    'R. J. Wilkins': '39208793'
}

def send_email(
        recipient: str = '',
        text_body: str = '',
        subject_line: str = '',
        html_body: str = '',
        bcc: str = '',
        cc: str = '',
        reply_to: str = '',
        attachment: str = '',
        sender_string: str = '') -> None:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        try:
            smtp.login(credentials['cadata_email_addr'], credentials['python_gmail_app_password'])
        except Exception as error:
            logging.error(f"Error at SSL login for {recipient} -- {error}", exc_info=True)
            smtp.quit()

        msg = EmailMessage()
        msg['Subject'] = subject_line
        msg['From'] = credentials['cadata_email_addr'] if sender_string == '' else sender_string
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

def return_typeform_response(responses, field_id):
    for response in responses:
        if response['field']['id'] == field_id:
            if response['type'] == 'choice':
                return response['choice']['label']
            elif response['type'] == 'choices':
                return ', '.join(response['choices']['labels'])
            elif response['type'] == 'text':
                return response['text']
            elif response['type'] == 'number':
                return response['number']
            elif response['type'] == 'date':
                return response['date']
            elif response['type'] == 'url':
                return response['url']
            
def new_supply_request(staff_name, department, contact_method, item_name, item_quantity, link_to_item, total_cost, due_date, notes, section_override=''):
    api = TodoistAPI(credentials['todoist_access_token'])
    supply_wizard_project_id = '2289889190'

    if section_override != '':
        section_id = section_override
    else:
        section_id = '86767515'

    try:
        task = api.add_task(
            content=f"* {item_quantity} [{item_name.title()}]({link_to_item}) (${total_cost})",
            description=f'{staff_name} - {due_date}',
            section_id=section_id,
            project_id=supply_wizard_project_id,
            priority=4,
            assignee_id=get_collaborators('Diamond Davis', supply_wizard_project_id),

        )
        logging.info(f"Task logged successfully: {pformat(task)}")
        if len(notes) > 0:
            comment_response = api.add_comment(
                content=f"**Comment from {staff_name}:** {notes}",
                task_id=task.id
            )
            logging.info(f"Added comment as well {comment_response}")
    except Exception as error:
        logging.error(error, exc_info=True)

def new_supply_request_from_form(request) -> None:
    answers = request.json['form_response']['answers']
    new_supply_request(
        staff_name=return_typeform_response(answers, 'tUEthDKlsDxn'),
        department=return_typeform_response(answers, 'AgCxx7YGr278'),
        contact_method=return_typeform_response(answers, 'R01zv68xOZs7'),
        item_name=return_typeform_response(answers, 'T9Pt0RUiGm24'),
        item_quantity=return_typeform_response(answers, 'gM0putEL4y0Y'),
        link_to_item=return_typeform_response(answers, '60QX6EQK1bEI'),
        total_cost=return_typeform_response(answers, 'PeDsVa6JqjZn'),
        due_date=return_typeform_response(answers, 'S2Xvyf7wsitr'),
        notes=return_typeform_response(answers, 'yyTUgLDswCHr')
    )
    send_email(
        recipient='supplies@livingstoncollegiate.org',
        subject_line=f'New Supply Request from {return_typeform_response(answers, "tUEthDKlsDxn")}',
        html_body=f"<p>Check the <a href='https://todoist.com/app/project/2289889190'>Supply Wizard Todoist project</a> for details</p><br><br>Requestor: {return_typeform_response(answers, 'tUEthDKlsDxn')}<br>Request: {return_typeform_response(answers, 'gM0putEL4y0Y')} {return_typeform_response(answers, 'T9Pt0RUiGm24')}<br>Link: {return_typeform_response(answers, '60QX6EQK1bEI')}<br>Total Cost: {return_typeform_response(answers, 'PeDsVa6JqjZn')}<br>Needed by: {return_typeform_response(answers, 'S2Xvyf7wsitr')}<br>Notes: {return_typeform_response(answers, 'yyTUgLDswCHr')}"
    )