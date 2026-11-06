from django.contrib import admin

from .models import UserLink

@admin.register(UserLink)
class UserLinkAdmin(admin.ModelAdmin):
    list_display = ('user', 'teacher', 'student')
    search_fields = ('user__username',)
    autocomplete_fields = ('user', 'teacher', 'student')
