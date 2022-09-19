import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    generate_attendance_letters('CBR', return_term_start_date('semester', 'CBR'), repeated_letters=True)