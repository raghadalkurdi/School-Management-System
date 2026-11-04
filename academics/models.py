from django.db import models

# Create your models here.

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    student_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    address = models.TextField()
    date_registered = models.DateTimeField(auto_now_add=True)
    parent_name=models.CharField(max_length=250)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.student_number}"

class Subject(models.Model):
    subject_code = models.CharField(max_length=20, unique=True)
    grade=models.IntegerField()
    subject_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"

class Exam(models.Model):
    exam_name = models.CharField(max_length=100)
    subject = models.ForeignKey( Subject,on_delete=models.PROTECT,related_name='exams')
    exam_date = models.DateField()
    total_marks = models.PositiveIntegerField()
    type=models.CharField(max_length=250)
    duration_minutes = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.exam_name} - {self.subject.subject_name}"

class Result(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE,related_name='results')
    exam = models.ForeignKey(Exam,on_delete=models.PROTECT,related_name='results')
    subject=models.ForeignKey(Subject,on_delete=models.CASCADE,related_name='results')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.student} - {self.exam} - {self.marks_obtained}"
