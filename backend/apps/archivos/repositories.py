"""
Repositorios para la app de archivos
Implementa el patrón Repository para acceso a datos de envíos, productos y tarifas
"""
from typing import Optional, List, Dict, Any
from django.db.models import QuerySet, Q, Sum, Count
from django.db import models
from datetime import datetime

from apps.core.base.base_repository import BaseRepository
from apps.core.exceptions import (
    EnvioNoEncontradoError,
    ProductoNoEncontradoError,
    TarifaNoEncontradaError
)
from .models import Envio, Producto, Tarifa, ImportacionExcel


class EnvioRepository(BaseRepository):
    """
    Repositorio para operaciones de Envío.
    Centraliza todas las consultas relacionadas con envíos.
    """
    
    @property
    def model(self):
        return Envio
    
    @property
    def select_related_fields(self) -> List[str]:
        return ['comprador']
    
    @property
    def prefetch_related_fields(self) -> List[str]:
        return ['productos']
    
    # ==================== CONSULTAS ESPECÍFICAS ====================
    
    def obtener_por_id(self, id: int) -> Envio:
        """
        Obtiene un envío por ID con relaciones optimizadas.
        
        Raises:
            EnvioNoEncontradoError: Si no existe el envío
        """
        try:
            return self._get_optimized_queryset().get(id=id)
        except self.model.DoesNotExist:
            raise EnvioNoEncontradoError(str(id))
    
    def obtener_por_hawb(self, hawb: str) -> Envio:
        """
        Obtiene un envío por HAWB.
        
        Raises:
            EnvioNoEncontradoError: Si no existe el envío
        """
        try:
            return self._get_optimized_queryset().get(hawb=hawb)
        except self.model.DoesNotExist:
            raise EnvioNoEncontradoError(hawb)
    
    # ==================== FILTROS POR PERMISOS ====================
    
    def filtrar_por_permisos_usuario(self, usuario) -> QuerySet:
        """
        Filtra envíos según los permisos del usuario.
        
        Args:
            usuario: Usuario que realiza la consulta
            
        Returns:
            QuerySet filtrado según permisos
        """
        queryset = self._get_optimized_queryset()
        
        # Admins, gerentes y digitadores pueden ver todos
        if usuario.es_admin or usuario.es_gerente or usuario.es_digitador:
            return queryset
        
        # Compradores solo ven sus propios envíos
        if usuario.es_comprador:
            return queryset.filter(comprador=usuario)
        
        return queryset.none()
    
    # ==================== FILTROS POR CRITERIOS ====================
    
    def filtrar_por_estado(self, estado: str, usuario=None) -> QuerySet:
        """Filtra envíos por estado"""
        queryset = self._get_optimized_queryset().filter(estado=estado)
        if usuario:
            if usuario.es_comprador:
                queryset = queryset.filter(comprador=usuario)
        return queryset
    
    def filtrar_por_comprador(self, comprador_id: int) -> QuerySet:
        """Filtra envíos por comprador"""
        return self._get_optimized_queryset().filter(comprador_id=comprador_id)
    
    def filtrar_por_fecha_rango(
        self,
        fecha_desde: datetime = None,
        fecha_hasta: datetime = None,
        usuario=None
    ) -> QuerySet:
        """Filtra envíos por rango de fechas"""
        queryset = self._get_optimized_queryset()
        
        if fecha_desde:
            queryset = queryset.filter(fecha_emision__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_emision__lte=fecha_hasta)
        
        if usuario and usuario.es_comprador:
            queryset = queryset.filter(comprador=usuario)
        
        return queryset
    
    def filtrar_por_criterios_multiples(
        self,
        usuario,
        estado: str = None,
        fecha_desde: datetime = None,
        fecha_hasta: datetime = None,
        ciudad_destino: str = None
    ) -> QuerySet:
        """
        Filtra envíos por múltiples criterios.
        Usado principalmente por búsqueda semántica.
        """
        queryset = self.filtrar_por_permisos_usuario(usuario)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        if fecha_desde:
            queryset = queryset.filter(fecha_emision__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_emision__lte=fecha_hasta)
        if ciudad_destino:
            queryset = queryset.filter(comprador__ciudad__icontains=ciudad_destino)
        
        return queryset
    
    # ==================== VALIDACIONES ====================
    
    def existe_hawb(self, hawb: str, excluir_id: int = None) -> bool:
        """Verifica si existe un envío con ese HAWB"""
        queryset = self.model.objects.filter(hawb=hawb)
        if excluir_id:
            queryset = queryset.exclude(id=excluir_id)
        return queryset.exists()
    
    # ==================== BÚSQUEDA ====================
    
    def buscar(self, termino: str, usuario=None) -> QuerySet:
        """
        Busca envíos por HAWB, nombre de comprador o estado.
        
        Args:
            termino: Término de búsqueda
            usuario: Usuario para filtrar por permisos
        """
        queryset = self._get_optimized_queryset().filter(
            Q(hawb__icontains=termino) |
            Q(comprador__nombre__icontains=termino) |
            Q(estado__icontains=termino)
        )
        
        if usuario and usuario.es_comprador:
            queryset = queryset.filter(comprador=usuario)
        
        return queryset
    
    # ==================== ESTADÍSTICAS ====================
    
    def obtener_estadisticas(self, usuario=None) -> Dict[str, Any]:
        """
        Obtiene estadísticas de envíos.
        
        Args:
            usuario: Usuario para filtrar (opcional)
        """
        queryset = self._get_optimized_queryset()
        
        if usuario and usuario.es_comprador:
            queryset = queryset.filter(comprador=usuario)
        
        return {
            'total_envios': queryset.count(),
            'envios_pendientes': queryset.filter(estado='pendiente').count(),
            'envios_en_transito': queryset.filter(estado='en_transito').count(),
            'envios_entregados': queryset.filter(estado='entregado').count(),
            'envios_cancelados': queryset.filter(estado='cancelado').count(),
            'total_peso': float(queryset.aggregate(
                total=Sum('peso_total')
            )['total'] or 0),
            'total_valor': float(queryset.aggregate(
                total=Sum('valor_total')
            )['total'] or 0),
        }
    
    def obtener_estadisticas_por_anio(
        self,
        comprador,
        anio: int = None
    ) -> Dict[str, Any]:
        """
        Obtiene estadísticas de envíos por año para un comprador.
        """
        if anio is None:
            anio = datetime.now().year
        
        envios = self.model.objects.filter(
            comprador=comprador,
            fecha_emision__year=anio
        )
        
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


