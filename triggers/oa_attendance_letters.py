import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    generate_attendance_letters('OA', '2022-08-08', repeated_letters=True)