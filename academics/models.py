
from django.db import models
from django.core.validators import MinValueValidator


class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    student_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    address = models.TextField()
    date_registered = models.DateTimeField(auto_now_add=True)
    parent_name = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.student_number}"


class Subject(models.Model):
    subject_code = models.CharField(max_length=20, unique=True)
    grade = models.PositiveSmallIntegerField()
    subject_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    # The teacher who teaches this subject (both grades of it may share a teacher).
    teacher = models.ForeignKey(
        'schedules.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subjects',
    )

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"


class Exam(models.Model):
    exam_name = models.CharField(max_length=100)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name='exams'
    )
    exam_date = models.DateField()
    total_marks = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    exam_type = models.CharField(max_length=50)
    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return f"{self.exam_name} - {self.subject.subject_name}"


class Result(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='results'
    )
    exam = models.ForeignKey(
        Exam,
        on_delete=models.PROTECT,
        related_name='results'
    )
    marks_obtained = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        # A student can only have one result per exam (a retake = a new Exam row).
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'exam'],
                name='unique_result_per_student_exam'
            ),
        ]

    def clean(self):
        super().clean()

        if self.exam_id and self.marks_obtained is not None:
            if self.marks_obtained > self.exam.total_marks:
                from django.core.exceptions import ValidationError
                raise ValidationError({
                    'marks_obtained': 'Marks cannot exceed the exam total.'
                })

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.marks_obtained}"
