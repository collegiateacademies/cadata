import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    try:
        generate_attendance_letters(
            school = 'RCA',
            start_date = return_term_start_date('semester', 'RCA'),
            repeated_letters = True
        )
    except Exception as error:
        logging.error(f"Error for RCA Attendance letters -- {error}", exc_info=True)