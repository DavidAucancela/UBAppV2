from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
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
        db_table = 'tarifa'
        verbose_name = 'Tarifa'
        verbose_name_plural = 'Tarifas'
        ordering = ['categoria', 'peso_minimo']
        unique_together = [['categoria', 'peso_minimo', 'peso_maximo']]

    def __str__(self):
        return f"{self.get_categoria_display()} - {self.peso_minimo}kg a {self.peso_maximo}kg: ${self.precio_por_kg}/kg"

    def clean(self):
        """Valida que peso_maximo sea mayor que peso_minimo"""
        from django.core.exceptions import ValidationError
        
        # Validación existente
        if self.peso_maximo <= self.peso_minimo:
            raise ValidationError("El peso máximo debe ser mayor que el peso mínimo")
        
        # NUEVA: Validar precio
        if self.precio_por_kg <= 0:
            raise ValidationError({
                'precio_por_kg': 'El precio por kg debe ser mayor que 0'
            })
        
        # NUEVA: Validar que no haya solapamiento con otras tarifas activas
        if self.pk:  # Si ya existe
            tarifas_solapadas = Tarifa.objects.filter(
                categoria=self.categoria,
                activa=True,
                peso_minimo__lt=self.peso_maximo,
                peso_maximo__gt=self.peso_minimo
            ).exclude(id=self.id)
        else:  # Si es nueva
            tarifas_solapadas = Tarifa.objects.filter(
                categoria=self.categoria,
                activa=True,
                peso_minimo__lt=self.peso_maximo,
                peso_maximo__gt=self.peso_minimo
            )
        
        if tarifas_solapadas.exists():
            raise ValidationError({
                'peso_minimo': 'Esta tarifa se solapa con otra tarifa activa de la misma categoría',
                'peso_maximo': 'Esta tarifa se solapa con otra tarifa activa de la misma categoría'
            })
            
    def calcular_costo(self, peso):
        """Calcula el costo para un peso dado"""
        return float(self.cargo_base) + (float(peso) * float(self.precio_por_kg))

