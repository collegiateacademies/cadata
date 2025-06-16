# Attendance Letter Data Checker: Overview, Schedule, and Process

## What Is the Attendance Letter Data Checker?

The Attendance Letter Data Checker is an automated process that verifies the completeness of required student data fields for generating attendance letters. It ensures that all necessary information (such as mailing address fields) is present in PowerSchool for each student, so that attendance letters can be generated and mailed without missing information.

## How Does the Attendance Checker Work?

- **Data Source:** The checker pulls student data directly from PowerSchool using a PowerQuery (`attendance_letter_data_checker`).
- **Field Validation:** For each student, it checks for missing required fields (e.g., first name, last name, mailing address, etc.).
- **Reporting:** If any required fields are missing, the checker compiles a list of students and the specific missing fields.
- **Notification:** An email is sent to the school's data manager with a summary of missing data, so corrections can be made in PowerSchool.

## When Does the Attendance Checker Run?

The attendance checker is scheduled to run automatically via cron jobs for each school, typically every Thursday morning.

**Note:** The attendance checker only runs on school days. If the scheduled cron job falls on a non-school day, the checker will not perform any checks or send any emails.

### Schedule by School

| School | Script | Cron Schedule (Central Time) | Data Manager Recipient |
|--------|--------|------------------------------|-----------------------|
| ASA    | `asa_attendance_letter_checker.py` | Thursdays at 5:00 AM | sadams1@collegiateacademies.org |
| LCA    | `lca_attendance_letter_checker.py` | Thursdays at 5:01 AM | ncowlin@collegiateacademies.org |
| WLC    | `wlc_attendance_letter_checker.py` | Thursdays at 5:02 AM | jeasley@collegiateacademies.org |
| GWC    | `gwc_attendance_letter_checker.py` | Thursdays at 5:03 AM | tdemuns@collegiateacademies.org |
| CBR    | `cbr_attendance_letter_checker.py` | Thursdays at 5:04 AM | fsall@collegiateacademies.org |
| OA     | `oa_attendance_letter_checker.py`  | Thursdays at 5:05 AM | kimani@collegiateacademies.org |

**Note:** All times are in America/Chicago timezone as set by `CRON_TZ=America/Chicago` in the crontab.

### Example Crontab Entries

```
0     5         *       *       4     cd /home/data_admin/cadata/triggers && /usr/bin/python3 asa_attendance_letter_checker.py
1     5         *       *       4     cd /home/data_admin/cadata/triggers && /usr/bin/python3 lca_attendance_letter_checker.py
2     5         *       *       4     cd /home/data_admin/cadata/triggers && /usr/bin/python3 wlc_attendance_letter_checker.py
3     5         *       *       4     cd /home/data_admin/cadata/triggers && /usr/bin/python3 gwc_attendance_letter_checker.py
4     5         *       *       4     cd /home/data_admin/cadata/triggers && /usr/bin/python3 cbr_attendance_letter_checker.py
5     5         *       *       4     cd /home/data_admin/cadata/triggers && /usr/bin/python3  oa_attendance_letter_checker.py
```

## How Is the Attendance Checker Triggered?

- **Automated:** The checker runs automatically via cron; no manual intervention is required.
- **Script Execution:** Each script imports the main checker logic and calls `attendance_field_checker()` with the appropriate school code.
- **Data Pull:** The checker uses a PowerQuery against PowerSchool to retrieve student data for the specified school.

## Where Are the Results Sent?

- If missing data is found, an email is sent to the school's data manager (as configured) with a list of students and missing fields.
- If no missing data is found, no email is sent and a log entry is created.

- **All emails are sent from `data@collegiateacademies.org`.**

## Additional Notes

- The checker helps ensure that attendance letters can be generated and mailed without interruption.
- The PowerQuery used is `attendance_letter_data_checker` and is specific to each school's PowerSchool ID.
- The process is fully automated and logs all actions for auditing and troubleshooting.

---

*Please contact tophermckee@gmail.com for any additional questions.*
