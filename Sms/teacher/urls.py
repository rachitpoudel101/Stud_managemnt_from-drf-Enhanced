from rest_framework.routers import DefaultRouter
from teacher.views import SubjectViewSet, AssignmentViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subjects')
router.register(r'assignments', AssignmentViewSet, basename='assignments')

urlpatterns = router.urls
