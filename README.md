# Student Management System

A full-stack Student Management System built with **Django 6**, **MySQL/SQLite**, and **Bootstrap 5** featuring student records, attendance, results, timetable, clubs, fees, grievances, exam forms, library, hostel, placements, leave management, course materials, feedback, photo gallery, alumni management, student council/elections, online fee payment (Razorpay/Stripe), SMS alerts, ID card PDF generation, and result PDF email.

## Features

### Core
- **Student Records** — Add/edit/soft-delete students with photo, guardian details, roll number, class
- **Attendance Tracking** — Bulk daily attendance (Present/Absent/Late/Leave) with history, summary, auto-SMS to guardian on absence, email/parent notifications
- **Result Management** — Subjects, exams, marks entry, auto-grade/SGPA calculation, class ranking, printable report cards, **email results as PDF**
- **Timetable** — Class-wise timetable with theory/lab slots, manage/add/delete via staff portal
- **Dashboard** — Staff dashboard with stats, quick actions; student portal with personalized navigation

### Academic Modules
- **Library** — Book catalog, issue/return (max 3 books, 14-day due date), my issues tracking
- **Hostel** — Hostel/room management, student room application, staff allocation/deallocation
- **Placements** — Company profiles, placement drives, student applications, staff status updates
- **Leave Management** — Student leave applications, staff approval/rejection workflow
- **Course Materials & Assignments** — Upload study materials, create assignments, student submissions with grading
- **Feedback System** — Faculty feedback with categories & questions, student submission, staff results view
- **Photo Gallery** — Albums with multiple photos, cover images, staff upload/deletion, public viewing
- **Alumni Management** — Alumni registration, verified directory with search/filter, alumni events with registration, donation system
- **Student Council/Elections** — Position-based elections, candidate registration (final year students only — Sem 7 & 8), one-student-one-vote-per-position, live vote counting with `F()` atomic increments, results with progress bars, winners displayed on homepage
- **Online Fee Payment** — Select pending fees, pay via Razorpay (checkout.js) or Stripe (Checkout Sessions), demo mode without API keys, signature verification, payment history

### Clubs & Cells
- 23 clubs/cells (technical, cultural, sports, outreach)
- Club detail pages with coordinator, members, events
- Student application & approval workflow with email notification
- Cell coordinators management

### Student Portal
- Session-based authentication (roll number + DOB)
- Attendance history, result history, fee dashboard
- Grievance submission & tracking
- Exam registration & status tracking
- ID card download (PDF), library issues, hostel allocation, leave applications, materials & assignments, feedback

### SMS & Notifications
- **Auto-SMS** on marking student absent (to guardian contact)
- **Bulk SMS** — Send absence alerts to all guardians of a class
- **Individual SMS** — Chat icon per student on summary page
- **Custom SMS** — Type any message and send to any student's guardian
- **Email Results** — Send result PDFs to students via staff portal
- Supports **MSG91** and **Twilio** providers (configurable)

### College Homepage (All Backend-Editable)
- **Leadership Team** — Add/edit/reorder members with photos
- **Director's Message** — Name, designation, message, photo
- **Programs Offered** — Department CRUD with descriptions
- **Placement Partners** — Company name, logo upload, website link
- **Testimonials** — Student name, batch, program, content
- **Contact Info** — Address, phone, email (single-instance)
- **Student Portal Section** — Green-themed cards highlighting Academics, Finance, Services, Engagement, Support features with login CTA
- **Election Winners Section** — Orange-themed cards showing winners from ended elections with name, photo, position, and election title

### Student ID Card
- Circular student photo via PIL `Image.composite`
- Name, roll number, class, DOB, blood group, guardian details, address
- Navy/gold bands, signature fields, QR code, validity dates

- **Additional Modules**
  - **Quiz** — Create quizzes, add questions, student attempts with auto-grading
  - **Mentor** — Mentor assignment, meetings, mentee tracking
  - **Sports** — Sports/tournament management, team registration
  - **Anti-Ragging** — Complaint submission & tracking
  - **Scholarships** — Schemes & student applications
  - **Exam Seating** — Seat allocation with PDF export
  - **Mess** — Menu, complaints, feedback
  - **Faculty** — Staff directory & profiles

## Tech Stack

- **Backend:** Django 6, Python 3.14
- **Database:** MySQL (production) / SQLite (development)
- **Frontend:** Bootstrap 5, jQuery, HTML5, CSS3
- **Static Files:** Whitenoise
- **Libraries:** xhtml2pdf, reportlab, Pillow, openpyxl, requests, razorpay, stripe

## Setup Instructions

### 1. Clone & Create Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Database

**Option A: SQLite (Default — Quick Start)**
- No configuration needed.

