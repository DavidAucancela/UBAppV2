from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    """Modelo de usuario personalizado con roles"""
    
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
    fecha_nacimiento = models.DateField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    es_activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

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
