from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UsuarioViewSet, 
    LoginView, 
    LogoutView,
    RegisterView,
    VerifyEmailView,
    ResendVerificationView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ListUsersView
)

router = DefaultRouter()
router.register(r'', UsuarioViewSet, basename='usuario')

urlpatterns = [
    # Autenticación
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    
    # Verificación de email
    path('auth/verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('auth/resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    
    # Recuperación de contraseña
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # Lista de usuarios
    path('auth/list-users/', ListUsersView.as_view(), name='list-users'),
    
    # ViewSet de usuarios (debe ir al final)
    path('', include(router.urls)),
] 