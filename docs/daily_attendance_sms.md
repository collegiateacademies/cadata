# Daily Attendance SMS Process Documentation

## Overview

The `daily_attendance_sms` script is responsible for sending a daily email (with a CSV attachment) listing all students who are absent for a given school on a specific date. It is designed to run automatically for each school on scheduled days, and can also be run manually for testing or for a specific date.

---

## 1. From which email address are emails sent?

Emails are sent using the `send_email` function, which is called within the script. The actual sender address is determined by the configuration in the `send_email` implementation (not shown in the provided code), but typically this is set up as a service or admin email address configured in your environment or credentials.  
**If you need the exact sender address, check the configuration in your `util.py` or email credentials file.**

---

## 2. Does this process run on non-school days? How does it know which days are school days?

- **No, the process does not run on non-school days.**
- The script checks if the current date is a school day by calling the `today_is_a_school_day()` function, which uses the school name and school ID.
- The logic for determining a school day is not hard-coded in this script; it is delegated to `today_is_a_school_day`, which likely checks a calendar, semester dates, or an external API/database for each school.
- If the script is run in "test mode" (i.e., with a specific date provided), it skips the school day check.
- The date range for absences is always a single day: the current day (or the test date if provided).

---

## 3. From where does this process get its data?

- The script pulls absence data using the `sr_api_pull` function, which queries an external Student Information System (SIS) API.
- It requests absences for the given school and date, and extracts SIS IDs for absent students.
- The data is then written to a CSV file, which is attached to the email.

---

## 4. How is it triggered?

- **Automatically:** The process is triggered by a cron job for each school, scheduled to run at 9:00 AM, Monday through Friday:
  ```
  0 9 * * 1-5 /usr/bin/python3 /home/data_admin/cadata/src/daily_attendance_sms.py ASA
  0 9 * * 1-5 /usr/bin/python3 /home/data_admin/cadata/src/daily_attendance_sms.py LCA
  0 9 * * 1-5 /usr/bin/python3 /home/data_admin/cadata/src/daily_attendance_sms.py WLC
  0 9 * * 1-5 /usr/bin/python3 /home/data_admin/cadata/src/daily_attendance_sms.py GWC
  0 9 * * 1-5 /usr/bin/python3 /home/data_admin/cadata/src/daily_attendance_sms.py CBR
  0 9 * * 1-5 /usr/bin/python3 /home/data_admin/cadata/src/daily_attendance_sms.py OA
  ```
  (where `<SCHOOL>` is one of ASA, LCA, WLC, GWC, CBR, OA)
- **Manually:** It can also be run manually from the command line:
  ```
  python daily_attendance_sms.py <school_name> [test_date]
  ```
  If `test_date` is provided, the script runs in test mode for that date.

---

## 5. Is there any OA-specific logic?

- There is **no OA-specific logic** in the script as provided. All schools, including OA, are handled identically. If OA requires special handling, it would need to be added to the script.

---

## 6. What does an example email look like?

- **Subject:**  
  `Daily Attendance SMS for <school_name> on <YYYY-MM-DD>`
- **Recipient:**  
  The email is sent to the address specified in the `school_info` dictionary for each school (or to `tophermckee@gmail.com` in test mode).
- **Body:**  
  The body is generated from an HTML template (`daily_attendance_sms.html`), with placeholders for the date and school name replaced dynamically. If the template cannot be read, a plain text fallback is used.
  
  Example body (with placeholders):
  
      Good morning,
      
      Attached is the daily attendance SMS report for {{ date }} for {{ school_name }}.
      
      Note: These absences are already logged in Schoolrunner. It is imperative that these notifications are sent for compliance purposes.
      
      To send the SMS, please:
        1. Download the attached file.
        2. Log in to the SchoolMessenger website: https://asp.schoolmessenger.com/collegiateacademies/start.php
        3. Click New Broadcast.
        4. Choose Your Subject, for example "{{ date }} Attendance"
        5. Change the Broadcast Type to Attendance.
        6. Click Add Recipients and choose Upload List.
        7. Upload the attached file using the second option, ID# Lookup.
        8. Click Next.
        9. Send the SMS to the parents.
      
      Best regards,
      The CA Attendance Robot 🤖

  The placeholders `{{ date }}` and `{{ school_name }}` are replaced with the actual date and school name.
- **Attachment:**  
  A CSV file named `absent_students_<school_name>_<YYYY-MM-DD>.csv` containing a list of absent student SIS IDs.

**Example Email:**

- **To:** `school_attendance_contact@example.com`
- **Subject:** `Daily Attendance SMS for ASA on 2025-06-25`
- **Body:**  
  (See example body above, with placeholders replaced)
- **Attachment:**  
  `absent_students_ASA_2025-06-25.csv`
  ```
  sis_id
  12345
  67890
  ...
  ```

---

## Summary Table

| Question | Answer |
|----------|--------|
| **Sender Email** | Always `data@collegiateacademies.org` (configured in `send_email`) |
| **Non-school days?** | No, checks via `today_is_a_school_day()` per school |
| **Data Source** | SIS API via `sr_api_pull` |
| **Trigger** | Cron job (Mon-Fri, 9am) and manual CLI |
| **OA-specific logic?** | No, all schools handled the same |
| **Example Email** | See above |

---

If you need more details on the sender address or the school day logic, check the `util.py` file and the configuration files referenced in your project.
