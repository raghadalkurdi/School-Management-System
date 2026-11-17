# Project Assets — School Management System

This folder contains supporting materials for the SMS project submission.

## Folder Structure

```
assets/
├── screenshots/          # App UI screenshots captured from the running system
│   ├── 01_landing_page.png       — Public landing page (WTM crest branding)
│   ├── 02_login_page.png         — Role-based login form
│   ├── 03_admin_login.png        — Django admin login
│   ├── 04_admin_dashboard.png    — Admin home with all models
│   ├── 05_student_dashboard.png  — Student portal (results, timetable)
│   └── 06_teacher_dashboard.png  — Teacher portal (timetable, issues)
│
├── database/             # Database design documentation
│   └── erd_diagram.png   — Full ERD (crow's foot notation, all 11 models)
│
└── testing/              # Test evidence
    └── test_results.txt  — 28 unit tests, all passing (0 failures)
```

## Test Summary

| Module      | Tests | Result |
|-------------|-------|--------|
| academics   | 12    | ✅ All pass |
| schedules   | 7     | ✅ All pass |
| operations  | 9     | ✅ All pass |
| **Total**   | **28**| ✅ **28/28** |

## ERD Overview

The ERD covers all 11 application models across 3 modules + auth layer:

- **Module 1 — Academics**: Student, Subject, Exam, Result
- **Module 2 — Schedules**: Teacher, Classroom, Timetable
- **Module 3 — Operations**: ClassroomStudent, Attendance, Issues
- **Auth layer**: Django User + UserLink

## Screenshots

Screenshots were captured from the live development server (`python manage.py runserver`)
with the seeded demo data loaded (24 students, 5 teachers, 12 subjects).
