from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, ListView, CreateView, DeleteView
from django.contrib import messages
from django.db import models as db_models
from students.models import Class
from results.models import Subject
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
            day_order = db_models.Case(*[db_models.When(day=d, then=db_models.Value(i)) for i, d in enumerate(DAY_ORDER)])
            ctx['time_slots'] = TimeSlot.objects.filter(
                student_class_id=selected_class_id
            ).annotate(day_order=day_order).order_by('day_order', 'start_time')
        else:
            ctx['time_slots'] = TimeSlot.objects.none()
        return ctx


class ManageTimetableView(LoginRequiredMixin, TemplateView):
    template_name = 'timetable/manage_timetable.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['classes'] = Class.objects.all()
        selected_class_id = self.request.GET.get('class_id')
        if selected_class_id:
            ctx['selected_class'] = get_object_or_404(Class, id=selected_class_id)
            day_order = db_models.Case(*[db_models.When(day=d, then=db_models.Value(i)) for i, d in enumerate(DAY_ORDER)])
            ctx['time_slots'] = TimeSlot.objects.filter(
                student_class_id=selected_class_id
            ).annotate(day_order=day_order).order_by('day_order', 'start_time')
            ctx['subjects'] = Subject.objects.filter(student_class_id=selected_class_id)
        else:
            ctx['time_slots'] = TimeSlot.objects.none()
            ctx['subjects'] = Subject.objects.none()
        ctx['days'] = [('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday')]
        return ctx


class AddSlotView(LoginRequiredMixin, View):
    def post(self, request):
        class_id = request.POST.get('class_id')
        subject_id = request.POST.get('subject_id')
        day = request.POST.get('day')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        room = request.POST.get('room', '')

        if not all([class_id, subject_id, day, start_time, end_time]):
            messages.error(request, 'All fields are required.')
            return redirect(f'{reverse_lazy("timetable:manage")}?class_id={class_id}')

        TimeSlot.objects.create(
            student_class_id=class_id,
            subject_id=subject_id,
            day=day,
            start_time=start_time,
            end_time=end_time,
            room=room,
        )
        messages.success(request, 'Time slot added successfully.')
        return redirect(f'{reverse_lazy("timetable:manage")}?class_id={class_id}')


class DeleteSlotView(LoginRequiredMixin, View):
    def post(self, request, pk):
        slot = get_object_or_404(TimeSlot, pk=pk)
        class_id = slot.student_class_id
        slot.delete()
        messages.success(request, 'Time slot deleted.')
        return redirect(f'{reverse_lazy("timetable:manage")}?class_id={class_id}')
