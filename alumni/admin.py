from django.contrib import admin
from .models import Alumni, AlumniEvent, EventRegistration, Donation


@admin.register(Alumni)
class AlumniAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'graduation_year', 'program', 'is_verified', 'is_visible', 'registered_at']
    list_filter = ['is_verified', 'is_visible', 'graduation_year', 'program']
    search_fields = ['first_name', 'last_name', 'email', 'company']
    list_editable = ['is_verified', 'is_visible']


@admin.register(AlumniEvent)
class AlumniEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'location', 'is_published', 'max_participants']
    list_filter = ['is_published', 'date']
    search_fields = ['title', 'location']


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['alumni', 'event', 'registered_at', 'attended']
    list_filter = ['attended', 'event']
    search_fields = ['alumni__first_name', 'alumni__last_name', 'event__title']


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donor_name', 'amount', 'purpose', 'payment_method', 'donated_at', 'is_anonymous']
    list_filter = ['payment_method', 'is_anonymous']
    search_fields = ['donor_name', 'donor_email', 'transaction_id']
