from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, LoginView, LogoutView, ResetPasswordView, VerifyEmailView, RegisterCompradorView
from .views_ubicaciones import (
    obtener_provincias_view,
    obtener_cantones_view,
    obtener_ciudades_view,
    obtener_coordenadas_view
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [

]

router = DefaultRouter()
router.register(r'', UsuarioViewSet, basename='usuario')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/register/', RegisterCompradorView.as_view(), name='register-comprador'),
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    

    # Endpoints de ubicaciones
    path('ubicaciones/provincias/', obtener_provincias_view, name='provincias'),
    path('ubicaciones/cantones/', obtener_cantones_view, name='cantones'),
    path('ubicaciones/ciudades/', obtener_ciudades_view, name='ciudades'),
    path('ubicaciones/coordenadas/', obtener_coordenadas_view, name='coordenadas'),
] 