**Option B: MySQL (Production)**
1. Create database:
   ```sql
   CREATE DATABASE student_management CHARACTER SET utf8mb4;
   ```
2. Set environment variables or `.env`:
   ```
   DJANGO_DB_ENGINE=mysql
   DB_NAME=student_management
   DB_USER=root
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=3306
   ```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Seed Sample Data

```bash
python manage.py seed_data                 # students, classes, attendance, results
python manage.py seed_members              # 5 members per club (115 memberships)
python manage.py seed_club_photos          # club-relevant aesthetic images
python manage.py seed_student_photos       # profile photos for club members
python manage.py seed_timetable            # timetable for all 48 classes
```

### 7. Configure Payment Gateway (Optional)

Set in `.env` for real payments:
```
PAYMENT_GATEWAY=razorpay       # or 'stripe'
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_secret
STRIPE_PUBLISHABLE_KEY=your_pk
STRIPE_SECRET_KEY=your_sk
```

Without these, the system runs in **Demo Mode** — payments appear successful without real charges.

### 8. Configure SMS (Optional)

Add to `settings.py` for real SMS:

```python
SMS_PROVIDER = 'msg91'  # or 'twilio'
SMS_API_KEY = 'your-api-key'
```

Without this, SMS is logged to console.

### 9. Run Development Server

```bash
python manage.py runserver
```

### 10. Access

- **App:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/
- **Staff Login:** http://127.0.0.1:8000/accounts/login/
- **Student Portal:** http://127.0.0.1:8000/accounts/student-portal/

## Default Credentials (After Seed)

| Username  | Password    | Role    |
|-----------|-------------|---------|
| admin     | admin123    | Admin   |
| teacher   | teacher123  | Teacher |
| teacher2  | teacher123  | Teacher |

## Project Structure

```
student_management/
├── accounts/               # Custom User model, auth, homepage sections (leadership, depts, partners, etc.)
├── students/               # Student & Class CRUD, ID card PDF
├── attendance/             # Mark/history/summary/notify, SMS utils
├── results/                # Subjects, exams, marks, report cards, email PDF
├── timetable/              # Timetable management
├── clubs/                  # Clubs & cells with members
├── fees/                   # Fee structures, payments, online payment (Razorpay/Stripe)
├── grievances/             # Grievance submission & management
├── exam_forms/             # Exam registration & approval
├── placements/             # Placement partners, drives, apps
├── library/                # Book catalog, issue/return
├── hostel/                 # Hostel/room management, allocations
├── leave_management/       # Leave applications & approvals
├── course_materials/       # Study materials, assignments, submissions
├── feedback/               # Faculty feedback with categories
├── gallery/                # Photo albums with multi-upload
├── alumni/                 # Alumni directory, events, donations
├── elections/              # Student council candidates, voting, results
├── notices/                # Notice publishing
├── events/                 # Event management
├── mentor/                 # Mentor/mentee assignments & meetings
├── sports/                 # Sports & tournament management
├── quiz/                   # Quiz creation & student attempts
├── antiragging/            # Anti-ragging complaints
├── scholarships/           # Scholarship schemes & applications
├── exam_seating/           # Exam seating allocation
├── mess/                   # Mess menu & complaints
├── faculty/                # Staff directory (separate from auth users)
├── templates/              # All HTML templates
├── static/                 # CSS, JS, images
├── student_management/     # Project settings, URLs, WSGI
└── staticfiles/            # Collected static (auto-generated)
```

## Management Commands

| Command | Description |
|---------|-------------|
| `seed_data` | Seed students (720), classes (48), attendance, results |
| `seed_members` | Seed 5 members per club |
| `seed_club_photos` | Fetch club-relevant photos from loremflickr |
| `seed_student_photos` | Generate profile photos for club members |
| `seed_timetable` | Generate timetable slots for all classes |

## SMS Providers

| Provider | Setup |
|----------|-------|
| **MSG91** | Set `SMS_PROVIDER='msg91'`, `SMS_API_KEY`, `SMS_SENDER_ID` in settings |
| **Twilio** | Set `SMS_PROVIDER='twilio'`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` |
| **Console** | Default — logs SMS to console for development |

## Key Design Decisions

- **Session-based auth** for students (`request.session.student_id`) vs Django auth for staff
- **Soft-delete** (`is_deleted` field) for student records; restorable from admin
- **ID card** uses PIL `Image.composite` for circular photo crop
- **Result PDF** via xhtml2pdf, attached to email via `EmailMessage`
- **SMS** sent via ThreadPoolExecutor for bulk operations; auto-sent on marking absent
- **College homepage** sections are fully editable from Django admin
