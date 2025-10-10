from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from django.core.cache import cache
from datetime import datetime, timedelta
from .serializers import UsuarioSerializer, UsuarioListSerializer, CompradorSerializer

Usuario = get_user_model()

class LoginView(APIView):
    """Vista para autenticación de usuarios con límite de intentos"""
    permission_classes = [permissions.AllowAny]
    
    MAX_INTENTOS = 5  # Máximo de intentos fallidos
    TIEMPO_BLOQUEO = 900  # 15 minutos en segundos
    
    def get_cache_key(self, username):
        """Genera la clave de cache para el usuario"""
        return f'login_intentos_{username}'
    
    def verificar_intentos(self, username):
        """Verifica si el usuario está bloqueado"""
        cache_key = self.get_cache_key(username)
        intentos = cache.get(cache_key, 0)
        
        if intentos >= self.MAX_INTENTOS:
            return False, intentos
        return True, intentos
    
    def registrar_intento_fallido(self, username):
        """Registra un intento fallido de login"""
        cache_key = self.get_cache_key(username)
        intentos = cache.get(cache_key, 0)
        intentos += 1
        cache.set(cache_key, intentos, self.TIEMPO_BLOQUEO)
        return intentos
    
    def limpiar_intentos(self, username):
        """Limpia los intentos fallidos después de login exitoso"""
        cache_key = self.get_cache_key(username)
        cache.delete(cache_key)
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Se requieren username y password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar intentos de login
        puede_intentar, intentos = self.verificar_intentos(username)
        
        if not puede_intentar:
            tiempo_espera = self.TIEMPO_BLOQUEO // 60  # Convertir a minutos
            return Response({
                'error': f'Cuenta bloqueada temporalmente. Demasiados intentos fallidos. Intente nuevamente en {tiempo_espera} minutos.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            # Registrar intento fallido
            intentos_actuales = self.registrar_intento_fallido(username)
            intentos_restantes = self.MAX_INTENTOS - intentos_actuales
            
            mensaje_error = 'Credenciales inválidas'
            if intentos_restantes > 0:
                mensaje_error += f'. Le quedan {intentos_restantes} intentos.'
            else:
                mensaje_error += f'. Cuenta bloqueada por {self.TIEMPO_BLOQUEO // 60} minutos.'
            
            return Response({
                'error': mensaje_error,
                'intentos_restantes': max(0, intentos_restantes)
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'error': 'Usuario desactivado'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Login exitoso - limpiar intentos
        self.limpiar_intentos(username)
        
        # Crear o obtener token
        token, created = Token.objects.get_or_create(user=user)
        
        # Serializar datos del usuario
        serializer = UsuarioSerializer(user)
        
        return Response({
            'token': token.key,
            'user': serializer.data,
            'message': 'Login exitoso'
        })

class LogoutView(APIView):
    """Vista para cerrar sesión"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Eliminar token del usuario
        try:
            request.user.auth_token.delete()
        except:
            pass
        
        return Response({
            'message': 'Logout exitoso'
        })

class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para el modelo Usuario"""
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'nombre', 'correo', 'cedula']
    ordering_fields = ['nombre', 'fecha_creacion', 'rol']
    ordering = ['-fecha_creacion']

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return UsuarioListSerializer
        return UsuarioSerializer

    def perform_create(self, serializer):
        """Solo admin puede crear usuarios"""
        if not self.request.user.es_admin:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Solo los administradores pueden crear usuarios")
        serializer.save()

    def perform_update(self, serializer):
        """Solo admin puede cambiar roles"""
        if 'rol' in self.request.data and not self.request.user.es_admin:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Solo los administradores pueden cambiar roles")
        serializer.save()

    def get_queryset(self):
        """Filtra el queryset según el usuario y su rol"""
        user = self.request.user
        
        # Admins pueden ver todos los usuarios
        if user.es_admin:
            return Usuario.objects.all()
        
        # Gerentes pueden ver todos excepto admins
        if user.es_gerente:
            return Usuario.objects.exclude(rol=1)
        
        # Digitadores pueden ver compradores y otros digitadores
        if user.es_digitador:
            return Usuario.objects.filter(rol__in=[3, 4])
        
        # Compradores solo pueden ver su propio perfil
        return Usuario.objects.filter(id=user.id)

    @action(detail=False, methods=['get'])
    def perfil(self, request):
        """Obtiene el perfil del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def actualizar_perfil(self, request):
        """Actualiza el perfil del usuario actual"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def cambiar_password(self, request):
        """Cambia la contraseña del usuario actual"""
        user = request.user
        password_actual = request.data.get('password_actual')
        password_nuevo = request.data.get('password_nuevo')
        password_confirm = request.data.get('password_confirm')

        if not user.check_password(password_actual):
            return Response({'error': 'Contraseña actual incorrecta'}, status=status.HTTP_400_BAD_REQUEST)

        if password_nuevo != password_confirm:
            return Response({'error': 'Las contraseñas no coinciden'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password_nuevo)
        user.save()
        return Response({'message': 'Contraseña actualizada correctamente'})

    @action(detail=True, methods=['post'])
    def activar_desactivar(self, request, pk=None):
        """Activa o desactiva un usuario (solo para admin y gerente)"""
        if not (request.user.es_admin or request.user.es_gerente):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)

        usuario = self.get_object()
        
        # Verificar que no se desactive el último admin
        if usuario.es_admin and usuario.es_activo:
            admins_activos = Usuario.objects.filter(rol=1, es_activo=True).count()
            if admins_activos <= 1:
                return Response(
                    {'error': 'No se puede desactivar el último administrador del sistema'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        usuario.es_activo = not usuario.es_activo
        usuario.save()
        
        estado = "activado" if usuario.es_activo else "desactivado"
        return Response({'message': f'Usuario {estado} correctamente'})

    @action(detail=False, methods=['get'])
    def compradores(self, request):
        """Obtiene solo los usuarios con rol de comprador"""
        compradores = Usuario.objects.filter(rol=4, es_activo=True)
        serializer = CompradorSerializer(compradores, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_rol(self, request):
        """Obtiene usuarios filtrados por rol"""
        rol = request.query_params.get('rol')
        if rol:
            usuarios = Usuario.objects.filter(rol=rol, es_activo=True)
            serializer = UsuarioListSerializer(usuarios, many=True)
            return Response(serializer.data)
        return Response({'error': 'Parámetro rol requerido'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de usuarios por rol"""
        if not (request.user.es_admin or request.user.es_gerente):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        stats = {}
        for rol_id, rol_nombre in Usuario.ROLES_CHOICES:
            count = Usuario.objects.filter(rol=rol_id, es_activo=True).count()
            stats[rol_nombre] = count
        
        return Response(stats)