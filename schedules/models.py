from django.db import models

# Create your models here.
class Teacher(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    sex = models.CharField(max_length=20)
    address = models.CharField(max_length=250)
    date_of_join = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Classroom(models.Model):
    room_number = models.CharField(max_length=20, unique=True)
    section = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    grade=models.CharField(max_length=20)
    teacher=models.ForeignKey(Teacher,on_delete=models.PROTECT,related_name='classrooms')
    
    def __str__(self):
        return f"{self.room_number} - {self.section}"


class Timetable(models.Model):
    DAYS = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.PROTECT,
        related_name='timetables'
    )

    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.PROTECT,
        related_name='timetables'
    )

    # Which subject this period is for (each teacher teaches specific subjects)
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timetables'
    )
    day = models.CharField(max_length=10, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.teacher} - {self.day}"
