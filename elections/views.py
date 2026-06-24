from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, TemplateView
from students.models import Student
from .models import Position, Election, Candidate, Vote


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['admin', 'teacher']

    login_url = 'accounts:login'


def get_student(request):
    sid = request.session.get('student_id')
    if not sid:
        return None
    try:
        return Student.objects.get(id=sid, is_deleted=False)
    except Student.DoesNotExist:
        return None


class StudentRequiredMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('student_id'):
            messages.error(request, 'Please login as a student first.')
            return redirect('accounts:student_login')
        try:
            Student.objects.get(id=request.session['student_id'], is_deleted=False)
        except Student.DoesNotExist:
            del request.session['student_id']
            messages.error(request, 'Session expired. Please login again.')
            return redirect('accounts:student_login')
        return super().dispatch(request, *args, **kwargs)


class ElectionListView(ListView):
    template_name = 'elections/election_list.html'
    context_object_name = 'elections'

    def get_queryset(self):
        return Election.objects.filter(is_published=True).prefetch_related('positions')


class ElectionDetailView(View):
    template_name = 'elections/election_detail.html'

    def get(self, request, election_id):
        election = get_object_or_404(Election, pk=election_id)
        student = get_student(request)
        voted_positions = set()
        my_candidacies = set()
        if student:
            voted_positions = set(
                Vote.objects.filter(student=student, election=election)
                .values_list('position_id', flat=True)
            )
            my_candidacies = set(
                Candidate.objects.filter(student=student, election=election)
                .values_list('position_id', flat=True)
            )
        candidates = Candidate.objects.filter(
            election=election
        ).select_related('student', 'position').order_by('position__display_order', 'student')
        positions = election.positions.all().order_by('display_order')
        return render(request, self.template_name, {
            'election': election,
            'positions': positions,
            'candidates': candidates,
            'student': student,
            'voted_positions': voted_positions,
            'my_candidacies': my_candidacies,
        })


class CastVoteView(StudentRequiredMixin, View):
    def post(self, request, election_id):
        election = get_object_or_404(Election, pk=election_id)
        if not election.is_ongoing:
            messages.error(request, 'This election is not currently open for voting.')
            return redirect('elections:election_detail', election_id=election_id)

        student = get_student(request)
        if not student:
            messages.error(request, 'Please login as a student.')
            return redirect('accounts:student_login')

        candidate_id = request.POST.get('candidate_id')
        candidate = get_object_or_404(Candidate, pk=candidate_id, election=election)

        if Candidate.objects.filter(student=student, election=election, position=candidate.position).exists():
            messages.error(request, 'You are a candidate in this election and cannot vote.')
            return redirect('elections:election_detail', election_id=election_id)

        if Vote.objects.filter(student=student, election=election, position=candidate.position).exists():
            messages.error(request, 'You have already voted for this position.')
            return redirect('elections:election_detail', election_id=election_id)

        Vote.objects.create(
            student=student,
            election=election,
            candidate=candidate,
            position=candidate.position,
        )
        Candidate.objects.filter(pk=candidate.pk).update(vote_count=F('vote_count') + 1)

        messages.success(request, f'Your vote for {candidate.position.title} has been cast successfully!')
        return redirect('elections:election_detail', election_id=election_id)


class ElectionResultsView(View):
    template_name = 'elections/election_results.html'

    def get(self, request, election_id):
        election = get_object_or_404(Election, pk=election_id)
        if not election.is_published and not (request.user.is_authenticated and request.user.role in ['admin', 'teacher']):
            messages.error(request, 'Results have not been published yet.')
            return redirect('elections:election_detail', election_id=election_id)

        positions = election.positions.all().order_by('display_order')
        results = {}
        for pos in positions:
            candidates = Candidate.objects.filter(
                election=election, position=pos
            ).select_related('student').order_by('-vote_count')
            total_votes = sum(c.vote_count for c in candidates)
            results[pos] = {
                'candidates': candidates,
                'total_votes': total_votes,
                'winner_votes': candidates[0].vote_count if candidates else 0,
            }

        return render(request, self.template_name, {
            'election': election,
            'results': results,
        })


