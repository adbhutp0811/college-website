from django.core.management.base import BaseCommand
from clubs.models import Club, ClubMembership
from students.models import Student
import random


class Command(BaseCommand):
    help = 'Add 5 students as members (1 coordinator, 1 vice_coordinator, 3 members) to each club and cell'

    def handle(self, *args, **options):
        clubs = Club.objects.filter(is_active=True)
        students = list(Student.objects.filter(is_deleted=False))

        if not students:
            self.stdout.write(self.style.ERROR('No students found. Please seed students first.'))
            return

        total_created = 0

        for club in clubs:
            existing_members = list(ClubMembership.objects.filter(club=club))
            existing_ids = {m.student_id for m in existing_members}

            needed = 5 - len(existing_ids)

            if needed > 0:
                available = [s for s in students if s.id not in existing_ids]
                if len(available) < needed:
                    chosen = available
                else:
                    chosen = random.sample(available, needed)

                for student in chosen:
                    ClubMembership.objects.create(club=club, student=student)
                    total_created += 1
                existing_members = list(ClubMembership.objects.filter(club=club))

            members = list(ClubMembership.objects.filter(club=club))
            random.shuffle(members)

            roles = ['coordinator', 'vice_coordinator', 'member', 'member', 'member']
            for membership, role in zip(members, roles):
                if membership.role != role:
                    membership.role = role
                    membership.save(update_fields=['role'])

            self.stdout.write(f'  {club.name}: 1 coordinator, 1 vice_coordinator, 3 members')

        self.stdout.write(self.style.SUCCESS(f'Done! {total_created} memberships created, roles assigned across {clubs.count()} clubs'))
