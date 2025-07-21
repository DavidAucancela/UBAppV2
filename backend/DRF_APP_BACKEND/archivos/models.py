from django.db import models
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class Envio(models.Model):
    """Modelo para gestionar envíos"""
    hawb = models.CharField(max_length=50, unique=True, verbose_name="HAWB")
    peso_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Peso Total")
    cantidad_total = models.IntegerField(verbose_name="Cantidad Total")
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Total")
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
        self.save()

class Producto(models.Model):
    """Modelo para productos en envíos"""
    descripcion = models.CharField(max_length=200, verbose_name="Descripción")
    peso = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Peso")
    cantidad = models.IntegerField(verbose_name="Cantidad")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    
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
        self.envio.calcular_totales()
