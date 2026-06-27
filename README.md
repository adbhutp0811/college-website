# Miracle Institute - Student Management System

A comprehensive Django-based Student Management System designed for educational institutions. It provides modules for managing students, faculty, attendance, results, fees, library, hostel, placements, events, and more.

## Features

- **Accounts** - User authentication, roles (admin, faculty, student), and profile management
- **Students** - Student enrollment, profiles, and academic records
- **Attendance** - Mark and track student attendance
- **Results** - Manage and publish exam results
- **Timetable** - Class and exam scheduling
- **Fees** - Fee management with Razorpay and Stripe payment gateway integration
- **Library** - Book catalog and issue/return management
- **Hostel** - Hostel allocation and room management
- **Mess** - Mess menu and fee management
- **Faculty & Mentor** - Faculty profiles and mentor allocation
- **Placements** - Placement drives and student applications
- **Events** - Event management and registration
- **Clubs & Sports** - Club and sports team management
- **Notices** - Notice board with announcements
- **Exam Forms & Seating** - Online exam form submission and seating arrangement
- **Quiz** - Online quiz system
- **Course Materials** - Upload and share study materials
- **Feedback** - Student feedback system
- **Grievances** - Complaint/grievance redressal system
- **Leave Management** - Leave application and approval
- **Gallery** - Photo gallery
- **Scholarships** - Scholarship applications and management
- **Anti-Ragging** - Anti-ragging compliance management
- **Alumni** - Alumni network and management
- **Elections** - Student council elections

## Tech Stack

- **Framework**: Django 6.0
- **Frontend**: Bootstrap 5 (via django-crispy-forms)
- **Database**: SQLite (default), MySQL, or PostgreSQL
- **Payment**: Razorpay & Stripe integration
- **PDF**: ReportLab & xhtml2pdf
- **Deployment**: Render, Gunicorn, WhiteNoise

## Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd student_management_system
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your settings.

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Deployment

The project includes configuration for **Render** (`render.yaml`, `build.sh`, `start.sh`). Static files are served via WhiteNoise. PostgreSQL is supported for production.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django secret key | - |
| `DJANGO_DEBUG` | Debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `DJANGO_DB_ENGINE` | Database engine (`sqlite`, `mysql`, `postgresql`) | `sqlite` |
| `DATABASE_URL` | PostgreSQL connection URL (overrides other DB settings) | - |
| `RAZORPAY_KEY_ID` | Razorpay key ID | - |
| `RAZORPAY_KEY_SECRET` | Razorpay key secret | - |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | - |
| `STRIPE_SECRET_KEY` | Stripe secret key | - |
| `PAYMENT_GATEWAY` | Active payment gateway | `razorpay` |

---

> Made by **❤Miracle AD**
