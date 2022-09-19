import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    try:
        generate_attendance_letters(
            school = 'CBR',
            start_date = return_term_start_date('semester', 'CBR'),
            repeated_letters = True
        )
    except Exception as error:
        logging.error(f"Error for CBR Attendance letters -- {error}", exc_info=True)