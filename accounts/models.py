from django.contrib.auth.models import AbstractUser
from django.db import models


class LeadershipMember(models.Model):
    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='leadership/', blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return f'{self.name} - {self.designation}'


class DirectorMessage(models.Model):
    name = models.CharField(max_length=200)
    designation = models.CharField(max_length=200)
    message = models.TextField()
    photo = models.ImageField(upload_to='director/', blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name} - {self.designation}'

    class Meta:
        verbose_name = "Director's Message"
        verbose_name_plural = "Director's Messages"


class Department(models.Model):
    code = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=200)
    description = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return f'{self.code} - {self.full_name}'


class PlacementPartner(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='partners/', blank=True)
    website = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.name


class Testimonial(models.Model):
    student_name = models.CharField(max_length=200)
    batch = models.CharField(max_length=50)
    program = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    photo = models.ImageField(upload_to='testimonials/', blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return f'{self.student_name} ({self.batch})'


class ContactInfo(models.Model):
    address = models.TextField()
    phone = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    map_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return 'Contact Information'

    class Meta:
        verbose_name = 'Contact Information'
        verbose_name_plural = 'Contact Information'


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        TEACHER = 'teacher', 'Teacher'
        STUDENT = 'student', 'Student'
        PARENT = 'parent', 'Parent'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.TEACHER)
    phone = models.CharField(max_length=15, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f'{self.get_full_name()} ({self.get_role_display()})'
