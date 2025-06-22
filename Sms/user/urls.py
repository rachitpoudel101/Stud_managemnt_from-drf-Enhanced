from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CustomTokenObtainPairView ,NoticeViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'notice', NoticeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
