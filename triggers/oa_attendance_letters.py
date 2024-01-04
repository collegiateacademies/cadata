import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    try:
        generate_attendance_letters(
            school = 'OA', 
            start_date = '2024-01-08',#return_term_start_date('year', 'OA'),
            repeated_letters = True
        )
    except Exception as error:
        logging.error(f"Error for OA Attendance letters -- {error}", exc_info=True)