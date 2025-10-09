from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import secrets
from datetime import timedelta

class Usuario(AbstractUser):
    """Modelo de usuario personalizado con roles y funcionalidades de seguridad"""
    
    ROLES_CHOICES = [
        (1, 'Admin'),
        (2, 'Gerente'),
        (3, 'Digitador'),
        (4, 'Comprador'),
    ]
    
    # Campos básicos requeridos
    nombre = models.CharField(max_length=100, blank=True, null=True)
    correo = models.EmailField(unique=True, blank=True, null=True)
    cedula = models.CharField(max_length=20, unique=True, blank=True, null=True)
    rol = models.IntegerField(choices=ROLES_CHOICES, default=4)
    
    # Campos adicionales
    telefono = models.CharField(max_length=15, blank=True, null=True)
    # Condiciones especiales (p.ej. discapacidad, notas de accesibilidad)
    tiene_discapacidad = models.BooleanField(default=False)
    tipo_discapacidad = models.CharField(max_length=100, blank=True, null=True)
    notas_accesibilidad = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    es_activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Campos para verificación de email y recuperación de contraseña
    email_verificado = models.BooleanField(default=False)
    token_verificacion = models.CharField(max_length=100, blank=True, null=True)
    token_verificacion_expira = models.DateTimeField(blank=True, null=True)
    token_recuperacion = models.CharField(max_length=100, blank=True, null=True)
    token_recuperacion_expira = models.DateTimeField(blank=True, null=True)
    
    # Campos para políticas de seguridad
    ultima_actividad = models.DateTimeField(default=timezone.now)
    intentos_login_fallidos = models.IntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(blank=True, null=True)
    debe_cambiar_password = models.BooleanField(default=False)
    ultima_cambio_password = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - {self.cedula}"

    def get_rol_display_name(self):
        """Obtiene el nombre del rol"""
        return dict(self.ROLES_CHOICES)[self.rol]

    @property
    def es_admin(self):
        return self.rol == 1

    @property
    def es_gerente(self):
        return self.rol == 2

    @property
    def es_digitador(self):
        return self.rol == 3

    @property
    def es_comprador(self):
        return self.rol == 4
    
    def generar_token_verificacion(self):
        """Genera un token único para verificación de email"""
        self.token_verificacion = secrets.token_urlsafe(32)
        self.token_verificacion_expira = timezone.now() + timedelta(hours=24)
        self.save()
        return self.token_verificacion
    
    def generar_token_recuperacion(self):
        """Genera un token único para recuperación de contraseña"""
        self.token_recuperacion = secrets.token_urlsafe(32)
        self.token_recuperacion_expira = timezone.now() + timedelta(hours=2)
        self.save()
        return self.token_recuperacion
    
    def verificar_email(self, token):
        """Verifica el email del usuario si el token es válido"""
        if (self.token_verificacion == token and 
            self.token_verificacion_expira and 
            self.token_verificacion_expira > timezone.now()):
            self.email_verificado = True
            self.token_verificacion = None
            self.token_verificacion_expira = None
            self.save()
            return True
        return False
    
    def puede_recuperar_password(self, token):
        """Verifica si el token de recuperación es válido"""
        return (self.token_recuperacion == token and 
                self.token_recuperacion_expira and 
                self.token_recuperacion_expira > timezone.now())
    
    def actualizar_ultima_actividad(self):
        """Actualiza el timestamp de última actividad"""
        self.ultima_actividad = timezone.now()
        self.save(update_fields=['ultima_actividad'])



# verificacion de intentos del login 
    def esta_bloqueado(self):
        """Verifica si el usuario está bloqueado por intentos fallidos"""
        if self.bloqueado_hasta:
            if self.bloqueado_hasta > timezone.now():
                return True
            else:
                # Desbloquear si ya pasó el tiempo
                self.bloqueado_hasta = None
                self.intentos_login_fallidos = 0
                self.save()
        return False
    
    def incrementar_intentos_fallidos(self):
        """Incrementa el contador de intentos fallidos y bloquea si es necesario"""
        self.intentos_login_fallidos += 1
        if self.intentos_login_fallidos >= 5:
            self.bloqueado_hasta = timezone.now() + timedelta(minutes=30)
        self.save()
    
    def resetear_intentos_fallidos(self):
        """Resetea el contador de intentos fallidos"""
        self.intentos_login_fallidos = 0
        self.bloqueado_hasta = None
        self.save()
