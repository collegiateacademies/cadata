import sys
sys.path.append("..")
from src.util import *

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
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
            "school_ids": school_codes[school],
            'expand': 'grade_level, student_detail' # student_attrs.student_attr_type
        }
    )

    absences = sr_api_pull(
        'absences',
        parameters = {
            'active': '1',
            'school_ids': 15,
            'min_date': min_date,
            'max_date': today_yyyy_mm_dd,
            # 'out_of_school_only': '1',                        # pull everything because you need to include tardies
            'expand': 'absence_type, student.grade_level'
        }
    )