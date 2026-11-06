import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_management.settings")
django.setup()

from django.contrib.auth.models import Group, User
from academics.models import Student
from schedules.models import Teacher
from accounts.models import UserLink

teachers_group, _ = Group.objects.get_or_create(name="Teachers")
students_group, _ = Group.objects.get_or_create(name="Students")

# drop the old demo usernames first (teacher1/student1) so their UserLinks
# stop owning the person records; links are recreated for the name-based logins
User.objects.filter(username__in=("teacher1", "student1"), is_superuser=False).delete()


from django.db.models import Q


def login_username(person):
    base = f"{person.first_name.lower()}.{person.last_name.lower()}"
    username, suffix = base, 2
    while User.objects.filter(username=username).exists():
        username = f"{base}{suffix}"
        suffix += 1
    return username


def ensure_login(person, password, group, field):
    """Create or refresh the name-based login for this person.

    Reuses any existing linked account (renaming it to the canonical
    firstname.lastname form) so re-runs are stable.
    """
    User.objects.filter(is_superuser=False).filter(
        Q(link__isnull=True)
        | Q(link__student__isnull=True, link__teacher__isnull=True)
    ).delete()  # sweep stale accounts from crashed runs

    link = UserLink.objects.filter(**{field: person}).select_related("user").first()
    if link is not None:
        user = link.user
        base = f"{person.first_name.lower()}.{person.last_name.lower()}"
        if user.username != base:
            others = User.objects.filter(username=base).exclude(pk=user.pk).exists()
            user.username = base if not others else f"{base}2"
        user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        user.email = person.email
        user.save()
        user.groups.add(group)
        return f"{user.username} (updated) -> {group.name} -> {person}"

    user, created = User.objects.get_or_create(
        username=login_username(person),
        defaults={"email": person.email},
    )
    user.set_password(password)
    user.is_staff = False
    user.is_superuser = False
    user.email = person.email
    user.save()
    user.groups.add(group)
    link, _ = UserLink.objects.get_or_create(user=user)
    setattr(link, field, person)
    link.save()
    return f"{user.username} ({'created' if created else 'updated'}) -> {group.name} -> {person}"

first_teacher = Teacher.objects.first()
first_student = Student.objects.order_by("student_number").first()
if not first_teacher:
    first_teacher = Teacher.objects.create(
        first_name="Demo", last_name="Teacher", email="demo.teacher@sms-fake.local",
        phone_number="055-000-0001", date_of_birth="1990-05-01", sex="F",
        address="Demo Street 1")
if not first_student:
    first_student = Student.objects.create(
        first_name="Demo", last_name="Student", student_number="S2026-001",
        email="demo.student@sms-fake.local", phone_number="055-000-0002",
        date_of_birth="2011-03-14", address="Demo Street 2", parent_name="Demo Parent")

print("enrolling every seeded person:")
for t in Teacher.objects.all().order_by("id"):
    print(" ", ensure_login(t, "Teacher@2026", teachers_group, "teacher"))
for s in Student.objects.all().order_by("student_number"):
    print(" ", ensure_login(s, "Student@2026", students_group, "student"))

print("accounts:", [(u.username, u.is_superuser, [g.name for g in u.groups.all()]) for u in User.objects.all()])
print("users total:", User.objects.count())
