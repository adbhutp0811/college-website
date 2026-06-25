import threading

from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View, TemplateView
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.mail import send_mail
from .models import Club, ClubMembership, ClubEvent, ClubApplication
from students.models import Student


CELL_CATEGORIES = ['Student Welfare', 'Career & Placement', 'Innovation & Entrepreneurship', 'Student Activities']


def _send_application_emails(club, student, reason=''):
    student_info = (
        f'  Name    : {student.full_name}\n'
        f'  Branch  : {student.student_class}\n'
        f'  Session : {student.session}\n'
        f'  Email   : {student.email}\n'
        f'  Contact : {student.contact_number}\n'
        f'  Reason  : {reason or "Not specified"}'
    )
    coords = ClubMembership.objects.filter(club=club, role__in=['coordinator', 'vice_coordinator']).select_related('student')
    for c in coords:
        if c.student.email:
            try:
                send_mail(
                    subject=f'📋 New Club Application - {club.name}',
                    message=(
                        f'Dear {c.student.full_name},\n\n'
                        f'A student has applied to join {club.name}. Below are the details:\n\n'
                        f'{student_info}\n\n'
                        f'Please log in to the student portal to review and take action.\n\n'
                        f'Regards,\n'
                        f'{club.name}\n'
                        f'Miracle Institute of Technology'
                    ),
                    from_email=None, recipient_list=[c.student.email], fail_silently=True,
                )
            except Exception:
                pass
    if club.coordinator and club.coordinator.email:
        try:
            send_mail(
                subject=f'📋 New Club Application - {club.name}',
                message=(
                    f'Dear {club.coordinator.get_full_name() or club.coordinator.username},\n\n'
                    f'A student has applied to join {club.name}. Below are the details:\n\n'
                    f'{student_info}\n\n'
                    f'Please log in to the staff portal to review and take action.\n\n'
                    f'Regards,\n'
                    f'{club.name}\n'
                    f'Miracle Institute of Technology'
                ),
                from_email=None, recipient_list=[club.coordinator.email], fail_silently=True,
            )
        except Exception:
            pass


class ClubListView(ListView):
    model = Club
    template_name = 'clubs/club_list.html'
    context_object_name = 'clubs'

    def get_queryset(self):
        return Club.objects.filter(is_active=True).exclude(category__in=CELL_CATEGORIES).prefetch_related(
            'memberships__student',
        )


