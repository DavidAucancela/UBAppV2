from django.contrib.auth.models import AbstractUser
from django.db import models
import re
from django.core.exceptions import ValidationError

def validar_cedula_ecuatoriana(cedula):
    """Valida cédula ecuatoriana usando algoritmo módulo 10"""
    if not cedula or len(cedula) != 10:
        raise ValidationError("La cédula debe tener 10 dígitos")
    
    # Verificar que solo contenga dígitos
    if not cedula.isdigit():
        raise ValidationError("La cédula solo debe contener números")
    
    # Verificar provincia (primeros 2 dígitos entre 01 y 24)
    provincia = int(cedula[0:2])
    if provincia < 1 or provincia > 24:
        raise ValidationError("Los dos primeros dígitos deben estar entre 01 y 24 (código de provincia)")
    
    # Tercer dígito debe ser menor a 6 (personas naturales)
    if int(cedula[2]) >= 6:
        raise ValidationError("El tercer dígito debe ser menor a 6 para personas naturales")
    
    # Algoritmo módulo 10
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0
    
    for i in range(9):
        valor = int(cedula[i]) * coeficientes[i]
        if valor >= 10:
            valor -= 9
        suma += valor
    
    resultado = suma % 10
    verificador = 0 if resultado == 0 else 10 - resultado
    
    if verificador != int(cedula[9]):
        raise ValidationError("El dígito verificador de la cédula no es válido")

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
    cedula = models.CharField(
        max_length=10, 
        unique=True, 
        blank=False, 
        null=False,
        validators=[validar_cedula_ecuatoriana],
        help_text="Cédula ecuatoriana de 10 dígitos"
    )
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