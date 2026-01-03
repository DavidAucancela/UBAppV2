from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinLengthValidator
from .validators import validar_cedula_ecuatoriana

class Usuario(AbstractUser):
    """Modelo de usuario personalizado con roles"""
    
    ROLES_CHOICES = [
        (1, 'Admin'),
        (2, 'Gerente'),
        (3, 'Digitador'),
        (4, 'Comprador'),
    ]
    
    # Eliminar campos heredados de AbstractUser que no existen en la BD
    first_name = None
    last_name = None
    email = None
    # Nota: is_active se hereda de AbstractUser y mapea a columna 'is_active' en BD
    # Usamos propiedad es_activo como alias en español
    
    # Campos básicos requeridos
    nombre = models.CharField(
        max_length=100,
        blank=False,
        null=True,
        validators=[MinLengthValidator(2, 'El nombre debe tener al menos 2 caracteres')]
    )
    correo = models.EmailField(unique=True, blank=False, null=True)
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
    
    # Cupo anual para compradores (en kilogramos)
    cupo_anual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1000.00,
        verbose_name="Cupo Anual (kg)",
        help_text="Límite de peso anual que puede enviar el comprador"
    )
    
    # Campos de ubicación para mapa (Provincia -> Cantón -> Ciudad)
    provincia = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Provincia",
        help_text="Provincia de residencia del usuario"
    )
    canton = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Cantón",
        help_text="Cantón de residencia del usuario"
    )
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ciudad",
        help_text="Ciudad de residencia del usuario"
    )
    
    # NO redefinir es_activo como campo - usar propiedad que apunta a is_active heredado
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} - {self.cedula}"

    def get_rol_display_name(self):
        """Obtiene el nombre del rol"""
        return dict(self.ROLES_CHOICES)[self.rol]
    
    def get_ubicacion_completa(self):
        """Retorna la ubicación completa en formato legible"""
        partes = []
        if self.ciudad:
            partes.append(self.ciudad)
        if self.canton:
            partes.append(self.canton)
        if self.provincia:
            partes.append(self.provincia)
        return ', '.join(partes) if partes else 'Sin ubicación'
    
    
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
    
    # Propiedad es_activo como alias del campo heredado is_active
    @property
    def es_activo(self):
        """Alias en español para is_active (campo heredado de AbstractUser)"""
        return self.is_active
    
    @es_activo.setter
    def es_activo(self, value):
        """Setter para es_activo: actualiza is_active"""
        self.is_active = value
    
    def obtener_peso_usado_anual(self, anio=None):
        """Calcula el peso total de envíos del comprador en un año específico"""
        from datetime import datetime
        from django.db.models import Sum
        
        if anio is None:
            anio = datetime.now().year
        
        # Sumar peso de todos los envíos del año
        peso_total = self.envio_set.filter(
            fecha_emision__year=anio
        ).exclude(
            estado='cancelado'
        ).aggregate(
            total=Sum('peso_total')
        )['total'] or 0
        
        return float(peso_total)
    
    def obtener_peso_disponible_anual(self, anio=None):
        """Calcula el peso disponible del cupo anual"""
        peso_usado = self.obtener_peso_usado_anual(anio)
        return float(self.cupo_anual) - peso_usado
    
    def obtener_porcentaje_cupo_usado(self, anio=None):
        """Calcula el porcentaje del cupo anual usado"""
        if float(self.cupo_anual) == 0:
            return 0
        peso_usado = self.obtener_peso_usado_anual(anio)
        return (peso_usado / float(self.cupo_anual)) * 100
    
    def obtener_estadisticas_envios(self, anio=None):
        """Obtiene estadísticas completas de envíos del comprador"""
        from datetime import datetime
        from django.db.models import Sum, Count
        
        if anio is None:
            anio = datetime.now().year
        
        envios = self.envio_set.filter(fecha_emision__year=anio)
        
        return {
            'total_envios': envios.count(),
            'envios_pendientes': envios.filter(estado='pendiente').count(),
            'envios_en_transito': envios.filter(estado='en_transito').count(),
            'envios_entregados': envios.filter(estado='entregado').count(),
            'envios_cancelados': envios.filter(estado='cancelado').count(),
            'peso_total': float(envios.exclude(estado='cancelado').aggregate(
                total=Sum('peso_total')
            )['total'] or 0),
            'valor_total': float(envios.exclude(estado='cancelado').aggregate(
                total=Sum('valor_total')
            )['total'] or 0),
            'costo_servicio_total': float(envios.exclude(estado='cancelado').aggregate(
                total=Sum('costo_servicio')
            )['total'] or 0),
        }