from django.db import models
from students.models import Student


class FeeStructure(models.Model):
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    semester = models.CharField(max_length=20)
    is_mandatory = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f'{self.name} - {self.semester}'


class Payment(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('paid', 'Paid'), ('overdue', 'Overdue'), ('partial', 'Partial')]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)
    razorpay_order_id = models.CharField(max_length=200, blank=True)
    stripe_session_id = models.CharField(max_length=200, blank=True)
    payment_intent_id = models.CharField(max_length=200, blank=True)
    gateway = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ['-paid_at']

    def __str__(self):
        return f'{self.student.roll_number} - {self.fee_structure.name}'

    @property
    def due_amount(self):
        return self.fee_structure.amount - self.amount_paid


class OnlinePayment(models.Model):
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('attempted', 'Attempted'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='online_payments')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=200, unique=True)
    gateway_payment_id = models.CharField(max_length=200, blank=True)
    signature = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    gateway = models.CharField(max_length=20, default='razorpay')
    payment_record = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='online_payments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student.roll_number} - {self.amount} - {self.status}'
