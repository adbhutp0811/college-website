from django.db import models
from django.utils.text import slugify


class Faculty(models.Model):
    DESIGNATION_CHOICES = [
        ('professor_hod', 'Professor & HOD'),
        ('professor', 'Professor'),
        ('associate_professor', 'Associate Professor'),
        ('assistant_professor', 'Assistant Professor'),
        ('lecturer', 'Lecturer'),
        ('lab_assistant', 'Lab Assistant'),
    ]

    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    designation = models.CharField(max_length=50, choices=DESIGNATION_CHOICES)
    qualification = models.CharField(max_length=200)
    specialization = models.TextField(blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    experience = models.CharField(max_length=50, blank=True)
    profile_pic = models.ImageField(upload_to='faculty/', blank=True)
    classes = models.ManyToManyField('students.Class', related_name='faculty_members', blank=True)
    joining_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        db_table = 'faculty'
        ordering = ['first_name', 'last_name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f'{self.first_name} {self.last_name}')
            slug = base
            counter = 1
            while Faculty.objects.filter(slug=slug).exists():
                slug = f'{base}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title} {self.first_name} {self.last_name}'

    @property
    def title(self):
        return 'Dr.' if 'Ph.D' in (self.qualification or '') else 'Er.'

    @property
    def full_name(self):
        return f'{self.title} {self.first_name} {self.last_name}'

    @property
    def initial(self):
        return self.first_name[0] if self.first_name else '?'

    @property
    def department(self):
        classes = self.classes.all()
        if classes:
            branches = set(c.name for c in classes)
            return ', '.join(sorted(branches))
        return 'Not Assigned'

    @property
    def designation_display(self):
        return dict(self.DESIGNATION_CHOICES).get(self.designation, self.designation)
