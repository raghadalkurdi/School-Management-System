"""
Seed realistic demo data for the School Management System.
Idempotent: wipes all school data, then re-seeds. Demo logins (teacher1/student1)
must have entered data first — order matters: fixtures restore in dependency order.
Run:  python _seed_data.py
"""
import datetime
import os
import random

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_management.settings")
django.setup()

from django.contrib.auth.models import User
from academics.models import Exam, Result, Student, Subject
from operations.models import Attendance, ClassroomStudent, Issues
from schedules.models import Classroom, Teacher, Timetable
from accounts.models import UserLink

random.seed(42)

# ---------------------------------------------------------------- cleanup
# Order matters: leaves first (PROTECT forbids deleting referenced rows)
for m in (Result, Attendance, Issues, ClassroomStudent, Timetable,
          Exam, Classroom, Student, Teacher, Subject):
    m.objects.all().delete()
print("old data cleared")

# ---------------------------------------------------------------- teachers
teachers_data = [
    ("Meriam", "Saleh", "meriam.saleh@sms-fake.local", "055-111-0001", "1990-03-12", "F", "12 Birch Ave"),
    ("Omar", "Haddad", "omar.haddad@sms-fake.local", "055-111-0002", "1985-11-02", "M", "8 Cedar Rd"),
    ("Lina", "Farouk", "lina.farouk@sms-fake.local", "055-111-0003", "1992-07-19", "F", "22 Maple St"),
    ("Yusuf", "Rahim", "yusuf.rahim@sms-fake.local", "055-111-0004", "1988-01-30", "M", "17 Oak Ln"),
    ("Dana", "Kamal", "dana.kamal@sms-fake.local", "055-111-0005", "1994-09-08", "F", "5 Willow Way"),
]
teachers = {}
for fn, ln, email, phone, dob, sex, addr in teachers_data:
    t = Teacher.objects.create(
        first_name=fn, last_name=ln, email=email, phone_number=phone,
        date_of_birth=django.utils.timezone.datetime.fromisoformat(dob).date(),
        sex=sex, address=addr,
    )
    teachers[fn] = t

# ---------------------------------------------------------------- subjects (grades 7 & 8)
# Each subject code is owned by one teacher across both grades, so every
# teacher teaches 1-2 subjects (Dana carries CS + Art).
code_owner = {
    "MATH": "Meriam", "ENG": "Omar", "SCI": "Lina",
    "SST": "Yusuf", "CS": "Dana", "ART": "Dana",
}
subject_defs = [
    ("MATH", "Mathematics"), ("ENG", "English"), ("SCI", "Science"),
    ("SST", "Social Studies"), ("CS", "Computer Science"), ("ART", "Art"),
]
subjects = {}
for grade in (7, 8):
    for code, name in subject_defs:
        s = Subject.objects.create(
            subject_code=f"{code}-{grade}", grade=grade, subject_name=name,
            description=f"{name} curriculum for grade {grade}.",
            teacher=teachers[code_owner[code]],
        )
        subjects[(grade, code)] = s

# ---------------------------------------------------------------- classrooms
classroom_defs = [
    ("R-101", "A", "Grade 7", "Meriam", 30),
    ("R-102", "B", "Grade 7", "Omar", 28),
    ("R-201", "A", "Grade 8", "Lina", 32),
]
rooms = {}         # room_number -> Classroom
grade_rooms = {}   # grade number -> [rooms of that grade]
for room, section, grade, tn, cap in classroom_defs:
    key = int(grade.split()[-1])  # "Grade 7" -> 7
    c = Classroom.objects.create(
        room_number=room, section=section, grade=grade, capacity=cap,
        teacher=teachers[tn],
    )
    rooms[room] = c
    grade_rooms.setdefault(key, []).append(c)

# ---------------------------------------------------------------- students
first_names = ["Ahmad", "Sara", "Khalid", "Noor", "Adam", "Hana", "Zaid", "Mariam",
               "Samir", "Layla", "Tarek", "Rana", "Bilal", "Yara", "Nabil", "Salma",
               "Waleed", "Aisha", "Faris", "Dina", "Hasan", "Rima", "Ismail", "Rania"]
last_names = ["Nasser", "Aziz", "Baker", "Darwish", "Emara", "Fahmy", "Ghali", "Hamdi",
              "Ismail", "Jaber", "Kanaan", "Lotfy", "Mansour", "Nagi", "Omar", "Pasha",
              "Qasim", "Rifai", "Said", "Tawfiq", "Usman", "Wahba", "Younis", "Zaki"]
students = []
student_room = {}
grade_counts = {7: 0, 8: 0}
n = 0
for grade in (7, 7, 8, 8):
    for i in range(6):
        n += 1
        fn, ln = first_names[n - 1], last_names[n - 1]
        s = Student.objects.create(
            first_name=fn, last_name=ln,
            student_number=f"S2026-{n:03d}",
            email=f"{fn.lower()}.{ln.lower()}{n}@sms-fake.local",
            phone_number=f"055-{200+n:04d}",
            date_of_birth=datetime.date(2012 if grade == 7 else 2011, (n % 12) + 1, (n % 27) + 1),
            address=f"{n} Palm St",
            parent_name=f"{last_names[n - 1]} Senior",
        )
        room = grade_rooms[grade][grade_counts[grade] % len(grade_rooms[grade])]
        grade_counts[grade] += 1
        students.append((s, grade))
        student_room[s.id] = room
        ClassroomStudent.objects.create(student=s, classroom=room)

