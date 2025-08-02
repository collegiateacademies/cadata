import sys
sys.path.append("..")
from src.util import *


def individualized_attendance_reports(school: str, start_date: str) -> None:
    
    if today_is_a_school_day(school, school_info[school]['sr_id']):
        pass
    else:
        return

    student_list = sr_api_pull(
        search_key="students",
        parameters={
            'active': '1',
            'school_ids': school_info[school]['sr_id'],
            'expand': 'grade_level, student_detail, student_attrs.student_attr_type',
            # 'limit': '1'
        },
        # page_limit=1
    )

    absence_list = sr_api_pull(
        search_key='absences',
        parameters={
            'active': '1',
            'school_ids': school_info[school]['sr_id'],
            'min_date': start_date,
            'max_date': today_yyyy_mm_dd,
            'expand': 'absence_type'
        }
    )

    for student in student_list:
        table_data = ''
        au = 0
        codes_to_send = ['AU', 'AEO', 'AEP']

        logging.info(f"Processing for {student['first_name']} {student['last_name']} -- {datetime.datetime.now().strftime('%I:%M:%S')}")
        email = extract_sr_student_attribute(student['student_attrs'], 'student_email')
        p1_email = extract_sr_student_attribute(student['student_attrs'], 'Primary_1_Email')

        for absence in absence_list:
            absence_date = convert_yyyy_mm_dd_date(absence['date'])
            
            if absence['student_id'] == student['student_id'] and absence['absence_type']['code'] in codes_to_send:
                table_data += f"<tr><td>{absence_date.strftime('%A, %B %-d, %Y')}</td><td>{absence['absence_type']['display_name']}</td></tr>"
                if absence['student_id'] == student['student_id'] and absence['absence_type']['code'] == 'AU':
                    au += 1

            with open('../html/individualized_attendance_report.html', 'r') as file:

                if school_info[school]['seat_time']['contact'] == 'OA':
                    html_email = file.read().replace('###table_data###', table_data).replace('###au###', str(au)).replace('###attendance_email###', school_info[school]['individualized_report_reply']).replace('###seat_time###', f'You can email any absent notes, doctor notes, etc., to hello@opportunitiesacademy.org. ').replace('###9absences###', '').replace('###attendance_policy###', "You can read more about the OA Attendance Policy on page 28 of the <a href='https://docs.google.com/document/d/1SBNFq8LPEkuImfc18VOKm0a9hg0GBnXma6_y4_SuFL8/edit?usp=sharing'>OA Handbook.</a>")
                elif school_info[school]['seat_time']['calendar']:
                    html_email = file.read().replace('###table_data###', table_data).replace('###au###', str(au)).replace('###attendance_email###', school_info[school]['individualized_report_reply']).replace('###seat_time###', f'<a href="{school_info[school]["seat_time"]["link"]}">You can find our seat time calendar here.</a> ').replace('###9absences###', 'A student must have no more than 9 unexcused absences per semester to earn credit for their courses. ').replace('###attendance_policy###', "If you would like more information on our Attendance Policy, <a href='https://docs.google.com/document/d/1cRCqwb1FAqGg2mcLgsuA_kab14Ci5A-2GEkC4BrrQnI/edit?usp=sharing'>click here.</a>")
                elif school_info[school]['seat_time']['contact']:
                    html_email = file.read().replace('###table_data###', table_data).replace('###au###', str(au)).replace('###attendance_email###', school_info[school]['individualized_report_reply']).replace('###seat_time###', f'Students may recover up unexcused absences by attending seat time. Reach out to <a href="mailto:{school_info[school]["seat_time"]["contact_email"]}?subject=Seat%20time%20dates%20and%20times&body=Hi%20there%2C%0A%0AWhat%20are%20the%20dates%20and%20times%20for%20seat%20time%20recovery%3F%0A%0AThank%20you%2C%0A{student["first_name"]}%20{student["last_name"]}">{school_info[school]["seat_time"]["contact_name"]}</a> for dates and times. ').replace('###9absences###', 'A student must have no more than 9 unexcused absences per semester to earn credit for their courses. ').replace('###attendance_policy###', "If you would like more information on our Attendance Policy, <a href='https://docs.google.com/document/d/1cRCqwb1FAqGg2mcLgsuA_kab14Ci5A-2GEkC4BrrQnI/edit?usp=sharing'>click here.</a>")
        
        if (school == 'OA' and au > 0) or (school != 'OA'):
            send_email(
                recipient=email,
                subject_line=f"{today_yyyy_mm_dd} Attendance Update", 
                html_body=html_email,
                cc=p1_email,
                reply_to=school_info[school]['attendance_email'],
                sender_string=f"{school} Attendance Updates",
                sender=school
            )
            
            newline="\n"
            log_communication(
                student_id = student['student_id'],
                communication_method_id = '9',
                communication_type_id = '2',
                staff_member_id = '11690',
                contact_person = 'Student + parent cc\'d',
                comments = f"Weekly Attendance Report (contents below) {newline}{BeautifulSoup(html_email, 'html.parser').body.get_text(separator=newline)}",
                school_id = school_info[school]['sr_id'],
                sandbox=False
            )
        
            time.sleep(3)


