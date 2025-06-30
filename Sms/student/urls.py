from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentProfileViewSet, MarksViewSet, StudentSubmissionViewSet

router = DefaultRouter()
router.register(r'student-profiles', StudentProfileViewSet, basename='student-profiles')
router.register(r'marks', MarksViewSet)
router.register(r'submissions', StudentSubmissionViewSet)

urlpatterns = router.urls
