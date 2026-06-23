from django.urls import path
from .views import FeeListView, FeePaymentView, StudentFeeListView

app_name = 'fees'
urlpatterns = [
    path('', FeeListView.as_view(), name='fee_list'),
    path('student/', StudentFeeListView.as_view(), name='student_fees'),
    path('pay/<int:pk>/', FeePaymentView.as_view(), name='pay'),
]
