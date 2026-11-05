from django.contrib import admin
from .models import ClassroomStudent, Attendance, Issues

@admin.register(ClassroomStudent)
class ClassroomStudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('date', 'status', 'remarks')
    list_filter = ('status', 'date')

@admin.register(Issues)
class IssuesAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_resolved', 'reported_at')
    list_filter = ('is_resolved',)
    search_fields = ('title', 'description')