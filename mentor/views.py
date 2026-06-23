from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from accounts.models import User
from students.models import Student
from .models import MentorAssignment, MentorMeeting, MentorMeetingAttendance, MentorNote


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['admin', 'teacher']


class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.session.get('student_id') is not None


class MentorDashboardView(StaffRequiredMixin, TemplateView):
    template_name = 'mentor/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        faculty = self.request.user
        mentees = Student.objects.filter(mentor__faculty=faculty, mentor__is_active=True)
        meetings = MentorMeeting.objects.filter(faculty=faculty)
        ctx['mentee_count'] = mentees.count()
        ctx['meeting_count'] = meetings.count()
        ctx['recent_meetings'] = meetings[:5]
        ctx['recent_notes'] = MentorNote.objects.filter(faculty=faculty)[:5]
        return ctx


class MyMenteesView(StaffRequiredMixin, ListView):
    template_name = 'mentor/my_mentees.html'
    context_object_name = 'mentees'

    def get_queryset(self):
        return Student.objects.filter(mentor__faculty=self.request.user, mentor__is_active=True).select_related('student_class')


class MenteeDetailView(StaffRequiredMixin, DetailView):
    model = Student
    template_name = 'mentor/mentee_detail.html'
    context_object_name = 'mentee'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['notes'] = MentorNote.objects.filter(student=self.get_object(), faculty=self.request.user)
        return ctx


class AddMentorNoteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        note_text = request.POST.get('note', '').strip()
        if note_text:
            MentorNote.objects.create(student=student, faculty=request.user, note=note_text)
            messages.success(request, 'Note added successfully.')
        else:
            messages.error(request, 'Note cannot be empty.')
        return redirect('mentor:mentee_detail', pk=pk)


class MeetingListView(StaffRequiredMixin, ListView):
    template_name = 'mentor/meeting_list.html'
    context_object_name = 'meetings'

    def get_queryset(self):
        return MentorMeeting.objects.filter(faculty=self.request.user).prefetch_related('attendees__student')


class CreateMeetingView(StaffRequiredMixin, View):
    template_name = 'mentor/create_meeting.html'

    def get(self, request):
        mentees = Student.objects.filter(mentor__faculty=request.user, mentor__is_active=True)
        return render(request, self.template_name, {'mentees': mentees})

    def post(self, request):
        meeting_date = request.POST.get('meeting_date')
        notes = request.POST.get('notes', '').strip()
        student_ids = request.POST.getlist('students')
        if not meeting_date or not notes or not student_ids:
            messages.error(request, 'All fields are required.')
            return redirect('mentor:create_meeting')
        meeting = MentorMeeting.objects.create(faculty=request.user, meeting_date=meeting_date, notes=notes)
        for sid in student_ids:
            student = get_object_or_404(Student, pk=sid)
            MentorMeetingAttendance.objects.create(meeting=meeting, student=student)
        messages.success(request, f'Meeting recorded with {len(student_ids)} students.')
        return redirect('mentor:meetings')


class AssignMentorView(StaffRequiredMixin, View):
    template_name = 'mentor/assign.html'

    def get(self, request):
        faculty_list = User.objects.filter(role='teacher')
        students = Student.objects.filter(is_deleted=False)
        assignments = MentorAssignment.objects.filter(is_active=True).select_related('faculty', 'student')
        return render(request, self.template_name, {
            'faculty_list': faculty_list,
            'students': students,
            'assignments': assignments,
        })

    def post(self, request):
        faculty_id = request.POST.get('faculty')
        student_id = request.POST.get('student')
        action = request.POST.get('action', 'assign')
        if action == 'remove':
            MentorAssignment.objects.filter(faculty_id=faculty_id, student_id=student_id).update(is_active=False)
            messages.success(request, 'Mentor assignment removed.')
        else:
            if faculty_id and student_id:
                MentorAssignment.objects.update_or_create(
                    student_id=student_id,
                    defaults={'faculty_id': faculty_id, 'is_active': True}
                )
                messages.success(request, 'Mentor assigned successfully.')
        return redirect('mentor:assign')


class StudentMentorView(StudentRequiredMixin, TemplateView):
    template_name = 'mentor/student_mentor.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student_id = self.request.session.get('student_id')
        student = get_object_or_404(Student, pk=student_id)
        try:
            assignment = MentorAssignment.objects.get(student=student, is_active=True)
            ctx['mentor'] = assignment.faculty
            ctx['notes'] = MentorNote.objects.filter(student=student)
            ctx['meetings'] = MentorMeetingAttendance.objects.filter(student=student).select_related('meeting')
        except MentorAssignment.DoesNotExist:
            ctx['mentor'] = None
        ctx['student'] = student
        return ctx
