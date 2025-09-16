from util import *

# Function to sanitize text for PDF output
def sanitize_text(text):
    if not isinstance(text, str):
        return text
    replacements = {
        '\u2018': "'",  # left single quotation mark
        '\u2019': "'",  # right single quotation mark
        '\u201c': '"',   # left double quotation mark
        '\u201d': '"',   # right double quotation mark
        '\u2013': '-',    # en dash
        '\u2014': '-',    # em dash
        '\u2026': '...',  # ellipsis
        '\u00a0': ' ',    # non-breaking space
    }
    for uni, ascii_char in replacements.items():
        text = text.replace(uni, ascii_char)
    # Remove invisible Unicode formatting characters (e.g., LRM, RLM, directional marks)
    invisible_chars = [
        '\u200e', # LEFT-TO-RIGHT MARK
        '\u200f', # RIGHT-TO-LEFT MARK
        '\u202a', # LEFT-TO-RIGHT EMBEDDING
        '\u202b', # RIGHT-TO-LEFT EMBEDDING
        '\u202c', # POP DIRECTIONAL FORMATTING
        '\u202d', # LEFT-TO-RIGHT OVERRIDE
        '\u202e', # RIGHT-TO-LEFT OVERRIDE
    ]
    for uni in invisible_chars:
        text = text.replace(uni, '')
    # Also replace any remaining curly quotes directly
    text = text.replace('’', "'").replace('‘', "'")
    text = text.replace('“', '"').replace('”', '"')
    return text

def generate_attendance_letters(school: str, start_date: str, test_mode: bool = False, test_date: str = None) -> None:

    if test_mode and test_date:
        today_date = datetime.datetime.strptime(test_date, "%Y-%m-%d")
        today_yyyy_mm_dd = test_date
    else:
        today_date = datetime.datetime.today()
        today_yyyy_mm_dd = today_date.strftime("%Y-%m-%d")

    bypass_school_day_check = test_mode

    if bypass_school_day_check or today_is_a_school_day(school, school_info[school]['sr_id']):
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

    if sys.platform == "darwin":
        base_dir = "/Users/tophermckee/cadata/"
    else:
        base_dir = "/home/data_admin/cadata/"
    logs_dir = os.path.join(base_dir, "logs/json")
    os.makedirs(logs_dir, exist_ok=True)

    with open(os.path.join(logs_dir, f"{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}_{school}_attendance_database.json"), "w") as file:
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
            pdf.image(os.path.join(base_dir, f"assets/{school.lower()}_letterhead.png"), x=125, y=5, h=8)
            pdf.multi_cell(
                w=0,
                h=4,
                new_x="LMARGIN",
                new_y="NEXT",
                text=sanitize_text(f"{database[student]['first_name']} {database[student]['last_name']} - {today_date.strftime('%A, %B %-d, %Y')} (3 Absence Letter)"),
                markdown=True
            )
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", text='')

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

            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", text='')

            if school == 'OA':
                generate_page_content(pdf, school, oa_attendance_letter_blocks)

            else:
                if database[student]['home_language'] == '113':
                    generate_page_content(pdf, school, attendance_letter3_blocks_spanish_page2)
                else:
                    generate_page_content(pdf, school, attendance_letter3_blocks_page2)

            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", text='Sincerely,')
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", text=school_info[school]['principal'])

            if school == 'OA':
                pdf.add_page()

            pdf.text(15, 255, sanitize_text(f"Parents/Guardians of {database[student]['first_name']} {database[student]['last_name']}"))
            pdf.text(15, 260, sanitize_text(database[student]['street']))
            pdf.text(15, 265, sanitize_text(f"{database[student]['city']}, {database[student]['state']} {database[student]['zip']}"))

            log_communication(
                student_id = database[student]['sr_id'],
                communication_method_id = '15' if database[student]['home_language'] == '113' else '17',
                communication_type_id = '2',
                staff_member_id = '11690',
                school_id = school_info[school]['sr_id'],
                contact_person = 'Parent/Guardian letter',
                comments = '3+ AU Letter',
                sandbox=True if test_mode else False
            )

        if database[student]['au'] >= 5 and database[student]['5au_letters_logged'] == 0:
            pdf.add_page()
            pdf.image(os.path.join(base_dir, f"assets/{school.lower()}_letterhead.png"), x=125, y=5, h=8)
            pdf.multi_cell(
                w=0,
                h=4,
                new_x="LMARGIN",
                new_y="NEXT",
                text=sanitize_text(f"{database[student]['first_name']} {database[student]['last_name']} - {today_date.strftime('%A, %B %-d, %Y')} (5 Absence Letter)"),
                markdown=True
            )
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", text='')

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

            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", text='')

            if school == 'OA':
                generate_page_content(pdf, school, oa_attendance_letter_blocks)
            else:
                if database[student]['home_language'] == '113':
                    generate_page_content(pdf, school, attendance_letter5_blocks_spanish_page2)
                else:
                    generate_page_content(pdf, school, attendance_letter5_blocks_page2)

            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", text='Sincerely,')
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", text=school_info[school]['principal'])

            if school == 'OA':
                pdf.add_page()

            pdf.text(15, 255, sanitize_text(f"Parents/Guardians of {database[student]['first_name']} {database[student]['last_name']}"))
            pdf.text(15, 260, sanitize_text(database[student]['street']))
            pdf.text(15, 265, sanitize_text(f"{database[student]['city']}, {database[student]['state']} {database[student]['zip']}"))

            log_communication(
                student_id = database[student]['sr_id'],
                communication_method_id = '15' if database[student]['home_language'] == '113' else '17',
                communication_type_id = '2',
                staff_member_id = '11690',
                school_id = school_info[school]['sr_id'],
                contact_person = 'Parent/Guardian letter',
                comments = '5+ AU Letter',
                sandbox=True if test_mode else False
            )

        if database[student]['au'] >= 10 and database[student]['10au_letters_logged'] == 0:
            pdf.add_page()
            pdf.image(os.path.join(base_dir, f"assets/{school.lower()}_letterhead.png"), x=125, y=5, h=8)
            pdf.multi_cell(
                w=0,
                h=4,
                new_x="LMARGIN",
                new_y="NEXT",
                text=sanitize_text(f"{database[student]['first_name']} {database[student]['last_name']} - {today_date.strftime('%A, %B %-d, %Y')} (10 Absence Letter)"),
                markdown=True
            )
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", text='')

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

            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", text='')

            if school == 'OA':
                generate_page_content(pdf, school, oa_attendance_letter_blocks)
            else:
                if database[student]['home_language'] == '113':
                    generate_page_content(pdf, school, attendance_letter10_blocks_spanish_page2)
                else:
                    generate_page_content(pdf, school, attendance_letter10_blocks_page2)

            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", text='Sincerely,')
            pdf.multi_cell(w=0, h=4, new_x="LMARGIN", new_y="NEXT", text=school_info[school]['principal'])

            if school == 'OA':
                pdf.add_page()

            pdf.text(15, 255, sanitize_text(f"Parents/Guardians of {database[student]['first_name']} {database[student]['last_name']}"))
            pdf.text(15, 260, sanitize_text(database[student]['street']))
            pdf.text(15, 265, sanitize_text(f"{database[student]['city']}, {database[student]['state']} {database[student]['zip']}"))

            log_communication(
                student_id = database[student]['sr_id'],
                communication_method_id = '15' if database[student]['home_language'] == '113' else '17',
                communication_type_id = '2',
                staff_member_id = '11690',
                school_id = school_info[school]['sr_id'],
                contact_person = 'Parent/Guardian letter',
                comments = '10+ AU Letter',
                sandbox=True if test_mode else False
            )

    pdf_dir = os.path.join(base_dir, "pdf")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"{school}_{today_yyyy_mm_dd}_attendance_letter.pdf")
    print(f"[DEBUG] Writing PDF to: {pdf_path}")
    print(f"[DEBUG] Directory exists: {os.path.isdir(pdf_dir)}")
    print(f"[DEBUG] Directory contents: {os.listdir(pdf_dir)}")
    pdf.output(pdf_path)
    if test_mode:
        test_recipient = 'tophermckee@gmail.com'
        real_recipient = school_info[school]['attendance_letter_recipient']

        send_email(
            recipient=test_recipient,
            text_body='Good morning,\n\nThe following letters have already been logged in Schoolrunner for you. All you need to do is fold, stuff, stamp, and send them out!\n\n- The CA Data Robot 🤖',
            subject_line=f'TEST TO {real_recipient}: {school} Attendance Letters {today_yyyy_mm_dd}',
            attachment=pdf_path,
        )

        upload_basic(
            drive_name=f"{school}_{today_yyyy_mm_dd}_attendance_letter.pdf",
            local_path=pdf_path,
            mimetype='application/pdf',
            folder_id='1KzBEJAhcn5oFktHomopbhmx3FcDi2gT4'
        )
    else:
        send_email(
            recipient=school_info[school]['attendance_letter_recipient'],
            text_body='Good morning,\n\nThe following letters have already been logged in Schoolrunner for you. All you need to do is fold, stuff, stamp, and send them out!\n\n- The CA Data Robot 🤖',
            subject_line=f'{school} Attendance Letters {today_yyyy_mm_dd}',
            attachment=pdf_path,
            cc="shogarty@collegiateacademies.org,klambrecht@collegiateacademies.org,afelter@collegiateacademies.org"
        )

        upload_basic(
            drive_name=f"{school}_{today_yyyy_mm_dd}_attendance_letter.pdf",
            local_path=pdf_path,
            mimetype='application/pdf',
            folder_id='1KzBEJAhcn5oFktHomopbhmx3FcDi2gT4'
        )

