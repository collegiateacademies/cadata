import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    individualized_attendance_reports(
        school = 'OA',
        start_date = return_term_start_date('year', 'OA')
    )