class ClubDetailView(DetailView):
    model = Club
    template_name = 'clubs/club_detail.html'
    context_object_name = 'club'
    slug_field = 'pk'

    def get_queryset(self):
        return Club.objects.filter(is_active=True).prefetch_related(
            'memberships__student',
            'events',
            'coordinators',
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        club = self.object
        members = list(club.memberships.all().select_related('student'))
        members.sort(key=lambda m: {'coordinator': 0, 'vice_coordinator': 1, 'member': 2}.get(m.role, 3))
        ctx['members'] = members
        ctx['member_count'] = len(members)
        ctx['pending_apps'] = club.applications.filter(status='pending').count()
        ctx['coordinators'] = club.coordinators.all()

        student_id = self.request.session.get('student_id')
        if student_id:
            student = Student.objects.filter(id=student_id).first()
            ctx['student'] = student
            ctx['is_member'] = any(m.student_id == student_id for m in members) if student else False
            if student:
                app = club.applications.filter(student=student).first()
                ctx['application'] = app
                ctx['has_applied'] = app is not None
                ctx['app_status'] = app.status if app else None
            else:
                ctx['application'] = None
                ctx['has_applied'] = False
                ctx['app_status'] = None
        else:
            ctx['student'] = None
            ctx['is_member'] = False
            ctx['application'] = None
            ctx['has_applied'] = False
            ctx['app_status'] = None
        return ctx


@method_decorator(csrf_protect, name='dispatch')
class ClubApplyView(View):
    def post(self, request, *args, **kwargs):
        club = get_object_or_404(Club, pk=kwargs['pk'])
        roll = request.POST.get('roll_number', '').strip()
        reason = request.POST.get('reason', '').strip()

        try:
            student = Student.objects.get(roll_number=roll, is_deleted=False)
        except Student.DoesNotExist:
            messages.error(request, 'Student not found with this roll number.')
            return redirect('clubs:club_detail', pk=club.pk)

        if ClubMembership.objects.filter(club=club, student=student).exists():
            messages.warning(request, f'You are already a member of {club.name}.')
            return redirect('clubs:club_detail', pk=club.pk)

        existing = ClubApplication.objects.filter(club=club, student=student).first()
        if existing:
            if existing.status == 'pending':
                messages.warning(request, f'You have already applied to {club.name}. Wait for review.')
                return redirect('clubs:club_detail', pk=club.pk)
            existing.delete()

        ClubApplication.objects.create(club=club, student=student, reason=reason)
        threading.Thread(target=_send_application_emails, args=(club, student, reason), daemon=True).start()
        messages.success(request, f'Application submitted to {club.name}. Wait for approval.')
        return redirect('clubs:club_detail', pk=club.pk)


class StaffClubApplicationsView(LoginRequiredMixin, TemplateView):
    template_name = 'clubs/staff_applications.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        clubs = Club.objects.filter(coordinator=user)
        applications = ClubApplication.objects.filter(club__in=clubs, status='pending').select_related('student', 'club')
        ctx['applications'] = applications
        ctx['my_clubs'] = clubs
        return ctx

    def post(self, request):
        app_id = request.POST.get('application_id')
        action = request.POST.get('action')
        app = get_object_or_404(ClubApplication, pk=app_id, club__coordinator=request.user)

        if action == 'approve':
            app.status = 'approved'
            app.reviewed_at = timezone.now()
            app.reviewed_by = request.user
            app.save()
            ClubMembership.objects.get_or_create(club=app.club, student=app.student, defaults={'role': 'member'})
            try:
                send_mail(
                    subject=f'🎉 Club Application Approved - {app.club.name}',
                    message=(
                        f'Dear {app.student.full_name},\n\n'
                        f'Congratulations! Your application to join {app.club.name} has been approved. 🎉\n\n'
                        f'You are now a proud member of the club. Stay tuned for upcoming events and activities!\n\n'
                        f'Warm regards,\n'
                        f'{app.club.name}\n'
                        f'Miracle Institute of Technology'
                    ),
                    from_email=None, recipient_list=[app.student.email], fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, f'{app.student.full_name} approved for {app.club.name}.')

        elif action == 'reject':
            app.status = 'rejected'
            app.reviewed_at = timezone.now()
            app.reviewed_by = request.user
            app.save()
            try:
                send_mail(
                    subject=f'Club Application Status - {app.club.name}',
                    message=(
                        f'Dear {app.student.full_name},\n\n'
                        f'Thank you for your interest in joining {app.club.name}.\n\n'
                        f'After careful review, we regret to inform you that your application has not been approved at this time.\n\n'
                        f'We encourage you to apply again in the future and participate in our events.\n\n'
                        f'Warm regards,\n'
                        f'{app.club.name}\n'
                        f'Miracle Institute of Technology'
                    ),
                    from_email=None, recipient_list=[app.student.email], fail_silently=True,
                )
            except Exception:
                pass
            messages.info(request, f'{app.student.full_name} rejected for {app.club.name}.')

        return redirect('clubs:staff_applications')


class StudentClubManageView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('student_id'):
            messages.error(request, 'Please login first.')
            return redirect('accounts:student_login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        student_id = request.session['student_id']
        my_memberships = ClubMembership.objects.filter(
            student_id=student_id, role__in=['coordinator', 'vice_coordinator']
        ).select_related('club')
        club_ids = [m.club_id for m in my_memberships]
        applications = ClubApplication.objects.filter(club_id__in=club_ids, status='pending').select_related('student', 'club')
        members = list(ClubMembership.objects.filter(club_id__in=club_ids).select_related('student', 'club'))
        members.sort(key=lambda m: {'coordinator': 0, 'vice_coordinator': 1, 'member': 2}.get(m.role, 3))
        return render(request, 'clubs/student_manage.html', {
            'my_memberships': my_memberships,
            'my_clubs': [m.club for m in my_memberships],
            'applications': applications,
            'members': members,
            'is_coordinator': any(m.role == 'coordinator' for m in my_memberships),
        })

    def post(self, request):
        student_id = request.session['student_id']
        app_id = request.POST.get('application_id')
        member_id = request.POST.get('member_id')
        action = request.POST.get('action')

        if app_id:
            if action in ('approve', 'reject'):
                app = get_object_or_404(ClubApplication, pk=app_id)
                is_authorized = ClubMembership.objects.filter(
                    student_id=student_id, club=app.club, role__in=['coordinator', 'vice_coordinator']
                ).exists()
                if not is_authorized:
                    messages.error(request, 'You are not authorized for this club.')
                    return redirect('clubs:student_manage')

                if action == 'approve':
                    app.status = 'approved'
                    app.reviewed_at = timezone.now()
                    app.save()
                    ClubMembership.objects.get_or_create(club=app.club, student=app.student, defaults={'role': 'member'})
                    try:
                        send_mail(
                            subject=f'🎉 Club Application Approved - {app.club.name}',
                            message=(
                                f'Dear {app.student.full_name},\n\n'
                                f'Congratulations! Your application to join {app.club.name} has been approved. 🎉\n\n'
                                f'You are now a proud member of the club. Stay tuned for upcoming events and activities!\n\n'
                                f'Warm regards,\n'
                                f'{app.club.name}\n'
                                f'Miracle Institute of Technology'
                            ),
                            from_email=None, recipient_list=[app.student.email], fail_silently=True,
                        )
                    except Exception:
                        pass
                    messages.success(request, f'{app.student.full_name} approved for {app.club.name}.')
                elif action == 'reject':
                    app.status = 'rejected'
                    app.reviewed_at = timezone.now()
                    app.save()
                    try:
                        send_mail(
                            subject=f'Club Application Status - {app.club.name}',
                            message=(
                                f'Dear {app.student.full_name},\n\n'
                                f'Thank you for your interest in joining {app.club.name}.\n\n'
                                f'After careful review, we regret to inform you that your application has not been approved at this time.\n\n'
                                f'We encourage you to apply again in the future and participate in our events.\n\n'
                                f'Warm regards,\n'
                                f'{app.club.name}\n'
                                f'Miracle Institute of Technology'
                            ),
                            from_email=None, recipient_list=[app.student.email], fail_silently=True,
                        )
                    except Exception:
                        pass
                    messages.info(request, f'{app.student.full_name} rejected for {app.club.name}.')

        elif member_id and action in ('set_vc', 'remove', 'demote'):
            membership = get_object_or_404(ClubMembership, pk=member_id)
            is_coord = ClubMembership.objects.filter(
                student_id=student_id, club=membership.club, role='coordinator'
            ).exists()
            if not is_coord:
                messages.error(request, 'Only the coordinator can manage members.')
                return redirect('clubs:student_manage')

            if action == 'set_vc':
                membership.role = 'vice_coordinator'
                membership.save()
                if membership.student.email:
                    try:
                        send_mail(
                            subject=f'🎖 Congratulations - Vice Coordinator of {membership.club.name}',
                            message=(
                                f'Dear {membership.student.full_name},\n\n'
                                f'Congratulations! You have been promoted to Vice Coordinator of {membership.club.name}. 🎉\n\n'
                                f'We look forward to your leadership and contributions.\n\n'
                                f'Warm regards,\n'
                                f'{membership.club.name}\n'
                                f'Miracle Institute of Technology'
                            ),
                            from_email=None, recipient_list=[membership.student.email], fail_silently=True,
                        )
                    except Exception:
                        pass
                messages.success(request, f'{membership.student.full_name} is now Vice Coordinator.')
            elif action == 'demote':
                membership.role = 'member'
                membership.save()
                if membership.student.email:
                    try:
                        send_mail(
                            subject=f'Role Update - {membership.club.name}',
                            message=(
                                f'Dear {membership.student.full_name},\n\n'
                                f'Your role in {membership.club.name} has been updated to Member.\n\n'
                                f'Thank you for your service as Vice Coordinator. We value your continued participation.\n\n'
                                f'Warm regards,\n'
                                f'{membership.club.name}\n'
                                f'Miracle Institute of Technology'
                            ),
                            from_email=None, recipient_list=[membership.student.email], fail_silently=True,
                        )
                    except Exception:
                        pass
                messages.info(request, f'{membership.student.full_name} demoted to Member.')
            elif action == 'remove':
                club_name = membership.club.name
                student_email = membership.student.email
                student_name = membership.student.full_name
                membership.delete()
                if student_email:
                    try:
                        send_mail(
                            subject=f'Membership Update - {club_name}',
                            message=(
                                f'Dear {student_name},\n\n'
                                f'You have been removed from {club_name}.\n\n'
                                f'If you have any questions, please contact the club coordinator.\n\n'
                                f'Warm regards,\n'
                                f'{club_name}\n'
                                f'Miracle Institute of Technology'
                            ),
                            from_email=None, recipient_list=[student_email], fail_silently=True,
                        )
                    except Exception:
                        pass
                messages.info(request, f'{student_name} removed from club.')

        return redirect('clubs:student_manage')
