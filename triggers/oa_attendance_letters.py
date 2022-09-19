import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    generate_attendance_letters('OA', return_term_start_date('quarter', 'OA'), repeated_letters=True)