# the demo login must stay attached to a real student record
demo_student = Student.objects.get(student_number="S2026-001")

# ---------------------------------------------------------------- exams
exams = []
for grade in (7, 8):
    for code, _ in subject_defs:
        subj = subjects[(grade, code)]
        e1 = Exam.objects.create(
            exam_name=f"Midterm - {subj.subject_name} G{grade}", subject=subj,
            exam_date=datetime.date(2026, 10, 20), total_marks=100,
            exam_type="Midterm", duration_minutes=90)
        e2 = Exam.objects.create(
            exam_name=f"Quiz 1 - {subj.subject_name} G{grade}", subject=subj,
            exam_date=datetime.date(2026, 11, 2), total_marks=50,
            exam_type="Quiz", duration_minutes=30)
        exams.append((e1, grade))
        exams.append((e2, grade))

# ---------------------------------------------------------------- results
# each student sits every exam of their grade level; marks clustered by ability
count_r = 0
for student, grade in students:
    ability = random.uniform(0.55, 0.98)  # a good student stays a good student
    for exam, exam_grade in exams:
        if exam_grade != grade:
            continue
        raw = exam.total_marks * min(1.0, ability + random.uniform(-0.15, 0.15))
        Result.objects.create(
            student=student, exam=exam,
            marks_obtained=round(max(0, min(exam.total_marks, raw)), 2),
        )
        count_r += 1

# ---------------------------------------------------------------- timetable
# one slot per subject per day per classroom (08:00-14:00 band).
# Each slot names the SUBJECT it covers, taught by that subject's owner.
# Rooms rotate their subject offsets so no two rooms hit the same subject
# in the same period -- therefore no teacher is ever double-booked.
rooms_list = list(rooms.values())
slot = 0
for room_idx, room in enumerate(rooms_list):
    grade_key = int(room.grade.split()[-1])
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        for period, _ in enumerate(subject_defs[:5]):
            code_idx = (period + room_idx) % 5
            subj = subjects[(grade_key, subject_defs[code_idx][0])]
            t = Timetable.objects.create(
                teacher=teachers[code_owner[subject_defs[code_idx][0]]],
                classroom=room, subject=subj, day=day,
                start_time=datetime.time(8 + period, 0),
                end_time=datetime.time(9 + period, 0),
            )
            slot += 1

# ---------------------------------------------------------------- attendance
# last 5 school days (Mon-Fri of this week)
school_days = [datetime.date(2026, 11, 2), datetime.date(2026, 11, 3),
               datetime.date(2026, 11, 4), datetime.date(2026, 11, 5),
               datetime.date(2026, 11, 6)]
statuses = ["PRESENT"] * 8 + ["ABSENT"] + ["LATE"] + ["EXCUSED"]
count_a = 0
for student, grade in students:
    for d in school_days:
        status = random.choice(statuses)
        Attendance.objects.create(
            student=student, classroom=student_room[student.id], date=d,
            status=status,
            remarks="Arrived late (traffic)." if status == "LATE" else None,
        )
        count_a += 1

# ---------------------------------------------------------------- issues
issue_defs = [
    ("Repeated missing homework", "Phase 1", False, "Meriam"),
    ("Disruptive in class this week", "Phase 2", True, "Omar"),
    ("Lost library book", "Phase 1", True, "Dana"),
    ("Needs parent meeting about grades", "Phase 2", False, "Yusuf"),
    ("Unexcused absence cluster", "Phase 1", False, "Meriam"),
]
for i, (title, detail, resolved, tn) in enumerate(issue_defs):
    Issues.objects.create(
        student=students[i][0], reported_by=teachers[tn],
        title=title, description=detail + ". " + title,
        is_resolved=resolved,
    )

# ---------------------------------------------------------------- relink demo logins
from django.contrib.auth.models import Group, User

teacher_login = f"{teachers['Meriam'].first_name.lower()}.{teachers['Meriam'].last_name.lower()}"
student_login = f"{demo_student.first_name.lower()}.{demo_student.last_name.lower()}"
for username, password, field, group_name, obj in (
    (teacher_login, "Teacher@2026", "teacher", "Teachers", teachers["Meriam"]),
    (student_login, "Student@2026", "student", "Students", demo_student),
):
    grp, _ = Group.objects.get_or_create(name=group_name)
    user, created = User.objects.get_or_create(
        username=username, defaults={"email": obj.email})
    user.set_password(password)
    user.is_staff = False
    user.is_superuser = False
    user.save()
    user.groups.add(grp)
    link, _ = UserLink.objects.get_or_create(user=user)
    setattr(link, field, obj)
    link.save()
    User.objects.filter(username__in=("teacher1", "student1")).delete()

print(f"teachers={Teacher.objects.count()} subjects={Subject.objects.count()} "
      f"classrooms={Classroom.objects.count()} students={Student.objects.count()} "
      f"exams={Exam.objects.count()} results={count_r} "
      f"timetable={Timetable.objects.count()} attendance={count_a} issues={Issues.objects.count()}")
