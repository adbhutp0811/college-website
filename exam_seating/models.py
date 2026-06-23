from django.db import models
from students.models import Student
from results.models import Exam, Subject


class ExamSchedule(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='schedules')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exam_schedules')
    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['exam_date', 'start_time']

    def __str__(self):
        return f'{self.exam.name} - {self.subject.name} - {self.exam_date}'


class SeatAllocation(models.Model):
    schedule = models.ForeignKey(ExamSchedule, on_delete=models.CASCADE, related_name='seats')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='exam_seats')
    seat_number = models.CharField(max_length=20)

    class Meta:
        unique_together = ('schedule', 'seat_number')
        ordering = ['seat_number']

    def __str__(self):
        return f'{self.student.roll_number} - {self.schedule} - Seat {self.seat_number}'
