# Lunch Service Provider Email Process

## Overview
The Lunch Service Provider process is an automated script that generates and sends weekly attendance summary emails for each school in the Collegiate Academies network. The emails are intended for lunch service providers and contain a table of daily attendance data for the previous week.

---

### 1. From which email address are emails sent?
Emails are sent from the account configured in the script's email-sending logic. Based on the code, this is likely a Google account authenticated via OAuth (using `simplegmail` or Gmail API). The specific email address is determined by the credentials in `creds.json` and related files in the `cadata` directory. Typically, this would be a service account or a designated data/attendance robot email (e.g., something like `data@collegiateacademies.org`).

---

### 2. Does this process run on non-school days? How does it know whether or not to run, and what date range does it use?
- **Non-School Days:**  
  The process does **not** run on non-school days. Before generating and sending reports, the script checks if the current day is a school day for each school.
- **How it Checks:**  
  The function `today_is_a_school_day(school, school_info[school]['sr_id'])` is called for each school. This function likely checks against a calendar of school days, which may be pulled from an API, a database, or a hard-coded list of dates. The exact source is not shown, but it is not a simple weekday check; it is school-specific.
- **Date Range:**  
  The report covers the previous week, typically from the last Monday to the previous Friday (or the last 7 days, depending on implementation). The default parameters in the `attendance_report` function are:
  - `start_date = today - 7 days`
  - `end_date = today - 1 day`
  This means the report is for the week prior to the day the script runs.

---

### 3. From where does this process get its data?
- **Data Source:**  
  The process pulls attendance and enrollment data from the Schoolrunner API (or a similar SIS API), using the `sr_api_pull` function. This function is called with parameters specific to each school, using their unique school IDs.
- **Configuration:**  
  School-specific information (IDs, names, emails, etc.) is stored in the `school_info` dictionary in `src/util.py`.

---

### 4. How is it triggered?
- **Trigger:**  
  The process is triggered by a cron job on the server.
- **Crontab Entry:**  
  ```
  0 11 * * * cd /home/data_admin/cadata/triggers && /usr/bin/python3 lunch_service_provider_email.py
  ```
  This means the script runs every day at 11:00 AM server time.
- **Script:**  
  The cron job runs `lunch_service_provider_email.py`, which calls the `attendance_report` function for each school.

---

### 5. Is there any OA (Opportunities Academy) specific logic?
There is no OA-specific logic in the `lunch_service_provider_email.py` script itself. The script calls `attendance_report(school=...)` for each school, including OA. Any OA-specific logic would be handled inside the `attendance_report` function or in the data returned for OA, but there is no evidence of special handling for OA in the triggering script.

---

### 6. What does a typical email look like (not in HTML), and how is its content generated?
- **Content Generation:**  
  The email body is generated using the `lunch_service_provider.html` template. Placeholders like `###school###` and `###table_data###` are replaced with the actual school name and a table of attendance data for the week.
- **Typical Email (Plain Text Example):**

  ```
  Good Morning,

  Here is the attendance report from the previous week for [School Name]:

  Date         Enrolled   Absent   Present
  2025-06-16   500        25       475
  2025-06-17   500        20       480
  2025-06-18   500        22       478
  2025-06-19   500        18       482
  2025-06-20   500        30       470

  - The Collegiate Academies Attendance Robot 🤖
  ```

  The actual email is sent in HTML format, but the above is a plain-text representation. The table is dynamically generated for each school and week.

---

## Summary Table

| Question | Answer |
|----------|--------|
| **From which email address?** | The address configured in `creds.json` (likely a service or robot account). |
| **Non-school days?** | No; checks via `today_is_a_school_day` using school-specific calendars. |
| **Data source?** | Schoolrunner API (or similar), using school IDs from `school_info`. |
| **How triggered?** | Daily at 11:00 AM by cron, running `lunch_service_provider_email.py`. |
| **OA-specific logic?** | None in the trigger script; handled generically like other schools. |
| **Email content?** | Weekly attendance table, generated from a template, sent as HTML. |

---

If you need more technical details about the data source or the school day check, please refer to the `src/util.py` and `src/main.py` files for the implementation of `today_is_a_school_day` and data-pulling functions.
