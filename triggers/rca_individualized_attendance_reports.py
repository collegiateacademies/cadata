import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    individualized_attendance_reports(
        school = 'RCA',
        start_date = return_term_start_date('semester', 'RCA')
    )