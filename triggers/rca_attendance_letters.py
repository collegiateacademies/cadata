import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    generate_attendance_letters('RCA', return_term_start_date('semester', 'RCA'), repeated_letters=True)