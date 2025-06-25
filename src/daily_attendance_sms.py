from util import *

def daily_attendance_sms(school_name, test_date=None):
    """
    Sends daily attendance SMS to all students who are absent for a given school on a specific date.
    
    - Checks if the given date (or today, if not provided) is a school day using today_is_a_school_day().
    - If not a school day, exits (today_is_a_school_day logs this already).
    - In test mode, you can provide a test_date (YYYY-MM-DD string or datetime.date).
    - Creates a CSV file with the SIS IDs of absent students for that date (using sr_api_pull).
    - Emails the CSV to the school's daily_attendance_sms recipient (or tophermckee@gmail.com in test mode), with a dynamic HTML body.
    - Sends SMS notifications (placeholder for actual SMS logic).
    
    Args:
        school_name (str): The name of the school.
        test_date (str or datetime.date, optional): The date to check attendance for. If None, uses today.
    """
    # Translate school name to school id and get recipient
    try:
        school_info_entry = school_info[school_name]
        school_id = school_info_entry['sr_id']
        recipient = school_info_entry.get('daily_attendance_sms', None)
        logging.info(f"Translated school_name '{school_name}' to school_id '{school_id}' using school_info.")
    except KeyError:
        logging.error(f"School name '{school_name}' not found in school_info. Exiting.")
        return

    # Determine the date to use
    if test_date is not None:
        logging.info(f"Test mode enabled. Using test_date: {test_date}")
        if isinstance(test_date, str):
            date_obj = datetime.datetime.strptime(test_date, '%Y-%m-%d').date()
        else:
            date_obj = test_date
        is_test = True
    else:
        date_obj = datetime.date.today()
        logging.info(f"No test_date provided. Using today's date: {date_obj}")
        is_test = False

    # Only check if it's a school day if not in test mode
    if not is_test:
        logging.info(f"Checking if {date_obj} is a school day for {school_name} (school_id: {school_id})...")
        if not today_is_a_school_day(school_name, school_id, print_response=True):
            logging.info(f"{date_obj} is not a school day for {school_name}. Exiting.")
            return
        logging.info(f"{date_obj} is a school day for {school_name}.")
    else:
        logging.info(f"Test mode: Skipping school day check for {date_obj}.")

    logging.info(f"Retrieving absences for {school_name} (school_id: {school_id}) on {date_obj} using sr_api_pull...")

    # Use sr_api_pull to get absences for the date and school
    date_str = date_obj.strftime('%Y-%m-%d')
    parameters = {
        'min_date': date_str,
        'max_date': date_str,
        'active': '1',
        'school_ids': school_id,
        'out_of_school_only': '1',
        'expand': 'absence_type, student'
    }
    absences = sr_api_pull(
        search_key='absences',
        parameters=parameters
    )
    # Extract SIS IDs from absences
    sis_ids = [a['student'].get('sis_id') for a in absences if a.get('student') and a['student'].get('sis_id')] if absences else []
    logging.info(f"Absent student SIS IDs to be written: {sis_ids}")

    # Choose output directory based on OS
    if sys.platform == 'darwin':
        output_dir = '/Users/tophermckee/cadata/attendance_outputs/'
        html_path = '/Users/tophermckee/cadata/html/daily_attendance_sms.html'
    else:
        output_dir = '/home/tophermckee/cadata/attendance_outputs/'
        html_path = '/home/tophermckee/cadata/html/daily_attendance_sms.html'
    os.makedirs(output_dir, exist_ok=True)

    # Write SIS IDs to CSV
    csv_filename = f"absent_students_{school_name}_{date_obj}.csv"
    csv_path = os.path.join(output_dir, csv_filename)
    logging.info(f"Writing absent student SIS IDs to CSV file: {csv_path}")
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['sis_id'])
        for sid in sis_ids:
            writer.writerow([sid])
    logging.info(f"Absent student SIS IDs written to {csv_path}")

    # Prepare email
    if is_test:
        real_recipient = recipient or 'unknown'
        recipient = 'tophermckee@gmail.com'
        subject = f"Daily Attendance SMS for {school_name} on {date_obj} (test: {real_recipient})"
    else:
        subject = f"Daily Attendance SMS for {school_name} on {date_obj}"

    # Prepare HTML body
    try:
        with open(html_path, 'r') as f:
            html_body = f.read()
        html_body = html_body.replace('{{ date }}', str(date_obj)).replace('{{ school_name }}', school_name)
    except Exception as e:
        logging.error(f"Failed to read or process HTML template: {e}")
        html_body = f"Daily Attendance SMS for {school_name} on {date_obj}"

    # Send email
    logging.info(f"Sending email to {recipient} with subject '{subject}' and attachment '{csv_path}'...")
    send_email(
        recipient=recipient,
        subject_line=subject,
        html_body=html_body,
        attachment=csv_path
    )
    logging.info(f"Email sent to {recipient}.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python daily_attendance_sms.py <school_name> [test_date]")
        sys.exit(1)
    school_name = sys.argv[1]
    test_date = sys.argv[2] if len(sys.argv) > 2 else None
    daily_attendance_sms(school_name, test_date)