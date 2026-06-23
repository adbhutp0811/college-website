from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, LeadershipMember, DirectorMessage, Department, PlacementPartner, Testimonial, ContactInfo


@admin.register(LeadershipMember)
class LeadershipMemberAdmin(admin.ModelAdmin):
    list_display = ['name', 'designation', 'display_order', 'is_active']
    list_editable = ['display_order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'designation']


@admin.register(DirectorMessage)
class DirectorMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'designation', 'is_active']
    list_filter = ['is_active']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'full_name', 'display_order', 'is_active']
    list_editable = ['display_order', 'is_active']
    search_fields = ['code', 'full_name']


@admin.register(PlacementPartner)
class PlacementPartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'display_order', 'is_active']
    list_editable = ['display_order', 'is_active']
    search_fields = ['name']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'batch', 'display_order', 'is_active']
    list_editable = ['display_order', 'is_active']
    search_fields = ['student_name']


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    list_display = ['address', 'phone', 'is_active']
    list_filter = ['is_active']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('role', 'phone', 'profile_pic')}),
    )
