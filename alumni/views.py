from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib import messages
from .models import Alumni, AlumniEvent, EventRegistration, Donation
from .forms import AlumniRegistrationForm, AlumniProfileForm, DonationForm, EventForm


class AlumniDirectoryView(ListView):
    model = Alumni
    template_name = 'alumni/directory.html'
    context_object_name = 'alumni_list'
    paginate_by = 20

    def get_queryset(self):
        qs = Alumni.objects.filter(is_verified=True, is_visible=True)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(first_name__icontains=q) | qs.filter(last_name__icontains=q) | qs.filter(company__icontains=q)
        year = self.request.GET.get('graduation_year')
        if year:
            qs = qs.filter(graduation_year=year)
        program = self.request.GET.get('program')
        if program:
            qs = qs.filter(program__icontains=program)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['years'] = Alumni.BATCH_YEARS
        return ctx


class AlumniRegistrationView(CreateView):
    model = Alumni
    form_class = AlumniRegistrationForm
    template_name = 'alumni/register.html'
    success_url = reverse_lazy('alumni:registration_success')

    def form_valid(self, form):
        student_id = self.request.session.get('student_id')
        if student_id:
            from students.models import Student
            try:
                form.instance.student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                pass
        messages.success(self.request, 'Registration submitted successfully!')
        return super().form_valid(form)


class RegistrationSuccessView(TemplateView):
    template_name = 'alumni/registration_success.html'


class AlumniProfileView(UpdateView):
    model = Alumni
    form_class = AlumniProfileForm
    template_name = 'alumni/profile.html'
    success_url = reverse_lazy('alumni:my_profile')

    def get_object(self, queryset=None):
        email = self.request.session.get('alumni_email')
        if email:
            return get_object_or_404(Alumni, email=email)
        student_id = self.request.session.get('student_id')
        if student_id:
            alumni = Alumni.objects.filter(student_id=student_id).first()
            if alumni:
                return alumni
        return get_object_or_404(Alumni, pk=self.request.GET.get('pk'))

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class AlumniEventListView(ListView):
    model = AlumniEvent
    template_name = 'alumni/event_list.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        return AlumniEvent.objects.filter(is_published=True)


class AlumniEventDetailView(DetailView):
    model = AlumniEvent
    template_name = 'alumni/event_detail.html'
    context_object_name = 'event'
    pk_url_kwarg = 'event_id'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        alumni_email = self.request.session.get('alumni_email')
        ctx['is_registered'] = False
        if alumni_email:
            alumni = Alumni.objects.filter(email=alumni_email).first()
            if alumni:
                ctx['is_registered'] = EventRegistration.objects.filter(alumni=alumni, event=self.object).exists()
                ctx['alumni'] = alumni
        return ctx


class RegisterForEventView(View):
    def post(self, request, event_id):
        event = get_object_or_404(AlumniEvent, pk=event_id, is_published=True)
        alumni_email = request.session.get('alumni_email')
        if not alumni_email:
            messages.error(request, 'Please register your alumni profile first.')
            return redirect('alumni:register')
        alumni = get_object_or_404(Alumni, email=alumni_email)
        if EventRegistration.objects.filter(alumni=alumni, event=event).exists():
            messages.warning(request, 'You are already registered for this event.')
            return redirect('alumni:event_detail', event_id=event_id)
        if event.max_participants > 0 and event.registrations.count() >= event.max_participants:
            messages.error(request, 'Sorry, this event is fully booked.')
            return redirect('alumni:event_detail', event_id=event_id)
        EventRegistration.objects.create(alumni=alumni, event=event)
        messages.success(request, f'Successfully registered for "{event.title}"!')
        return redirect('alumni:event_detail', event_id=event_id)


class DonationView(CreateView):
    model = Donation
    form_class = DonationForm
    template_name = 'alumni/donate.html'
    success_url = reverse_lazy('alumni:donation_success')

    def form_valid(self, form):
        alumni_email = self.request.session.get('alumni_email')
        if alumni_email:
            alumni = Alumni.objects.filter(email=alumni_email).first()
            if alumni:
                form.instance.alumni = alumni
        messages.success(self.request, 'Thank you for your donation!')
        return super().form_valid(form)


class DonationSuccessView(TemplateView):
    template_name = 'alumni/donation_success.html'


class ManageAlumniView(LoginRequiredMixin, ListView):
    model = Alumni
    template_name = 'alumni/manage_alumni.html'
    context_object_name = 'alumni_list'
    paginate_by = 50

    def get_queryset(self):
        qs = Alumni.objects.all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(first_name__icontains=q) | qs.filter(last_name__icontains=q) | qs.filter(email__icontains=q)
        return qs


class VerifyAlumniView(LoginRequiredMixin, View):
    def post(self, request, pk):
        alumni = get_object_or_404(Alumni, pk=pk)
        alumni.is_verified = not alumni.is_verified
        alumni.save()
        status = 'verified' if alumni.is_verified else 'unverified'
        messages.success(request, f'{alumni.first_name} {alumni.last_name} is now {status}.')
        return redirect('alumni:manage')


class DeleteAlumniView(LoginRequiredMixin, DeleteView):
    model = Alumni
    template_name = 'alumni/confirm_delete.html'
    success_url = reverse_lazy('alumni:manage')
    context_object_name = 'object'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Alumni record deleted successfully.')
        return super().delete(request, *args, **kwargs)


class ManageEventsView(LoginRequiredMixin, ListView):
    model = AlumniEvent
    template_name = 'alumni/manage_events.html'
    context_object_name = 'events'
    paginate_by = 50

    def get_queryset(self):
        return AlumniEvent.objects.all()


class CreateEventView(LoginRequiredMixin, CreateView):
    model = AlumniEvent
    form_class = EventForm
    template_name = 'alumni/event_form.html'
    success_url = reverse_lazy('alumni:manage_events')

    def form_valid(self, form):
        messages.success(self.request, 'Event created successfully!')
        return super().form_valid(form)


class EditEventView(LoginRequiredMixin, UpdateView):
    model = AlumniEvent
    form_class = EventForm
    template_name = 'alumni/event_form.html'
    success_url = reverse_lazy('alumni:manage_events')
    pk_url_kwarg = 'event_id'

    def form_valid(self, form):
        messages.success(self.request, 'Event updated successfully!')
        return super().form_valid(form)


class DeleteEventView(LoginRequiredMixin, DeleteView):
    model = AlumniEvent
    template_name = 'alumni/confirm_delete.html'
    success_url = reverse_lazy('alumni:manage_events')
    pk_url_kwarg = 'event_id'
    context_object_name = 'object'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Event deleted successfully.')
        return super().delete(request, *args, **kwargs)


class DonationListView(LoginRequiredMixin, ListView):
    model = Donation
    template_name = 'alumni/donation_list.html'
    context_object_name = 'donations'
    paginate_by = 50

    def get_queryset(self):
        qs = Donation.objects.all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(donor_name__icontains=q) | qs.filter(donor_email__icontains=q)
        return qs
