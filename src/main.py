import sys
sys.path.append("..")
from src.util import *

def generate_attendance_letters(school: str, start_date: str, repeated_letters: bool) -> None:
    
    if today_is_a_school_day(school, school_info[school]['sr_id']):
        pass
    else:
        return

    database = {}

    student_list = sr_api_pull(
        search_key="students",
        parameters={
            "active": "1",
            "school_ids": school_info[school]['sr_id'],
            'expand': 'grade_level, student_details, student_attrs.student_attr_type',
        }
    )

    absence_list = sr_api_pull(
        'absences',
        parameters = {
            'active': '1',
            'school_ids': school_info[school]['sr_id'],
            'min_date': start_date,
            'max_date': today_yyyy_mm_dd,
            # 'out_of_school_only': '1',                        # pull everything because you need to include tardies
            'expand': 'absence_type, student.grade_level'
        }
    )

    communications_list = sr_api_pull(
        'communications',
        parameters = {
            'active': '1',
            'school_ids': school_info[school]['sr_id'],
            'min_date': start_date,
            'max_date': today_yyyy_mm_dd,
            'expand': 'communication_method, communication_type, student'
        }
    )

    for student in student_list:
        if student['student_id'] in database:
            continue
        else:
            database[student['student_id']] = {
                'first_name': student['first_name'].replace("’", "'"),
                'last_name': student['last_name'].replace("’", "'"),
                'grade_level': student['grade_level']['order_key'],
                'street': extract_sr_student_detail(student['student_details'], 'mailing_street'),
                'city': extract_sr_student_detail(student['student_details'], 'mailing_city'),
                'state': extract_sr_student_detail(student['student_details'], 'mailing_state'),
                'zip': extract_sr_student_detail(student['student_details'], 'mailing_zip'),
                'home_language': extract_sr_student_attribute(student['student_attrs'], 'S_LA_STU_Language_X.LanguageCode'),
                'sis_id': student['sis_id'],
                'sr_id': student['student_id'],
                'au': 0,
                'tu': 0,
                '3au_letters_logged': 0,
                '5au_letters_logged': 0,
                '10au_letters_logged': 0,
            }
    
    for absence in absence_list:
        if absence['absence_type']['code'] == 'AU' and absence['student']['active'] == '1' and absence['student']['school_id'] == school_info[school]['sr_id']:
            database[absence['student_id']]['au'] += 1
        elif absence['absence_type']['code'] == 'TU' and absence['student']['active'] == '1' and absence['student']['school_id'] == school_info[school]['sr_id']:
            database[absence['student_id']]['tu'] += 1
    
    for communication in communications_list:
        if communication['student_id'] in database and communication['student']['active'] == '1' and communication['communication_method']['name'] == "Letter" and communication['communication_type']['name'] == 'Attendance' and communication['comments'] == '3+ AU Letter':
            database[communication['student_id']]['3au_letters_logged'] += 1
        elif communication['student_id'] in database and communication['student']['active'] == '1' and communication['communication_method']['name'] == "Letter" and communication['communication_type']['name'] == 'Attendance' and communication['comments'] == '5+ AU Letter':
            database[communication['student_id']]['5au_letters_logged'] += 1
        elif communication['student_id'] in database and communication['student']['active'] == '1' and communication['communication_method']['name'] == "Letter" and communication['communication_type']['name'] == 'Attendance' and communication['comments'] == '10+ AU Letter':
            database[communication['student_id']]['10au_letters_logged'] += 1

    ##########################################################################
    ########                PDF GENERATION STARTS HERE              ##########
    ##########################################################################

    with open(f"../logs/json/{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}_{school}_attendance_database.json", "w") as file:
            logging.info('dumping attendance database info to logs folder')
            json.dump(database, file, indent=4)

    class MyFPDF(FPDF, HTMLMixin):
        pass
    pdf = MyFPDF(orientation='P', unit='mm', format='Letter')
    pdf.set_margin(5)
    pdf.set_font('helvetica', size=10)

    for student in database:
        if database[student]['street'] == None or database[student]['city'] == None or database[student]['state'] == None or database[student]['zip'] == None:
            continue
        if database[student]['au'] >= 3 and database[student]['3au_letters_logged'] == 0:
            pdf.add_page()
            pdf.image(f"../assets/{school.lower()}_letterhead.png", x=125, y=5, h=8)
            pdf.multi_cell(
                w=0,
                h=4,
                new_x="LMARGIN",
                new_y="NEXT",
                txt=f"{database[student]['first_name']} {database[student]['last_name']} - {datetime.datetime.today().strftime('%A, %B %-d, %Y')} (3 Absence Letter)",
                markdown=True
            )
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt='')
            
            if school == 'OA':
                pass
            else:
                if database[student]['home_language'] == '113':
                    generate_page_content(pdf, school, attendance_letter_blocks_spanish_page1)
                else:
                    generate_page_content(pdf, school, attendance_letter_blocks_page1)
                pdf.add_page()

            data = (
                ("Scholar Attendance Summary", f"{database[student]['first_name']} {database[student]['last_name']}"),
                ("Unexcused Absences", str(database[student]['au'])),
                ("Unexcused Tardies", str(database[student]['tu'])),
            )

            line_height = pdf.font_size * 2.5
            col_width = pdf.epw / 3  # distribute content evenly
            for row in data:
                for datum in row:
                    pdf.multi_cell(col_width, line_height, datum, border=1, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
                pdf.ln(line_height)

            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt='')

            if school == 'OA':
                generate_page_content(pdf, school, oa_attendance_letter_blocks)
                
            else:
                if database[student]['home_language'] == '113':
                    generate_page_content(pdf, school, attendance_letter3_blocks_spanish_page2)
                else:
                    generate_page_content(pdf, school, attendance_letter3_blocks_page2)
                
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt='Sincerely,')
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt=school_info[school]['principal'])

            if school == 'OA':
                pdf.add_page()

            pdf.text(15, 255, f"Parents/Guardians of {database[student]['first_name']} {database[student]['last_name']}")
            pdf.text(15, 260, database[student]['street'])
            pdf.text(15, 265, f"{database[student]['city']}, {database[student]['state']} {database[student]['zip']}")
            
            log_communication(
                student_id = database[student]['sr_id'],
                communication_method_id = '15' if database[student]['home_language'] == '113' else '17',
                communication_type_id = '2',
                staff_member_id = '11690',
                school_id = school_info[school]['sr_id'],
                contact_person = 'Parent/Guardian letter',
                comments = '3+ AU Letter',
                sandbox=False
            )
        
        if database[student]['au'] >= 5 and database[student]['5au_letters_logged'] == 0:
            pdf.add_page()
            pdf.image(f"../assets/{school.lower()}_letterhead.png", x=125, y=5, h=8)
            pdf.multi_cell(
                w=0,
                h=4,
                new_x="LMARGIN",
                new_y="NEXT",
                txt=f"{database[student]['first_name']} {database[student]['last_name']} - {datetime.datetime.today().strftime('%A, %B %-d, %Y')} (5 Absence Letter)",
                markdown=True
            )
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt='')
            
            if school == 'OA':
                pass
            else:
                if database[student]['home_language'] == '113':
                    generate_page_content(pdf, school, attendance_letter_blocks_spanish_page1)
                else:
                    generate_page_content(pdf, school, attendance_letter_blocks_page1)
                pdf.add_page()

            data = (
                ("Scholar Attendance Summary", f"{database[student]['first_name']} {database[student]['last_name']}"),
                ("Unexcused Absences", str(database[student]['au'])),
                ("Unexcused Tardies", str(database[student]['tu'])),
            )
            line_height = pdf.font_size * 2.5
            col_width = pdf.epw / 3  # distribute content evenly
            for row in data:
                for datum in row:
                    pdf.multi_cell(col_width, line_height, datum, border=1, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
                pdf.ln(line_height)

            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt='')
            
            if school == 'OA':
                generate_page_content(pdf, school, oa_attendance_letter_blocks)
            else:
                if database[student]['home_language'] == '113':
                    generate_page_content(pdf, school, attendance_letter5_blocks_spanish_page2)
                else:
                    generate_page_content(pdf, school, attendance_letter5_blocks_page2)
                
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt='Sincerely,')
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt=school_info[school]['principal'])
            
            if school == 'OA':
                pdf.add_page()

            pdf.text(15, 255, f"Parents/Guardians of {database[student]['first_name']} {database[student]['last_name']}")
            pdf.text(15, 260, database[student]['street'])
            pdf.text(15, 265, f"{database[student]['city']}, {database[student]['state']} {database[student]['zip']}")

            log_communication(
                student_id = database[student]['sr_id'],
                communication_method_id = '15' if database[student]['home_language'] == '113' else '17',
                communication_type_id = '2',
                staff_member_id = '11690',
                school_id = school_info[school]['sr_id'],
                contact_person = 'Parent/Guardian letter',
                comments = '5+ AU Letter',
                sandbox=False
            )

        if database[student]['au'] >= 10 and database[student]['10au_letters_logged'] == 0:
            pdf.add_page()
            pdf.image(f"../assets/{school.lower()}_letterhead.png", x=125, y=5, h=8)
            pdf.multi_cell(
                w=0,
                h=4,
                new_x="LMARGIN",
                new_y="NEXT",
                txt=f"{database[student]['first_name']} {database[student]['last_name']} - {datetime.datetime.today().strftime('%A, %B %-d, %Y')} (10 Absence Letter)",
                markdown=True
            )
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt='')
            
            if school == 'OA':
                pass
            else:
                if database[student]['home_language'] == '113':
                    generate_page_content(pdf, school, attendance_letter_blocks_spanish_page1)
                else:
                    generate_page_content(pdf, school, attendance_letter_blocks_page1)
                pdf.add_page()

            data = (
                ("Scholar Attendance Summary", f"{database[student]['first_name']} {database[student]['last_name']}"),
                ("Unexcused Absences", str(database[student]['au'])),
                ("Unexcused Tardies", str(database[student]['tu'])),
            )
            line_height = pdf.font_size * 2.5
            col_width = pdf.epw / 3  # distribute content evenly
            for row in data:
                for datum in row:
                    pdf.multi_cell(col_width, line_height, datum, border=1, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
                pdf.ln(line_height)

            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt='')
            
            if school == 'OA':
                generate_page_content(pdf, school, oa_attendance_letter_blocks)
            else:
                if database[student]['home_language'] == '113':
                    generate_page_content(pdf, school, attendance_letter10_blocks_spanish_page2)
                else:
                    generate_page_content(pdf, school, attendance_letter10_blocks_page2)
                
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt='Sincerely,')
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", txt=school_info[school]['principal'])
            
            if school == 'OA':
                pdf.add_page()

            pdf.text(15, 255, f"Parents/Guardians of {database[student]['first_name']} {database[student]['last_name']}")
            pdf.text(15, 260, database[student]['street'])
            pdf.text(15, 265, f"{database[student]['city']}, {database[student]['state']} {database[student]['zip']}")

            log_communication(
                student_id = database[student]['sr_id'],
                communication_method_id = '15' if database[student]['home_language'] == '113' else '17',
                communication_type_id = '2',
                staff_member_id = '11690',
                school_id = school_info[school]['sr_id'],
                contact_person = 'Parent/Guardian letter',
                comments = '10+ AU Letter',
                sandbox=False
            )

    pdf.output(f"../pdf/{school}_{today_yyyy_mm_dd}_attendance_letter.pdf")
    
    send_email(
        recipient=school_info[school]['attendance_letter_recipient'],
        text_body='Good morning,\n\nThe following letters have already been logged in Schoolrunner for you. All you need to do is fold, stuff, stamp, and send them out!\n\n- The CA Data Robot 🤖',
        subject_line=f'{school} Attendance Letters {today_yyyy_mm_dd}',
        attachment=f"../pdf/{school}_{today_yyyy_mm_dd}_attendance_letter.pdf",
        cc="shogarty@collegiateacademies.org"
    )


