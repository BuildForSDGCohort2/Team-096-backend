from django.urls import path, include
from gricapi import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename="user-profile")
router.register(r'catalog/produce', views.ProduceViewSet, basename="products")
router.register(r'catalog/produce-category',
                views.ProduceCategoryViewSet, basename="produce-category")
router.register(r'shop/order', views.OrderViewSet, basename='shopping')

# schema_view = get_schema_view(
#     title='GRIC API',
#     description="Api endpoints to use GricApp",
#     renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer],
# )

app_name = "api"
urlpatterns = [
    path('', include(router.urls)),
]
