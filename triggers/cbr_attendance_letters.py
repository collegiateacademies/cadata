import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    generate_attendance_letters('CBR', '2022-08-03', repeated_letters=True)