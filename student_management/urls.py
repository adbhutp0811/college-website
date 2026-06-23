from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from accounts.views import CollegeHomeView, DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', CollegeHomeView.as_view(), name='college_home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('students/', include('students.urls', namespace='students')),
    path('attendance/', include('attendance.urls', namespace='attendance')),
    path('results/', include('results.urls', namespace='results')),
    path('clubs/', include('clubs.urls', namespace='clubs')),
    path('fees/', include('fees.urls', namespace='fees')),
    path('notices/', include('notices.urls', namespace='notices')),
    path('timetable/', include('timetable.urls', namespace='timetable')),
    path('library/', include('library.urls', namespace='library')),
    path('events/', include('events.urls', namespace='events')),
    path('placements/', include('placements.urls', namespace='placements')),
    path('hostel/', include('hostel.urls', namespace='hostel')),
    path('grievances/', include('grievances.urls', namespace='grievances')),
    path('exam-forms/', include('exam_forms.urls', namespace='exam_forms')),
    path('faculty/', include('faculty.urls', namespace='faculty')),
    path('mentor/', include('mentor.urls', namespace='mentor')),
    path('sports/', include('sports.urls', namespace='sports')),
    path('scholarships/', include('scholarships.urls', namespace='scholarships')),
    path('mess/', include('mess.urls', namespace='mess')),
    path('antiragging/', include('antiragging.urls', namespace='antiragging')),
    path('exam-seating/', include('exam_seating.urls', namespace='exam_seating')),
    path('quiz/', include('quiz.urls', namespace='quiz')),
    path('course-materials/', include('course_materials.urls', namespace='course_materials')),
    path('feedback/', include('feedback.urls', namespace='feedback')),
    path('leave-management/', include('leave_management.urls', namespace='leave_management')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