def daily_attendance_email(school: str) -> None:
    
    if today_is_a_school_day(school, school_info[school]['sr_id']):
        pass
    else:
        return

    database = {

        'grades': {},
        'totals': {
            'students': 0,
            'absences': 0
        }
    }

    student_list = sr_api_pull(
        search_key='students',
        parameters={
            'active': '1',
            'school_ids': school_info[school]['sr_id'],
            'expand': 'grade_level'
        }
    )

    for student in student_list:
        if student['grade_level']['order_key'] not in database['grades']:
            database['grades'][student['grade_level']['order_key']] = {
                'int': int(student['grade_level']['order_key']),
                'total_students': 0,
                'total_out_of_school': 0,
                'names_list': ''
            }
            database['grades'][student['grade_level']['order_key']]['total_students'] += 1
            database['totals']['students'] += 1
        else:
            database['grades'][student['grade_level']['order_key']]['total_students'] += 1
            database['totals']['students'] += 1

    absence_list = sr_api_pull(
        search_key='absences',
        parameters={
            'min_date': today_yyyy_mm_dd,
            'max_date': today_yyyy_mm_dd,
            'active': '1',
            'school_ids': school_info[school]['sr_id'],
            'out_of_school_only': '1',
            'expand': 'absence_type, student.grade_level, student.student_attrs.student_attr_type'
        }
    )

    for absence in absence_list:
        if absence['student']['grade_level']['order_key'] in database['grades']:
            database['grades'][absence['student']['grade_level']['order_key']]['total_out_of_school'] += 1
            database['grades'][absence['student']['grade_level']['order_key']]['names_list'] += f"{absence['student']['display_name']} - ({absence['absence_type']['code']})<br>" #  - {extract_sr_student_attribute(absence['student']['student_attrs'], 'Advisor')} SAVE THIS FOR WHEN ADVISORIES MAKE SENSE
            database['totals']['absences'] += 1

    header_html = '<tr>'
    student_list_html = '<tr>'
    for grade in database['grades']:
        if school != 'OA' and grade == '13':
            continue
        else:
            header_html += f"<td>{grade}th: {str( round((int(database['grades'][grade]['total_students'])  - int(database['grades'][grade]['total_out_of_school']))  / int(database['grades'][grade]['total_students'])  * 100 , 2))}%</td>"
            student_list_html += f"<td>{database['grades'][grade]['names_list']}</td>"
    header_html += '</tr>'
    student_list_html += '</tr>'

    current_hour = datetime.datetime.now().hour
    match current_hour:
        case _ if current_hour <= 11:
            time_of_day = "Morning"
        case _ if current_hour > 11 and current_hour <= 2:
            time_of_day = "Mid-Day"
        case _ if current_hour > 2:
            time_of_day = "EOD"

    with open('../html/daily_attendance.html', 'r') as file:
        html_email = file.read()

    send_email(
        recipient=school_info[school]['attendance_letter_recipient'],
        subject_line=f"{today_yyyy_mm_dd} {time_of_day} Attendance Email",
        html_body=html_email
            .replace('###grade_headers###', header_html)
            .replace('###name_lists###', student_list_html)
            .replace( '###total###',      str( round((int(database['totals']['students'])   - int(database['totals']['absences']))        / int(database['totals']['students'])   * 100 , 2)))
    )


