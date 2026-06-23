# Student Management System

A full-stack Student Management System built with **Django 6**, **MySQL/SQLite**, and **Bootstrap 5** featuring student records, attendance, results, timetable, clubs, fees, grievances, exam forms, placement partners, and ID card generation.

## Features

### Core
- **Student Records** — Add/edit/soft-delete students with photo, guardian details, roll number, class
- **Attendance Tracking** — Bulk daily attendance (Present/Absent/Late/Leave) with history, summary, and parent email notifications
- **Result Management** — Subjects, exams, marks entry, auto-grade calculation, class ranking, printable report cards
- **Timetable** — Class-wise timetable with theory/lab slots, ordered by custom day sequence (Mon–Fri)
- **Dashboard** — Staff dashboard with stats, student portal with personalized quick links

### Clubs & Cells
- 23 clubs/cells (technical, cultural, sports, outreach)
- Club detail pages with coordinator, vice-coordinator, and member lists (5 members each)
- Club-relevant aesthetic photos (fetched from loremflickr per topic)
- Student profile photos with gradient-initial generation via Pillow

### Student Portal
- Session-based authentication (roll number + DOB)
- Attendance history, result history, fee dashboard
- Grievance submission & tracking
- Exam registration & status tracking
- Download ID card (PDF)

### Placement Partners
- Dedicated placement partners page with company logos
- Placement drive listings and applications
- 18+ company logos (real SVGs from Wikimedia Commons)

### Student ID Card
- Circular student photo via PIL `Image.composite`
- Name, roll number, class, DOB, blood group, guardian details, address
- Navy/gold bands, signature fields, QR code, validity dates

### Additional Modules
- **Fees** — Fee structure, student fee dashboard with balance, simulated payment gateway
- **Grievances** — Student grievance submission, staff manage/resolve workflow
- **Exam Forms** — Exam registration per semester, subject selection, staff approval/rejection
- **College Homepage** — Programs, testimonials, placement partners, back navigation on all pages

## Tech Stack

- **Backend:** Django 6, Python 3.12
- **Database:** MySQL (production) / SQLite (development)
- **Frontend:** Bootstrap 5, jQuery, HTML5, CSS3
- **Static Files:** Whitenoise
- **Libraries:** django-crispy-forms, reportlab 5.0, Pillow 12.2, openpyxl

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

### 7. Run Development Server

```bash
python manage.py runserver
```

### 8. Access

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
├── accounts/               # Custom User model, auth views
├── students/               # Student & Class CRUD, ID card PDF
├── attendance/             # Mark/history/summary/notify views
├── results/                # Subjects, exams, marks, report cards
├── timetable/              # Timetable management
├── clubs/                  # Clubs & cells with members
├── fees/                   # Fee structures, payments
├── grievances/             # Grievance submission & management
├── exam_forms/             # Exam registration & approval
├── placements/             # Placement partners, drives, apps
├── templates/              # All HTML templates
├── static/                 # CSS, JS, images
│   └── images/partners/    # Company logo SVGs
├── student_management/     # Project settings, URLs, WSGI
└── staticfiles/            # Collected static (auto-generated)
```

## Management Commands

| Command | Description |
|---------|-------------|
| `seed_data` | Seed students (720), classes (48), attendance, results |
| `seed_members` | Seed 5 members per club (coordinator + vice_coordinator + 3 members) |
| `seed_club_photos` | Fetch club-relevant photos from loremflickr |
| `seed_student_photos` | Generate profile photos (initials + gradient) for club members |
| `seed_timetable` | Generate timetable slots for all classes |
| `send_attendance_alerts` | Email absent students' parents (cron-ready) |

## Key Design Decisions

- **Session-based auth** for students (`request.session.student_id`) vs Django auth for staff
- **Student nav priority** checked before staff nav in `base.html` to prevent staff nav in student portal
- **Soft-delete** (`is_deleted` field) for student records; restorable from admin
- **ID card** uses PIL `Image.composite` for circular photo crop (avoids reportlab clip path bugs)
- **PDF streams** use `/ASCII85Decode /FlateDecode` filters (reportlab 5.0)
- **Company logos** sourced from Wikimedia Commons SVGs (public domain / fair use)
