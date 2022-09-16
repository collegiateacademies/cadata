import sys
sys.path.append("..")
from src.util import *

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s -- %(filename)s on line %(lineno)s\n\tFunction name: %(funcName)s\n\tMessage: %(message)s\n",
    datefmt='%B-%d-%Y %H:%M:%S',
    filename=f"../logs/{Path(__file__).stem}.log",
    filemode='w'
)

def generate_attendance_letters(school: str, min_date: str, repeated_letters: bool) -> None:
    
    if today_is_a_school_day(school, school_info[school]['sr_id']):
        pass
    else:
        return

    database = {}

    student_list = sr_api_pull(
        "students",
        {
            "active": "1",
            "school_ids": school_info[school]['sr_id'],
            'expand': 'grade_level, student_detail' # student_attrs.student_attr_type
        }
    )

    absence_list = sr_api_pull(
        'absences',
        parameters = {
            'active': '1',
            'school_ids': school_info[school]['sr_id'],
            'min_date': min_date,
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
            'min_date': min_date,
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
                'street': student['student_detail']['street'],
                'city': student['student_detail']['city'],
                'state': student['student_detail']['state'],
                'zip': student['student_detail']['zip'],
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
        if communication['student']['active'] == '1' and communication['communication_method']['name'] == "Letter" and communication['communication_type']['name'] == 'Attendance' and communication['comments'] == '3+ AU Letter':
            database[communication['student_id']]['3au_letters_logged'] += 1
        elif communication['student']['active'] == '1' and communication['communication_method']['name'] == "Letter" and communication['communication_type']['name'] == 'Attendance' and communication['comments'] == '5+ AU Letter':
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
                h=5,
                new_x="LMARGIN",
                new_y="NEXT",
                txt=f"{database[student]['first_name']} {database[student]['last_name']} - {datetime.datetime.today().strftime('%A, %B %-d, %Y')} (3 Absence Letter)",
                markdown=True
            )
            pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
            for block in attendance_letter_blocks_page1:
                if 'bullet_level' in block:
                    if block['bullet_level'] == 1:
                        pdf.set_x(10)
                        pdf.multi_cell(w=5, h=5, txt="\x95", new_x="END", new_y="LAST")
                        pdf.multi_cell(
                            w=0,
                            h=5,
                            new_x="LMARGIN",
                            new_y="NEXT",
                            txt=block['text']
                                .replace("###school_name###", school_info[school]['long_name'])
                                .replace('###school_phone###', school_info[school]['phone'])
                                .replace('###attendace_email###', school_info[school]['attendance_email'])
                                .replace('###fax_number###', school_info[school]['fax']),
                            markdown=True
                        )
                        pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
                    elif block['bullet_level'] == 2:
                        pdf.set_x(20)
                        pdf.multi_cell(w=5, h=5, txt="\x95", new_x="END", new_y="LAST")
                        pdf.multi_cell(
                            w=0,
                            h=5,
                            new_x="LMARGIN",
                            new_y="NEXT",
                            txt=block['text']
                                .replace("###school_name###", school_info[school]['long_name'])
                                .replace('###school_phone###', school_info[school]['phone'])
                                .replace('###attendace_email###', school_info[school]['attendance_email'])
                                .replace('###fax_number###', school_info[school]['fax']),
                            markdown=True
                        )
                        pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
                else:
                    pdf.multi_cell(
                        w=0,
                        h=5,
                        new_x="LMARGIN",
                        new_y="NEXT",
                        txt=block['text']
                                .replace("###school_name###", school_info[school]['long_name'])
                                .replace('###school_phone###', school_info[school]['phone'])
                                .replace('###attendace_email###', school_info[school]['attendance_email'])
                                .replace('###fax_number###', school_info[school]['fax']),
                        markdown=True
                    )
                    pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
            
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

            pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')

            for block in attendance_letter3_blocks_page2:
                if 'bullet_level' in block:
                    if block['bullet_level'] == 1:
                        pdf.set_x(10)
                        pdf.multi_cell(w=5, h=5, txt="\x95", new_x="END", new_y="LAST")
                        pdf.multi_cell(
                            w=0,
                            h=5,
                            new_x="LMARGIN",
                            new_y="NEXT",
                            txt=block['text']
                                .replace("###school_name###", school_info[school]['long_name'])
                                .replace('###school_phone###', school_info[school]['phone'])
                                .replace('###attendace_email###', school_info[school]['attendance_email'])
                                .replace('###fax_number###', school_info[school]['fax']),
                            markdown=True
                        )
                        pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
                    elif block['bullet_level'] == 2:
                        pdf.set_x(20)
                        pdf.multi_cell(w=5, h=5, txt="\x95", new_x="END", new_y="LAST")
                        pdf.multi_cell(
                            w=0,
                            h=5,
                            new_x="LMARGIN",
                            new_y="NEXT",
                            txt=block['text']
                                .replace("###school_name###", school_info[school]['long_name'])
                                .replace('###school_phone###', school_info[school]['phone'])
                                .replace('###attendace_email###', school_info[school]['attendance_email'])
                                .replace('###fax_number###', school_info[school]['fax']),
                            markdown=True
                        )
                        pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
                else:
                    pdf.multi_cell(
                        w=0,
                        h=5,
                        new_x="LMARGIN",
                        new_y="NEXT",
                        txt=block['text']
                                .replace("###school_name###", school_info[school]['long_name'])
                                .replace('###school_phone###', school_info[school]['phone'])
                                .replace('###attendace_email###', school_info[school]['attendance_email'])
                                .replace('###fax_number###', school_info[school]['fax']),
                        markdown=True
                    )
                    pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
            pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='Sincerely,')
            pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt=school_info[school]['principal'])

            pdf.text(15, 250, f"Parents/Guardians of {database[student]['first_name']} {database[student]['last_name']}")
            pdf.text(15, 255, database[student]['street'])
            pdf.text(15, 260, f"{database[student]['city']}, {database[student]['state']} {database[student]['zip']}")

            # log_communication(
            #     student_id = database[student]['sr_id'],
            #     communication_method_id = '17',
            #     communication_type_id = '2',
            #     staff_member_id = '11690',
            #     school_id = school_info[school]['sr_id'],
            #     contact_person = 'Parent/Guardian letter',
            #     comments = '3+ AU Letter',
            #     sandbox=True
            # )
        
        if database[student]['au'] >= 5 and database[student]['5au_letters_logged'] == 0:
            pdf.add_page()
            pdf.image(f"../assets/{school.lower()}_letterhead.png", x=125, y=5, h=8)
            pdf.multi_cell(
                w=0,
                h=5,
                new_x="LMARGIN",
                new_y="NEXT",
                txt=f"{database[student]['first_name']} {database[student]['last_name']} - {datetime.datetime.today().strftime('%A, %B %-d, %Y')} (5 Absence Letter)",
                markdown=True
            )
            pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
            for block in attendance_letter_blocks_page1:
                if 'bullet_level' in block:
                    if block['bullet_level'] == 1:
                        pdf.set_x(10)
                        pdf.multi_cell(w=5, h=5, txt="\x95", new_x="END", new_y="LAST")
                        pdf.multi_cell(
                            w=0,
                            h=5,
                            new_x="LMARGIN",
                            new_y="NEXT",
                            txt=block['text']
                                .replace("###school_name###", school_info[school]['long_name'])
                                .replace('###school_phone###', school_info[school]['phone'])
                                .replace('###attendace_email###', school_info[school]['attendance_email'])
                                .replace('###fax_number###', school_info[school]['fax']),
                            markdown=True
                        )
                        pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
                    elif block['bullet_level'] == 2:
                        pdf.set_x(20)
                        pdf.multi_cell(w=5, h=5, txt="\x95", new_x="END", new_y="LAST")
                        pdf.multi_cell(
                            w=0,
                            h=5,
                            new_x="LMARGIN",
                            new_y="NEXT",
                            txt=block['text']
                                .replace("###school_name###", school_info[school]['long_name'])
                                .replace('###school_phone###', school_info[school]['phone'])
                                .replace('###attendace_email###', school_info[school]['attendance_email'])
                                .replace('###fax_number###', school_info[school]['fax']),
                            markdown=True
                        )
                        pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
                else:
                    pdf.multi_cell(
                        w=0,
                        h=5,
                        new_x="LMARGIN",
                        new_y="NEXT",
                        txt=block['text']
                                .replace("###school_name###", school_info[school]['long_name'])
                                .replace('###school_phone###', school_info[school]['phone'])
                                .replace('###attendace_email###', school_info[school]['attendance_email'])
                                .replace('###fax_number###', school_info[school]['fax']),
                        markdown=True
                    )
                    pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
            
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

            pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')

            for block in attendance_letter5_blocks_page2:
                if 'bullet_level' in block:
                    if block['bullet_level'] == 1:
                        pdf.set_x(10)
                        pdf.multi_cell(w=5, h=5, txt="\x95", new_x="END", new_y="LAST")
                        pdf.multi_cell(
                            w=0,
                            h=5,
                            new_x="LMARGIN",
                            new_y="NEXT",
                            txt=block['text']
                                .replace("###school_name###", school_info[school]['long_name'])
                                .replace('###school_phone###', school_info[school]['phone'])
                                .replace('###attendace_email###', school_info[school]['attendance_email'])
                                .replace('###fax_number###', school_info[school]['fax']),
                            markdown=True
                        )
                        pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
                    elif block['bullet_level'] == 2:
                        pdf.set_x(20)
                        pdf.multi_cell(w=5, h=5, txt="\x95", new_x="END", new_y="LAST")
                        pdf.multi_cell(
                            w=0,
                            h=5,
                            new_x="LMARGIN",
                            new_y="NEXT",
                            txt=block['text']
                                .replace("###school_name###", school_info[school]['long_name'])
                                .replace('###school_phone###', school_info[school]['phone'])
                                .replace('###attendace_email###', school_info[school]['attendance_email'])
                                .replace('###fax_number###', school_info[school]['fax']),
                            markdown=True
                        )
                        pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
                else:
                    pdf.multi_cell(
                        w=0,
                        h=5,
                        new_x="LMARGIN",
                        new_y="NEXT",
                        txt=block['text']
                                .replace("###school_name###", school_info[school]['long_name'])
                                .replace('###school_phone###', school_info[school]['phone'])
                                .replace('###attendace_email###', school_info[school]['attendance_email'])
                                .replace('###fax_number###', school_info[school]['fax']),
                        markdown=True
                    )
                    pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
            pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='Sincerely,')
            pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt=school_info[school]['principal'])

            pdf.text(15, 250, f"Parents/Guardians of {database[student]['first_name']} {database[student]['last_name']}")
            pdf.text(15, 255, database[student]['street'])
            pdf.text(15, 260, f"{database[student]['city']}, {database[student]['state']} {database[student]['zip']}")

            # log_communication(
            #     student_id = database[student]['sr_id'],
            #     communication_method_id = '17',
            #     communication_type_id = '2',
            #     staff_member_id = '11690',
            #     school_id = school_info[school]['sr_id'],
            #     contact_person = 'Parent/Guardian letter',
            #     comments = '5+ AU Letter',
            #     sandbox=True
            # )

    pdf.output(f"../pdf/{school}_{today_yyyy_mm_dd}_attendance_letter.pdf")

