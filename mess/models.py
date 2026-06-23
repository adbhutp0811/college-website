from django.db import models
from students.models import Student


class MessMenu(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday'),
    ]
    MEAL_CHOICES = [
        ('breakfast', 'Breakfast'), ('lunch', 'Lunch'), ('snacks', 'Evening Snacks'), ('dinner', 'Dinner'),
    ]
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    meal_type = models.CharField(max_length=10, choices=MEAL_CHOICES)
    items = models.TextField(help_text='Comma-separated list of items')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day', 'meal_type']
        unique_together = ('day', 'meal_type')

    def __str__(self):
        return f'{self.get_day_display()} - {self.get_meal_type_display()}'


class MessFeePeriod(models.Model):
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
    ]
    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    due_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ('month', 'year')

    def __str__(self):
        return f'{self.get_month_display()} {self.year} - ₹{self.amount}'


class MessPayment(models.Model):
    STATUS_CHOICES = [('paid', 'Paid'), ('pending', 'Pending'), ('overdue', 'Overdue')]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='mess_payments')
    fee_period = models.ForeignKey(MessFeePeriod, on_delete=models.CASCADE, related_name='payments')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-fee_period__year', '-fee_period__month']
        unique_together = ('student', 'fee_period')

    def __str__(self):
        return f'{self.student.roll_number} - {self.fee_period}'


class MessComplaint(models.Model):
    CATEGORY_CHOICES = [
        ('food_quality', 'Food Quality'),
        ('hygiene', 'Hygiene'),
        ('service', 'Service'),
        ('menu', 'Menu Suggestion'),
        ('other', 'Other'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='mess_complaints')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student.full_name} - {self.subject}'
