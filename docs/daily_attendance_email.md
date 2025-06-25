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

- **No.** The process checks if today is a school day for the specific school by querying the Schoolrunner calendar API for the current date and school. If the calendar indicates that the school is not in session, the script exits and does not send an email.
- **How does it know?** There are no hard-coded dates or semester checks. The check is dynamic and school-specific, using the Schoolrunner calendar API (`/api/v1/calendar_days`) to determine if the school is in session for the current date.
- **Date range:** The process only considers the current day for absences and attendance rates.

## From Where Does This Process Get Its Data?

- **Student and absence data are pulled from Schoolrunner via its API.**
    - Students: `/api/v1/students` endpoint, filtered by school and active status.
    - Absences: `/api/v1/absences` endpoint, filtered by school, active status, and current date.
    - The process uses the Schoolrunner calendar API to determine if today is a school day.

## Is There Any OA-Specific Logic?

- **No.** The daily attendance email process is the same for all schools, including OA. There is no OA-specific logic in this process.

## What Does a Typical Daily Attendance Email Look Like?

A typical daily attendance email is an HTML email that provides:

- The overall daily attendance percentage for the school.
- Attendance rates by grade.
- Lists of students who are absent (out-of-school absences), organized by grade.

**Example Email Structure:**

- A table with the daily attendance percentage at the top.
- Grade headers as table rows.
- Lists of absent students under each grade.

The email is visually formatted using a table for clarity and readability.

### How Is the Email Content Generated?

1. **Data Collection:**
   - The script pulls student and absence data from the Schoolrunner API, filtered by school, active status, and the current date.

2. **Attendance Calculation:**
   - For each grade, it calculates the attendance rate and compiles lists of absent students.

3. **HTML Generation:**
   - The email content is generated using an HTML template (`html/daily_attendance.html`).
   - Placeholders in the template (such as `###total###`, `###grade_headers###`, and `###name_lists###`) are replaced with the calculated attendance percentage, grade headers, and lists of absent students, respectively.

4. **Email Sending:**
   - The completed HTML is sent as an email from `data@collegiateacademies.org` to the designated attendance contact for the school.

**Sample HTML Template:**

```
<html>
  <body style="font-family: sans-serif;">
    <table style="border-collapse: collapse; width: 100%;">
      <tr>
        <td colspan="4" style="text-align: center; font-weight: bold;">Daily Attendance Percentage: 83.94%</td>
      </tr>
      <tr>
        <th style="border: 1px solid #000;">12th: 99.32%</th>
        <th style="border: 1px solid #000;">11th: 69.93%</th>
        <th style="border: 1px solid #000;">10th: 84.76%</th>
        <th style="border: 1px solid #000;">9th: 82.25%</th>
      </tr>
      <tr>
        <td style="border: 1px solid #000; vertical-align: top;">
          Student 1 - (AU)<br>
          Student 2 - (AU)<br>
          Student 3 - (AU)<br>
          ...
        </td>
        <td style="border: 1px solid #000; vertical-align: top;">
          Student 2 - (OSS)<br>
          Student 3 - (OSS)<br>
          Student 4 - (AU)<br>
          ...
        </td>
        <td style="border: 1px solid #000; vertical-align: top;">
          Student 5 - (AU)<br>
          Student 6 - (AU)<br>
          Student 7 - (AU)<br>
          ...
        </td>
        <td style="border: 1px solid #000; vertical-align: top;">
          Student 8 - (OSS)<br>
          Student 9 - (OSS)<br>
          Student 10 - (AU)<br>
          ...
        </td>
      </tr>
    </table>
  </body>
</html>
```

**Visual Example:**

**Daily Attendance Percentage: 83.94%**

| 12th: 99.32%         | 11th: 69.93%         | 10th: 84.76%         | 9th: 82.25%         |
|----------------------|----------------------|----------------------|---------------------|
| Student 1 - (AU)<br>Student 2 - (AU)<br>Student 3 - (AU)<br>... | Student 2 - (OSS)<br>Student 3 - (OSS)<br>Student 4 - (AU)<br>... | Student 5 - (AU)<br>Student 6 - (AU)<br>Student 7 - (AU)<br>... | Student 8 - (OSS)<br>Student 9 - (OSS)<br>Student 10 - (AU)<br>... |

**Daily Attendance Percentage:** 83.94%

*This is an automated message from Collegiate Academies Data Team.*

The actual content will reflect the current day's attendance data for the school, with each grade as a column and absent students listed vertically under each grade.

## Summary

- **Emails sent from:** `data@collegiateacademies.org`
- **Runs on non-school days?** No; checks Schoolrunner calendar dynamically per school.
- **How does it know whether to run?** Uses Schoolrunner calendar API for the current date and school; not hard-coded.
- **Data source:** Schoolrunner API (students, absences, calendar).
- **Trigger:** Automated via cron jobs, twice daily per school.
- **OA-specific logic:** None; OA is handled the same as other schools.

---

*Please contact tophermckee@gmail.com for any additional questions.*
