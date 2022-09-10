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
    # database = {}

    # student_list = sr_api_pull(
    #     "students",
    #     {
    #         "active": "1",
    #         "school_ids": school_codes[school],
    #         'expand': 'grade_level, student_detail' # student_attrs.student_attr_type
    #     }
    # )

    # absences = sr_api_pull(
    #     'absences',
    #     parameters = {
    #         'active': '1',
    #         'school_ids': 15,
    #         'min_date': min_date,
    #         'max_date': today_yyyy_mm_dd,
    #         # 'out_of_school_only': '1',                        # pull everything because you need to include tardies
    #         'expand': 'absence_type, student.grade_level'
    #     }
    # )
    class MyFPDF(FPDF, HTMLMixin):
        pass

    pdf = MyFPDF(orientation='P', unit='mm', format='Letter')
    pdf.set_margin(5)
    pdf.add_page()
    pdf.set_font('helvetica', size=10)

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
                    txt=block['text'],
                    markdown=True
                )
            elif block['bullet_level'] == 2:
                pdf.set_x(20)
                pdf.multi_cell(w=5, h=5, txt="\x95", new_x="END", new_y="LAST")
                pdf.multi_cell(
                    w=0,
                    h=5,
                    new_x="LMARGIN",
                    new_y="NEXT",
                    txt=block['text'],
                    markdown=True
                )
        else:
            pdf.multi_cell(
                w=0,
                h=5,
                new_x="LMARGIN",
                new_y="NEXT",
                txt=block['text'],
                markdown=True
            )
            pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
    
    pdf.add_page()

    data = (
        ("Scholar Attendance Summary", ""),
        ("Unexcused Absences", "15"),
        ("Unexcused Tardies", "15"),
    )
    line_height = pdf.font_size * 2.5
    col_width = pdf.epw / 3  # distribute content evenly
    for row in data:
        for datum in row:
            pdf.multi_cell(col_width, line_height, datum, border=1, new_x="RIGHT", new_y="TOP", max_line_height=pdf.font_size)
        pdf.ln(line_height)

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
                    txt=block['text'],
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
                    txt=block['text'],
                    markdown=True
                )
                pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')
        else:
            pdf.multi_cell(
                w=0,
                h=5,
                new_x="LMARGIN",
                new_y="NEXT",
                txt=block['text'],
                markdown=True
            )
            pdf.multi_cell(w=0, h=5, new_x="LMARGIN", new_y="NEXT", txt='')

    pdf.output("../pdf/attendance_letter.pdf")

if __name__ == '__main__':
    generate_attendance_letters('test', 'test', True)