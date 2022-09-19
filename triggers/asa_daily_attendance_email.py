import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    generate_attendance_letters('ASA', '2022-08-01', repeated_letters=True)