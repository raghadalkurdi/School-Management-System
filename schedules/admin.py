from django.contrib import admin

from .models import Teacher, Classroom, Timetable

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'sex')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'section', 'grade', 'capacity', 'teacher')

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time', 'teacher', 'subject', 'classroom')
    list_filter = ('day', 'teacher')
