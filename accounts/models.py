from django.contrib.auth.models import User
from django.db import models

from academics.models import Student
from schedules.models import Teacher


class UserLink(models.Model):
    """Links a login account (auth User) to its person records.

    Superusers don't need a link. Teacher and student logins must have
    exactly one of the two links set to be recognized by the portals.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='link',
    )
    student = models.OneToOneField(
        Student,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='login',
    )
    teacher = models.OneToOneField(
        Teacher,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='login',
    )

    def __str__(self):
        who = self.teacher or self.student or 'unlinked'
        return f"{self.user.username} → {who}"
