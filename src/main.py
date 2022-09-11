import sys
sys.path.append("..")
from src.util import *

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(asctime)s -- %(filename)s on line %(lineno)s\n\tFunction name: %(funcName)s\n\tMessage: %(message)s\n",
    datefmt='%B-%d-%Y %H:%M:%S',
    filename=f"../logs/{Path(__file__).stem}.log",
    filemode='w'
)

def generate_attendance_letters(school: string, min_date: string, repeated_letters: bool) -> None:
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
            }
    
    for absence in absence_list:
        if absence['absence_type']['code'] == 'AU' and absence['student']['active'] == '1' and absence['student']['school_id'] == school_info[school]['sr_id']:
            database[absence['student_id']]['au'] += 1
        elif absence['absence_type']['code'] == 'TU' and absence['student']['active'] == '1' and absence['student']['school_id'] == school_info[school]['sr_id']:
            database[absence['student_id']]['tu'] += 1

    ##########################################################################
    ########                PDF GENERATION STARTS HERE              ##########
    ##########################################################################

    class MyFPDF(FPDF, HTMLMixin):
        pass
    pdf = MyFPDF(orientation='P', unit='mm', format='Letter')
    pdf.set_margin(5)
    pdf.set_font('helvetica', size=10)

    for student in database:
        if database[student]['au'] >= 3:
            pdf.add_page()
            pdf.multi_cell(
                w=0,
                h=5,
                new_x="LMARGIN",
                new_y="NEXT",
                txt=f"{database[student]['first_name']} {database[student]['last_name']} - {datetime.datetime.today().strftime('%A, %B %-d, %Y')}",
                markdown=True
            )
            pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
            for block in attendance_letter3_blocks_page1:
                if 'bullet_level' in block:
                    if block['bullet_level'] == 1:
                        pdf.set_x(10)
                        pdf.multi_cell(w=5, h=5, txt="\x95", new_x="END", new_y="LAST")
                        pdf.multi_cell(
                            w=0,
                            h=5,
                            new_x="LMARGIN",
                            new_y="NEXT",
                            txt=block['text'].replace("###school_name###", school_info[school]['long_name']),
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
                            txt=block['text'].replace("###school_name###", school_info[school]['long_name']),
                            markdown=True
                        )
                        pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
                else:
                    pdf.multi_cell(
                        w=0,
                        h=5,
                        new_x="LMARGIN",
                        new_y="NEXT",
                        txt=block['text'].replace("###school_name###", school_info[school]['long_name']),
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
                            txt=block['text'].replace("###school_name###", school_info[school]['long_name']),
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
                            txt=block['text'].replace("###school_name###", school_info[school]['long_name']),
                            markdown=True
                        )
                        pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
                else:
                    pdf.multi_cell(
                        w=0,
                        h=5,
                        new_x="LMARGIN",
                        new_y="NEXT",
                        txt=block['text'].replace("###school_name###", school_info[school]['long_name']),
                        markdown=True
                    )
                    pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
            pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='Sincerely,')
            pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt=school_info[school]['principal'])

            pdf.text(15, 250, f"Parents/Guardians of {database[student]['first_name']} {database[student]['last_name']}")
            pdf.text(15, 255, database[student]['street'])
            pdf.text(15, 260, f"{database[student]['city']}, {database[student]['state']} {database[student]['zip']}")

            log_communication(
                student_id = database[student]['sr_id'],
                communication_method_id = '17',
                communication_type_id = '2',
                staff_member_id = '11690',
                school_id = school_info[school]['sr_id'],
                contact_person = 'Parent/Guardian letter',
                comments = '3+ AU Letter'
            )

    pdf.output(f"../pdf/{school}_{today_yyyy_mm_dd}_attendance_letter.pdf")

    # TODO get email addresses from felter (attendance contacts)
    # TODO confirm fax numbers
    # TODO confirm who they want things logged as (data admin right?)
    # TODO confirm whether or not people want repeat letters functionality
    # TODO add add sr log