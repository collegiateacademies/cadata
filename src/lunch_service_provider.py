from util import *
import sys

def get_most_recent_monday(ref_date=None):
    """Return the most recent Monday before or on ref_date (defaults to today)."""
    if ref_date is None:
        ref_date = datetime.date.today()
    return ref_date - datetime.timedelta(days=ref_date.weekday())

def attendance_report(
    start_date: datetime.date = None,
    end_date: datetime.date = None,
    school: str = '',
    test_mode: bool = False,
    test_date: datetime.date = None
) -> None:
    """
    Generates and emails an attendance report for a given school over a specified date range.

    Args:
        start_date (datetime.date): The start date for the attendance report (default: most recent Monday).
        end_date (datetime.date): The end date for the attendance report (default: last Sunday).
        school (str): The name of the school to generate the report for.
        test_mode (bool): If True, send the report only to tophermckee@gmail.com.
        test_date (datetime.date): If set, use this as the 'today' date for test runs.
    """
    # Set up dates
    if test_mode and test_date:
        today = test_date
    else:
        today = datetime.date.today()
    if start_date is None:
        start_date = get_most_recent_monday(today)
    if end_date is None:
        end_date = start_date + datetime.timedelta(days=6)

    # Set file paths based on OS
    if sys.platform == 'darwin':
        csv_path = f"/Users/tophermckee/cadata/logs/csv/{school.lower()}_attendance_report_{today.strftime('%Y-%m-%d')}.csv"
        html_path = "/Users/tophermckee/cadata/html/lunch_service_provider.html"
    elif sys.platform == 'linux':
        csv_path = f"/home/data_admin/cadata/logs/csv/{school.lower()}_attendance_report_{today.strftime('%Y-%m-%d')}.csv"
        html_path = "/home/data_admin/cadata/html/lunch_service_provider.html"

    # Only check for Monday if not in test mode
    if test_mode or today_is_monday():
        # Pull student data
        students = sr_api_pull(
            search_key = 'students',
            parameters = {
                'school_ids': school_info[school]['sr_id'],
                'expand': 'student_detail'
            }
        )

        # Pull absences data
        absences_list = sr_api_pull(
            search_key = 'absences',
            parameters = {
                'school_ids': school_info[school]['sr_id'],
                'active': '1',
                'out_of_school_only': '1',
                'min_date':  start_date.strftime('%Y-%m-%d'),
                'max_date': end_date.strftime('%Y-%m-%d'),
            }
        )

        # Pull calendar days data
        calendar_days = sr_api_pull(
            search_key = 'calendar-days',
            parameters = {
                'school_ids': school_info[school]['sr_id'],
                'active': '1',
                'min_date':  start_date.strftime('%Y-%m-%d'),
                'max_date': end_date.strftime('%Y-%m-%d'),
            }
        )

        table_data = ''

        # Write CSV and build HTML table
        with open(csv_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["date", "in session", "enrolled", "absent", "present"])
            for day in range(7):
                students_enrolled = 0
                absences = 0
                current_loop_date = start_date + datetime.timedelta(days=day)

                # Check if school is in session for the day
                for day_info in calendar_days:
                    if day_info['date'] == current_loop_date.strftime('%Y-%m-%d'):
                        in_session = day_info['in_session'] == '1'
                        break
                else:
                    in_session = False

                # Count enrolled students for the day
                for student in students:
                    if student['student_detail'] is None:
                        continue
                    student_entry_year  = int(student['student_detail']['entry_date'][0:4])
                    student_entry_month = int(student['student_detail']['entry_date'][5:7])
                    student_entry_day   = int(student['student_detail']['entry_date'][8:10])
                    student_entry_date  = datetime.date(student_entry_year, student_entry_month , student_entry_day)

                    student_exit_year  = int(student['student_detail']['exit_date'][0:4])
                    student_exit_month = int(student['student_detail']['exit_date'][5:7])
                    student_exit_day   = int(student['student_detail']['exit_date'][8:10])
                    student_exit_date  = datetime.date(student_exit_year, student_exit_month , student_exit_day)
                    
                    if student_entry_date <= current_loop_date and student_exit_date >= current_loop_date:
                        students_enrolled += 1

                # Count absences for the day
                for absence in absences_list:
                    if absence['date'] == current_loop_date.strftime('%Y-%m-%d'):
                        absences += 1
                
                # Write row to table and CSV
                if in_session:
                    table_data += f"<tr><td style='border: 1px solid black; border-collapse: collapse; padding: 10px; text-align: center;'>{current_loop_date.strftime('%a %b %d')}</td><td style='border: 1px solid black; border-collapse: collapse; padding: 10px; text-align: center;'>{students_enrolled}</td><td style='border: 1px solid black; border-collapse: collapse; padding: 10px; text-align: center;'>{absences}</td><td style='border: 1px solid black; border-collapse: collapse; padding: 10px; text-align: center;'>{students_enrolled-absences}</td></tr>"
                    writer.writerow([current_loop_date.strftime('%Y-%m-%d'), "true", students_enrolled, absences, students_enrolled-absences])
                else:
                    table_data += f"<tr><td style='border: 1px solid black; border-collapse: collapse; padding: 10px; text-align: center;'>{current_loop_date.strftime('%a %b %d')}</td><td style='border: 1px solid black; border-collapse: collapse; padding: 10px; text-align: center;' colspan='3'><span style='color: red'>SCHOOL NOT IN SESSION</span></td></tr>"
                    writer.writerow([current_loop_date.strftime('%Y-%m-%d'), "false", 0, 0, 0])

        # Read HTML template and insert table data
        with open(html_path, 'r') as file:
            html_email = file.read().replace('###table_data###', table_data).replace('###school###', school)

        # Send email with report
        if test_mode:
            recipient = 'tophermckee@gmail.com'
        else:
            recipient = 'afelter@collegiateacademies.org,kwelch@collegiateacademies.org,tess@schoolfoodsolutions.org,kaylee@schoolfoodsolutions.org,JPickel@collegiateacademies.org,ali@schoolfoodsolutions.org'
        send_email(
            recipient = recipient,
            subject_line = f'Attendance Report for {school}',
            html_body = html_email,
            sender_string = 'CA Service Provider Reports',
            attachment = csv_path
        )
    else:
        logging.info(f"No need to send email to service providers today. {today} is not a Monday.")

if __name__ == "__main__":
    # Usage: python lunch_service_provider.py SCHOOL [--test] [--test-date YYYY-MM-DD]
    # Example: python lunch_service_provider.py KAYLEE --test --test-date 2024-06-10
    school = None
    test_mode = False
    test_date = None
    for i, arg in enumerate(sys.argv[1:]):
        if arg == '--test':
            test_mode = True
        elif arg == '--test-date' and i+2 < len(sys.argv):
            try:
                test_date = datetime.datetime.strptime(sys.argv[i+2], '%Y-%m-%d').date()
            except Exception:
                print('Invalid test date format. Use YYYY-MM-DD.')
                sys.exit(1)
        elif not arg.startswith('--') and school is None:
            school = arg
    if not school:
        print("Usage: python lunch_service_provider.py SCHOOL [--test] [--test-date YYYY-MM-DD]")
        sys.exit(1)
    attendance_report(school=school, test_mode=test_mode, test_date=test_date)