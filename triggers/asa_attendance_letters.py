import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    try:
        generate_attendance_letters(
            school = 'ASA',
            start_date = return_term_start_date('semester', 'ASA'),
            repeated_letters = True
        )
    except Exception as error:
        logging.error(f"Error for ASA Attendance letters -- {error}", exc_info=True)