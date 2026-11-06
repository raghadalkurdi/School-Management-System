from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.conf import settings

from academics.models import Exam, Result, Student, Subject
from operations.models import Attendance, ClassroomStudent, Issues
from schedules.models import Classroom, Teacher, Timetable

from .models import UserLink

DAY_ORDER = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4}


def _has_logo():
    """True when the real WTM SCHOOLHUB logo file is present for static serving."""
    return (settings.BASE_DIR / 'accounts' / 'static' / 'accounts' / 'img'
            / 'logo.png').exists()


def resolve_role(user):
    """Return 'admin', 'teacher', 'student', or None for a logged-in user."""
    if user.is_superuser:
        return 'admin'
    link = getattr(user, 'link', None)
    if link and link.teacher_id:
        return 'teacher'
    if link and link.student_id:
        return 'student'
    if user.groups.filter(name='Teachers').exists():
        return 'teacher'
    if user.groups.filter(name='Students').exists():
        return 'student'
    return None


def _portal_for(role):
    return {'admin': '/admin/', 'teacher': '/teacher/', 'student': '/student/'}[role]


def home(request):
    """Public landing page for the school brand (WTM SCHOOLHUB).

    Aggregate counts are public-safe. Logged-in users get a 'My portal'
    shortcut instead of being force-redirected away.
    """
    role = resolve_role(request.user) if request.user.is_authenticated else None
    context = {
        'role': role,
        'has_logo': _has_logo(),
        'student_count': Student.objects.count(),
        'teacher_count': Teacher.objects.count(),
        'subject_count': Subject.objects.count(),
        'exam_count': Exam.objects.count(),
    }
    return render(request, 'accounts/landing.html', context)


@login_required
def no_role(request):
    """Authenticated user with no teacher/student link and no group — explain why."""
    return render(request, 'accounts/no_record.html', {'portal': 'teacher or student'})


def login_view(request):
    """Login page for teacher/student portal users (admin uses /admin/)."""
    error = None
    if request.method == 'POST':
        from django.contrib.auth import authenticate, login
        user = authenticate(
            request,
            username=request.POST.get('username', ''),
            password=request.POST.get('password', ''),
        )
        if user is not None:
            login(request, user)
            role = resolve_role(user)
            if role is None:
                return redirect('no_role')
            return redirect(_portal_for(role))
        error = 'Invalid username or password.'
    return render(request, 'accounts/login.html', {'error': error})


@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('home')


def _link_for(user):
    return getattr(user, 'link', None)


@login_required
def teacher_dashboard(request):
    role = resolve_role(request.user)
    if role not in ('teacher', 'admin'):
        return redirect('no_role' if role is None else _portal_for(role))

    link = _link_for(request.user)
    me = link.teacher if link and link.teacher_id else None
    my_classrooms = me.classrooms.all() if me else Classroom.objects.none()
    my_timetable = sorted(
        Timetable.objects.filter(teacher=me) if me else Timetable.objects.none(),
        key=lambda t: (DAY_ORDER.get(t.day, 9), str(t.start_time)),
    )
    my_attendance = Attendance.objects.filter(
        classroom__in=my_classrooms).order_by('-date')[:15] if me else None
    my_issues = Issues.objects.filter(reported_by=me) if me else None

    # The academics tables, visible to every teacher (per spec) — read-only for now
    academics = {
        'students': Student.objects.order_by('student_number'),
        'subjects': Subject.objects.order_by('grade', 'subject_code'),
        'exams': Exam.objects.select_related('subject').order_by('-exam_date'),
        'results': [],
    }
    for r in Result.objects.select_related('student', 'exam__subject').order_by('-id')[:50]:
        academics['results'].append({
            'student': r.student,
            'exam': r.exam,
            'marks': r.marks_obtained,
            'percent': round(r.marks_obtained / r.exam.total_marks * 100, 1),
        })

    context = {
        'me': me,
        'is_admin_preview': role == 'admin',
        'my_classrooms': my_classrooms,
        'my_timetable': my_timetable,
        'my_attendance': my_attendance,
        'my_issues': my_issues,
        **academics,
        'student_count': Student.objects.count(),
        'subject_count': Subject.objects.count(),
        'exam_count': Exam.objects.count(),
        'result_count': Result.objects.count(),
    }
    return render(request, 'accounts/teacher_dashboard.html', context)


@login_required
def student_dashboard(request):
    role = resolve_role(request.user)
    if role not in ('student', 'admin'):
        return redirect('no_role' if role is None else _portal_for(role))

    link = _link_for(request.user)
    me = link.student if link and link.student_id else None
    if me is None:
        return render(request, 'accounts/no_record.html', {'portal': 'student'})

    assignments = ClassroomStudent.objects.filter(student=me).select_related('classroom')
    my_classroom = assignments.first().classroom if assignments.exists() else None
    my_timetable = sorted(
        Timetable.objects.filter(classroom=my_classroom) if my_classroom else [],
        key=lambda t: (DAY_ORDER.get(t.day, 9), str(t.start_time)),
    )
    my_results = Result.objects.filter(
        student=me).select_related('exam__subject').order_by('-exam__exam_date')
    results_display = [{
        'subject': r.exam.subject,
        'exam': r.exam,
        'marks': r.marks_obtained,
        'total': r.exam.total_marks,
        'percent': round(r.marks_obtained / r.exam.total_marks * 100, 1) if r.exam.total_marks else None,
    } for r in my_results]

    average = None
    if results_display:
        average = round(
            sum(r['percent'] for r in results_display) / len(results_display), 1)

    context = {
        'me': me,
        'is_admin_preview': role == 'admin',
        'my_classroom': my_classroom,
        'my_timetable': my_timetable,
        'results': results_display,
        'average': average,
        'attendance': Attendance.objects.filter(student=me).order_by('-date')[:15],
        'issues': Issues.objects.filter(student=me).order_by('-reported_at'),
        'subjects': Subject.objects.order_by('grade', 'subject_code'),
    }
    return render(request, 'accounts/student_dashboard.html', context)
