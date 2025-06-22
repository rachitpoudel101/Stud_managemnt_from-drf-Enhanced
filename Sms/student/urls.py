from rest_framework.routers import DefaultRouter
from student.views import MarksViewSet

router = DefaultRouter()
router.register(r'marks', MarksViewSet, basename='marks')

urlpatterns = router.urls