def assessments_export():
    assessments = sr_api_pull(
        search_key="assessments",
        parameters={
            'min_date': '2022-07-01',
            'active': '1',
            'expand': 'school, staff_member, assessment_type, assessment_courses, assessment_section_period_links.section_period.section.course_definition'
        }
    )

    term_bins = sr_api_pull(
        search_key="term-bins",
        parameters={
            'active': '1'
        }
    )

    output = [['School', 'PowerSchool Course', 'SR Course', 'Sections', 'Teacher ID', 'Teacher', 'Term Bin', 'Week of', 'Name', 'Assessment ID']]

    for assessment in assessments:
        
        ps_course_list = []
        sr_course_list = []
        section_list = []

        for sr_course in assessment['assessment_courses']:
            sr_course_list.append(sr_course['display_name'])

        for section in assessment['assessment_section_period_links']:
            if section['section_period']['section_id'] not in section_list:
                section_list.append(f"{section['section_period']['section_id']}")
            if section['section_period']['section']['course_definition']['display_name'] not in ps_course_list:
                ps_course_list.append(f"{section['section_period']['section']['course_definition']['display_name']}")

        term_bin_output = ''
        for term_bin in term_bins:
            if term_bin['start_date'] is not None:
                term_start_date = convert_yyyy_mm_dd_date(term_bin['start_date'])
            if term_bin['end_date'] is not None:
                term_end_date = convert_yyyy_mm_dd_date(term_bin['end_date'])
            assessment_date = convert_yyyy_mm_dd_date(assessment['date'])

            if term_start_date <= assessment_date and term_end_date >= assessment_date and assessment['school_id'] == term_bin['school_id'] and 'quarter' in term_bin['long_name'].lower():
                term_bin_output = term_bin['short_name']

        if len(ps_course_list) == 0:
            output.append([
                assessment['school']['short_name'],
                assessment['assessment_section_period_links'][0]['section_period']['section']['course_definition']['display_name'] if len(assessment['assessment_section_period_links']) > 0 else "No Course",
                ','.join(sr_course_list),
                ','.join(section_list),
                assessment['staff_member']['sis_id'],
                assessment['staff_member']['display_name'],
                term_bin_output,
                return_monday(assessment['date']),
                assessment['display_name'],
                assessment['assessment_id']
            ])
        
        for x in range(len(ps_course_list)):
            output.append([
                assessment['school']['short_name'],
                ps_course_list[x],
                ','.join(sr_course_list),
                ','.join(section_list),
                assessment['staff_member']['sis_id'],
                assessment['staff_member']['display_name'],
                term_bin_output,
                return_monday(assessment['date']),
                assessment['display_name'],
                assessment['assessment_id']
            ])

    update_googlesheet_by_key(
        spreadsheet_key='1gaMzfvMbG1O7Nh1-sWc_UupVzKl5xFyyFZAHSodLMps',
        sheet_name='assessments',
        data=output,
        starting_cell='A1'
    )
    
    # This little guy is for later down the line if we decide to sort this sheet
    # return_googlesheet_by_key(spreadsheet_key='1gaMzfvMbG1O7Nh1-sWc_UupVzKl5xFyyFZAHSodLMps', sheet_name='assessments').sort((6, 'asc'), (0, 'asc'), (4, 'asc'), range = f'A2:{return_numeric_column(len(output[0]))}{len(output)}')


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
                sender_string=f"{school} Attendance Updates"
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
