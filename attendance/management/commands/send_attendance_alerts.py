from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from attendance.models import Attendance


class Command(BaseCommand):
    help = 'Send attendance alerts to parents of absent students'

    def handle(self, *args, **options):
        today = timezone.localdate()
        absences = Attendance.objects.filter(date=today, status='absent').select_related('student')
        sent = 0
        errors = 0
        for a in absences:
            student = a.student
            if student.email:
                try:
                    send_mail(
                        subject='Attendance Alert - Absent Today',
                        message=f'Dear Parent,\n\nYour ward {student.full_name} ({student.roll_number}) was marked ABSENT on {today}.\n\nPlease contact the institute for more details.\n\n- Miracle Institute of Technology',
                        from_email=None,
                        recipient_list=[student.email],
                        fail_silently=True,
                    )
                    sent += 1
                except Exception:
                    errors += 1
        self.stdout.write(self.style.SUCCESS(f'Sent {sent} alerts ({errors} errors)'))
