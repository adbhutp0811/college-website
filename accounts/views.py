from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View
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
        today = timezone.localdate()
        context['total_students'] = Student.objects.filter(is_deleted=False).count()
        context['classes_count'] = Class.objects.values('name').distinct().count()
        context['exams_count'] = Exam.objects.count()
        context['departments'] = [
            {'code': code, 'name': full, 'desc': desc}
            for code, (full, desc) in sorted(DEPT_NAMES.items())
        ]
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
