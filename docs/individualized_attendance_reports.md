# Individualized Attendance Reports: Overview, Schedule, and Process

## What Are Individualized Attendance Reports?

Individualized attendance reports are automated emails sent to students (and their primary contacts) summarizing their attendance for the current semester. These reports include a table of absences, the number of unexcused absences, and information about attendance policies and seat time recovery.

## How Do Individualized Attendance Reports Work?

- **Data Collection:** The process pulls student and absence data from Schoolrunner via its API.
- **Report Generation:** For each student, it generates an HTML email with a table of absences, the count of unexcused absences, and policy information.
- **Email Delivery:** The report is emailed to the student and CC'd to their primary contact.

## When Do Individualized Attendance Reports Run?

Individualized attendance reports are scheduled to run automatically via cron jobs for each school, once per week in the afternoon. Each school has a specific day and time.

### Schedule by School

| School | Script | Cron Schedule (Central Time) | Day/Time |
|--------|--------|------------------------------|----------|
| LCA    | `lca_individualized_attendance_reports.py` | Mondays at 4:00 PM | Monday 4:00 PM |
| GWC    | `gwc_individualized_attendance_reports.py` | Tuesdays at 4:00 PM | Tuesday 4:00 PM |
| ASA    | `asa_individualized_attendance_reports.py` | Wednesdays at 4:00 PM | Wednesday 4:00 PM |
| WLC    | `wlc_individualized_attendance_reports.py` | Thursdays at 4:00 PM | Thursday 4:00 PM |
| OA     | `oa_individualized_attendance_reports.py`  | Fridays at 4:00 PM | Friday 4:00 PM |
| CBR    | `cbr_individualized_attendance_reports.py` | Fridays at 4:30 PM | Friday 4:30 PM |

**Note:** All times are in America/Chicago timezone as set by `CRON_TZ=America/Chicago` in the crontab.

### Example Crontab Entries

```
0     16        *       *        1    cd /home/data_admin/cadata/triggers && /usr/bin/python3 lca_individualized_attendance_reports.py
0     16        *       *        2    cd /home/data_admin/cadata/triggers && /usr/bin/python3 gwc_individualized_attendance_reports.py
0     16        *       *        3    cd /home/data_admin/cadata/triggers && /usr/bin/python3 asa_individualized_attendance_reports.py
0     16        *       *        4    cd /home/data_admin/cadata/triggers && /usr/bin/python3 wlc_individualized_attendance_reports.py
0     16        *       *        5    cd /home/data_admin/cadata/triggers && /usr/bin/python3  oa_individualized_attendance_reports.py
30    16        *       *        5    cd /home/data_admin/cadata/triggers && /usr/bin/python3 cbr_individualized_attendance_reports.py
```

## How Are Individualized Attendance Reports Triggered?

- **Automated:** The process is fully automated via cron. No manual intervention is required.
- **Script Execution:** Each script imports the main logic and calls `individualized_attendance_reports(school, start_date)`.
- **Conditional Sending:** Before sending, the script checks if today is a school day for the given school using the `today_is_a_school_day()` function, which queries the Schoolrunner calendar for the current date and school. If today is not a school day, no emails are sent.

## From Which Email Address Are Emails Sent?

## From Which Email Address Are Emails Sent?

- **Individualized attendance reports are now sent from school-specific email addresses.**
    - For each school, the report is sent from that school's designated email address (e.g., `asa@collegiateacademies.org` for ASA, `gwc@collegiateacademies.org` for GWC, etc.).
    - For OA (Opportunities Academy), the report is sent from `data@collegiateacademies.org`.
- The `reply-to` address is set to the school's attendance email (e.g., `frontdesk@sciacademy.org` for ASA).

## Does This Process Run on Non-School Days?

- **No.** The process checks if today is a school day for the specific school by querying the Schoolrunner calendar API for the current date and school. If the calendar indicates that the school is not in session, the script exits and does not send any emails. There are no hard-coded dates or semester checks; the check is dynamic and school-specific.

## From Where Does This Process Get Its Data?

- **Student and absence data are pulled from Schoolrunner via its API.**
    - Students: `/api/v1/students` endpoint, filtered by school and active status.
    - Absences: `/api/v1/absences` endpoint, filtered by school, active status, and the current semester date range.
    - The process uses the Schoolrunner calendar API to determine if today is a school day.
    - The semester start date is determined dynamically using the current semester for the school.

## Is There Anything Different for OA (Opportunities Academy)?

- **Yes.** For OA, the email content is customized:
    - The attendance policy and seat time information are OA-specific.
    - The report is only sent if the student has at least one unexcused absence.
    - The OA attendance contact and policy links are used in the email template.

## What Does a Typical Email Look Like and How Is Its Content Generated?

A typical individualized attendance report email is an automated HTML message sent to each student (and their primary contact) summarizing their attendance for the current semester. The content is generated as follows:

- **Greeting:** Opens with a polite greeting (e.g., "Good afternoon,").
- **Absence Summary:** States the number of unexcused absences (e.g., "You have 3 unexcused absence(s) currently.").
- **Absence Table:** Includes a table listing each absence, with columns for "Absence Date" and "Absence Code".
- **Contact Link:** Provides a mailto link to the school's attendance office for questions.
- **Policy and Seat Time Info:** Shows seat time and attendance policy information, with special formatting (e.g., highlighted warnings) if the student is at risk.
- **Closing:** Ends with a signature from the "Collegiate Academies Attendance Robot 🤖".

**How the Content Is Generated:**
- The script pulls student and absence data from the Schoolrunner API, filtered by school, active status, and the current semester.
- For each student, it counts unexcused absences and builds a table of their absences.
- The HTML template (`individualized_attendance_report.html`) contains placeholders (e.g., `###au###`, `###table_data###`, `###attendance_email###`) that are replaced with the actual data for each student.
- The email is sent from `data@collegiateacademies.org`, with the school's attendance email as the reply-to address.
- For OA (Opportunities Academy), the content is customized and only sent if the student has at least one unexcused absence.

**Example Email (simplified):**

```
Good afternoon,

You have 3 unexcused absence(s) currently.

| Absence Date | Absence Code |
|--------------|--------------|
| 2025-05-01   | AU           |
| 2025-05-10   | AU           |
| 2025-06-01   | AU           |

Click here to email us or reply to this email if you have any questions about your attendance.

[Seat time and attendance policy info]

Sincerely,
The Collegiate Academies Attendance Robot 🤖
```

The actual email uses the HTML template for formatting and may include additional policy details or warnings as needed.

---

*Please contact tophermckee@gmail.com for any additional questions.*