class ProductoRepository(BaseRepository):
    """
    Repositorio para operaciones de Producto.
    """
    
    @property
    def model(self):
        return Producto
    
    @property
    def select_related_fields(self) -> List[str]:
        return ['envio', 'envio__comprador']
    
    # ==================== CONSULTAS ESPECÍFICAS ====================
    
    def obtener_por_id(self, id: int) -> Producto:
        """
        Obtiene un producto por ID.
        
        Raises:
            ProductoNoEncontradoError: Si no existe el producto
        """
        try:
            return self._get_optimized_queryset().get(id=id)
        except self.model.DoesNotExist:
            raise ProductoNoEncontradoError(str(id))
    
    def obtener_por_envio(self, envio_id: int) -> QuerySet:
        """Obtiene productos de un envío específico"""
        return self.model.objects.filter(envio_id=envio_id)
    
    # ==================== FILTROS POR PERMISOS ====================
    
    def filtrar_por_permisos_usuario(self, usuario) -> QuerySet:
        """Filtra productos según permisos del usuario"""
        queryset = self._get_optimized_queryset()
        
        if usuario.es_admin or usuario.es_gerente or usuario.es_digitador:
            return queryset
        
        if usuario.es_comprador:
            return queryset.filter(envio__comprador=usuario)
        
        return queryset.none()
    
    # ==================== FILTROS POR CRITERIOS ====================
    
    def filtrar_por_categoria(self, categoria: str, usuario=None) -> QuerySet:
        """Filtra productos por categoría"""
        queryset = self.model.objects.filter(categoria=categoria)
        
        if usuario and usuario.es_comprador:
            queryset = queryset.filter(envio__comprador=usuario)
        
        return queryset
    
    # ==================== BÚSQUEDA ====================
    
    def buscar(self, termino: str, usuario=None) -> QuerySet:
        """Busca productos por descripción, categoría o HAWB del envío"""
        queryset = self._get_optimized_queryset().filter(
            Q(descripcion__icontains=termino) |
            Q(categoria__icontains=termino) |
            Q(envio__hawb__icontains=termino)
        )
        
        if usuario and usuario.es_comprador:
            queryset = queryset.filter(envio__comprador=usuario)
        
        return queryset
    
    # ==================== ESTADÍSTICAS ====================
    
    def obtener_estadisticas(self, usuario=None) -> Dict[str, Any]:
        """Obtiene estadísticas de productos"""
        queryset = self._get_optimized_queryset()
        
        if usuario and usuario.es_comprador:
            queryset = queryset.filter(envio__comprador=usuario)
        
        # Stats por categoría
        stats_por_categoria = {}
        for cat_id, cat_nombre in Producto._meta.get_field('categoria').choices:
            count = queryset.filter(categoria=cat_id).count()
            if count > 0:
                stats_por_categoria[cat_nombre] = count
        
        return {
            'total_productos': queryset.count(),
            'total_peso': float(queryset.aggregate(total=Sum('peso'))['total'] or 0),
            'total_valor': float(queryset.aggregate(total=Sum('valor'))['total'] or 0),
            'por_categoria': stats_por_categoria
        }
    
    # ==================== OPERACIONES MASIVAS ====================
    
    def crear_multiples_para_envio(
        self,
        envio: Envio,
        productos_data: List[Dict[str, Any]]
    ) -> List[Producto]:
        """
        Crea múltiples productos para un envío.
        
        Args:
            envio: Instancia del envío
            productos_data: Lista de diccionarios con datos de productos
        """
        productos = []
        for data in productos_data:
            data['envio'] = envio
            productos.append(self.model(**data))
        
        return self.model.objects.bulk_create(productos)


