import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    individualized_attendance_reports(
        school = 'OA',
        start_date = '2026-01-05', # return_term_start_date('year', 'OA') UPDATED BY TOPHER ON 2026-01-04
    )
