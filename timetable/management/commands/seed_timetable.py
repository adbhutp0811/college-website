from django.core.management.base import BaseCommand
from students.models import Class
from results.models import Subject
from timetable.models import TimeSlot
from datetime import time
import random


DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']

TIME_SLOTS = [
    (time(9, 0), time(10, 0)),
    (time(10, 0), time(11, 0)),
    (time(11, 15), time(12, 15)),
    (time(12, 15), time(13, 15)),
    (time(14, 0), time(15, 0)),
    (time(15, 0), time(16, 0)),
]

LAB_SLOTS = [
    (time(9, 0), time(11, 0)),
    (time(11, 15), time(13, 15)),
    (time(14, 0), time(16, 0)),
]

ROOMS = ['A101', 'A102', 'A103', 'A104', 'A105',
         'B201', 'B202', 'B203', 'B204',
         'C301', 'C302', 'C303',
         'Lab-1', 'Lab-2', 'Lab-3', 'Lab-4', 'Lab-5', 'Lab-6']


class Command(BaseCommand):
    help = 'Seed timetable data for all classes'

    def handle(self, *args, **options):
        if TimeSlot.objects.exists():
            self.stdout.write('Timetable data already exists. Delete all TimeSlot records first to reseed.')
            return

        classes = Class.objects.all()
        total = 0

        for cls in classes:
            subjects = list(Subject.objects.filter(student_class=cls))
            if not subjects:
                continue

            labs = [s for s in subjects if s.is_lab]
            theory = [s for s in subjects if not s.is_lab]

            used_pairs = set()

            for i, sub in enumerate(theory):
                day = DAYS[i % len(DAYS)]
                slot_idx = (i // len(DAYS)) % len(TIME_SLOTS)
                start, end = TIME_SLOTS[slot_idx]
                room = ROOMS[hash(f'{cls.id}-{sub.id}') % len(ROOMS)]

                key = (day, start)
                if key not in used_pairs:
                    TimeSlot.objects.create(
                        student_class=cls, subject=sub,
                        day=day, start_time=start, end_time=end, room=room,
                    )
                    used_pairs.add(key)
                    total += 1

            for i, sub in enumerate(labs):
                day = DAYS[(i + len(theory)) % len(DAYS)]
                start, end = LAB_SLOTS[i % len(LAB_SLOTS)]
                room = f'Lab-{(hash(f"{cls.id}-lab-{i}") % 6) + 1}'

                key = (day, start)
                if key not in used_pairs:
                    TimeSlot.objects.create(
                        student_class=cls, subject=sub,
                        day=day, start_time=start, end_time=end, room=room,
                    )
                    used_pairs.add(key)
                    total += 1

            self.stdout.write(f'  {cls}')

        self.stdout.write(self.style.SUCCESS(f'Created {total} time slots across {classes.count()} classes'))