def parse_bool(val):
    if isinstance(val, bool):
        return val
    if val.lower() in ("true", "1", "yes", "y"): return True
    if val.lower() in ("false", "0", "no", "n"): return False
    raise ValueError(f"Cannot parse boolean value from '{val}'")

def is_date_string(s):
    import re
    return bool(re.match(r"\d{4}-\d{2}-\d{2}", s))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python attendance_letters.py <school> <semester|year|YYYY-MM-DD> [test] [test_date]")
        print("Example: python attendance_letters.py ASA semester")
        print("Example: python attendance_letters.py OA year test 2025-03-15")
        print("Example: python attendance_letters.py OA 2025-01-01")
        sys.exit(1)
    school = sys.argv[1]
    term_or_date = sys.argv[2]
    test_mode = False
    test_date = None
    if len(sys.argv) > 3 and sys.argv[3].lower() == 'test':
        test_mode = True
        if len(sys.argv) > 4:
            test_date = sys.argv[4]
    if term_or_date.lower() in ("semester", "year"):
        start_date = return_term_start_date(term_or_date.lower(), school)
    elif is_date_string(term_or_date):
        start_date = term_or_date
    else:
        print("Second argument must be 'semester', 'year', or a date in YYYY-MM-DD format.")
        sys.exit(1)
    try:
        generate_attendance_letters(
            school=school,
            start_date=start_date,
            test_mode=test_mode,
            test_date=test_date
        )
    except Exception as error:
        logging.error(f"Error for {school} Attendance letters -- {error}", exc_info=True)
