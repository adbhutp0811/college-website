from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import ListView, DetailView, View, TemplateView
from django.contrib import messages
from django.utils import timezone
from .models import Hostel, Room, RoomAllocation
from students.models import Student


class HostelListView(ListView):
    model = Hostel
    template_name = 'hostel/hostel_list.html'
    context_object_name = 'hostels'


class HostelDetailView(DetailView):
    model = Hostel
    template_name = 'hostel/hostel_detail.html'
    context_object_name = 'hostel'
    slug_field = 'pk'


class ApplyRoomView(View):
    template_name = 'hostel/apply_room.html'

    def get(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        if not room.is_available:
            messages.error(request, 'This room is full.')
            return redirect('hostel:hostel_detail', pk=room.hostel.pk)
        return render(request, self.template_name, {'room': room})

    def post(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        student_id = request.session.get('student_id')
        if not student_id:
            messages.error(request, 'Please login as student first.')
            return redirect('accounts:student_login')
        student = get_object_or_404(Student, id=student_id)
        if RoomAllocation.objects.filter(student=student, is_active=True).exists():
            messages.error(request, 'You already have an active room allocation.')
            return redirect('hostel:hostel_detail', pk=room.hostel.pk)
        if not room.is_available:
            messages.error(request, 'Room is no longer available.')
            return redirect('hostel:hostel_detail', pk=room.hostel.pk)
        RoomAllocation.objects.create(student=student, room=room)
        room.occupied += 1
        room.save()
        messages.success(request, f'Room {room.room_number} in {room.hostel.name} allocated successfully!')
        return redirect('hostel:my_allocation')


class MyAllocationView(TemplateView):
    template_name = 'hostel/my_allocation.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student_id = self.request.session.get('student_id')
        if student_id:
            student = get_object_or_404(Student, id=student_id)
            ctx['allocation'] = RoomAllocation.objects.filter(student=student, is_active=True).select_related('room__hostel').first()
            ctx['history'] = RoomAllocation.objects.filter(student=student).select_related('room__hostel')[:5]
        return ctx


class StaffAllocationsView(LoginRequiredMixin, ListView):
    model = RoomAllocation
    template_name = 'hostel/staff_allocations.html'
    context_object_name = 'allocations'

    def get_queryset(self):
        return RoomAllocation.objects.filter(is_active=True).select_related('student', 'room__hostel')


class DeallocateRoomView(LoginRequiredMixin, View):
    def post(self, request, pk):
        allocation = get_object_or_404(RoomAllocation, pk=pk, is_active=True)
        allocation.is_active = False
        allocation.end_date = timezone.now().date()
        allocation.save()
        allocation.room.occupied -= 1
        allocation.room.save()
        messages.success(request, f'Student {allocation.student.roll_number} deallocated from {allocation.room.room_number}.')
        return redirect('hostel:staff_allocations')
