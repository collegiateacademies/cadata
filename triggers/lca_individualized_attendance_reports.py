import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    individualized_attendance_reports(
        school = 'LCA',
        start_date = return_term_start_date('semester', 'LCA')
    )