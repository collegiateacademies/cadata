import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    try:
        generate_attendance_letters(
            school = 'WLC',
            start_date = return_term_start_date('semester', 'WLC'),
            repeated_letters = True
        )
    except Exception as error:
        logging.error(f"Error for WLC Attendance letters -- {error}", exc_info=True)