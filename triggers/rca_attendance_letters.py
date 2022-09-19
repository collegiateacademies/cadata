import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    generate_attendance_letters('RCA', '2022-08-08', repeated_letters=True)