from django.urls import path, include
from gricapi import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'catalog/produce', views.ProduceViewSet, basename="products")
router.register(r'catalog/produce-category',
                views.ProduceCategoryViewSet, basename="produce-category")
router.register(r'shop/order', views.OrderViewSet, basename='shopping')

app_name = "api"
urlpatterns = [
    path('', include(router.urls)),
]
