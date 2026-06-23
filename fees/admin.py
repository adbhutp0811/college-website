from django.contrib import admin
from .models import FeeStructure, OnlinePayment, Payment

admin.site.register(FeeStructure)
admin.site.register(Payment)
admin.site.register(OnlinePayment)
