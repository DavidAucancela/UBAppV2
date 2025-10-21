from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import json

Usuario = get_user_model()


class Tarifa(models.Model):
    """Modelo para tarifas de envío por categoría y peso"""
    categoria = models.CharField(
        max_length=50,
        choices=[
            ('electronica', 'Electrónica'),
            ('ropa', 'Ropa'),
            ('hogar', 'Hogar'),
            ('deportes', 'Deportes'),
            ('otros', 'Otros'),
        ],
        verbose_name="Categoría"
    )
    peso_minimo = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name="Peso Mínimo (kg)",
        help_text="Peso mínimo en kilogramos para aplicar esta tarifa"
    )
    peso_maximo = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name="Peso Máximo (kg)",
        help_text="Peso máximo en kilogramos para aplicar esta tarifa"
    )
    precio_por_kg = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        verbose_name="Precio por Kg ($)",
        help_text="Precio en dólares por kilogramo"
    )
    cargo_base = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0,
        verbose_name="Cargo Base ($)",
        help_text="Cargo fijo base para esta categoría y rango de peso"
    )
    activa = models.BooleanField(default=True, verbose_name="Activa")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tarifa'
        verbose_name_plural = 'Tarifas'
        ordering = ['categoria', 'peso_minimo']
        unique_together = [['categoria', 'peso_minimo', 'peso_maximo']]

    def __str__(self):
        return f"{self.get_categoria_display()} - {self.peso_minimo}kg a {self.peso_maximo}kg: ${self.precio_por_kg}/kg"

    def clean(self):
        """Valida que peso_maximo sea mayor que peso_minimo"""
        if self.peso_maximo <= self.peso_minimo:
            raise ValidationError("El peso máximo debe ser mayor que el peso mínimo")

    def calcular_costo(self, peso):
        """Calcula el costo para un peso dado"""
        return float(self.cargo_base) + (float(peso) * float(self.precio_por_kg))


class Envio(models.Model):
    """Modelo para gestionar envíos"""
    hawb = models.CharField(max_length=50, unique=True, verbose_name="HAWB")
    peso_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Peso Total")
    cantidad_total = models.IntegerField(verbose_name="Cantidad Total")
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Total")
    costo_servicio = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name="Costo del Servicio",
        help_text="Costo calculado automáticamente según tarifas"
    )
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Emisión")
    
    # Relación con comprador
    comprador = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        limit_choices_to={'rol': 4},  # Solo compradores
        verbose_name="Comprador"
    )
    
    # Campos adicionales
    estado = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('en_transito', 'En Tránsito'),
            ('entregado', 'Entregado'),
            ('cancelado', 'Cancelado'),
        ],
        default='pendiente',
        verbose_name="Estado"
    )
    
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Envío'
        verbose_name_plural = 'Envíos'
        ordering = ['-fecha_emision']

    def __str__(self):
        return f"HAWB: {self.hawb} - {self.comprador.nombre}"

    def calcular_totales(self):
        """Calcula los totales basados en los productos"""
        productos = self.productos.all()
        self.peso_total = sum(p.peso for p in productos)
        self.cantidad_total = sum(p.cantidad for p in productos)
        self.valor_total = sum(p.valor for p in productos)
        
        # Calcular costo del servicio basado en tarifas
        self.costo_servicio = self.calcular_costo_servicio()
        self.save()
    
    def calcular_costo_servicio(self):
        """Calcula el costo del servicio basado en productos y tarifas"""
        costo_total = 0
        productos = self.productos.all()
        
        for producto in productos:
            # Buscar tarifa aplicable para esta categoría y peso
            tarifa = Tarifa.objects.filter(
                categoria=producto.categoria,
                peso_minimo__lte=producto.peso,
                peso_maximo__gte=producto.peso,
                activa=True
            ).first()
            
            if tarifa:
                # Calcular costo para este producto
                costo_producto = tarifa.calcular_costo(producto.peso) * producto.cantidad
                costo_total += costo_producto
                # Guardar el costo en el producto para referencia
                Producto.objects.filter(id=producto.id).update(costo_envio=costo_producto)
            else:
                # Si no hay tarifa, mantener costo en 0 o usar valor por defecto
                Producto.objects.filter(id=producto.id).update(costo_envio=0)
        
        return costo_total

