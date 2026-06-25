import threading

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from accounts.models import User
from students.models import Student
from .models import MentorAssignment, MentorMeeting, MentorMeetingAttendance, MentorNote, PeerMentor


def _send_faculty_mentor_email(student, faculty):
    if student.email:
        try:
            send_mail(
                subject='🎓 Faculty Mentor Assigned',
                message=(
                    f'Dear {student.full_name},\n\n'
                    f'You have been assigned a faculty mentor: {faculty.get_full_name()}.\n'
                    f'Email: {faculty.email}\n\n'
                    f'Please log in to the student portal to view your mentor details.\n\n'
                    f'Regards,\n'
                    f'Miracle Institute of Technology'
                ),
                from_email=None, recipient_list=[student.email], fail_silently=True,
            )
        except Exception:
            pass


def _send_peer_mentor_email(mentee, mentor):
    if mentee.email:
        try:
            send_mail(
                subject='👥 Peer Mentor Assigned',
                message=(
                    f'Dear {mentee.full_name},\n\n'
                    f'You have been assigned a peer mentor: {mentor.full_name} ({mentor.roll_number}).\n'
                    f'Your peer mentor is a final year student who will guide you.\n\n'
                    f'Please log in to the student portal to view your peer mentor details.\n\n'
                    f'Regards,\n'
                    f'Miracle Institute of Technology'
                ),
                from_email=None, recipient_list=[mentee.email], fail_silently=True,
            )
        except Exception:
            pass


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
        filter_type = request.GET.get('filter', '')
        students = Student.objects.filter(is_deleted=False)
        if filter_type == 'final_year':
            students = students.filter(student_class__section__in=['Sem 7', 'Sem 8'])
        assignments = MentorAssignment.objects.filter(is_active=True).select_related('faculty', 'student')
        all_count = Student.objects.filter(is_deleted=False).count()
        final_year_count = Student.objects.filter(is_deleted=False, student_class__section__in=['Sem 7', 'Sem 8']).count()
        return render(request, self.template_name, {
            'faculty_list': faculty_list,
            'students': students,
            'assignments': assignments,
            'filter_type': filter_type,
            'all_count': all_count,
            'final_year_count': final_year_count,
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
                faculty = User.objects.get(pk=faculty_id)
                student = Student.objects.get(pk=student_id)
                MentorAssignment.objects.update_or_create(
                    student_id=student_id,
                    defaults={'faculty_id': faculty_id, 'is_active': True}
                )
                threading.Thread(target=_send_faculty_mentor_email, args=(student, faculty), daemon=True).start()
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


class AssignPeerMentorView(StaffRequiredMixin, View):
    template_name = 'mentor/peer_assign.html'

    def get(self, request):
        mentors = Student.objects.filter(is_deleted=False, student_class__section__in=['Sem 7', 'Sem 8'])
        mentees = Student.objects.filter(is_deleted=False, student_class__section__in=['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4', 'Sem 5', 'Sem 6'])
        assignments = PeerMentor.objects.filter(is_active=True).select_related('mentor', 'mentee')
        return render(request, self.template_name, {
            'mentors': mentors,
            'mentees': mentees,
            'assignments': assignments,
        })

    def post(self, request):
        mentor_id = request.POST.get('mentor')
        mentee_id = request.POST.get('mentee')
        action = request.POST.get('action', 'assign')
        if action == 'remove':
            PeerMentor.objects.filter(mentor_id=mentor_id, mentee_id=mentee_id).update(is_active=False)
            messages.success(request, 'Peer mentor assignment removed.')
        else:
            if mentor_id and mentee_id:
                mentor = get_object_or_404(Student, pk=mentor_id)
                mentee = get_object_or_404(Student, pk=mentee_id)
                current_count = PeerMentor.objects.filter(mentor=mentor, is_active=True).count()
                if current_count >= 5:
                    messages.error(request, f'{mentor.full_name} already has {current_count} mentees. Max 5 allowed.')
                    return redirect('mentor:peer_assign')
                PeerMentor.objects.update_or_create(
                    mentee_id=mentee_id,
                    defaults={'mentor_id': mentor_id, 'is_active': True}
                )
                threading.Thread(target=_send_peer_mentor_email, args=(mentee, mentor), daemon=True).start()
                messages.success(request, 'Peer mentor assigned successfully.')
        return redirect('mentor:peer_assign')
