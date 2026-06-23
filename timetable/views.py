from django.views.generic import TemplateView
from django.db import models
from students.models import Class
from .models import TimeSlot


DAY_ORDER = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']


class TimetableView(TemplateView):
    template_name = 'timetable/timetable.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['classes'] = Class.objects.all()
        selected_class_id = self.request.GET.get('class_id')
        if selected_class_id:
            ctx['selected_class'] = Class.objects.get(id=selected_class_id)
            day_order = models.Case(*[models.When(day=d, then=models.Value(i)) for i, d in enumerate(DAY_ORDER)])
            ctx['time_slots'] = TimeSlot.objects.filter(
                student_class_id=selected_class_id
            ).annotate(day_order=day_order).order_by('day_order', 'start_time')
        else:
            ctx['time_slots'] = TimeSlot.objects.none()
        return ctx