class RegisterCandidacyView(StudentRequiredMixin, View):
    template_name = 'elections/register_candidacy.html'

    def is_final_year(self, student):
        sem = student.student_class.section
        return sem in ['Sem 7', 'Sem 8']

    def get(self, request):
        student = get_student(request)
        if not self.is_final_year(student):
            messages.error(request, 'Only final year students (Sem 7 & Sem 8) can register as candidates.')
            return redirect('elections:election_list')
        elections = Election.objects.filter(is_active=True, end_date__gte=timezone.now())
        return render(request, self.template_name, {
            'elections': elections,
            'positions': Position.objects.all(),
            'student': student,
        })

    def post(self, request):
        student = get_student(request)
        if not self.is_final_year(student):
            messages.error(request, 'Only final year students (Sem 7 & Sem 8) can register as candidates.')
            return redirect('elections:election_list')
        election_id = request.POST.get('election')
        position_id = request.POST.get('position')
        manifesto = request.POST.get('manifesto', '')
        photo = request.FILES.get('photo')

        if not election_id or not position_id:
            messages.error(request, 'Please select both an election and a position.')
            return redirect('elections:register_candidacy')

        election = get_object_or_404(Election, pk=election_id)
        position = get_object_or_404(Position, pk=position_id)

        if Candidate.objects.filter(student=student, election=election, position=position).exists():
            messages.error(request, 'You have already registered for this position in this election.')
            return redirect('elections:register_candidacy')

        Candidate.objects.create(
            student=student,
            election=election,
            position=position,
            manifesto=manifesto,
            photo=photo,
        )
        messages.success(request, 'Your candidacy has been registered and is pending approval.')
        return redirect('elections:my_candidacies')


class MyCandidaciesView(StudentRequiredMixin, View):
    template_name = 'elections/my_candidacies.html'

    def get(self, request):
        student = get_student(request)
        candidacies = Candidate.objects.filter(student=student).select_related(
            'election', 'position'
        ).order_by('-nomination_date')
        return render(request, self.template_name, {
            'candidacies': candidacies,
            'student': student,
        })


class ManageElectionsView(StaffRequiredMixin, View):
    template_name = 'elections/manage_elections.html'

    def get(self, request):
        elections = Election.objects.all().prefetch_related('positions').order_by('-start_date')
        return render(request, self.template_name, {'elections': elections})


class CreateElectionView(StaffRequiredMixin, View):
    template_name = 'elections/election_form.html'

    def get(self, request):
        positions = Position.objects.all()
        return render(request, self.template_name, {
            'positions': positions,
            'election': None,
        })

    def post(self, request):
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        position_ids = request.POST.getlist('positions')

        if not title or not start_date or not end_date or not position_ids:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('elections:create_election')

        election = Election.objects.create(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
        )
        election.positions.set(position_ids)
        messages.success(request, 'Election created successfully.')
        return redirect('elections:manage_elections')


class EditElectionView(StaffRequiredMixin, View):
    template_name = 'elections/election_form.html'

    def get(self, request, election_id):
        election = get_object_or_404(Election, pk=election_id)
        positions = Position.objects.all()
        return render(request, self.template_name, {
            'positions': positions,
            'election': election,
        })

    def post(self, request, election_id):
        election = get_object_or_404(Election, pk=election_id)
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        position_ids = request.POST.getlist('positions')

        if not title or not start_date or not end_date or not position_ids:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('elections:edit_election', election_id=election_id)

        election.title = title
        election.description = description
        election.start_date = start_date
        election.end_date = end_date
        election.save()
        election.positions.set(position_ids)
        messages.success(request, 'Election updated successfully.')
        return redirect('elections:manage_elections')


class DeleteElectionView(StaffRequiredMixin, View):
    def post(self, request, election_id):
        election = get_object_or_404(Election, pk=election_id)
        election.delete()
        messages.success(request, 'Election deleted successfully.')
        return redirect('elections:manage_elections')


class ManageCandidatesView(StaffRequiredMixin, View):
    template_name = 'elections/manage_candidates.html'

    def get(self, request, election_id):
        election = get_object_or_404(Election, pk=election_id)
        candidates = Candidate.objects.filter(election=election).select_related(
            'student', 'position'
        ).order_by('position__display_order', '-nomination_date')
        return render(request, self.template_name, {
            'election': election,
            'candidates': candidates,
        })


class ApproveCandidateView(StaffRequiredMixin, View):
    def post(self, request, election_id, candidate_id):
        candidate = get_object_or_404(Candidate, pk=candidate_id, election_id=election_id)
        candidate.is_approved = True
        candidate.save()
        messages.success(request, f'Candidate {candidate.student.full_name} approved.')
        return redirect('elections:manage_candidates', election_id=election_id)


class RejectCandidateView(StaffRequiredMixin, View):
    def post(self, request, election_id, candidate_id):
        candidate = get_object_or_404(Candidate, pk=candidate_id, election_id=election_id)
        candidate.is_approved = False
        candidate.save()
        messages.success(request, f'Candidate {candidate.student.full_name} rejected.')
        return redirect('elections:manage_candidates', election_id=election_id)
