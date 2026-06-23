from django.contrib import admin
from .models import AntiRaggingCommittee, AntiRaggingUndertaking, AntiRaggingComplaint

admin.site.register(AntiRaggingCommittee)
admin.site.register(AntiRaggingUndertaking)
admin.site.register(AntiRaggingComplaint)
