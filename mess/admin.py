from django.contrib import admin
from .models import MessMenu, MessFeePeriod, MessPayment, MessComplaint

admin.site.register(MessMenu)
admin.site.register(MessFeePeriod)
admin.site.register(MessPayment)
admin.site.register(MessComplaint)
