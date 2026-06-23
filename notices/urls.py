from django.urls import path
from .views import NoticeListView, NoticeDetailView, CreateNoticeView

app_name = 'notices'
urlpatterns = [
    path('', NoticeListView.as_view(), name='notice_list'),
    path('<int:pk>/', NoticeDetailView.as_view(), name='notice_detail'),
    path('create/', CreateNoticeView.as_view(), name='create_notice'),
]
