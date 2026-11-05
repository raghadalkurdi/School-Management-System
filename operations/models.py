from django.db import models
from academics.models import Student
from schedules.models import Teacher, Classroom

class ClassroomStudent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='classroom_students')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='classroom_students')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} in {self.classroom}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EXCUSED', 'Excused'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Attendance for {self.student} on {self.date} - {self.status}"

class Issues(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='issues')
    reported_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_issues')
    title = models.CharField(max_length=200)
    description = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.student}"