# Attendance Letters: Overview, Schedule, and Process

## What Are Attendance Letters?

Attendance letters are automated notifications generated for students who have reached certain thresholds of unexcused absences or tardies. These letters are intended to inform parents/guardians about their child's attendance status, outline school attendance policies, and prompt necessary interventions.

## How Do Attendance Letters Work?

- **Data Collection:** The system pulls student, absence, and communication data from Schoolrunner via API.
- **Thresholds:** Letters are generated for students who meet or exceed specific absence/tardy thresholds (e.g., 3, 5, or 10 unexcused absences).
- **PDF Generation:** For each qualifying student, a personalized PDF letter is created, including attendance summaries and policy explanations.
- **Logging:** Each letter sent is logged as a communication in Schoolrunner.
- **Email Delivery:** The generated letters are compiled into a PDF and emailed to the designated school attendance contact for mailing.

## From Which Email Address Are Emails Sent?

All attendance letter emails are sent from **`data@collegiateacademies.org`**. This is configured in the system and used for all outgoing attendance letter communications.

## How Does the Process Decide Whether to Run on a Given Day?

- **School Day Check:** The process checks if today is a school day for the respective school by querying the Schoolrunner API's calendar days endpoint. It does **not** rely on hard-coded dates or only on semester start/end dates.
- **How It Works:** Before generating and sending letters, the script calls a function (`today_is_a_school_day`) that checks the Schoolrunner calendar for the current date and school. If today is not a school day (e.g., weekend, holiday, or break), the process exits and does not send any letters.
- **Date Range for Data:** The process uses the current term's start date (e.g., semester) as the lower bound and today as the upper bound for pulling absence and communication data. The term start date is determined dynamically for each school and term type using Schoolrunner's term-bin API.

## From Where Does This Process Get Its Data?

- **Primary Source:** All student, absence, and communication data is pulled directly from the Schoolrunner API.
- **APIs Used:** The process uses endpoints for students, absences, communications, and calendar days, among others.
- **Configuration:** School-specific configuration (IDs, contacts, etc.) is stored in the codebase and referenced as needed.

## How Are Attendance Letters Triggered?

- **Automated:** The process is fully automated via cron jobs.
- **Script Execution:** Each school has a dedicated Python script in the `/triggers` directory. The cron job executes the script at the scheduled time.
- **No Manual Intervention:** No manual steps are required for regular operation.

## Is There Any OA (Opportunities Academy) Specific Logic?

Yes. Opportunities Academy (OA) has custom logic and letter content:
- **Custom Letter Content:** OA uses a different set of letter blocks and messaging tailored to its unique attendance and IEP requirements.
- **Conditional Logic:** The script checks if the school is OA and applies OA-specific templates and logic for generating letters.

## When Do Attendance Letters Run?

Attendance letters are scheduled to run automatically via cron jobs. Each school has its own scheduled time, typically early Monday mornings. The process is triggered by Python scripts located in the `/triggers` directory.

### Schedule by School

| School | Script | Cron Schedule (Central Time) | Description |
|--------|--------|------------------------------|-------------|
| ASA    | `asa_attendance_letters.py` | Mondays at 5:00 AM | Abramson Sci Academy |
| LCA    | `lca_attendance_letters.py` | Mondays at 5:05 AM | Livingston Collegiate Academy |
| WLC    | `wlc_attendance_letters.py` | Mondays at 5:10 AM | Walter L. Cohen High School |
| GWC    | `gwc_attendance_letters.py` | Mondays at 5:15 AM | G.W. Carver High School |
| CBR    | `cbr_attendance_letters.py` | Mondays at 5:20 AM | Collegiate Baton Rouge |
| OA     | `oa_attendance_letters.py`  | Mondays at 5:25 AM | Opportunities Academy |

**Note:** All times are in America/Chicago timezone as set by `CRON_TZ=America/Chicago` in the crontab.

### Example Crontab Entries

```
0     5     	*     	*     	1     cd /home/data_admin/cadata/triggers && /usr/bin/python3 asa_attendance_letters.py
5     5     	*     	*     	1     cd /home/data_admin/cadata/triggers && /usr/bin/python3 lca_attendance_letters.py
10    5     	*     	*     	1     cd /home/data_admin/cadata/triggers && /usr/bin/python3 wlc_attendance_letters.py
15    5     	*     	*     	1     cd /home/data_admin/cadata/triggers && /usr/bin/python3 gwc_attendance_letters.py
20    5     	*     	*     	1     cd /home/data_admin/cadata/triggers && /usr/bin/python3 cbr_attendance_letters.py
25    5     	*     	*     	1     cd /home/data_admin/cadata/triggers && /usr/bin/python3  oa_attendance_letters.py
```

## Where Are the Letters Sent?

- The compiled PDF of attendance letters is emailed to the school's designated attendance contact(s) as specified in the configuration.
- The recipient is responsible for printing, mailing, or otherwise distributing the letters to families.
- **All emails are sent from `data@collegiateacademies.org`.**

## Additional Notes

- **Data Checks:** There are separate cron jobs for checking data completeness for attendance letters (see `*_attendance_letter_checker.py` scripts).
- **Customization:** Letter content and thresholds can be customized per school in the configuration files.
- **Logs:** All actions are logged for auditing and troubleshooting.

---

*Please contact tophermckee@gmail.com for any additional questions.*