def daily_attendance_email(school: str) -> None:
    database = {
        '9': {
            'total_students': 0,
            'total_out_of_school': 0,
            'names_list': ''
        },
        '10': {
            'total_students': 0,
            'total_out_of_school': 0,
            'names_list': ''
        },
        '11': {
            'total_students': 0,
            'total_out_of_school': 0,
            'names_list': ''
        },
        '12': {
            'total_students': 0,
            'total_out_of_school': 0,
            'names_list': ''
        },
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
        if student['grade_level']['order_key'] in database:
            database[student['grade_level']['order_key']]['total_students'] += 1
            database['totals']['students'] += 1

    absence_list = sr_api_pull(
        search_key='absences',
        parameters={
            'min_date': '2022-09-09',# today_yyyy_mm_dd,
            'max_date': '2022-09-09',# today_yyyy_mm_dd,
            'active': '1',
            'school_ids': school_info[school]['sr_id'],
            'out_of_school_only': '1',
            'expand': 'absence_type, student.grade_level, student.student_attrs.student_attr_type'
        }
    )

    for absence in absence_list:
        if absence['student']['grade_level']['order_key'] in database:
            database[absence['student']['grade_level']['order_key']]['total_out_of_school'] += 1
            database[absence['student']['grade_level']['order_key']]['names_list'] += f"{absence['student']['display_name']} - {extract_sr_student_attribute(absence['student']['student_attrs'], 'Advisor')} - ({absence['absence_type']['code']})<br>"
            database['totals']['absences'] += 1

    with open('../logs/json/testingtesting.json', 'w') as file:
        json.dump(database, file, indent=4)

    with open('../html/daily_attendance.html', 'r') as file:
        html_email = file.read()
    
    send_email(
        recipient='tophermckee@gmail.com',
        subject_line='hey there',
        html_body=html_email
            .replace('###9th_list###', database['9']['names_list'])
            .replace('###10th_list###', database['10']['names_list'])
            .replace('###11th_list###', database['11']['names_list'])
            .replace('###12th_list###', database['12']['names_list'])
            .replace( '###total###',      str( round((int(database['totals']['students'])   - int(database['totals']['absences']))        / int(database['totals']['students'])   * 100 , 2)))
            .replace( '###9th_total###',  str( round((int(database['9']['total_students'])  - int(database['9']['total_out_of_school']))  / int(database['9']['total_students'])  * 100 , 2)))
            .replace( '###10th_total###', str( round((int(database['10']['total_students']) - int(database['10']['total_out_of_school'])) / int(database['10']['total_students']) * 100 , 2)))
            .replace( '###11th_total###', str( round((int(database['11']['total_students']) - int(database['11']['total_out_of_school'])) / int(database['11']['total_students']) * 100 , 2)))
            .replace( '###12th_total###', str( round((int(database['12']['total_students']) - int(database['12']['total_out_of_school'])) / int(database['12']['total_students']) * 100 , 2)))
    )