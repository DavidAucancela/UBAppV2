from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnvioViewSet, ProductoViewSet, TarifaViewSet, ImportacionExcelViewSet

router = DefaultRouter()
router.register(r'envios', EnvioViewSet, basename='envio')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'tarifas', TarifaViewSet, basename='tarifa')
router.register(r'importaciones-excel', ImportacionExcelViewSet, basename='importacion-excel')

urlpatterns = [
    path('', include(router.urls)),
] 