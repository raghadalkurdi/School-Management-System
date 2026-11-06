"""
Unit tests for the operations module.
Covers: ClassroomStudent, Attendance, Issues models.
"""

from django.test import TestCase
from django.db import IntegrityError
from datetime import date

from academics.models import Student, Subject
from schedules.models import Teacher, Classroom
from operations.models import ClassroomStudent, Attendance, Issues


def make_student(n=1):
    return Student.objects.create(
        first_name=f"Test{n}",
        last_name=f"Student{n}",
        student_number=f"S{n:04d}",
        email=f"student{n}@test.local",
        phone_number="0500000000",
        date_of_birth=date(2005, 1, 1),
        address="123 Test St",
        parent_name="Parent Name",
    )


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
# ClassroomStudent model
# ---------------------------------------------------------------------------

class ClassroomStudentModelTest(TestCase):

    def setUp(self):
        self.student = make_student(1)
        self.teacher = make_teacher(1)
        self.classroom = make_classroom(self.teacher, 1)

    def test_create_classroom_student(self):
        cs = ClassroomStudent.objects.create(
            student=self.student,
            classroom=self.classroom,
        )
        self.assertIn("Test1 Student1", str(cs))

    def test_student_can_be_in_multiple_classrooms(self):
        """A student may be enrolled in more than one classroom."""
        teacher2 = make_teacher(2)
        classroom2 = make_classroom(teacher2, 2)
        ClassroomStudent.objects.create(student=self.student, classroom=self.classroom)
        ClassroomStudent.objects.create(student=self.student, classroom=classroom2)
        self.assertEqual(ClassroomStudent.objects.filter(student=self.student).count(), 2)


# ---------------------------------------------------------------------------
# Attendance model
# ---------------------------------------------------------------------------

class AttendanceModelTest(TestCase):

    def setUp(self):
        self.student = make_student(1)
        self.teacher = make_teacher(1)
        self.classroom = make_classroom(self.teacher, 1)

    def test_create_attendance_present(self):
        a = Attendance.objects.create(
            student=self.student,
            classroom=self.classroom,
            date=date(2026, 10, 1),
            status="PRESENT",
        )
        self.assertEqual(a.status, "PRESENT")

    def test_all_status_choices_accepted(self):
        for i, status in enumerate(["PRESENT", "ABSENT", "LATE", "EXCUSED"], start=1):
            Attendance.objects.create(
                student=self.student,
                classroom=self.classroom,
                date=date(2026, 10, i),
                status=status,
            )
        self.assertEqual(Attendance.objects.count(), 4)

    def test_default_status_is_present(self):
        a = Attendance.objects.create(
            student=self.student,
            date=date(2026, 10, 10),
        )
        self.assertEqual(a.status, "PRESENT")


# ---------------------------------------------------------------------------
# Issues model
# ---------------------------------------------------------------------------

class IssuesModelTest(TestCase):

    def setUp(self):
        self.student = make_student(1)
        self.teacher = make_teacher(1)

    def test_create_issue(self):
        issue = Issues.objects.create(
            student=self.student,
            reported_by=self.teacher,
            title="Late to class",
            description="Student was 10 minutes late.",
        )
        self.assertFalse(issue.is_resolved)
        self.assertIn("Late to class", str(issue))

    def test_issue_default_unresolved(self):
        issue = Issues.objects.create(
            student=self.student,
            title="Missing homework",
            description="Student did not submit homework.",
        )
        self.assertFalse(issue.is_resolved)

    def test_resolve_issue(self):
        issue = Issues.objects.create(
            student=self.student,
            title="Misconduct",
            description="Disruption during exam.",
        )
        issue.is_resolved = True
        issue.save()
        self.assertTrue(Issues.objects.get(pk=issue.pk).is_resolved)

    def test_issue_without_reporter(self):
        """reported_by is optional (nullable FK)."""
        issue = Issues.objects.create(
            student=self.student,
            reported_by=None,
            title="Anonymous report",
            description="Some concern.",
        )
        self.assertIsNone(issue.reported_by)