def log_cleaner():
    if sys.platform == 'darwin':
        log_path = '/Users/tophermckee/cadata/logs'
    elif sys.platform == 'linux':
        log_path = '/home/data_admin/cadata/logs'

    for root, dirs, files in os.walk(log_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.stat(file_path)
            if file != '.gitkeep':
                if file_size.st_size >= 1_000_000:
                    logging.info(f"removing {file_path} because it is over 1 MB at {file_size.st_size} bytes")
                    os.remove(file_path)
                elif (datetime.datetime.now() - datetime.datetime.fromtimestamp(file_size.st_mtime)).days > 30:
                    logging.info(f"removing {file_path} because it is older than 30 days")
                    os.remove(file_path)


def mail_monitor():
    gmail = Gmail()
    labels = gmail.list_labels()
    messages = gmail.get_unread_inbox()

    for message in messages:
        print("To: " + message.recipient)
        print("From: " + message.sender)
        print("Subject: " + message.subject)
        print("Date: " + message.date)
        print("Preview: " + message.snippet)
        
        print("Message Body: " + message.plain)  # or message.html

def upload_map_file():
    os.system("7z x ~/services_kit/report/bin/map_output/342339.zip")
    output = []
    with open('AssessmentResults.csv') as file:
        csv_reader = csv.reader(file)
        row = []
        for row in csv_reader:
            output.append(row)
    update_googlesheet_by_key(spreadsheet_key='17HNmMqS4Rwy3tZPcct69ZIz7yhuZIHv_mi4d9enJzD8', sheet_name='Sheet1', data = output, starting_cell="A1")

def send_staff_absence_emails(school: str, all_staff: int, spreadsheet_key: str) -> None:
    absence_data = return_googlesheet_by_key(spreadsheet_key = spreadsheet_key, sheet_name = 'Summary').get_values('A3:U')
    absence_types = return_googlesheet_by_key(spreadsheet_key = spreadsheet_key, sheet_name = 'Absences').get_values('A2:I')
    
    successful_sends = ''
    failed_sends     = ''

    for staff_member in absence_data:
        email_send              = staff_member[2]
        first_name              = staff_member[3]
        last_name               = staff_member[4]
        email                   = staff_member[5]
        pto_issued_tracker      = staff_member[10]
        pto_taken_tracker       = staff_member[11]
        pto_remaining_tracker   = staff_member[12]
        pto_issued_paylocity    = staff_member[13]
        pto_taken_paylocity     = staff_member[14]
        pto_remaining_paylocity = staff_member[15]
        unpaid_tracker          = staff_member[16]
        unpaid_paylocity        = staff_member[17]
        bereavement_tracker     = staff_member[18]
        bereavement_paylocity   = staff_member[19]
        tardies                 = staff_member[20]
        
        pto_types = ''

        for row in absence_types:
            if row[3] == staff_member[6] and row[0] != '' and row[1] != 'Tardy':
                pto_types += f"<li><code>{datetime.datetime.strptime(row[0], '%m/%d/%Y').strftime('%m-%d-%Y')}</code> - {row[1]} - {row[2]} hrs</li>"
        
        if sys.platform == 'darwin':
            html_path = '/Users/tophermckee/cadata/html/staff_absences.html'
        elif sys.platform == 'linux':
            html_path = '/home/data_admin/cadata/html/staff_absences.html'

        with open(html_path, 'r') as file:
            html_email = file.read()
            
            if all_staff == 1:
                pass
            elif all_staff == 0 and email_send == 'FALSE':
                continue
            
            if staff_member[1] == 'Active':                         # terminated column
                pass
            else:
                continue

            if send_email(
                recipient = email,
                subject_line = 'Staff Attendance Update',
                reply_to = school_info[school]['staff_pto_replyto'],
                sender_string = 'CA Staff Updates',
                html_body = html_email
                    .replace('###staff_name###', f"{first_name} {last_name}")
                    .replace('###pto_issued_tracker###',        pto_issued_tracker)
                    .replace('###pto_taken_tracker###',         pto_taken_tracker)
                    .replace('###pto_remaining_tracker###',     pto_remaining_tracker)
                    .replace('###pto_issued_paylocity###',      pto_issued_paylocity)
                    .replace('###pto_taken_paylocity###',       pto_taken_paylocity)
                    .replace('###pto_remaining_paylocity###',   pto_remaining_paylocity)
                    .replace('###unpaid_tracker###',            unpaid_tracker)
                    .replace('###unpaid_paylocity###',          unpaid_paylocity)
                    .replace('###bereavement_tracker###',       bereavement_tracker)
                    .replace('###bereavement_paylocity###',     bereavement_paylocity)
                    .replace('###tardies###',                   tardies)
                    .replace('###pto_types###',                 pto_types)
            ):
                successful_sends += f"<li><code>[{datetime.datetime.now().strftime('%m/%d/%y %I:%M %p')}]</code> Sent to {first_name} {last_name}</li>"
            else:
                failed_sends += f"<li><code>[{datetime.datetime.now().strftime('%m/%d/%y %I:%M %p')}]</code> Failed send to {first_name} {last_name}</li>"

    if sys.platform == 'darwin':
        html_path_dfo = '/Users/tophermckee/cadata/html/staff_absences_dfo.html'
    elif sys.platform == 'linux':
        html_path_dfo = '/home/data_admin/cadata/html/staff_absences_dfo.html'

    with open(html_path_dfo, 'r') as dfo_file:
        html_email_dfo = dfo_file.read()

        if len(failed_sends) == 0:
            failed_sends = '<li style="color: green;">No failures!</li>'

        send_email(
            recipient = school_info[school]['staff_pto_replyto'],
            subject_line = 'Staff Attendance Wrap-Up',
            reply_to = 'afelter@collegiateacademies.org',
            sender_string = 'CA Staff Updates',
            html_body = html_email_dfo
                    .replace('###dfo_name###',                  f"{school_info[school]['dfo_name']}")
                    .replace('###successful_sends###',          successful_sends)
                    .replace('###failed_sends###',              failed_sends)
        )
        

def update_typeform_staff_names(typeform_id: str = '', names_field_id: str = ''):
    staff_list = powerschool_powerquery(
        query_name='com.collegiateacademies.tophermckee.tables.staff',
        payload={
            'schoolid': '4'
        }
    )

    current_form = get_typeform(typeform_id)

    for item in current_form['fields']:
        if item['id'] == names_field_id:
            item['properties']['choices'] = []
            for staff_member in staff_list:
                if staff_member['tables']['schoolstaff']['status'] == '1':
                    item['properties']['choices'].append({'label': f"{staff_member['tables']['users']['first_name']} {staff_member['tables']['users']['last_name']}"})

    try:
        logging.info(f"🤞🏼 Attempting to update LCA Supply Wizard with new staff names 🤞🏼")
        typeform_name_update_request = requests.put(f"https://api.typeform.com/forms/{typeform_id}", data=json.dumps(current_form), headers={'Authorization': f'Bearer {credentials["typeform_token"]}'}).json()
        logging.info(f"🥂 Successfully updated LCA Supply Wizard with new staff names 🥂")
    except Exception as err:
        logging.error(f"Error updating LCA Supply Wizard with new staff names: {err}", exc_info=True)

    return typeform_name_update_request

def network_staff_export():
    staff_list = powerschool_powerquery(
            query_name='com.collegiateacademies.tophermckee.tables.all_staff',
            payload={
                'schoolid': '4'
            }
        )
    
    output = []

    for staff_member in staff_list:
        output.append([
            staff_member['tables']['users']['first_name'],
            staff_member['tables']['users']['preferredname'],
            staff_member['tables']['users']['last_name'],
            staff_member['tables']['users']['email_addr'],
            staff_member['tables']['users']['homeschoolid'],
            staff_member['tables']['schoolstaff']['status'],
        ])
    
    update_googlesheet_by_key(
        spreadsheet_key='1PkiVhI9UzLQOSKxtmLFyhLWB4ZehR8v_1I0ury4goV4',
        sheet_name='Sheet1',
        data=output,
        starting_cell='A1'
    )


def attendance_field_checker(school: str = '') -> None:

    if today_is_a_school_day(school, school_info[school]['sr_id']):
        pass
    else:
        return
    
    student_list = powerschool_powerquery(
        query_name='com.collegiateacademies.tophermckee.tables.attendance_letter_data_checker',
        payload={
            'school_id': school_info[school]['ps_id']
        }
    )

    total_missing_fields = 0
    list_items = ''

    for student in student_list:
        
        missing_fields = []
        for key in student['tables']['students'].keys():
            if student['tables']['students'][key] == None:
                missing_fields.append(key)
                total_missing_fields += 1
        if len(missing_fields) > 0:
            list_items += f"<li>{student['tables']['students']['first_name']} {student['tables']['students']['last_name']} ({student['tables']['students']['student_number']}) is missing the following fields: <code>{', '.join(missing_fields)}</code></li>"
        
    if total_missing_fields > 0:

        with open('../html/attendance_letter_checker.html', 'r') as file:
            html_email = file.read().replace('###missing_data###', list_items)
        
        send_email(
            recipient = school_info[school]['data_manager'],
            subject_line = '[data request] Attendance Letter Data Update',
            html_body = html_email,
            reply_to = 'tophermckee@gmail.com,afelter@collegiateacademies.org',
            sender_string = 'CA Data Robot'
        )
    
    else:
        logging.info('No students are missing any fields')
