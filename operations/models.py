from django.db import models
from django.conf import settings

class ClassroomStudent(models.Model):
    # Link student to classroom (you can adjust ForeignKeys once Student/Classroom models are pushed)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Classroom-Student Assignment {self.id}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EXCUSED', 'Excused'),
    ]
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Attendance for {self.date} - {self.status}"

class Issues(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.title