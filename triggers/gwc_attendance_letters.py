import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    generate_attendance_letters('GWC', return_term_start_date('semester', 'GWC'), repeated_letters=True)