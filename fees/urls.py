from django.urls import path
from .views import (
    FeeListView, FeePaymentView, FeeSelectionView,
    InitiatePaymentView, OnlinePaymentHistoryView,
    PaymentSuccessView, StudentFeeListView,
)

app_name = 'fees'
urlpatterns = [
    path('', FeeListView.as_view(), name='fee_list'),
    path('student/', StudentFeeListView.as_view(), name='student_fees'),
    path('pay/<int:pk>/', FeePaymentView.as_view(), name='pay'),
    path('pay-online/', FeeSelectionView.as_view(), name='fee_selection'),
    path('pay-online/<int:fee_id>/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('payment/success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('payment/history/', OnlinePaymentHistoryView.as_view(), name='payment_history'),
]
