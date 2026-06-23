from django.contrib import admin
from .models import ExamSchedule, SeatAllocation

admin.site.register(ExamSchedule)
admin.site.register(SeatAllocation)
