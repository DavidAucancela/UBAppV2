"""
Tareas asíncronas de Celery para el módulo de usuarios.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_bienvenida(self, nombre, username, password, rol, correo, frontend_url=None):
    """Envía correo de bienvenida con credenciales al nuevo usuario."""
    if not frontend_url:
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:4200')
    try:
        send_mail(
            subject='Bienvenido a UBApp - Credenciales de acceso',
            message=f'''
Hola {nombre or username},

Tu cuenta ha sido creada exitosamente en UBApp.

Credenciales de acceso:
- Usuario: {username}
- Contraseña: {password}
- Rol: {rol}

Por favor, inicia sesión y cambia tu contraseña por razones de seguridad.

Puedes acceder al sistema en: {frontend_url}

Saludos,
Equipo UBApp
            ''',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ubapp.com'),
            recipient_list=[correo],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def enviar_reset_password(self, nombre, username, new_password, email):
    """Envía correo de restablecimiento de contraseña."""
    try:
        send_mail(
            subject='Restablecimiento de contraseña - UBApp',
            message=f'''
Hola {nombre or username},

Has solicitado restablecer tu contraseña en UBApp.

Tu nueva contraseña temporal es: {new_password}

Por favor, inicia sesión con esta contraseña y cámbiala inmediatamente por una contraseña segura.

Si no solicitaste este restablecimiento, por favor contacta al administrador del sistema.

Saludos,
Equipo UBApp
            ''',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ubapp.com'),
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)
