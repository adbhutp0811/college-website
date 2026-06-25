from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, FormView, ListView, TemplateView
from students.models import Class, Student
from .forms import AttendanceForm, BulkAttendanceForm
from .models import Attendance
from .sms_utils import send_sms


def check_low_attendance(student, month):
    year, m = month.split('-')
    records = Attendance.objects.filter(student=student, date__year=year, date__month=m)
    total = records.count()
    if total == 0:
        return False
    present = records.filter(status='present').count()
    pct = round((present / total * 100))
    if pct >= 75 or not student.email:
        return False
    try:
        send_mail(
            subject='Low Attendance Alert',
            message=(
                f'Dear {student.full_name},\n\n'
                f'Your attendance for {month} is {pct}%, which is below the required 75%.\n'
                f'Total working days: {total}\n'
                f'Days present: {present}\n'
                f'Attendance: {pct}%\n\n'
                f'Please ensure regular attendance.\n\n'
                f'- Miracle Institute of Technology'
            ),
            from_email=None,
            recipient_list=[student.email],
            fail_silently=True,
        )
        return True
    except Exception:
        return False


class MarkAttendanceView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/mark_attendance.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = AttendanceForm()
        ctx['classes'] = Class.objects.all()
        return ctx


class GetStudentsForClassView(LoginRequiredMixin, View):
    def get(self, request, class_id):
        date = request.GET.get('date', '')
        students = Student.objects.filter(student_class_id=class_id, is_deleted=False)
        existing = Attendance.objects.filter(date=date, student__student_class_id=class_id)
        existing_map = {a.student_id: a.status for a in existing}
        data = []
        for s in students:
            data.append({
                'id': s.id,
                'name': s.full_name,
                'roll': s.roll_number,
                'status': existing_map.get(s.id, 'present'),
                'photo': s.profile_photo.url if s.profile_photo else '',
            })
        return JsonResponse({'students': data})


class SaveAttendanceView(LoginRequiredMixin, View):
    def post(self, request):
        date = request.POST.get('date')
        class_id = request.POST.get('class_id')
        statuses = {k: v for k, v in request.POST.items() if k.startswith('status_')}
        student_ids = Student.objects.filter(
            student_class_id=class_id, is_deleted=False
        ).values_list('id', flat=True)
        sms_sent = 0
        for sid in student_ids:
            status = statuses.get(f'status_{sid}', 'present')
            Attendance.objects.update_or_create(
                student_id=sid,
                date=date,
                defaults={
                    'student_class_id': class_id,
                    'status': status,
                    'marked_by': request.user,
                }
            )
            if status == 'absent':
                try:
                    student = Student.objects.get(pk=sid)
                    if student.guardian_contact:
                        msg = (
                            f'Dear Parent, your ward {student.full_name} ({student.roll_number}) '
                            f'was marked ABSENT on {date}. '
                            f'- Miracle Institute of Technology'
                        )
                        if send_sms(student.guardian_contact, msg):
                            sms_sent += 1
                except Student.DoesNotExist:
                    pass
        msg = 'Attendance saved successfully!'
        if sms_sent:
            msg += f' Auto-SMS sent to {sms_sent} guardian(s).'
        messages.success(request, msg)
        return redirect('attendance:mark')


class AttendanceHistoryView(LoginRequiredMixin, ListView):
    model = Attendance
    template_name = 'attendance/attendance_history.html'
    context_object_name = 'records'
    paginate_by = 30

    def get_queryset(self):
        qs = Attendance.objects.select_related('student', 'student_class')
        student_id = self.request.GET.get('student_id', '')
        class_id = self.request.GET.get('class', '')
        month = self.request.GET.get('month', '')
        if student_id:
            qs = qs.filter(student_id=student_id)
        if class_id:
            qs = qs.filter(student_class_id=class_id)
        if month:
            year, m = month.split('-')
            qs = qs.filter(date__year=year, date__month=m)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['classes'] = Class.objects.all()
        ctx['students'] = Student.objects.filter(is_deleted=False)
        ctx['current_class'] = self.request.GET.get('class', '')
        ctx['current_student'] = self.request.GET.get('student_id', '')
        ctx['current_month'] = self.request.GET.get('month', '')
        return ctx


class AttendanceSummaryView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/attendance_summary.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        class_id = self.request.GET.get('class', '')
        month = self.request.GET.get('month', timezone.localdate().strftime('%Y-%m'))
        ctx['classes'] = Class.objects.all()
        ctx['current_class'] = class_id
        ctx['current_month'] = month
        students = Student.objects.filter(is_deleted=False)
        if class_id:
            students = students.filter(student_class_id=class_id)
        summary = []
        for s in students:
            records = Attendance.objects.filter(student=s)
            if month:
                year, m = month.split('-')
                records = records.filter(date__year=year, date__month=m)
            total = records.count()
            present = records.filter(status='present').count()
            absent = records.filter(status='absent').count()
            late = records.filter(status='late').count()
            leave = records.filter(status='leave').count()
            pct = round((present / total * 100)) if total else 0
            summary.append({
                'student': s,
                'total': total,
                'present': present,
                'absent': absent,
                'late': late,
                'leave': leave,
                'percentage': pct,
            })
        ctx['summary'] = summary
        return ctx


