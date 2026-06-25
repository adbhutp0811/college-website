from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from .forms import LoginForm
from students.models import Class, Student
from results.models import Exam, Result, calculate_sgpa
from faculty.models import Faculty

class AdmissionsView(TemplateView):
    template_name = 'admissions.html'

class MandatoryDisclosureView(TemplateView):
    template_name = 'mandatory_disclosure.html'

class AcademicCalendarView(TemplateView):
    template_name = 'academic_calendar.html'

class NIRFView(TemplateView):
    template_name = 'nirf.html'

class ResearchView(TemplateView):
    template_name = 'research.html'


class FacultyView(TemplateView):
    template_name = 'faculty.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from faculty.models import Faculty
        faculty_qs = Faculty.objects.filter(is_active=True).prefetch_related('classes')
        dept_order = list(dict.fromkeys(faculty_qs.values_list('classes__name', flat=True)))
        departments = []
        for code in dept_order:
            if not code:
                continue
            members = faculty_qs.filter(classes__name=code).distinct()
            if members.exists():
                full_name = DEPT_NAMES.get(code, [code])[0] if isinstance(DEPT_NAMES.get(code), (list, tuple)) else DEPT_NAMES.get(code, code)
                departments.append({
                    'name': f'{full_name} ({code})',
                    'code': code,
                    'faculty': members,
                })
        ctx['departments'] = departments
        ctx['total_faculty'] = faculty_qs.count()
        return ctx


class FacultyDetailView(TemplateView):
    template_name = 'faculty_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from faculty.models import Faculty
        ctx['faculty'] = get_object_or_404(Faculty, slug=kwargs['slug'])
        return ctx

class SyllabusView(TemplateView):
    template_name = 'syllabus.html'


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        return reverse_lazy('dashboard')


class StudentLoginView(View):
    template_name = 'accounts/student_login.html'

    def get(self, request):
        if request.session.get('student_id'):
            return redirect('accounts:student_portal')
        return render(request, self.template_name)

    def post(self, request):
        roll_number = request.POST.get('roll_number', '').strip()
        date_of_birth = request.POST.get('date_of_birth', '').strip()
        try:
            student = Student.objects.get(
                roll_number=roll_number,
                date_of_birth=date_of_birth,
                is_deleted=False
            )
            request.session['student_id'] = student.id
            request.session['student_name'] = student.full_name
            messages.success(request, f'Welcome, {student.full_name}!')
            return redirect('accounts:student_portal')
        except Student.DoesNotExist:
            messages.error(request, 'Invalid roll number or date of birth.')
            return render(request, self.template_name)


class StudentLogoutView(View):
    def get(self, request):
        request.session.pop('student_id', None)
        request.session.pop('student_name', None)
        messages.success(request, 'Logged out successfully.')
        return redirect('accounts:student_login')


