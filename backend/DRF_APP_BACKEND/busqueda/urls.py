from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusquedaViewSet

router = DefaultRouter()
router.register(r'', BusquedaViewSet, basename='busqueda')

urlpatterns = [
    path('', include(router.urls)),
] 