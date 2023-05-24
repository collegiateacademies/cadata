import sys
sys.path.append("..")
from src.main import *

if __name__ == '__main__':
    # upload_map_file()
    try:
        upload_basic(
            drive_name=f"AssessmentResults{datetime.datetime.now().strftime('%Y-%m-%d %I:%M')}.csv",
            local_path='AssessmentResults.csv',
            mimetype='text/csv',
            folder_id='147y1J5IEVkvMpYtxmTDFI9c1SziYwMXL'
    )
    except:
        pass