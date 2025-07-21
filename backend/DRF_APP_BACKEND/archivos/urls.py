from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnvioViewSet, ProductoViewSet

router = DefaultRouter()
router.register(r'envios', EnvioViewSet, basename='envio')
router.register(r'productos', ProductoViewSet, basename='producto')

urlpatterns = [
    path('', include(router.urls)),
] 