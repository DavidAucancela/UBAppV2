from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnvioViewSet, ProductoViewSet, TarifaViewSet

router = DefaultRouter()
router.register(r'envios', EnvioViewSet, basename='envio')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'tarifas', TarifaViewSet, basename='tarifa')

urlpatterns = [
    path('', include(router.urls)),
] 