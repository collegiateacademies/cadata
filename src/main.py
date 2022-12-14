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
                'first_name': student['first_name'],
                'last_name': student['last_name'],
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

    ##########################################################################
    ########                PDF GENERATION STARTS HERE              ##########
    ##########################################################################

    class MyFPDF(FPDF, HTMLMixin):
        pass
    pdf = MyFPDF(orientation='P', unit='mm', format='Letter')
    pdf.set_margin(5)
    pdf.set_font('helvetica', size=10)

    for student in database:
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

    pdf.output(f"../pdf/{school}_{today_yyyy_mm_dd}_attendance_letter.pdf")
    
    send_email(
        recipient=school_info[school]['attendance_letter_recipient'],
        text_body='Good morning,\n\nThe following letters have already been logged in Schoolrunner for you. All you need to do is fold, stuff, stamp, and send them out!\n\n- The CA Data Robot ????',
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
            'expand': 'school, staff_member, assessment_type, assessment_courses, assessment_section_period_links.section_period.section, assessment_section_period_links.section_period.period, assessment_section_period_links.section_period.calendar_day_type, assessment_section_period_links.section_period.staff_member, assessment_section_period_links.section_period.term'
        }
    )

    term_bins = sr_api_pull(
        search_key="term-bins",
        parameters={
            'active': '1'
        }
    )

    output = [['School', 'Course', 'Sections', 'Teacher ID', 'Teacher', 'Term Bin', 'Week of', 'Name', 'Assessment ID']]

    for assessment in assessments:
        
        course_list = []
        section_list = []

        for course in assessment['assessment_courses']:
            course_list.append(course['display_name'])

        for section in assessment['assessment_section_period_links']:
            if section['section_period']['section_id'] not in section_list:
                section_list.append(f"{section['section_period']['section_id']}")

        term_bin_output = ''
        for term_bin in term_bins:
            if term_bin['start_date'] is not None:
                term_start_date = convert_yyyy_mm_dd_date(term_bin['start_date'])
            if term_bin['end_date'] is not None:
                term_end_date = convert_yyyy_mm_dd_date(term_bin['end_date'])
            assessment_date = convert_yyyy_mm_dd_date(assessment['date'])

            if term_start_date <= assessment_date and term_end_date >= assessment_date and assessment['school_id'] == term_bin['school_id'] and 'quarter' in term_bin['long_name'].lower():
                term_bin_output = term_bin['short_name']

        output.append([
            assessment['school']['short_name'],
            ','.join(course_list),
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


def individualized_attendance_reports(school: str) -> None:
    
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
            'min_date': return_term_start_date('semester', school),
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
                if school_info[school]['seat_time']['calendar']:
                    html_email = file.read().replace('###table_data###', table_data).replace('###au###', str(au)).replace('###attendance_email###', school_info[school]['individualized_report_reply']).replace('###seat_time###', f'<a href="{school_info[school]["seat_time"]["link"]}">You can find our seat time calendar here.</a> ')
                elif school_info[school]['seat_time']['contact']:
                    html_email = file.read().replace('###table_data###', table_data).replace('###au###', str(au)).replace('###attendance_email###', school_info[school]['individualized_report_reply']).replace('###seat_time###', f'Students may recover up unexcused absences by attending seat time. Reach out to <a href="mailto:{school_info[school]["seat_time"]["contact_email"]}?subject=Seat%20time%20dates%20and%20times&body=Hi%20there%2C%0A%0AWhat%20are%20the%20dates%20and%20times%20for%20seat%20time%20recovery%3F%0A%0AThank%20you%2C%0A{student["first_name"]}%20{student["last_name"]}">{school_info[school]["seat_time"]["contact_name"]}</a> for dates and times.')
        
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