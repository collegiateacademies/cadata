# Daily Attendance Emails: Overview, Schedule, and Process

## What Are Daily Attendance Emails?

Daily attendance emails are automated summaries sent to each school's designated attendance contact. These emails provide a snapshot of student attendance for the current day, including attendance rates by grade and lists of students who are absent.

## How Do Daily Attendance Emails Work?

- **Data Collection:** The process pulls student and absence data from Schoolrunner via its API.
- **Attendance Calculation:** For each grade, it calculates the attendance rate and lists students who are absent (out-of-school absences).
- **Email Generation:** An HTML email is generated with attendance rates and absent student names, and sent to the school's attendance contact.

## When Do Daily Attendance Emails Run?

Daily attendance emails are scheduled to run automatically via cron jobs for each school, twice per day (typically at 11:00 AM and 3:00 PM, Monday through Friday).

### Schedule by School

| School | Script | Cron Schedule (Central Time) | Recipient |
|--------|--------|------------------------------|-----------|
| ASA    | `asa_daily_attendance_email.py` | Mon-Fri at 11:00 AM & 3:00 PM | `attendance_letter_recipient` in config |
| LCA    | `lca_daily_attendance_email.py` | Mon-Fri at 11:00 AM & 3:00 PM | `attendance_letter_recipient` in config |
| WLC    | `wlc_daily_attendance_email.py` | Mon-Fri at 11:00 AM & 3:00 PM | `attendance_letter_recipient` in config |
| GWC    | `gwc_daily_attendance_email.py` | Mon-Fri at 11:00 AM & 3:00 PM | `attendance_letter_recipient` in config |
| CBR    | `cbr_daily_attendance_email.py` | Mon-Fri at 11:00 AM & 3:00 PM | `attendance_letter_recipient` in config |
| OA     | `oa_daily_attendance_email.py`  | Mon-Fri at 11:00 AM & 3:00 PM | `attendance_letter_recipient` in config |

**Note:** All times are in America/Chicago timezone as set by `CRON_TZ=America/Chicago` in the crontab.

### Example Crontab Entries

```
0     11,15 	*	* 	1-5   cd /home/data_admin/cadata/triggers && /usr/bin/python3 lca_daily_attendance_email.py
0     11,15 	*	* 	1-5   cd /home/data_admin/cadata/triggers && /usr/bin/python3 gwc_daily_attendance_email.py
0     11,15 	*	* 	1-5   cd /home/data_admin/cadata/triggers && /usr/bin/python3 asa_daily_attendance_email.py
0     11,15 	*	* 	1-5   cd /home/data_admin/cadata/triggers && /usr/bin/python3 wlc_daily_attendance_email.py
0     11,15 	*	* 	1-5   cd /home/data_admin/cadata/triggers && /usr/bin/python3  oa_daily_attendance_email.py
0     11,15 	*	* 	1-5   cd /home/data_admin/cadata/triggers && /usr/bin/python3 cbr_daily_attendance_email.py
```

## How Are Daily Attendance Emails Triggered?

- **Automated:** The process is fully automated via cron. No manual intervention is required.
- **Script Execution:** Each script imports the main logic and calls `daily_attendance_email(school)`.
- **Conditional Sending:** Before sending, the script checks if today is a school day for the given school using the `today_is_a_school_day()` function, which queries the Schoolrunner calendar for the current date and school. If today is not a school day, no email is sent.

## From Which Email Address Are Emails Sent?

- **All daily attendance emails are sent from `data@collegiateacademies.org`.**

## Does This Process Run on Non-School Days?

- **No.** The process checks if today is a school day for the specific school by querying the Schoolrunner calendar API for the current date and school. If the calendar indicates that the school is not in session, the script exits and does not send an email. There are no hard-coded dates or semester checks; the check is dynamic and school-specific.

## From Where Does This Process Get Its Data?

- **Student and absence data are pulled from Schoolrunner via its API.**
    - Students: `/api/v1/students` endpoint, filtered by school and active status.
    - Absences: `/api/v1/absences` endpoint, filtered by school, active status, and current date.
    - The process uses the Schoolrunner calendar API to determine if today is a school day.

## Summary

- **Emails sent from:** `data@collegiateacademies.org`
- **Runs on non-school days?** No; checks Schoolrunner calendar dynamically per school.
- **Data source:** Schoolrunner API (students, absences, calendar).
- **Trigger:** Automated via cron jobs, twice daily per school.

---

*Please contact tophermckee@gmail.com for any additional questions.*
