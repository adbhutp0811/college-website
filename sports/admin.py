from django.contrib import admin
from .models import Sport, Team, Tournament, Achievement

admin.site.register(Sport)
admin.site.register(Team)
admin.site.register(Tournament)
admin.site.register(Achievement)
