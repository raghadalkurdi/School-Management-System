from django.contrib import admin

# Register your models here.
from .models import Student, Subject, Exam, Result

admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Exam)
admin.site.register(Result)