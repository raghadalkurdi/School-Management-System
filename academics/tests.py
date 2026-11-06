"""
Unit tests for the academics module.
Covers: Student, Subject, Exam, Result models + business rules.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date

from academics.models import Student, Subject, Exam, Result


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


def make_subject():
    return Subject.objects.create(
        subject_code="MATH101",
        grade=10,
        subject_name="Mathematics",
    )


def make_exam(subject, total=100):
    return Exam.objects.create(
        exam_name="Midterm",
        subject=subject,
        exam_date=date(2026, 5, 1),
        total_marks=total,
        exam_type="Written",
        duration_minutes=90,
    )


# ---------------------------------------------------------------------------
# Student model
# ---------------------------------------------------------------------------

class StudentModelTest(TestCase):

    def test_create_student(self):
        s = make_student(1)
        self.assertEqual(str(s), "Test1 Student1 - S0001")

    def test_student_number_unique(self):
        make_student(1)
        with self.assertRaises(IntegrityError):
            Student.objects.create(
                first_name="Dup",
                last_name="Dup",
                student_number="S0001",   # duplicate
                email="dup@test.local",
                phone_number="000",
                date_of_birth=date(2005, 1, 1),
                address="X",
                parent_name="Y",
            )

    def test_student_email_unique(self):
        make_student(1)
        with self.assertRaises(IntegrityError):
            Student.objects.create(
                first_name="Dup",
                last_name="Dup",
                student_number="S9999",
                email="student1@test.local",  # duplicate
                phone_number="000",
                date_of_birth=date(2005, 1, 1),
                address="X",
                parent_name="Y",
            )


# ---------------------------------------------------------------------------
# Subject model
# ---------------------------------------------------------------------------

class SubjectModelTest(TestCase):

    def test_create_subject(self):
        s = make_subject()
        self.assertEqual(str(s), "MATH101 - Mathematics")

    def test_subject_code_unique(self):
        make_subject()
        with self.assertRaises(IntegrityError):
            Subject.objects.create(
                subject_code="MATH101",  # duplicate
                grade=11,
                subject_name="Advanced Math",
            )


# ---------------------------------------------------------------------------
# Exam model
# ---------------------------------------------------------------------------

class ExamModelTest(TestCase):

    def setUp(self):
        self.subject = make_subject()

    def test_create_exam(self):
        e = make_exam(self.subject)
        self.assertEqual(str(e), "Midterm - Mathematics")

    def test_exam_total_marks_minimum(self):
        from django.core.exceptions import ValidationError
        e = Exam(
            exam_name="Bad Exam",
            subject=self.subject,
            exam_date=date(2026, 5, 1),
            total_marks=0,          # invalid
            exam_type="Written",
            duration_minutes=60,
        )
        with self.assertRaises(ValidationError):
            e.full_clean()


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------

class ResultModelTest(TestCase):

    def setUp(self):
        self.student = make_student(1)
        self.subject = make_subject()
        self.exam = make_exam(self.subject, total=100)

    def test_create_result(self):
        r = Result.objects.create(
            student=self.student,
            exam=self.exam,
            marks_obtained=85,
        )
        self.assertEqual(r.marks_obtained, 85)

    def test_marks_cannot_exceed_total(self):
        r = Result(
            student=self.student,
            exam=self.exam,
            marks_obtained=150,     # exam total is 100
        )
        with self.assertRaises(ValidationError):
            r.full_clean()

    def test_marks_at_boundary_allowed(self):
        """Marks equal to total_marks should be valid."""
        r = Result(
            student=self.student,
            exam=self.exam,
            marks_obtained=100,
        )
        r.full_clean()  # should not raise

    def test_unique_result_per_student_exam(self):
        Result.objects.create(
            student=self.student,
            exam=self.exam,
            marks_obtained=70,
        )
        with self.assertRaises(IntegrityError):
            Result.objects.create(
                student=self.student,
                exam=self.exam,     # same student + same exam
                marks_obtained=80,
            )

    def test_zero_marks_allowed(self):
        """A score of 0 is a valid result."""
        r = Result(
            student=self.student,
            exam=self.exam,
            marks_obtained=0,
        )
        r.full_clean()  # should not raise
