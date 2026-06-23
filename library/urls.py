from django.urls import path
from .views import BookListView, BookDetailView, IssueBookView, ReturnBookView, MyIssuesView

app_name = 'library'
urlpatterns = [
    path('', BookListView.as_view(), name='book_list'),
    path('<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('<int:pk>/issue/', IssueBookView.as_view(), name='issue_book'),
    path('issue/<int:pk>/return/', ReturnBookView.as_view(), name='return_book'),
    path('my-issues/', MyIssuesView.as_view(), name='my_issues'),
]