class StudentPortalView(TemplateView):
    template_name = 'accounts/student_portal.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('student_id'):
            messages.error(request, 'Please login with your roll number and date of birth.')
            return redirect('accounts:student_login')
        try:
            Student.objects.get(id=request.session['student_id'], is_deleted=False)
        except Student.DoesNotExist:
            del request.session['student_id']
            del request.session['student_name']
            messages.error(request, 'Session expired. Please login again.')
            return redirect('accounts:student_login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student = Student.objects.get(id=self.request.session['student_id'], is_deleted=False)
        from attendance.models import Attendance
        from results.models import Result
        ctx['student'] = student
        ctx['attendance_records'] = Attendance.objects.filter(student=student).order_by('-date')[:60]

        current_sem = int(student.student_class.section.replace('Sem ', ''))
        ctx['semesters'] = list(range(1, current_sem + 1))
        selected_sem = self.request.GET.get('sem')
        if selected_sem:
            try:
                selected_sem = int(selected_sem)
            except ValueError:
                selected_sem = current_sem
        else:
            selected_sem = current_sem
        ctx['selected_sem'] = selected_sem

        results = Result.objects.filter(student=student).select_related('exam', 'subject')
        if selected_sem:
            results = [r for r in results if r.exam.student_class.section == f'Sem {selected_sem}']

        exam_groups = {}
        for r in results:
            exam_groups.setdefault(r.exam, []).append(r)
        for exam, rlist in exam_groups.items():
            total_obtained = sum(r.total_marks for r in rlist)
            total_max = sum(r.subject.max_marks for r in rlist)
            from results.models import calculate_sgpa
            sgpa, total_credits = calculate_sgpa(rlist)
            rlist.append({
                'is_total_row': True,
                'total_obtained': round(total_obtained, 2),
                'total_max': total_max,
                'sgpa': sgpa,
                'total_credits': total_credits,
            })
        ctx['exam_groups'] = exam_groups

        total_present = Attendance.objects.filter(student=student, status='present').count()
        total_days = Attendance.objects.filter(student=student).count()
        ctx['attendance_pct'] = round((total_present / total_days * 100)) if total_days else 0
        ctx['department_name'] = DEPT_NAMES.get(student.student_class.name, [student.student_class.name])[0]
        from clubs.models import ClubApplication, ClubMembership
        ctx['club_apps'] = ClubApplication.objects.filter(student=student).select_related('club')
        ctx['club_memberships'] = ClubMembership.objects.filter(student=student).select_related('club')
        from mentor.models import MentorAssignment
        try:
            mentor_assignment = MentorAssignment.objects.get(student=student, is_active=True)
            ctx['faculty_mentor'] = mentor_assignment.faculty
        except MentorAssignment.DoesNotExist:
            ctx['faculty_mentor'] = None
        return ctx

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        student = Student.objects.get(
            id=request.session.get('student_id'),
            is_deleted=False
        )
        if student.profile_photo:
            messages.error(request, 'You can only upload a photo once. Contact admin to change it.')
            return redirect('accounts:student_portal')
        if request.FILES.get('profile_photo'):
            student.profile_photo = request.FILES['profile_photo']
            student.save()
            messages.success(request, 'Profile photo uploaded successfully!')
        else:
            messages.error(request, 'Please select a photo to upload.')
        return redirect('accounts:student_portal')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from attendance.models import Attendance
        from django.utils import timezone
        from attendance.views import check_low_attendance
        import json, os, calendar
        from django.conf import settings

        today = timezone.localdate()
        total_students = Student.objects.filter(is_deleted=False).count()
        today_records = Attendance.objects.filter(date=today)
        today_total = today_records.count()
        today_present = today_records.filter(status='present').count()
        context['total_students'] = total_students
        context['today_attendance_pct'] = round((today_present / today_total * 100)) if today_total else 0
        context['today_total_attendance'] = today_total
        context['today_present'] = today_present
        context['classes_count'] = Class.objects.values('name').distinct().count()
        context['exams_count'] = Exam.objects.count()

        last_day = calendar.monthrange(today.year, today.month)[1]
        if today.day >= last_day - 1:
            tracker = settings.BASE_DIR / '.attendance_tracker.json'
            month_key = today.strftime('%Y-%m')
            last_sent = {}
            if tracker.exists():
                try:
                    last_sent = json.loads(tracker.read_text())
                except Exception:
                    pass
            if last_sent.get('month') != month_key:
                students = Student.objects.filter(is_deleted=False)
                sent_count = 0
                for s in students:
                    if check_low_attendance(s, month_key):
                        sent_count += 1
                last_sent['month'] = month_key
                tracker.write_text(json.dumps(last_sent))

        recent_students = Student.objects.filter(is_deleted=False).order_by('-created_at')[:5]
        recent_attendance = Attendance.objects.select_related('student').order_by('-date', '-id')[:5]
        from grievances.models import Grievance
        recent_grievances = Grievance.objects.order_by('-created_at')[:5]
        from leave_management.models import LeaveApplication
        recent_leaves = LeaveApplication.objects.order_by('-applied_at')[:5]
        from notices.models import Notice
        recent_notices = Notice.objects.filter(is_published=True).order_by('-created_at')[:3]

        context['recent_students'] = recent_students
        context['recent_attendance'] = recent_attendance
        context['recent_grievances'] = recent_grievances
        context['recent_leaves'] = recent_leaves
        context['recent_notices'] = recent_notices

        return context


DEPT_NAMES = {
    'TT': ('Textile Technology', 'Fiber science, yarn & fabric manufacturing, design & testing.'),
    'TC': ('Textile Chemistry', 'Dyeing, printing, finishing, polymer chemistry & processing.'),
    'MMFT': ('Man-Made Fiber Technology', 'Melt spinning, specialty fibers, nanocomposites.'),
    'ME': ('Mechanical Engineering', 'Design, thermal, manufacturing & automation.'),
    'ECE': ('Electronics & Communication Eng.', 'VLSI, embedded systems, IoT & signal processing.'),
    'CSE': ('Computer Science & Engineering', 'AI/ML, cybersecurity, cloud computing & data science.'),
}

class CollegeHomeView(TemplateView):
    template_name = 'college_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from attendance.models import Attendance
        from django.utils import timezone
        from .models import LeadershipMember, DirectorMessage, Department, PlacementPartner, Testimonial, ContactInfo
        from elections.models import Election, Position, Candidate
        from django.db.models import Max
        from notices.models import Notice
        from faculty.models import Faculty
        today = timezone.localdate()
        context['total_students'] = Student.objects.filter(is_deleted=False).count()
        context['classes_count'] = Class.objects.values('name').distinct().count()
        context['exams_count'] = Exam.objects.filter(start_date__year=today.year).count()
        context['leadership_members'] = LeadershipMember.objects.filter(is_active=True)
        context['director_message'] = DirectorMessage.objects.filter(is_active=True).first()
        context['departments'] = Department.objects.filter(is_active=True)
        context['placement_partners'] = PlacementPartner.objects.filter(is_active=True)
        context['testimonials'] = Testimonial.objects.filter(is_active=True)
        context['contact_info'] = ContactInfo.objects.filter(is_active=True).first()
        context['latest_notices'] = Notice.objects.filter(is_published=True)[:5]
        faculty_qs = Faculty.objects.filter(is_active=True)
        context['faculty_count'] = faculty_qs.count()
        context['faculty_phd_count'] = faculty_qs.filter(qualification__icontains='ph.d').count()

        election_winners = []
        ended_elections = Election.objects.filter(end_date__lt=timezone.now(), is_published=True)
        for election in ended_elections:
            positions = election.positions.all()
            for position in positions:
                max_votes = Candidate.objects.filter(
                    election=election, position=position
                ).aggregate(Max('vote_count'))['vote_count__max']
                if max_votes and max_votes > 0:
                    winners = Candidate.objects.filter(
                        election=election, position=position, vote_count=max_votes
                    ).select_related('student')[:position.max_winners]
                    for w in winners:
                        election_winners.append({
                            'election': election,
                            'position': position,
                            'candidate': w,
                        })
        context['election_winners'] = election_winners

        context['quick_links'] = [
            {'title': 'Admissions', 'icon': 'bi-pencil-square', 'url': '/accounts/admissions/'},
            {'title': 'Academic Calendar', 'icon': 'bi-calendar-event', 'url': '/accounts/academic-calendar/'},
            {'title': 'Faculty', 'icon': 'bi-people-fill', 'url': '/accounts/faculty/'},
            {'title': 'Clubs', 'icon': 'bi-people', 'url': '/clubs/'},
            {'title': 'Notices', 'icon': 'bi-megaphone', 'url': '/notices/'},
            {'title': 'Events', 'icon': 'bi-calendar-event', 'url': '/events/'},
            {'title': 'Fee Structure', 'icon': 'bi-currency-rupee', 'url': '/fees/'},
            {'title': 'Library', 'icon': 'bi-book', 'url': '/library/'},
            {'title': 'Timetable', 'icon': 'bi-calendar-week', 'url': '/timetable/'},
            {'title': 'Placements', 'icon': 'bi-briefcase', 'url': '/placements/drives/'},
            {'title': 'Hostel', 'icon': 'bi-building', 'url': '/hostel/'},
            {'title': 'NIRF', 'icon': 'bi-trophy', 'url': '/accounts/nirf/'},
            {'title': 'Photo Gallery', 'icon': 'bi-images', 'url': '/gallery/'},
            {'title': 'Alumni', 'icon': 'bi-people-fill', 'url': '/alumni/'},
            {'title': 'Elections', 'icon': 'bi-person-check', 'url': '/elections/'},
            {'title': 'Pay Online', 'icon': 'bi-wallet', 'url': '/fees/pay-online/'},
        ]
        return context


class ResultPortalView(TemplateView):
    template_name = 'result_portal.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        roll_number = self.request.GET.get('roll_number', '').strip()
        if roll_number:
            try:
                student = Student.objects.get(roll_number=roll_number, is_deleted=False)
                ctx['student'] = student
                ctx['department_name'] = DEPT_NAMES.get(student.student_class.name, [student.student_class.name])[0]
                branch = student.student_class.name
                current_sem = int(student.student_class.section.replace('Sem ', ''))
                ctx['semesters'] = list(range(1, current_sem + 1))
                selected_sem = self.request.GET.get('sem')
                if selected_sem:
                    try:
                        selected_sem = int(selected_sem)
                    except ValueError:
                        selected_sem = current_sem
                else:
                    selected_sem = current_sem
                ctx['selected_sem'] = selected_sem

                results = Result.objects.filter(student=student).select_related('exam', 'subject')
                if selected_sem:
                    results = [r for r in results if r.exam.student_class.section == f'Sem {selected_sem}']

                exam_groups = {}
                for r in results:
                    exam_groups.setdefault(r.exam, []).append(r)
                for exam, rlist in exam_groups.items():
                    total_obtained = sum(r.total_marks for r in rlist)
                    total_max = sum(r.subject.max_marks for r in rlist)
                    sgpa, total_credits = calculate_sgpa(rlist)
                    rlist.append({
                        'is_total_row': True,
                        'total_obtained': round(total_obtained, 2),
                        'total_max': total_max,
                        'sgpa': sgpa,
                        'total_credits': total_credits,
                    })
                ctx['exam_groups'] = exam_groups
            except Student.DoesNotExist:
                ctx['error'] = 'No student found with this roll number.'
        return ctx

@method_decorator(ensure_csrf_cookie, name='dispatch')
class PortfolioView(TemplateView):
    template_name = 'portfolio.html'