class AttendanceNotifyView(LoginRequiredMixin, View):
    def post(self, request):
        student_id = request.POST.get('student_id')
        class_id = request.POST.get('class_id')
        today = timezone.localdate()

        if student_id:
            students = Student.objects.filter(pk=student_id, is_deleted=False)
        elif class_id:
            students = Student.objects.filter(student_class_id=class_id, is_deleted=False)
        else:
            students = Student.objects.filter(is_deleted=False)

        sent = 0
        skipped = 0
        for student in students:
            if not student.email:
                skipped += 1
                continue
            absences = Attendance.objects.filter(student=student, status='absent', date=today)
            if not absences.exists():
                skipped += 1
                continue
            try:
                send_mail(
                    subject='Attendance Alert - Absent Today',
                    message=f'Dear {student.full_name},\n\nYou were marked ABSENT on {today}.\n\nPlease contact the institute for more details.\n\n- Miracle Institute of Technology',
                    from_email=None,
                    recipient_list=[student.email],
                    fail_silently=True,
                )
                sent += 1
            except Exception:
                skipped += 1
        msg = f'Attendance alerts sent to {sent} student(s).'
        if skipped:
            msg += f' {skipped} skipped.'
        messages.success(request, msg)
        return redirect('attendance:summary')


class AttendanceSMSView(LoginRequiredMixin, View):
    def post(self, request):
        class_id = request.POST.get('class_id')
        student_id = request.POST.get('student_id')
        date = request.POST.get('date', '')
        status_filter = request.POST.get('status', 'absent')

        if student_id:
            students = Student.objects.filter(pk=student_id, is_deleted=False)
        elif class_id:
            students = Student.objects.filter(student_class_id=class_id, is_deleted=False)
        else:
            messages.error(request, 'Please select a class or student.')
            return redirect('attendance:summary')

        sent = 0
        skipped = 0

        for s in students:
            if not s.guardian_contact:
                skipped += 1
                continue

            records = Attendance.objects.filter(student=s)
            if date:
                records = records.filter(date=date)
            if status_filter:
                records = records.filter(status=status_filter)

            if not records.exists():
                skipped += 1
                continue

            absent_dates = records.filter(status='absent').values_list('date', flat=True)
            msg = (
                f'Dear Parent, your ward {s.full_name} ({s.roll_number}) '
                f'was absent on {", ".join(d.strftime("%d-%b") for d in absent_dates)}. '
                f'- Miracle Institute of Technology'
            )

            if send_sms(s.guardian_contact, msg):
                sent += 1
            else:
                skipped += 1

        msg_text = f'Attendance SMS sent to {sent} guardian(s).'
        if skipped:
            msg_text += f' {skipped} skipped (no contact or no absences).'
        messages.success(request, msg_text)
        return redirect('attendance:summary')


class CustomSMSView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/custom_sms.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['classes'] = Class.objects.all()
        ctx['students'] = Student.objects.filter(is_deleted=False)
        return ctx

    def post(self, request):
        student_id = request.POST.get('student_id')
        message = request.POST.get('message', '').strip()

        if not student_id or not message:
            messages.error(request, 'Please select a student and enter a message.')
            return redirect('attendance:custom_sms')

        student = get_object_or_404(Student, pk=student_id)

        if not student.guardian_contact:
            messages.error(request, f'{student.full_name} has no guardian contact number.')
            return redirect('attendance:custom_sms')

        full_msg = f'Dear Parent, {message} - Miracle Institute of Technology'
        if send_sms(student.guardian_contact, full_msg):
            messages.success(request, f'SMS sent to guardian of {student.full_name}.')
        else:
            messages.error(request, 'Failed to send SMS.')

        return redirect('attendance:custom_sms')


class CustomEmailView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/custom_email.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['classes'] = Class.objects.all()
        ctx['students'] = Student.objects.filter(is_deleted=False)
        return ctx

    def post(self, request):
        student_id = request.POST.get('student_id')
        class_id = request.POST.get('class_id')
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not subject or not message:
            messages.error(request, 'Please fill in all fields.')
            return redirect('attendance:custom_email')

        if student_id:
            students = Student.objects.filter(pk=student_id, is_deleted=False)
        elif class_id:
            students = Student.objects.filter(student_class_id=class_id, is_deleted=False)
        else:
            students = Student.objects.filter(is_deleted=False)

        if not students.exists():
            messages.error(request, 'No students found for the selected criteria.')
            return redirect('attendance:custom_email')

        sent = 0
        skipped = 0
        for student in students:
            if not student.email:
                skipped += 1
                continue
            full_msg = f'Dear {student.full_name},\n\n{message}\n\n- Miracle Institute of Technology'
            try:
                send_mail(
                    subject=subject,
                    message=full_msg,
                    from_email=None,
                    recipient_list=[student.email],
                    fail_silently=False,
                )
                sent += 1
            except Exception:
                skipped += 1

        msg_text = f'Email sent to {sent} student(s).'
        if skipped:
            msg_text += f' {skipped} skipped (no email address or send failed).'
        messages.success(request, msg_text)
        return redirect('attendance:custom_email')
