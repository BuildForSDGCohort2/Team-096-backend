from django.urls import path, include
from gricapi import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

app_name = "api"
urlpatterns = [
    path('api/', include(router.urls)),
]
