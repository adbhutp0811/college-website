from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView
from results.models import Exam, Subject
from students.models import Student
from .models import ExamSchedule, SeatAllocation


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['admin', 'teacher']


class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.session.get('student_id') is not None


class ScheduleListView(ListView):
    model = ExamSchedule
    template_name = 'exam_seating/schedule_list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        return ExamSchedule.objects.all().select_related('exam', 'subject').order_by('exam_date', 'start_time')


class ScheduleDetailView(DetailView):
    model = ExamSchedule
    template_name = 'exam_seating/schedule_detail.html'
    context_object_name = 'schedule'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['seats'] = SeatAllocation.objects.filter(schedule=self.get_object()).select_related('student')
        return ctx


class CreateScheduleView(StaffRequiredMixin, View):
    template_name = 'exam_seating/create_schedule.html'

    def get(self, request):
        exams = Exam.objects.all()
        subjects = Subject.objects.all()
        return render(request, self.template_name, {'exams': exams, 'subjects': subjects})

    def post(self, request):
        exam = get_object_or_404(Exam, pk=request.POST.get('exam'))
        subject = get_object_or_404(Subject, pk=request.POST.get('subject'))
        ExamSchedule.objects.create(
            exam=exam,
            subject=subject,
            exam_date=request.POST.get('exam_date'),
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
            room=request.POST.get('room'),
            notes=request.POST.get('notes', ''),
        )
        messages.success(request, 'Exam schedule created successfully.')
        return redirect('exam_seating:schedule_list')


class AllocateSeatsView(StaffRequiredMixin, View):
    template_name = 'exam_seating/allocate_seats.html'

    def get(self, request, pk):
        schedule = get_object_or_404(ExamSchedule, pk=pk)
        students = Student.objects.filter(student_class=schedule.subject.student_class, is_deleted=False)
        existing = SeatAllocation.objects.filter(schedule=schedule).select_related('student')
        return render(request, self.template_name, {
            'schedule': schedule,
            'students': students,
            'existing': existing,
        })

    def post(self, request, pk):
        schedule = get_object_or_404(ExamSchedule, pk=pk)
        SeatAllocation.objects.filter(schedule=schedule).delete()
        student_ids = request.POST.getlist('students')
        for i, sid in enumerate(student_ids, start=1):
            student = get_object_or_404(Student, pk=sid)
            SeatAllocation.objects.create(schedule=schedule, student=student, seat_number=str(i))
        messages.success(request, f'Seats allocated for {len(student_ids)} students.')
        return redirect('exam_seating:schedule_detail', pk=pk)


class StudentSeatingView(StudentRequiredMixin, ListView):
    template_name = 'exam_seating/student_seating.html'
    context_object_name = 'seats'

    def get_queryset(self):
        student_id = self.request.session.get('student_id')
        return SeatAllocation.objects.filter(student_id=student_id).select_related('schedule__exam', 'schedule__subject')
