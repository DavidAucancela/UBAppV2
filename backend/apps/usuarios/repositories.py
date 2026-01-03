"""
Repositorios para la app de usuarios
Implementa el patrón Repository para acceso a datos de usuarios
"""
from typing import Optional, List
from django.db.models import QuerySet, Q, Sum, Count
from django.contrib.auth import get_user_model

from apps.core.base.base_repository import BaseRepository
from apps.core.exceptions import UsuarioNoEncontradoError

Usuario = get_user_model()


class UsuarioRepository(BaseRepository):
    """
    Repositorio para operaciones de Usuario.
    Centraliza todas las consultas relacionadas con usuarios.
    """
    
    @property
    def model(self):
        return Usuario
    
    # ==================== CONSULTAS ESPECÍFICAS ====================
    
    def obtener_por_id(self, id: int) -> Usuario:
        """
        Obtiene un usuario por ID.
        
        Raises:
            UsuarioNoEncontradoError: Si no existe el usuario
        """
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            raise UsuarioNoEncontradoError(str(id))
    
    def obtener_por_username(self, username: str) -> Usuario:
        """
        Obtiene un usuario por username.
        
        Raises:
            UsuarioNoEncontradoError: Si no existe el usuario
        """
        try:
            return self.model.objects.get(username=username)
        except self.model.DoesNotExist:
            raise UsuarioNoEncontradoError(username)
    
    def obtener_por_cedula(self, cedula: str) -> Usuario:
        """
        Obtiene un usuario por cédula.
        
        Raises:
            UsuarioNoEncontradoError: Si no existe el usuario
        """
        try:
            return self.model.objects.get(cedula=cedula)
        except self.model.DoesNotExist:
            raise UsuarioNoEncontradoError(cedula)
    
    def obtener_por_correo(self, correo: str) -> Usuario:
        """
        Obtiene un usuario por correo.
        
        Raises:
            UsuarioNoEncontradoError: Si no existe el usuario
        """
        try:
            return self.model.objects.get(correo=correo)
        except self.model.DoesNotExist:
            raise UsuarioNoEncontradoError(correo)
    
    # ==================== FILTROS POR PERMISOS ====================
    
    def filtrar_por_permisos_usuario(self, usuario_actual) -> QuerySet:
        """
        Filtra usuarios según los permisos del usuario actual.
        
        Args:
            usuario_actual: Usuario que realiza la consulta
            
        Returns:
            QuerySet filtrado según permisos
        """
        # Admins pueden ver todos los usuarios
        if usuario_actual.es_admin:
            return self.model.objects.all()
        
        # Gerentes pueden ver todos excepto admins
        if usuario_actual.es_gerente:
            return self.model.objects.exclude(rol=1)
        
        # Digitadores pueden ver compradores y otros digitadores
        if usuario_actual.es_digitador:
            return self.model.objects.filter(rol__in=[3, 4])
        
        # Compradores solo pueden ver su propio perfil
        return self.model.objects.filter(id=usuario_actual.id)
    
    # ==================== FILTROS POR ROL ====================
    
    def obtener_compradores_activos(self) -> QuerySet:
        """Obtiene todos los compradores activos"""
        return self.model.objects.filter(rol=4, is_active=True)
    
    def obtener_por_rol(self, rol: int, solo_activos: bool = True) -> QuerySet:
        """
        Obtiene usuarios por rol.
        
        Args:
            rol: ID del rol
            solo_activos: Si True, solo retorna usuarios activos
        """
        queryset = self.model.objects.filter(rol=rol)
        if solo_activos:
            queryset = queryset.filter(is_active=True)
        return queryset
    
    def contar_admins_activos(self) -> int:
        """Cuenta la cantidad de administradores activos"""
        return self.model.objects.filter(rol=1, is_active=True).count()
    
    # ==================== FILTROS POR UBICACIÓN ====================
    
    def obtener_compradores_con_ubicacion(self) -> QuerySet:
        """Obtiene compradores activos con ubicación definida"""
        return self.model.objects.filter(
            rol=4,
            is_active=True
        ).exclude(
            Q(ciudad__isnull=True) | Q(ciudad='')
        )
    
    def obtener_compradores_por_ciudad(self, ciudad: str) -> QuerySet:
        """Obtiene compradores de una ciudad específica"""
        return self.obtener_compradores_con_ubicacion().filter(ciudad=ciudad)
    
    # ==================== VALIDACIONES ====================
    
    def existe_cedula(self, cedula: str, excluir_id: int = None) -> bool:
        """
        Verifica si existe un usuario con esa cédula.
        
        Args:
            cedula: Cédula a verificar
            excluir_id: ID de usuario a excluir (para updates)
        """
        queryset = self.model.objects.filter(cedula=cedula)
        if excluir_id:
            queryset = queryset.exclude(id=excluir_id)
        return queryset.exists()
    
    def existe_correo(self, correo: str, excluir_id: int = None) -> bool:
        """
        Verifica si existe un usuario con ese correo.
        
        Args:
            correo: Correo a verificar
            excluir_id: ID de usuario a excluir (para updates)
        """
        queryset = self.model.objects.filter(correo=correo)
        if excluir_id:
            queryset = queryset.exclude(id=excluir_id)
        return queryset.exists()
    
    def existe_username(self, username: str, excluir_id: int = None) -> bool:
        """
        Verifica si existe un usuario con ese username.
        
        Args:
            username: Username a verificar
            excluir_id: ID de usuario a excluir (para updates)
        """
        queryset = self.model.objects.filter(username=username)
        if excluir_id:
            queryset = queryset.exclude(id=excluir_id)
        return queryset.exists()
    
    # ==================== BÚSQUEDA ====================
    
    def buscar(self, termino: str) -> QuerySet:
        """
        Busca usuarios por nombre, correo, cédula o username.
        
        Args:
            termino: Término de búsqueda
        """
        return self.model.objects.filter(
            Q(nombre__icontains=termino) |
            Q(correo__icontains=termino) |
            Q(cedula__icontains=termino) |
            Q(username__icontains=termino)
        )
    
    # ==================== ESTADÍSTICAS ====================
    
    def obtener_estadisticas_por_rol(self) -> dict:
        """Obtiene conteo de usuarios activos por rol"""
        stats = {}
        for rol_id, rol_nombre in Usuario.ROLES_CHOICES:
            count = self.model.objects.filter(rol=rol_id, is_active=True).count()
            stats[rol_nombre] = count
        return stats


# Instancia singleton para uso en servicios
usuario_repository = UsuarioRepository()

