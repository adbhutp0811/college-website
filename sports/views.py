from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, ListView
from students.models import Student
from .models import Achievement, Sport, Team, Tournament


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role in ['admin', 'teacher']


class SportListView(ListView):
    model = Sport
    template_name = 'sports/sport_list.html'
    context_object_name = 'sports'

    def get_queryset(self):
        return Sport.objects.filter(is_active=True)


class SportDetailView(DetailView):
    model = Sport
    template_name = 'sports/sport_detail.html'
    context_object_name = 'sport'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        sport = self.get_object()
        ctx['teams'] = Team.objects.filter(sport=sport, is_active=True).prefetch_related('members')
        ctx['tournaments'] = Tournament.objects.filter(sport=sport)
        ctx['achievements'] = Achievement.objects.filter(sport=sport).select_related('student')
        return ctx


class CreateTeamView(StaffRequiredMixin, CreateView):
    model = Team
    template_name = 'sports/create_team.html'
    fields = ['name', 'members', 'coach_name']

    def form_valid(self, form):
        form.instance.sport_id = self.kwargs['sport_pk']
        messages.success(self.request, 'Team created successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.sport.get_absolute_url() if hasattr(self.object.sport, 'get_absolute_url') else '/sports/'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['sport'] = get_object_or_404(Sport, pk=self.kwargs['sport_pk'])
        ctx['students'] = Student.objects.filter(is_deleted=False)
        return ctx


class TeamDetailView(DetailView):
    model = Team
    template_name = 'sports/team_detail.html'
    context_object_name = 'team'


class TournamentListView(ListView):
    model = Tournament
    template_name = 'sports/tournament_list.html'
    context_object_name = 'tournaments'


class TournamentDetailView(DetailView):
    model = Tournament
    template_name = 'sports/tournament_detail.html'
    context_object_name = 'tournament'