class Envio(models.Model):
    """Modelo para gestionar envíos"""
    hawb = models.CharField(max_length=50, unique=True, verbose_name="HAWB")
    peso_total = models.DecimalField(max_digits=10, decimal_places=4, default=0, verbose_name="Peso Total")
    cantidad_total = models.IntegerField(default=0, verbose_name="Cantidad Total")
    valor_total = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name="Valor Total")
    costo_servicio = models.DecimalField(
        max_digits=12, 
        decimal_places=4, 
        default=0,
        verbose_name="Costo del Servicio",
        help_text="Costo calculado automáticamente según tarifas"
    )
    fecha_emision = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Emisión"
    )
    
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
        db_table = 'envio'
        verbose_name = 'Envío'
        verbose_name_plural = 'Envíos'
        ordering = ['-fecha_emision']
        indexes = [
            models.Index(fields=['hawb']),  # Búsqueda por HAWB
            models.Index(fields=['comprador', 'fecha_emision']),  # Filtros comunes
            models.Index(fields=['estado', 'fecha_emision']),  # Filtros por estado
            models.Index(fields=['-fecha_emision']),  # Ordenamiento
        ]

    def __str__(self):
        return f"HAWB: {self.hawb} - {self.comprador.nombre}"

    def calcular_totales(self):
        """Calcula los totales basados en los productos"""
        productos = self.productos.all()
        # Peso total = suma de (peso * cantidad) de cada producto
        # Usar Decimal para evitar problemas de precisión y normalizar a 2 decimales
        peso_total_calculado = sum(Decimal(str(p.peso)) * Decimal(str(p.cantidad)) for p in productos)
        self.peso_total = peso_total_calculado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Cantidad total = suma de cantidades
        self.cantidad_total = sum(p.cantidad for p in productos)
        
        # Valor total = suma de (valor * cantidad) de cada producto
        # Usar Decimal para evitar problemas de precisión y normalizar a 2 decimales
        valor_total_calculado = sum(Decimal(str(p.valor)) * Decimal(str(p.cantidad)) for p in productos)
        self.valor_total = valor_total_calculado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Calcular costo del servicio basado en tarifas
        # El método calcular_costo_servicio ya retorna un Decimal redondeado a 4 decimales
        self.costo_servicio = self.calcular_costo_servicio()
        self.save()
    
    def calcular_costo_servicio(self):
        """Calcula el costo del servicio basado en productos y tarifas"""
        # OPTIMIZACIÓN: Cargar todas las tarifas activas una sola vez
        tarifas_activas = list(Tarifa.objects.filter(activa=True))
        
        # Organizar tarifas por categoría para búsqueda rápida
        tarifas_por_categoria = {}
        for tarifa in tarifas_activas:
            if tarifa.categoria not in tarifas_por_categoria:
                tarifas_por_categoria[tarifa.categoria] = []
            tarifas_por_categoria[tarifa.categoria].append(tarifa)
        
        costo_total = Decimal('0.0')
        productos = self.productos.all()  # Ya optimizado con prefetch_related
        
        # Lista para actualizar productos en batch
        productos_a_actualizar = []
        
        for producto in productos:
            tarifa_aplicable = None
            tarifas_categoria = tarifas_por_categoria.get(producto.categoria, [])
            
            # Buscar tarifa aplicable para este peso específico
            for tarifa in tarifas_categoria:
                if tarifa.peso_minimo <= producto.peso <= tarifa.peso_maximo:
                    tarifa_aplicable = tarifa
                    break  # Usar la primera tarifa que coincida
            
            if tarifa_aplicable:
                # Calcular costo para este producto (asegurar que sea Decimal)
                costo_producto_decimal = Decimal(str(tarifa_aplicable.calcular_costo(producto.peso))) * Decimal(str(producto.cantidad))
                costo_total += costo_producto_decimal
                costo_producto = float(costo_producto_decimal)  # Para guardar en producto.costo_envio
                # Guardar el costo en el producto para referencia
                producto.costo_envio = costo_producto
                productos_a_actualizar.append(producto)
            else:
                # Si no hay tarifa, mantener costo en 0
                producto.costo_envio = 0
                productos_a_actualizar.append(producto)
        
        # OPTIMIZACIÓN: Actualizar productos en batch
        if productos_a_actualizar:
            Producto.objects.bulk_update(productos_a_actualizar, ['costo_envio'])
        
        # Redondear a 4 decimales para cumplir con la restricción del campo DecimalField (decimal_places=4)
        # Convertir a Decimal y redondear
        if isinstance(costo_total, Decimal):
            return costo_total.quantize(Decimal('0.0001'))
        else:
            return Decimal(str(costo_total)).quantize(Decimal('0.0001'))
    
    def save(self, *args, **kwargs):
        """Normalizar peso_total y valor_total a 2 decimales antes de guardar"""
        if self.peso_total is not None:
            self.peso_total = self.peso_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if self.valor_total is not None:
            self.valor_total = self.valor_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validaciones adicionales del modelo"""
        from django.core.exceptions import ValidationError
        
        # Solo validar totales si el envío ya está guardado y tiene productos
        # Esto permite crear envíos con totales en 0 que se calcularán después
        tiene_productos = self.pk and self.productos.exists()
        
        if tiene_productos:
            # Validar peso total (solo si el envío ya tiene productos)
            if self.peso_total is not None and self.peso_total <= 0:
                raise ValidationError({
                    'peso_total': 'El peso total debe ser mayor que 0'
                })
            
            # Validar cantidad total (solo si el envío ya tiene productos)
            if self.cantidad_total is not None and self.cantidad_total <= 0:
                raise ValidationError({
                    'cantidad_total': 'La cantidad total debe ser mayor que 0'
                })
        
        # Validar valor total (siempre, pero solo si no es None)
        if self.valor_total is not None and self.valor_total < 0:
            raise ValidationError({
                'valor_total': 'El valor total no puede ser negativo'
            })
        
        # Validar que tenga productos (si ya está guardado)
        if self.pk and not self.productos.exists():
            raise ValidationError(
                'Un envío debe tener al menos un producto'
            )
        
        # Validar que el comprador sea realmente un comprador
        if self.comprador and self.comprador.rol != 4:
            raise ValidationError({
                'comprador': 'El comprador debe tener rol de Comprador (4)'
            })
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para llamar a clean()"""
        self.full_clean()  # Llama a clean() automáticamente
        super().save(*args, **kwargs)


class Producto(models.Model):
    """Modelo para productos en envíos"""
    descripcion = models.CharField(max_length=200, verbose_name="Descripción")
    peso = models.DecimalField(max_digits=8, decimal_places=4, verbose_name="Peso")
    cantidad = models.IntegerField(verbose_name="Cantidad")
    valor = models.DecimalField(max_digits=10, decimal_places=4, verbose_name="Valor")
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
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['envio', 'categoria']),  # Filtros comunes
            models.Index(fields=['categoria']),  # Búsqueda por categoría
        ]

    def __str__(self):
        return f"{self.descripcion} - {self.envio.hawb}"

    def save(self, *args, **kwargs):
        """Normalizar peso y valor a 2 decimales antes de guardar"""
        if self.peso is not None:
            self.peso = self.peso.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if self.valor is not None:
            self.valor = self.valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validaciones adicionales del modelo"""
        from django.core.exceptions import ValidationError
        
        # Validar peso
        if self.peso <= 0:
            raise ValidationError({
                'peso': 'El peso debe ser mayor que 0'
            })
        
        # Validar cantidad
        if self.cantidad <= 0:
            raise ValidationError({
                'cantidad': 'La cantidad debe ser mayor que 0'
            })
        
        # Validar valor
        if self.valor < 0:
            raise ValidationError({
                'valor': 'El valor no puede ser negativo'
            })
        
        # Validar descripción
        if not self.descripcion or len(self.descripcion.strip()) < 3:
            raise ValidationError({
                'descripcion': 'La descripción debe tener al menos 3 caracteres'
            })
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para llamar a clean()"""
        self.full_clean()
        super().save(*args, **kwargs)

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
        db_table = 'archivo'
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
