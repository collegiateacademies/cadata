import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    # upload_map_file()
    os.remove('AssessmentResults.csv')
    time.sleep(3)
    os.system("7z x ~/services_kit/report/bin/map_output/342339.zip")
    output = []
    with open('AssessmentResults.csv') as file:
        csv_reader = csv.reader(file)
        row = []
        for row in csv_reader:
            output.append(row)
    upload_basic(
        drive_name=f"AssessmentResults{datetime.datetime.now().strftime('%Y-%m-%d %I:%M')}.csv",
        local_path='AssessmentResults.csv',
        mimetype='text/csv',
        folder_id='147y1J5IEVkvMpYtxmTDFI9c1SziYwMXL'
    )