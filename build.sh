#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Seed database
python manage.py seed_data
python manage.py seed_members
python manage.py seed_club_images
python manage.py seed_club_photos
python manage.py seed_student_photos
python manage.py seed_timetable

echo "Build complete"
