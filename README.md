# School Management System (SMS)

A Django-based school management system built as a team project. It manages
the core data flow of a school in three modules that build on each other:
who the people are (academic records), where they work (teaching schedules),
and what happens day to day (attendance, classroom membership, and reported issues).

## Tech Stack

- **Python 3.14** / **Django 6.1.2**
- **Database:** SQLite (development)
- **Admin:** Django admin as the primary user interface

## Modules

### Module 1 — Academic Tracking (`academics`)

The core people-and-results module.

| Model | Purpose |
|---|---|
| `Student` | Student profiles (name, contact, DOB, unique student number & email) |
| `Subject` | Subjects offered per grade (unique subject code) |
| `Exam` | Exams per subject with total marks, type, duration |
| `Result` | A student's marks per exam, validated so marks can't exceed the exam total |

### Module 2 — Teaching Schedules (`schedules`)

Who teaches where and when.

| Model | Purpose |
|---|---|
| `Teacher` | Teacher profiles (contact, DOB, join date) |
| `Classroom` | Physical rooms (unique room number, grade, capacity, teacher-in-charge) |
| `Timetable` | Weekly timetable slots (day, start/end time, teacher, classroom) |

### Module 3 — Operations (`operations`)

Day-to-day school operations, referencing the models above.

| Model | Purpose |
|---|---|
| `Attendance` | Daily student attendance status (Present / Absent / Late / Excused) |
| `ClassroomStudent` | Which students belong to which classroom |
| `Issues` | Concerns reported about a student, incl. who reported them and resolution status |

## Getting Started

### Prerequisites

- Python 3.14 (or newer)
- Git

### Setup

```powershell
# 1. Clone the repo
git clone https://github.com/raghadalkurdi/School-Management-System.git
cd SMS

# 2. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Create your admin account
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

Then open <http://127.0.0.1:8000/admin/> and log in.

### Suggested data-entry order

The models are FK-linked, so enter them parent-first:

1. **Students and Subjects** (independent)
2. **Teachers** → then **Classrooms** (a classroom requires a teacher-in-charge)
3. **Exams** (require a subject)
4. **Results** (require a student + exam)
5. **Timetables, Attendance, Issues** (require teachers/classrooms/students)

## Project Structure

```
SMS/
├── manage.py
├── requirements.txt
├── academics/       # Module 1: Student, Subject, Exam, Result
├── schedules/       # Module 2: Teacher, Classroom, Timetable
├── operations/      # Module 3: Attendance, ClassroomStudent, Issues
├── accounts/        # (currently default Django auth; no custom models)
└── school_management/  # Django settings/urls/wsgi project package
```

## Team Conventions

- **Migrations:** run `python manage.py makemigrations <app>` immediately after
  changing `models.py`, and commit the code and its migration files together.
- **Don't** manually edit generated migration files — regenerate them instead.
- **Never commit** `__pycache__/`, `.pyc` files, or `db.sqlite3`; they are
  ignored via `.gitignore`.
- Work on feature branches (e.g. `feature/<module>-<topic>`) and open a PR per module.
