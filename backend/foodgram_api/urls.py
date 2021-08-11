from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import FollowViewSet


router = DefaultRouter()
router.register('users', FollowViewSet, basename='follow')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # path('api/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),
]
