"""
Servicios para la app de archivos
Implementa la lógica de negocio relacionada con envíos, productos y tarifas
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, PermissionDenied
from apps.core.base.base_service import BaseService
from apps.core.exceptions import (
    EnvioNoEncontradoError,
    TarifaNoEncontradaError,
    TransicionEstadoInvalidaError,
    CupoExcedidoError
)
from .repositories import (
    envio_repository,
    producto_repository,
    tarifa_repository,
    importacion_repository
)
from .models import Envio, Producto

Usuario = get_user_model()


class EnvioService(BaseService):
    """
    Servicio para operaciones de envíos.
    Centraliza toda la lógica de negocio relacionada con envíos.
    """
    
    # Transiciones de estado válidas
    TRANSICIONES_VALIDAS = {
        'pendiente': ['en_transito', 'cancelado'],
        'en_transito': ['entregado', 'cancelado'],
        'entregado': [],  # Estado final
        'cancelado': []   # Estado final
    }
    
    # ==================== CREACIÓN ====================
    
    @staticmethod
    def crear_envio(data: Dict[str, Any], usuario_creador) -> Envio:
        """
        Crea un nuevo envío aplicando reglas de negocio.
        
        Reglas:
        - Solo admin, gerente y digitador pueden crear envíos
        - HAWB debe ser único
        - Validar cupo anual del comprador
        - Calcular costo automáticamente
        - Generar embedding para búsqueda semántica
        
        Args:
            data: Datos del envío
            usuario_creador: Usuario que realiza la creación
            
        Returns:
            Envío creado
        """
        BaseService.validar_puede_gestionar_envios(usuario_creador)
        
        # Validar HAWB único
        hawb = data.get('hawb')
        if hawb and envio_repository.existe_hawb(hawb):
            raise ValidationError({'hawb': f'El HAWB {hawb} ya existe'})
        
        # Validar cupo anual del comprador
        comprador_id = data.get('comprador') or data.get('comprador_id')
        if comprador_id:
            from apps.usuarios.repositories import usuario_repository as user_repo
            try:
                comprador = user_repo.obtener_por_id(
                    comprador_id.id if hasattr(comprador_id, 'id') else comprador_id
                )
                
                if comprador.es_comprador:
                    peso_total = float(data.get('peso_total', 0))
                    from apps.usuarios.services import UsuarioService
                    UsuarioService.validar_cupo_disponible(comprador, peso_total)
            except Exception as e:
                # Si falla la validación de cupo, continuar (puede ser otro tipo de usuario)
                BaseService.log_warning(f"Validación de cupo omitida: {str(e)}")
        
        # Extraer productos si vienen en data
        productos_data = data.pop('productos', [])
        
        # Calcular costo del servicio
        if productos_data:
            costo_calculado = EnvioService.calcular_costo_servicio(productos_data)
            # Redondear a 4 decimales para cumplir con la restricción del campo DecimalField
            data['costo_servicio'] = Decimal(str(costo_calculado)).quantize(Decimal('0.0001'))
        
        with transaction.atomic():
            # Crear envío
            envio = envio_repository.crear(**data)
            
            # Crear productos
            if productos_data:
                for prod_data in productos_data:
                    prod_data['envio'] = envio
                    producto_repository.crear(**prod_data)
                
                # Recalcular totales después de crear todos los productos
                envio.actualizar_totales()
            
            # Guardar ID para usar en tareas asíncronas (después de commit)
            envio_id = envio.id
            comprador_id = envio.comprador.id if envio.comprador else None
            hawb = envio.hawb
            peso_total = float(envio.peso_total)
            valor_total = float(envio.valor_total)
            estado = envio.estado
        
        # Operaciones asíncronas via Celery (no bloquean la respuesta del API)
        from .tasks import generar_embedding_envio, notificar_envio_creado, log_creacion_envio
        generar_embedding_envio.delay(envio_id)
        notificar_envio_creado.delay(envio_id)
        log_creacion_envio.delay(envio_id, usuario_creador.id, hawb, peso_total, valor_total, estado, comprador_id)
        
        # Recargar el envío desde BD para asegurar que tenemos los datos más recientes
        envio.refresh_from_db()
        return envio
    
    # ==================== ACTUALIZACIÓN ====================
    
    @staticmethod
    def actualizar_envio(
        envio_id: int,
        data: Dict[str, Any],
        usuario_actual
    ) -> Envio:
        """
        Actualiza un envío aplicando reglas de negocio.
        """
        BaseService.validar_puede_gestionar_envios(usuario_actual)
        
        envio = envio_repository.obtener_por_id(envio_id)
        
        # Guardar valores anteriores para notificaciones
        comprador_anterior = envio.comprador
        estado_anterior = envio.estado
        
        # Validar HAWB único si cambia
        nuevo_hawb = data.get('hawb')
        if nuevo_hawb and nuevo_hawb != envio.hawb:
            if envio_repository.existe_hawb(nuevo_hawb, excluir_id=envio_id):
                raise ValidationError({'hawb': f'El HAWB {nuevo_hawb} ya existe'})
        
        with transaction.atomic():
            envio = envio_repository.actualizar(envio, **data)
            envio_id = envio.id
            
        from .tasks import generar_embedding_envio, notificar_envio_creado, notificar_cambio_estado
        if comprador_anterior != envio.comprador:
            notificar_envio_creado.delay(envio_id)
        if estado_anterior != envio.estado:
            notificar_cambio_estado.delay(envio_id, estado_anterior)
        generar_embedding_envio.delay(envio_id, True)
        
        return envio
    
    # ==================== CAMBIO DE ESTADO ====================
    
    @staticmethod
    def cambiar_estado(
        envio_id: int,
        nuevo_estado: str,
        usuario_actual
    ) -> Envio:
        """
        Cambia el estado de un envío.
        
        Reglas:
        - Solo admin, gerente y digitador pueden cambiar estado
        - Validar transición de estado válida
        - Notificar al comprador
        """
        BaseService.validar_puede_gestionar_envios(usuario_actual)
        
        envio = envio_repository.obtener_por_id(envio_id)
        estado_anterior = envio.estado
        
        # Validar estado válido
        estados_validos = dict(Envio._meta.get_field('estado').choices)
        if nuevo_estado not in estados_validos:
            raise ValidationError({'estado': f'Estado inválido: {nuevo_estado}'})
        
        # Validar transición
        if not EnvioService._es_transicion_valida(estado_anterior, nuevo_estado):
            transiciones_validas = EnvioService.TRANSICIONES_VALIDAS.get(estado_anterior, [])
            raise TransicionEstadoInvalidaError(estado_anterior, nuevo_estado, transiciones_validas)
        
        with transaction.atomic():
            envio = envio_repository.actualizar(envio, estado=nuevo_estado)
            envio_id = envio.id
            hawb = envio.hawb
        
        from .tasks import generar_embedding_envio, notificar_cambio_estado
        notificar_cambio_estado.delay(envio_id, estado_anterior)
        generar_embedding_envio.delay(envio_id, True)
        
        BaseService.log_info(
            f"Estado de envío cambiado: {hawb} ({estado_anterior} -> {nuevo_estado})",
            {
                'envio_id': envio_id,
                'usuario_id': usuario_actual.id,
                'estado_anterior': estado_anterior,
                'estado_nuevo': nuevo_estado
            },
            usuario_id=usuario_actual.id
        )
        
        return envio
    
    @staticmethod
    def _es_transicion_valida(estado_actual: str, nuevo_estado: str) -> bool:
        """Valida si una transición de estado es válida"""
        return nuevo_estado in EnvioService.TRANSICIONES_VALIDAS.get(estado_actual, [])
    
    # ==================== CÁLCULO DE COSTOS ====================
    
    @staticmethod
    def calcular_costo_servicio(productos_data: List[Dict]) -> float:
        """
        Calcula el costo total del servicio basado en productos y tarifas.
        
        Args:
            productos_data: Lista de diccionarios con datos de productos
            
        Returns:
            Costo total calculado
        """
        costo_total = 0.0
        
        for producto in productos_data:
            categoria = producto.get('categoria', 'otros')
            peso = float(producto.get('peso', 0))
            cantidad = int(producto.get('cantidad', 1))
            
            tarifa = tarifa_repository.buscar_tarifa_aplicable(categoria, peso)
            
            if tarifa:
                costo_producto = tarifa.calcular_costo(peso) * cantidad
                costo_total += costo_producto
        
        return round(costo_total, 2)
    
    @staticmethod
    def calcular_costo_envio(envio: Envio) -> float:
        """Calcula el costo de un envío existente basado en sus productos"""
        productos = producto_repository.obtener_por_envio(envio.id)
        
        costo_total = 0.0
        for producto in productos:
            tarifa = tarifa_repository.buscar_tarifa_aplicable(
                producto.categoria,
                float(producto.peso)
            )
            
            if tarifa:
                costo = tarifa.calcular_costo(float(producto.peso)) * producto.cantidad
                costo_total += costo
                # Actualizar costo en producto
                producto_repository.actualizar(producto, costo_envio=costo)
        
        return round(costo_total, 2)
    
    # ==================== ESTADÍSTICAS ====================
    
    @staticmethod
    def obtener_estadisticas(usuario=None) -> Dict[str, Any]:
        """Obtiene estadísticas de envíos"""
        return envio_repository.obtener_estadisticas(usuario)
    


class ProductoService(BaseService):
    """
    Servicio para operaciones de productos.
    """
    
    @staticmethod
    def crear_producto(data: Dict[str, Any], usuario) -> Producto:
        """Crea un producto"""
        BaseService.validar_puede_gestionar_envios(usuario)
        
        with transaction.atomic():
            producto = producto_repository.crear(**data)
            
            # Recalcular totales del envío
            if producto.envio:
                producto.envio.actualizar_totales()
            
            return producto
    
    @staticmethod
    def actualizar_producto(
        producto_id: int,
        data: Dict[str, Any],
        usuario
    ) -> Producto:
        """Actualiza un producto"""
        BaseService.validar_puede_gestionar_envios(usuario)
        
        producto = producto_repository.obtener_por_id(producto_id)
        
        with transaction.atomic():
            producto = producto_repository.actualizar(producto, **data)
            
            # Recalcular totales del envío
            if producto.envio:
                producto.envio.actualizar_totales()
            
            return producto
    
    @staticmethod
    def eliminar_producto(producto_id: int, usuario):
        """Elimina un producto"""
        BaseService.validar_puede_gestionar_envios(usuario)
        
        producto = producto_repository.obtener_por_id(producto_id)
        envio = producto.envio
        
        with transaction.atomic():
            producto_repository.eliminar(producto)
            
            if envio:
                envio.actualizar_totales()
    
    @staticmethod
    def obtener_estadisticas(usuario=None) -> Dict[str, Any]:
        """Obtiene estadísticas de productos"""
        return producto_repository.obtener_estadisticas(usuario)


class TarifaService(BaseService):
    """
    Servicio para operaciones de tarifas.
    """
    
    @staticmethod
    def buscar_tarifa(categoria: str, peso: float) -> Optional[Dict[str, Any]]:
        """
        Busca la tarifa aplicable para una categoría y peso.
        
        Returns:
            Diccionario con tarifa y costo calculado, o None
        """
        tarifa = tarifa_repository.buscar_tarifa_aplicable(categoria, peso)
        
        if tarifa:
            return {
                'tarifa': tarifa,
                'costo_calculado': round(tarifa.calcular_costo(peso), 2)
            }
        
        return None
    
    @staticmethod
    def calcular_costo(categoria: str, peso: float, cantidad: int = 1) -> float:
        """Calcula el costo para una categoría, peso y cantidad"""
        tarifa = tarifa_repository.buscar_tarifa_aplicable(categoria, peso)
        
        if tarifa:
            return round(tarifa.calcular_costo(peso) * cantidad, 2)
        
        return 0.0