class TarifaRepository(BaseRepository):
    """
    Repositorio para operaciones de Tarifa.
    """
    
    @property
    def model(self):
        return Tarifa
    
    # ==================== CONSULTAS ESPECÍFICAS ====================
    
    def obtener_por_id(self, id: int) -> Tarifa:
        """
        Obtiene una tarifa por ID.
        
        Raises:
            TarifaNoEncontradaError: Si no existe la tarifa
        """
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            raise TarifaNoEncontradaError(str(id))
    
    def buscar_tarifa_aplicable(
        self,
        categoria: str,
        peso: float
    ) -> Optional[Tarifa]:
        """
        Busca la tarifa aplicable para una categoría y peso.
        
        Args:
            categoria: Categoría del producto
            peso: Peso del producto
            
        Returns:
            Tarifa aplicable o None
        """
        return self.model.objects.filter(
            categoria=categoria,
            peso_minimo__lte=peso,
            peso_maximo__gte=peso,
            activa=True
        ).first()
    
    def obtener_tarifas_por_categoria(
        self,
        categoria: str,
        solo_activas: bool = True
    ) -> QuerySet:
        """Obtiene tarifas de una categoría"""
        queryset = self.model.objects.filter(categoria=categoria)
        if solo_activas:
            queryset = queryset.filter(activa=True)
        return queryset.order_by('peso_minimo')


class ImportacionExcelRepository(BaseRepository):
    """
    Repositorio para operaciones de ImportacionExcel.
    """
    
    @property
    def model(self):
        return ImportacionExcel
    
    @property
    def select_related_fields(self) -> List[str]:
        return ['usuario']
    
    def filtrar_por_permisos_usuario(self, usuario) -> QuerySet:
        """Filtra importaciones según permisos"""
        queryset = self._get_optimized_queryset()
        
        if usuario.es_admin or usuario.es_gerente:
            return queryset
        
        return queryset.filter(usuario=usuario)
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtiene estadísticas de importaciones"""
        queryset = self.model.objects.all()
        
        return {
            'total_importaciones': queryset.count(),
            'importaciones_completadas': queryset.filter(estado='completado').count(),
            'importaciones_error': queryset.filter(estado='error').count(),
            'importaciones_pendientes': queryset.filter(
                estado__in=['pendiente', 'validando', 'validado', 'procesando']
            ).count(),
            'total_registros_procesados': sum(
                imp.registros_procesados for imp in queryset
            ),
            'total_registros_error': sum(
                imp.registros_errores for imp in queryset
            ),
        }


# Instancias singleton para uso en servicios
envio_repository = EnvioRepository()
producto_repository = ProductoRepository()
tarifa_repository = TarifaRepository()
importacion_repository = ImportacionExcelRepository()

