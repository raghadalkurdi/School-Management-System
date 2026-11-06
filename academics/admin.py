from django.contrib import admin

from .models import Student, Subject, Exam, Result

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_number', 'first_name', 'last_name', 'email', 'phone_number', 'date_registered')
    search_fields = ('first_name', 'last_name', 'student_number', 'email')
    list_filter = ('date_registered',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_code', 'subject_name', 'grade', 'teacher')
    search_fields = ('subject_code', 'subject_name')
    list_filter = ('grade', 'teacher')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('exam_name', 'subject', 'exam_date', 'exam_type', 'total_marks', 'duration_minutes')
    search_fields = ('exam_name', 'subject__subject_name')
    list_filter = ('exam_type', 'exam_date')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    # Custom validation error from Result.clean surfaces here if marks exceed the exam total
    list_display = ('student', 'exam', 'marks_obtained')
    search_fields = ('student__first_name', 'student__last_name', 'exam__exam_name')
