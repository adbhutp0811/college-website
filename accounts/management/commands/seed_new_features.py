from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User
from students.models import Class, Student
from results.models import Subject, Exam
from mentor.models import MentorAssignment, MentorMeeting, MentorMeetingAttendance, MentorNote
from sports.models import Sport, Team, Tournament, Achievement
from scholarships.models import ScholarshipScheme, ScholarshipApplication
from mess.models import MessMenu, MessFeePeriod, MessPayment, MessComplaint
from antiragging.models import AntiRaggingCommittee, AntiRaggingUndertaking, AntiRaggingComplaint
from exam_seating.models import ExamSchedule, SeatAllocation
from quiz.models import Quiz, Question, QuizAttempt, Answer
import random
from datetime import date, timedelta, time


class Command(BaseCommand):
    help = 'Seed data for all 7 new features: Mentor, Sports, Scholarships, Mess, Anti-Ragging, Exam Seating, Quiz'

    def handle(self, *args, **options):
        if MessMenu.objects.exists():
            self.stdout.write('New features data already seeded, skipping.')
            return

        teachers = list(User.objects.filter(role='teacher'))
        students = list(Student.objects.filter(is_deleted=False))
        classes = list(Class.objects.all())
        subjects = list(Subject.objects.all())
        exams = list(Exam.objects.all())

        if not teachers or not students:
            self.stdout.write(self.style.ERROR('Need teachers and students. Run seed_data first.'))
            return

        self._seed_mentor(teachers, students)
        self._seed_sports(students)
        self._seed_scholarships(students)
        self._seed_mess(students)
        self._seed_antiragging(students)
        self._seed_exam_seating(exams, subjects, students)
        self._seed_quiz(subjects, students)

        self.stdout.write(self.style.SUCCESS('All new features seeded successfully!'))

    def _seed_mentor(self, teachers, students):
        self.stdout.write('Seeding Mentor System...')
        for i, student in enumerate(students[:200]):
            teacher = teachers[i % len(teachers)]
            MentorAssignment.objects.get_or_create(
                student=student,
                defaults={'faculty': teacher, 'is_active': True}
            )
        for teacher in teachers:
            mentees = Student.objects.filter(mentor__faculty=teacher)[:5]
            for _ in range(3):
                meeting = MentorMeeting.objects.create(
                    faculty=teacher,
                    meeting_date=date.today() - timedelta(days=random.randint(1, 60)),
                    notes=f'Discussed academic progress and career guidance. Topics: {' ,'.join(random.sample(['assignments','exam prep','projects','attendance','career plans'], 2))}.'
                )
                for s in mentees:
                    MentorMeetingAttendance.objects.create(
                        meeting=meeting, student=s,
                        was_present=random.choice([True, True, False])
                    )
            for s in mentees[:3]:
                MentorNote.objects.create(
                    student=s, faculty=teacher,
                    note=f'Student is {random.choice(["doing well","improving","needs attention","consistent","showing great promise"])}. {random.choice(["Should focus on math practice","Good participation in class","Needs to improve attendance","Strong in practical subjects","Should take up leadership roles"])}.'
                )
        self.stdout.write(f'  Created {MentorAssignment.objects.count()} mentor assignments, meetings, and notes')

    def _seed_sports(self, students):
        self.stdout.write('Seeding Sports Management...')
        sports_data = [
            ('Cricket', 'team', 'Popular team sport played with bat and ball'),
            ('Football', 'team', 'Association football - the world\'s most popular sport'),
            ('Basketball', 'team', 'Fast-paced team sport played on a court'),
            ('Volleyball', 'team', 'Team sport with net and ball'),
            ('Athletics', 'individual', 'Track and field events including running, jumping, throwing'),
            ('Badminton', 'individual', 'Racket sport played with shuttlecock'),
            ('Chess', 'individual', 'Strategic board game'),
            ('Table Tennis', 'individual', 'Fast indoor racket sport'),
            ('Kabaddi', 'team', 'Traditional Indian contact team sport'),
            ('Tennis', 'individual', 'Lawn tennis racket sport'),
        ]
        sports = []
        for name, cat, desc in sports_data:
            sport, _ = Sport.objects.get_or_create(
                name=name,
                defaults={'category': cat, 'description': desc}
            )
            sports.append(sport)

        for sport in sports[:5]:
            for i in range(1, 3):
                members = random.sample(students, min(11, len(students)))
                team, _ = Team.objects.get_or_create(
                    sport=sport,
                    name=f'{sport.name} Team {chr(64+i)}',
                    defaults={'coach_name': random.choice(['Rahul Sir', 'Priya Ma\'am', 'Amit Sir', 'Neha Ma\'am', 'Vikram Sir'])}
                )
                team.members.add(*members)

        tournament_names = [
            ('Inter-Department Cricket Cup', 1), ('Annual Sports Meet', 0),
            ('Freshers Football Tournament', 1), ('Chess Championship', 6),
            ('Badminton Open', 5), ('Basketball League', 2),
        ]
        for name, sport_idx in tournament_names:
            start = date.today() - timedelta(days=random.randint(30, 120))
            Tournament.objects.get_or_create(
                name=name,
                sport=sports[sport_idx],
                defaults={
                    'start_date': start,
                    'end_date': start + timedelta(days=random.randint(3, 15)),
                    'venue': random.choice(['Main Ground', 'Indoor Stadium', 'Basketball Court', 'Seminar Hall', 'Sports Complex']),
                    'status': random.choice(['completed', 'completed', 'completed', 'ongoing', 'upcoming']),
                }
            )

        medal_types = ['gold', 'gold', 'silver', 'silver', 'bronze', 'bronze', 'participation']
        for i, student in enumerate(random.sample(students, min(50, len(students)))):
            sport = random.choice(sports)
            tournament = random.choice(Tournament.objects.all()) if Tournament.objects.exists() else None
            Achievement.objects.get_or_create(
                student=student,
                title=f'{random.choice(["1st Place","2nd Place","3rd Place","Best Player","Participation"])} in {sport.name}',
                defaults={
                    'sport': sport,
                    'tournament': tournament,
                    'medal': random.choice(medal_types),
                    'achievement_date': date.today() - timedelta(days=random.randint(10, 200)),
                }
            )
        self.stdout.write(f'  Created {Sport.objects.count()} sports, {Team.objects.count()} teams, {Tournament.objects.count()} tournaments, {Achievement.objects.count()} achievements')

    def _seed_scholarships(self, students):
        self.stdout.write('Seeding Scholarships...')
        schemes_data = [
            ('Merit Scholarship', 'For students with outstanding academic performance (80%+ in previous semester)', 25000, 'Minimum 80% aggregate in previous semester. No backlog.'),
            ('Need-Based Financial Aid', 'For economically disadvantaged students', 15000, 'Family income below 2.5 LPA. Minimum 60% in previous semester.'),
            ('Sports Excellence Award', 'For students who excel in sports at state/national level', 20000, 'Represented college at state/national level. Minimum 50% in academics.'),
            ('Girl Child Education Scholarship', 'Encouraging female students in higher education', 12000, 'Female student. Minimum 70% in previous semester. Family income below 3 LPA.'),
            ('Research & Innovation Grant', 'For innovative projects and research work', 30000, 'Proposal-based. Team of max 3 students. Faculty mentor required.'),
            ('SC/ST Merit Scholarship', 'For meritorious SC/ST students', 18000, 'SC/ST category. Minimum 65% in previous semester.'),
        ]
        schemes = []
        for name, desc, amount, eligibility in schemes_data:
            scheme, _ = ScholarshipScheme.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'amount': amount,
                    'eligibility_criteria': eligibility,
                    'application_deadline': date.today() + timedelta(days=random.randint(15, 90)),
                }
            )
            schemes.append(scheme)

        for scheme in schemes[:4]:
            for student in random.sample(students, min(10, len(students))):
                ScholarshipApplication.objects.get_or_create(
                    student=student,
                    scheme=scheme,
                    defaults={
                        'status': random.choice(['submitted', 'submitted', 'under_review', 'approved', 'rejected']),
                        'remarks': random.choice(['', '', 'Good academic record', 'Needs document verification']),
                    }
                )
        self.stdout.write(f'  Created {ScholarshipScheme.objects.count()} schemes, {ScholarshipApplication.objects.count()} applications')

    def _seed_mess(self, students):
        self.stdout.write('Seeding Mess & Canteen...')
        days = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        meals = ['breakfast','lunch','snacks','dinner']
        menu_items = {
            'breakfast': ['Aloo Paratha with Curd','Poha with Jalebi','Bread Butter Jam','Chole Bhature','Idli Sambar','Upma','Masala Dosa','Vegetable Sandwich','Poori Sabzi','Sprouts Chaat'],
            'lunch': ['Dal Rice Roti Salad','Rajma Rice Pickle','Chole Rice Onion','Mixed Veg Roti Dal','Kadhai Paneer Naan','Sambhar Rice Papad','Veg Biryani Raita','Dal Tadka Jeera Rice','Palak Paneer Roti','Bhindi Roti Dal'],
            'snacks': ['Samosa with Chutney','Veg Pakora','Bread Pakora','French Fries','Cutlet','Vada Pav','Pasta','Sandwich','Noodles','Spring Roll'],
            'dinner': ['Chapati Dal Sabzi','Pulao Raita','Kheer Poori','Veg Pulao Curd','Paratha Curd','Khichdi Papad','Pasta Salad','Pizza (Friday Special)','Veg Burger','Fried Rice Manchurian'],
        }
        for day in days:
            for meal in meals:
                items = random.sample(menu_items[meal], random.randint(3, 5))
                MessMenu.objects.get_or_create(
                    day=day, meal_type=meal,
                    defaults={'items': ', '.join(items)}
                )

        today = date.today()
        for month_offset in range(3):
            m = today.month - month_offset
            y = today.year
            while m < 1:
                m += 12
                y -= 1
            MessFeePeriod.objects.get_or_create(
                month=m, year=y,
                defaults={
                    'amount': random.choice([2500, 2800, 3000, 3200, 3500]),
                    'due_date': date(y, m, 10),
                }
            )

        periods = list(MessFeePeriod.objects.all())
        for student in random.sample(students, min(100, len(students))):
            for period in periods[:2]:
                paid = random.choice([True, False, True, True])
                if paid:
                    MessPayment.objects.get_or_create(
                        student=student, fee_period=period,
                        defaults={
                            'status': 'paid',
                            'paid_at': timezone.now() - timedelta(days=random.randint(1, 60)),
                            'transaction_id': f'MESS{random.randint(100000,999999)}',
                        }
                    )

        complaint_types = [
            ('food_quality', 'Food quality issue', 'The food served today was not up to the mark.'),
            ('hygiene', 'Hygiene concern', 'The dining area needs better cleaning.'),
            ('service', 'Slow service', 'Very slow service during lunch hours.'),
            ('menu', 'Menu suggestion', 'Can we have more variety in breakfast?'),
            ('other', 'General feedback', 'Need better seating arrangement in the mess.'),
        ]
        for student in random.sample(students, min(15, len(students))):
            cat, subj, desc = random.choice(complaint_types)
            MessComplaint.objects.get_or_create(
                student=student,
                subject=subj,
                defaults={
                    'category': cat,
                    'description': desc,
                    'is_resolved': random.choice([True, False, False]),
                    'resolved_at': timezone.now() - timedelta(days=random.randint(1, 10)) if random.choice([True, False]) else None,
                }
            )
        self.stdout.write(f'  Created {MessMenu.objects.count()} menu items, {MessFeePeriod.objects.count()} fee periods, {MessPayment.objects.count()} payments, {MessComplaint.objects.count()} complaints')

    def _seed_antiragging(self, students):
        self.stdout.write('Seeding Anti-Ragging...')
        committee_data = [
            ('Dr. Rajesh Kumar', 'Chairman', 'Professor & HOD (CSE)', 'rajesh@mit.ac.in'),
            ('Dr. Sunita Sharma', 'Member', 'Associate Professor (ECE)', 'sunita@mit.ac.in'),
            ('Mr. Amit Verma', 'Member', 'Assistant Professor (ME)', 'amit@mit.ac.in'),
            ('Ms. Priya Singh', 'Member', 'Assistant Professor (TT)', 'priya@mit.ac.in'),
            ('Dr. Vikram Patel', 'Member Secretary', 'Associate Dean (Student Affairs)', 'vikram@mit.ac.in'),
        ]
        for i, (name, role, designation, email) in enumerate(committee_data):
            AntiRaggingCommittee.objects.get_or_create(
                name=name, role=role,
                defaults={
                    'designation': designation,
                    'phone': f'+91{random.randint(7000000000, 9999999999)}',
                    'email': email,
                    'order': i + 1,
                }
            )

        for student in students[:random.randint(50, 100)]:
            AntiRaggingUndertaking.objects.get_or_create(
                student=student,
                defaults={
                    'is_accepted': random.choice([True, True, True, False]),
                    'signed_date': date.today() - timedelta(days=random.randint(1, 90)),
                }
            )

        complaint_samples = [
            ('ragging', 'Ragging incident reported', 'Some senior students were teasing freshers in the hostel common room.', True),
            ('harassment', 'Feeling unsafe on campus', 'I feel uncomfortable with the behavior of some students near the canteen.', True),
            ('discrimination', 'Discrimination complaint', 'Some students are being treated differently based on their background.', False),
        ]
        for cat, subj, desc, anon in complaint_samples:
            reporter = random.choice(students) if not anon else None
            AntiRaggingComplaint.objects.get_or_create(
                subject=subj,
                defaults={
                    'student': reporter,
                    'category': cat,
                    'description': desc,
                    'is_anonymous': anon,
                    'status': random.choice(['pending', 'investigating', 'resolved']),
                    'admin_response': 'Committee is looking into this matter.' if random.choice([True, False]) else '',
                }
            )
        self.stdout.write(f'  Created {AntiRaggingCommittee.objects.count()} committee members, {AntiRaggingUndertaking.objects.count()} undertakings, {AntiRaggingComplaint.objects.count()} complaints')

    def _seed_exam_seating(self, exams, subjects, students):
        self.stdout.write('Seeding Exam Seating...')
        rooms = ['A-101', 'A-102', 'A-103', 'B-201', 'B-202', 'C-301', 'C-302', 'Lab-1', 'Lab-2', 'Auditorium']
        schedules_created = 0
        for exam in exams[:10]:
            exam_subjects = [s for s in subjects if s.student_class_id == exam.student_class_id][:5]
            for sub in exam_subjects:
                if ExamSchedule.objects.filter(exam=exam, subject=sub).exists():
                    continue
                schedule = ExamSchedule.objects.create(
                    exam=exam,
                    subject=sub,
                    exam_date=date.today() + timedelta(days=random.randint(-5, 30)),
                    start_time=time(9, 0) if random.choice([True, False]) else time(14, 0),
                    end_time=time(12, 0) if random.choice([True, False]) else time(17, 0),
                    room=random.choice(rooms),
                    notes=random.choice(['', 'Bring own stationery', 'No electronic devices', 'Report 15 min early']),
                )
                schedules_created += 1
                class_students = Student.objects.filter(student_class=sub.student_class, is_deleted=False)[:10]
                for i, s in enumerate(class_students, start=1):
                    SeatAllocation.objects.get_or_create(
                        schedule=schedule, student=s,
                        defaults={'seat_number': str(i)}
                    )
        self.stdout.write(f'  Created {schedules_created} schedules with seat allocations')

    def _seed_quiz(self, subjects, students):
        self.stdout.write('Seeding Online Quizzes...')
        quiz_templates = [
            ('Python Basics Quiz', 'Test your knowledge of Python fundamentals including variables, data types, and control flow.', [
                ('What is the correct file extension for Python files?', '.py', '.pyt', '.pyth', '.pn', 'A', 1),
                ('Which keyword is used to define a function in Python?', 'func', 'define', 'def', 'function', 'C', 1),
                ('What is the output of print(2 ** 3)?', '6', '8', '9', '5', 'B', 1),
                ('Which data type is immutable in Python?', 'list', 'dict', 'tuple', 'set', 'C', 1),
                ('What does len() function do?', 'Returns length', 'Returns max', 'Returns min', 'Returns type', 'A', 1),
            ]),
            ('Mathematics Quiz', 'Test your mathematical skills with these questions.', [
                ('What is the value of Pi (approx)?', '3.14', '2.71', '1.61', '3.41', 'A', 1),
                ('What is the square root of 144?', '11', '12', '13', '14', 'B', 1),
                ('What is 15% of 200?', '25', '30', '35', '40', 'B', 1),
                ('How many sides does a hexagon have?', '5', '6', '7', '8', 'B', 1),
                ('What is 7! (7 factorial)?', '5040', '720', '40320', '2520', 'A', 1),
            ]),
            ('General Awareness', 'Current affairs and general knowledge quiz.', [
                ('Which planet is known as the Red Planet?', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'B', 1),
                ('What is the capital of India?', 'Mumbai', 'Kolkata', 'New Delhi', 'Chennai', 'C', 1),
                ('Which gas is most abundant in Earth\'s atmosphere?', 'Oxygen', 'Carbon Dioxide', 'Nitrogen', 'Argon', 'C', 1),
                ('Who wrote the Indian National Anthem?', 'Mahatma Gandhi', 'Rabindranath Tagore', 'Bankim Chandra', 'Premchand', 'B', 1),
                ('What is the chemical symbol for Gold?', 'Go', 'Gd', 'Au', 'Ag', 'C', 1),
            ]),
        ]

        for title, desc, questions_data in quiz_templates:
            target_subjects = Subject.objects.filter(name__icontains=title.split()[0])[:1]
            if not target_subjects:
                target_subjects = Subject.objects.all()[:1]
            subject = target_subjects[0]
            now = timezone.now()
            quiz, _ = Quiz.objects.get_or_create(
                title=title,
                subject=subject,
                defaults={
                    'description': desc,
                    'duration_minutes': 10,
                    'total_marks': len(questions_data),
                    'pass_marks': 3,
                    'start_time': now - timedelta(days=random.randint(1, 5)),
                    'end_time': now + timedelta(days=random.randint(5, 20)),
                    'is_published': True,
                }
            )
            for text, a, b, c, d, correct, marks in questions_data:
                Question.objects.get_or_create(
                    quiz=quiz, text=text,
                    defaults={
                        'option_a': a, 'option_b': b, 'option_c': c, 'option_d': d,
                        'correct_answer': correct, 'marks': marks,
                    }
                )

            for student in random.sample(students, min(5, len(students))):
                attempt, created = QuizAttempt.objects.get_or_create(
                    student=student, quiz=quiz,
                    defaults={'completed_at': timezone.now() - timedelta(hours=random.randint(1, 48))}
                )
                if created:
                    score = 0
                    total = 0
                    for q in quiz.questions.all():
                        selected = random.choice(['A', 'B', 'C', 'D'])
                        is_correct = selected == q.correct_answer
                        if is_correct:
                            score += q.marks
                        total += q.marks
                        Answer.objects.create(attempt=attempt, question=q, selected_answer=selected, is_correct=is_correct)
                    attempt.score = score
                    attempt.total_marks = total
                    attempt.save(update_fields=['score', 'total_marks'])
        self.stdout.write(f'  Created {Quiz.objects.count()} quizzes, {Question.objects.count()} questions, {QuizAttempt.objects.count()} attempts')
