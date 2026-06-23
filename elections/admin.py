from django.contrib import admin, messages
from .models import Position, Election, Candidate, Vote


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'display_order', 'max_winners']
    list_filter = ['max_winners']
    search_fields = ['title', 'description']


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'is_active', 'is_published']
    list_filter = ['is_active', 'is_published']
    search_fields = ['title', 'description']
    filter_horizontal = ['positions']
    actions = ['publish_results']

    def publish_results(self, request, queryset):
        updated = queryset.update(is_published=True)
        messages.success(request, f'{updated} election(s) marked as published.')
    publish_results.short_description = 'Publish Results'


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['student', 'election', 'position', 'is_approved', 'vote_count']
    list_filter = ['is_approved', 'election', 'position']
    search_fields = ['student__first_name', 'student__last_name', 'student__roll_number', 'manifesto']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['student', 'election', 'candidate', 'position', 'voted_at']
    list_filter = ['election', 'position']
    search_fields = ['student__first_name', 'student__last_name', 'student__roll_number']
