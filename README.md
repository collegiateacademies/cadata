# cadata

## Overview

**cadata** is a comprehensive data automation and reporting toolkit for Collegiate Academies. It automates daily, weekly, and on-demand data tasks for attendance, communication, reporting, and more. The project is designed to be modular, maintainable, and extensible for a variety of school data needs.

### How it Works

- Scheduled and manual scripts run to collect, process, and distribute data (attendance, letters, emails, reports, etc.)
- Scripts are organized by function in `src/` (core logic) and `triggers/` (school-specific or scheduled jobs)
- Configuration and credentials are managed via JSON files
- Output is delivered via email, SMS, or file exports

---

## 🚨 Documentation (in the `docs` folder)

> **A huge amount of documentation exists in the [`docs`](https://github.com/collegiateacademies/cadata/tree/main/docs) folder!**
>
> **If you are looking for how something works, start there!**

- [Attendance Checker](https://github.com/collegiateacademies/cadata/blob/main/docs/attendance_checker.md)
- [Attendance Letters](https://github.com/collegiateacademies/cadata/blob/main/docs/attendance_letters.md)
- [Daily Attendance Email](https://github.com/collegiateacademies/cadata/blob/main/docs/daily_attendance_email.md)
- [Daily Attendance SMS](https://github.com/collegiateacademies/cadata/blob/main/docs/daily_attendance_sms.md)
- [Individualized Attendance Reports](https://github.com/collegiateacademies/cadata/blob/main/docs/individualized_attendance_reports.md)
- [Lunch Service Provider](https://github.com/collegiateacademies/cadata/blob/main/docs/lunch_service_provider.md)
- [Map Upload](https://github.com/collegiateacademies/cadata/blob/main/docs/map_upload.md)

---

## 🗂️ Major Scripts

### Core Scripts (`src/`)

- [main.py](src/main.py) — Main entry point for running core jobs
- [daily_attendance_sms.py](src/daily_attendance_sms.py) — Sends daily attendance SMS
- [lunch_service_provider.py](src/lunch_service_provider.py) — Lunch service provider automation
- [supply_wizard.py](src/supply_wizard.py) — Supply wizard logic

### Scheduled/Triggered Scripts (`triggers/`)

- [oa_attendance_letter_checker.py](triggers/oa_attendance_letter_checker.py)
- [wlc_daily_attendance_email.py](triggers/wlc_daily_attendance_email.py)
- [assessments.py](triggers/assessments.py)
- [lca_supply_wizard_staff.py](triggers/lca_supply_wizard_staff.py)
- [network_staff_export.py](triggers/network_staff_export.py)
- [mail_monitor.py](triggers/mail_monitor.py)
- [map_upload.py](triggers/map_upload.py)

...and many more in the `triggers/` folder for each school and function.

---

## 🗓️ Schedule

Below is the current schedule for automated jobs:

![Schedule](https://github.com/collegiateacademies/cadata/raw/main/docs/schedule.png)

For a web version, see [`docs/schedule.html`](https://github.com/collegiateacademies/cadata/blob/main/docs/schedule.html).

---

For more, see the documentation!