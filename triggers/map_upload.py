import sys
sys.path.append("..")
from src.main import *

"""
This script downloads a file using basic authentication from:
https://api.mapnwea.org/services/reporting/dex

Replace YOUR_USERNAME and YOUR_PASSWORD with your actual credentials.
"""

def download_file(url, username, password, output_filename):
    # Send a GET request with basic authentication
    response = requests.get(url, auth=(username, password))
    
    if response.status_code == 200:
        with open(output_filename, "wb") as file:
            file.write(response.content)
        logging.info(f"File downloaded successfully and saved as '{output_filename}'.")
    else:
        logging.error(f"Failed to download file. Status code: {response.status_code}", exc_info=True)

def main():

    # Remove old files
    try:
        os.remove('map_output.zip')
        logging.info("Old map_output.zip removed successfully.")
    except FileNotFoundError:
        logging.info("Old map_output.zip not found, continuing with the script.")

    # Replace these with your actual credentials
    username = credentials['map_username']
    password = credentials['map_password']
    
    # URL of the file to download
    url = "https://api.mapnwea.org/services/reporting/dex"
    
    # Name of the file to save locally
    output_filename = "map_output.zip"
    
    download_file(url, username, password, output_filename)

    # Choose the path based on your operating system using sys.platform
    
    if sys.platform == 'linux':  # Linux
        map_output_path = '/home/data_admin/cadata/triggers/map_output.zip'
    elif sys.platform == 'darwin':  # macOS
        map_output_path = '/Users/tophermckee/cadata/triggers/map_output.zip'
    else:
        raise Exception("Unsupported operating system")
    
    # Remove old files
    try:
        os.remove('AssessmentResults.csv')
        os.remove('StudentsBySchool.csv')
        logging.info("Old csv files removed successfully.")
    except FileNotFoundError:
        logging.info("CSV files not found, continuing with the script.")
    
    logging.info("Waiting for 3 seconds before unzipping the file...")
    time.sleep(3)
    
    # Unzip the downloaded file
    logging.info(f"Unzipping the file '{map_output_path}'...")
    try:
        os.system(f"7z x {map_output_path}")
    except Exception as err:
        logging.error(f"Error unzipping the file: {err}", exc_info=True)

    # Upload the unzipped files to Google Drive
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

if __name__ == '__main__':
    main()