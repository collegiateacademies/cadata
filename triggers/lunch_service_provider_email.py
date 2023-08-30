import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    attendance_report(school='ASA')
    attendance_report(school='CBR')
    attendance_report(school='GWC')
    attendance_report(school='LCA')
    attendance_report(school='OA')
    attendance_report(school='WLC')