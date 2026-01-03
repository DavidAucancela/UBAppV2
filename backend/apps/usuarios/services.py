"""
Servicios para la app de usuarios
Implementa la lógica de negocio relacionada con usuarios
"""
from typing import Dict, Any, Optional
from datetime import datetime
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.core.base.base_service import BaseService
from apps.core.exceptions import (
    UsuarioNoEncontradoError,
    BusinessRuleViolationError
)
from .repositories import usuario_repository

Usuario = get_user_model()


class UsuarioService(BaseService):
    """
    Servicio para operaciones de usuarios.
    Centraliza toda la lógica de negocio relacionada con usuarios.
    """
    
    # ==================== CREACIÓN ====================
    
    @staticmethod
    def crear_usuario(data: Dict[str, Any], usuario_creador) -> Usuario:
        """
        Crea un nuevo usuario aplicando reglas de negocio.
        
        Reglas:
        - Solo admin puede crear usuarios (excepto registro público de compradores)
        - Cédula debe ser única
        - Correo debe ser único
        - Username debe ser único
        
        Args:
            data: Datos del usuario
            usuario_creador: Usuario que realiza la creación
            
        Returns:
            Usuario creado
            
        Raises:
            PermissionDenied: Si no tiene permisos
            ValidationError: Si datos son inválidos
        """
        # Validar permisos (solo admin puede crear usuarios)
        if not usuario_creador.es_admin:
            raise PermissionDenied("Solo administradores pueden crear usuarios")
        
        # Validar unicidad
        UsuarioService._validar_unicidad_datos(data)
        
        # Crear usuario
        with transaction.atomic():
            BaseService.log_operacion(
                operacion='crear',
                entidad='Usuario',
                usuario_id=usuario_creador.id,
                detalles={'username': data.get('username'), 'rol': data.get('rol')}
            )
            
            usuario = usuario_repository.crear(**data)
            
            BaseService.log_info(
                f"Usuario creado exitosamente: {usuario.username}",
                {'usuario_id': usuario.id, 'creador_id': usuario_creador.id, 'rol': usuario.rol},
                usuario_id=usuario_creador.id
            )
            
            return usuario
    
    @staticmethod
    def registrar_comprador(data: Dict[str, Any]) -> Usuario:
        """
        Registra un nuevo comprador (registro público).
        
        Reglas:
        - Solo se puede registrar rol comprador
        - Usuario activo por defecto
        
        Args:
            data: Datos del comprador
            
        Returns:
            Usuario comprador creado
        """
        # Forzar rol comprador
        data['rol'] = 4
        data['is_active'] = True  # Usar is_active (campo heredado de AbstractUser)
        
        # Validar unicidad
        UsuarioService._validar_unicidad_datos(data)
        
        # Crear usuario
        with transaction.atomic():
            password = data.pop('password', None)
            usuario = usuario_repository.crear(**data)
            
            if password:
                usuario.set_password(password)
                usuario.save()
            
            BaseService.log_info(
                f"Comprador registrado: {usuario.username}",
                {'usuario_id': usuario.id}
            )
            
            return usuario
    
    # ==================== ACTUALIZACIÓN ====================
    
    @staticmethod
    def actualizar_usuario(
        usuario_id: int,
        data: Dict[str, Any],
        usuario_actual
    ) -> Usuario:
        """
        Actualiza un usuario aplicando reglas de negocio.
        
        Reglas:
        - Solo admin puede cambiar rol
        - No se puede cambiar la cédula
        - Validar unicidad de correo/username si cambian
        
        Args:
            usuario_id: ID del usuario a actualizar
            data: Datos a actualizar
            usuario_actual: Usuario que realiza la actualización
        """
        usuario = usuario_repository.obtener_por_id(usuario_id)
        
        # Solo admin puede cambiar rol
        if 'rol' in data and not usuario_actual.es_admin:
            raise PermissionDenied("Solo administradores pueden cambiar roles")
        
        # No se puede cambiar la cédula
        if 'cedula' in data and data['cedula'] != usuario.cedula:
            raise ValidationError({'cedula': 'No se puede cambiar la cédula'})
        
        # Validar unicidad si cambian
        if 'correo' in data and data['correo'] != usuario.correo:
            if usuario_repository.existe_correo(data['correo'], excluir_id=usuario_id):
                raise ValidationError({'correo': 'Este correo ya está registrado'})
        
        if 'username' in data and data['username'] != usuario.username:
            if usuario_repository.existe_username(data['username'], excluir_id=usuario_id):
                raise ValidationError({'username': 'Este username ya está registrado'})
        
        # Actualizar
        with transaction.atomic():
            usuario = usuario_repository.actualizar(usuario, **data)
            
            BaseService.log_info(
                f"Usuario actualizado: {usuario.username}",
                {'usuario_id': usuario.id, 'actualizador_id': usuario_actual.id}
            )
            
            return usuario
    
    @staticmethod
    def actualizar_perfil(usuario, data: Dict[str, Any]) -> Usuario:
        """
        Actualiza el perfil del usuario actual.
        
        Reglas:
        - No puede cambiar su propio rol
        - No puede cambiar su cédula
        """
        # Quitar campos no permitidos
        campos_no_permitidos = ['rol', 'cedula', 'es_activo', 'is_active', 'is_staff', 'is_superuser']
        for campo in campos_no_permitidos:
            data.pop(campo, None)
        
        return UsuarioService.actualizar_usuario(usuario.id, data, usuario)
    
    # ==================== ACTIVACIÓN/DESACTIVACIÓN ====================
    
    @staticmethod
    def activar_desactivar_usuario(
        usuario_id: int,
        usuario_actual
    ) -> Usuario:
        """
        Activa o desactiva un usuario.
        
        Reglas:
        - Solo admin y gerente pueden realizar esta acción
        - No se puede desactivar el último admin
        """
        BaseService.validar_es_admin_o_gerente(usuario_actual)
        
        usuario = usuario_repository.obtener_por_id(usuario_id)
        
        # Verificar que no se desactive el último admin
        if usuario.es_admin and usuario.es_activo:
            admins_activos = usuario_repository.contar_admins_activos()
            if admins_activos <= 1:
                raise BusinessRuleViolationError(
                    "No se puede desactivar el último administrador del sistema",
                    "ultimo_admin"
                )
        
        # Toggle estado (usar is_active, campo heredado de AbstractUser)
        usuario = usuario_repository.actualizar(
            usuario,
            is_active=not usuario.is_active
        )
        
        estado = "activado" if usuario.is_active else "desactivado"
        BaseService.log_info(
            f"Usuario {estado}: {usuario.username}",
            {'usuario_id': usuario.id, 'actualizador_id': usuario_actual.id}
        )
        
        return usuario
    
    # ==================== CONTRASEÑA ====================
    
    @staticmethod
    def cambiar_password(
        usuario,
        password_actual: str,
        password_nuevo: str,
        password_confirm: str
    ) -> bool:
        """
        Cambia la contraseña del usuario.
        
        Args:
            usuario: Usuario que cambia su contraseña
            password_actual: Contraseña actual
            password_nuevo: Nueva contraseña
            password_confirm: Confirmación de nueva contraseña
        """
        # Validar contraseña actual
        if not usuario.check_password(password_actual):
            raise ValidationError({'password_actual': 'Contraseña actual incorrecta'})
        
        # Validar que coincidan
        if password_nuevo != password_confirm:
            raise ValidationError({'password_confirm': 'Las contraseñas no coinciden'})
        
        # Validar fortaleza
        from .validators import validar_password_fuerte
        try:
            validar_password_fuerte(password_nuevo)
        except Exception as e:
            raise ValidationError({'password_nuevo': str(e)})
        
        # Actualizar
        usuario.set_password(password_nuevo)
        usuario.save()
        
        BaseService.log_info(
            f"Contraseña cambiada: {usuario.username}",
            {'usuario_id': usuario.id}
        )
        
        return True
    
    # ==================== CUPO ANUAL ====================
    
    @staticmethod
    def obtener_peso_usado_anual(usuario, anio: int = None) -> float:
        """
        Obtiene el peso total usado en el año.
        
        Args:
            usuario: Usuario (comprador)
            anio: Año a consultar (por defecto año actual)
        """
        if anio is None:
            anio = datetime.now().year
        
        from django.db.models import Sum
        
        peso_total = usuario.envio_set.filter(
            fecha_emision__year=anio
        ).exclude(
            estado='cancelado'
        ).aggregate(
            total=Sum('peso_total')
        )['total'] or 0
        
        return float(peso_total)
    
    @staticmethod
    def obtener_cupo_disponible(usuario, anio: int = None) -> float:
        """Obtiene el cupo disponible del usuario"""
        peso_usado = UsuarioService.obtener_peso_usado_anual(usuario, anio)
        return float(usuario.cupo_anual) - peso_usado
    
    @staticmethod
    def validar_cupo_disponible(
        usuario,
        peso_nuevo: float,
        anio: int = None
    ) -> bool:
        """
        Valida si el usuario tiene cupo disponible para un peso.
        
        Args:
            usuario: Usuario (comprador)
            peso_nuevo: Peso a validar
            anio: Año a consultar
            
        Returns:
            True si tiene cupo disponible
            
        Raises:
            CupoExcedidoError: Si no tiene cupo disponible
        """
        from apps.core.exceptions import CupoExcedidoError
        
        cupo_disponible = UsuarioService.obtener_cupo_disponible(usuario, anio)
        
        if cupo_disponible < peso_nuevo:
            raise CupoExcedidoError(cupo_disponible, peso_nuevo)
        
        return True
    
    # ==================== ESTADÍSTICAS ====================
    
    @staticmethod
    def obtener_estadisticas_envios(usuario, anio: int = None) -> Dict[str, Any]:
        """Obtiene estadísticas de envíos del usuario"""
        from apps.archivos.repositories import envio_repository
        return envio_repository.obtener_estadisticas_por_anio(usuario, anio)
    
    @staticmethod
    def obtener_dashboard_usuario(usuario, anio: int = None) -> Dict[str, Any]:
        """Obtiene datos completos del dashboard del usuario"""
        if anio is None:
            anio = datetime.now().year
        
        # Estadísticas de envíos
        estadisticas = UsuarioService.obtener_estadisticas_envios(usuario, anio)
        
        # Cupo (solo para compradores)
        if usuario.es_comprador:
            peso_usado = UsuarioService.obtener_peso_usado_anual(usuario, anio)
            peso_disponible = UsuarioService.obtener_cupo_disponible(usuario, anio)
            porcentaje_usado = (peso_usado / float(usuario.cupo_anual)) * 100 if float(usuario.cupo_anual) > 0 else 0
        else:
            peso_usado = 0
            peso_disponible = 0
            porcentaje_usado = 0
        
        return {
            'usuario': usuario,
            'cupo_anual': float(usuario.cupo_anual),
            'peso_usado': peso_usado,
            'peso_disponible': peso_disponible,
            'porcentaje_usado': porcentaje_usado,
            'anio': anio,
            **estadisticas
        }
    
    # ==================== MÉTODOS PRIVADOS ====================
    
    @staticmethod
    def _validar_unicidad_datos(data: Dict[str, Any], excluir_id: int = None):
        """Valida unicidad de cédula, correo y username"""
        errores = {}
        
        if 'cedula' in data and usuario_repository.existe_cedula(data['cedula'], excluir_id):
            errores['cedula'] = 'Esta cédula ya está registrada'
        
        if 'correo' in data and usuario_repository.existe_correo(data['correo'], excluir_id):
            errores['correo'] = 'Este correo ya está registrado'
        
        if 'username' in data and usuario_repository.existe_username(data['username'], excluir_id):
            errores['username'] = 'Este username ya está registrado'
        
        if errores:
            raise ValidationError(errores)