class Producto(models.Model):
    """Modelo para productos en envíos"""
    descripcion = models.CharField(max_length=200, verbose_name="Descripción")
    peso = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Peso")
    cantidad = models.IntegerField(verbose_name="Cantidad")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    costo_envio = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Costo de Envío",
        help_text="Costo calculado según tarifa de categoría y peso"
    )
    
    # Relación con envío
    envio = models.ForeignKey(
        Envio, 
        on_delete=models.CASCADE, 
        related_name='productos',
        verbose_name="Envío"
    )
    
    # Campos adicionales
    categoria = models.CharField(
        max_length=50,
        choices=[
            ('electronica', 'Electrónica'),
            ('ropa', 'Ropa'),
            ('hogar', 'Hogar'),
            ('deportes', 'Deportes'),
            ('otros', 'Otros'),
        ],
        default='otros',
        verbose_name="Categoría"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.descripcion} - {self.envio.hawb}"

    def save(self, *args, **kwargs):
        """Recalcula totales del envío al guardar"""
        super().save(*args, **kwargs)
        # Solo recalcular totales si no estamos en update_fields
        # (evita recursión cuando se actualiza solo costo_envio)
        if not kwargs.get('update_fields'):
            self.envio.calcular_totales()


class ImportacionExcel(models.Model):
    """Modelo para gestionar importaciones de archivos Excel"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('validando', 'Validando'),
        ('validado', 'Validado'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('error', 'Error'),
    ]
    
    # Información del archivo
    archivo = models.FileField(
        upload_to='importaciones/%Y/%m/',
        verbose_name="Archivo Excel"
    )
    nombre_original = models.CharField(
        max_length=255,
        verbose_name="Nombre Original del Archivo"
    )
    
    # Estado de la importación
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estado"
    )
    
    # Usuario que realizó la importación
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='importaciones',
        verbose_name="Usuario"
    )
    
    # Estadísticas de la importación
    total_registros = models.IntegerField(
        default=0,
        verbose_name="Total de Registros"
    )
    registros_validos = models.IntegerField(
        default=0,
        verbose_name="Registros Válidos"
    )
    registros_errores = models.IntegerField(
        default=0,
        verbose_name="Registros con Errores"
    )
    registros_duplicados = models.IntegerField(
        default=0,
        verbose_name="Registros Duplicados"
    )
    registros_procesados = models.IntegerField(
        default=0,
        verbose_name="Registros Procesados"
    )
    
    # Detalles de validación y errores
    errores_validacion = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Errores de Validación",
        help_text="Detalles de errores encontrados durante la validación"
    )
    
    # Configuración de importación
    columnas_mapeadas = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Mapeo de Columnas",
        help_text="Mapeo entre columnas del Excel y campos del modelo"
    )
    
    registros_seleccionados = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Índices de Registros Seleccionados",
        help_text="Lista de índices de registros que se importarán"
    )
    
    # Resultados
    mensaje_resultado = models.TextField(
        blank=True,
        null=True,
        verbose_name="Mensaje de Resultado"
    )
    
    # Fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_completado = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Completado"
    )
    
    class Meta:
        verbose_name = 'Importación de Excel'
        verbose_name_plural = 'Importaciones de Excel'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre_original} - {self.get_estado_display()} ({self.fecha_creacion.strftime('%d/%m/%Y %H:%M')})"
    
    def marcar_como_completado(self):
        """Marca la importación como completada"""
        from django.utils import timezone
        self.estado = 'completado'
        self.fecha_completado = timezone.now()
        self.save()
    
    def agregar_error(self, fila, columna, mensaje):
        """Agrega un error de validación"""
        if not isinstance(self.errores_validacion, dict):
            self.errores_validacion = {}
        
        clave_fila = f"fila_{fila}"
        if clave_fila not in self.errores_validacion:
            self.errores_validacion[clave_fila] = []
        
        self.errores_validacion[clave_fila].append({
            'columna': columna,
            'mensaje': mensaje
        })
        self.registros_errores += 1
