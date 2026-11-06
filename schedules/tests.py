"""
Unit tests for the schedules module.
Covers: Teacher, Classroom, Timetable models.
"""

from django.test import TestCase
from django.db import IntegrityError
from datetime import date, time

from schedules.models import Teacher, Classroom, Timetable


def make_teacher(n=1):
    return Teacher.objects.create(
        first_name=f"Teacher{n}",
        last_name=f"Last{n}",
        email=f"teacher{n}@test.local",
        phone_number="0500000000",
        date_of_birth=date(1980, 1, 1),
        sex="Male",
        address="456 Teacher Ave",
    )


def make_classroom(teacher, n=1):
    return Classroom.objects.create(
        room_number=f"R{n:03d}",
        section=f"Section {n}",
        capacity=30,
        grade="10",
        teacher=teacher,
    )


# ---------------------------------------------------------------------------
# Teacher model
# ---------------------------------------------------------------------------

class TeacherModelTest(TestCase):

    def test_create_teacher(self):
        t = make_teacher(1)
        self.assertEqual(str(t), "Teacher1 Last1")

    def test_teacher_email_unique(self):
        make_teacher(1)
        with self.assertRaises(IntegrityError):
            Teacher.objects.create(
                first_name="Dup",
                last_name="Dup",
                email="teacher1@test.local",  # duplicate
                phone_number="000",
                date_of_birth=date(1980, 1, 1),
                sex="Female",
                address="X",
            )


# ---------------------------------------------------------------------------
# Classroom model
# ---------------------------------------------------------------------------

class ClassroomModelTest(TestCase):

    def setUp(self):
        self.teacher = make_teacher(1)

    def test_create_classroom(self):
        c = make_classroom(self.teacher, 1)
        self.assertEqual(str(c), "R001 - Section 1")

    def test_room_number_unique(self):
        make_classroom(self.teacher, 1)
        with self.assertRaises(IntegrityError):
            Classroom.objects.create(
                room_number="R001",   # duplicate
                section="Another",
                capacity=25,
                grade="11",
                teacher=self.teacher,
            )

    def test_classroom_requires_teacher(self):
        """Classroom cannot be created without a teacher."""
        with self.assertRaises(Exception):
            Classroom.objects.create(
                room_number="R999",
                section="Orphan",
                capacity=20,
                grade="9",
                teacher=None,
            )


# ---------------------------------------------------------------------------
# Timetable model
# ---------------------------------------------------------------------------

class TimetableModelTest(TestCase):

    def setUp(self):
        self.teacher = make_teacher(1)
        self.classroom = make_classroom(self.teacher, 1)

    def test_create_timetable_slot(self):
        tt = Timetable.objects.create(
            teacher=self.teacher,
            classroom=self.classroom,
            day="Monday",
            start_time=time(8, 0),
            end_time=time(9, 0),
        )
        self.assertEqual(str(tt), "Teacher1 Last1 - Monday")

    def test_timetable_day_choices(self):
        """Only valid weekday names should be accepted."""
        from django.core.exceptions import ValidationError
        tt = Timetable(
            teacher=self.teacher,
            classroom=self.classroom,
            day="Saturday",   # not in choices
            start_time=time(8, 0),
            end_time=time(9, 0),
        )
        with self.assertRaises(ValidationError):
            tt.full_clean()
