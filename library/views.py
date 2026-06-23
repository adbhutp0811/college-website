from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, View, TemplateView
from django.contrib import messages
from django.utils import timezone
from .models import Book, BookIssue
from students.models import Student
from datetime import timedelta


class BookListView(ListView):
    model = Book
    template_name = 'library/book_list.html'
    context_object_name = 'books'
    paginate_by = 20

    def get_queryset(self):
        qs = Book.objects.all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(author__icontains=q)
        return qs


class BookDetailView(DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'
    slug_field = 'pk'


class IssueBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        if book.available_copies < 1:
            messages.error(request, 'No copies available for issue.')
            return redirect('library:book_detail', pk=pk)
        student_id = request.session.get('student_id')
        if not student_id:
            messages.error(request, 'Please login as student first.')
            return redirect('accounts:student_login')
        student = get_object_or_404(Student, id=student_id)
        active_issues = BookIssue.objects.filter(student=student, status='issued').count()
        if active_issues >= 3:
            messages.error(request, 'You already have 3 active book issues. Return a book first.')
            return redirect('library:book_detail', pk=pk)
        BookIssue.objects.create(
            book=book,
            student=student,
            issued_by=request.user,
            due_date=timezone.now().date() + timedelta(days=14),
        )
        book.available_copies -= 1
        book.save()
        messages.success(request, f'Book "{book.title}" issued successfully! Due in 14 days.')
        return redirect('library:my_issues')


class ReturnBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        issue = get_object_or_404(BookIssue, pk=pk, status='issued')
        issue.status = 'returned'
        issue.returned_at = timezone.now()
        issue.save()
        issue.book.available_copies += 1
        issue.book.save()
        messages.success(request, f'Book "{issue.book.title}" returned successfully.')
        return redirect('library:my_issues')


class MyIssuesView(TemplateView):
    template_name = 'library/my_issues.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        student_id = self.request.session.get('student_id')
        if student_id:
            student = get_object_or_404(Student, id=student_id)
            ctx['active_issues'] = BookIssue.objects.filter(student=student, status='issued').select_related('book')
            ctx['returned_issues'] = BookIssue.objects.filter(student=student, status='returned').select_related('book')[:10]
        return ctx
