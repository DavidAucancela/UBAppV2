from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
from .serializers import UsuarioSerializer, UsuarioListSerializer, CompradorSerializer, CompradorMapaSerializer, DashboardUsuarioSerializer
from .permissions import SoloAdmin
from .validators import validar_password_fuerte
from .datos_ecuador import (
    obtener_provincias, 
    obtener_cantones, 
    obtener_ciudades,
    obtener_coordenadas
)

Usuario = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """Vista para autenticación de usuarios con límite de intentos"""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # No usar autenticación en login
    
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
        
        # Crear tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Serializar datos del usuario
        serializer = UsuarioSerializer(user)
        
        return Response({
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': serializer.data,
            'message': 'Login exitoso'
        })

class LogoutView(APIView):
    """Vista para cerrar sesión"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Para JWT, simplemente confirmamos el logout
        # El frontend eliminará los tokens del localStorage
        # Opcionalmente podrías blacklistear el token aquí
        try:
            # Si usas el refresh token para blacklist
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception as e:
            # Si no tienes blacklist habilitado o hay algún error, continuar
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

    def get_permissions(self):
        """Aplica permisos por acción: crear/eliminar solo admin; resto autenticados."""
        if self.action in ['create', 'destroy']:
            return [SoloAdmin()]
        return [permissions.IsAuthenticated()]

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
        
        # Validación fuerte centralizada
        try:
            validar_password_fuerte(password_nuevo)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar contraseña
        user.set_password(password_nuevo)
        user.save()

        # Con JWT no necesitamos invalidar tokens manualmente
        # El usuario deberá iniciar sesión nuevamente con la nueva contraseña

        return Response({'message': 'Contraseña actualizada correctamente. Vuelva a iniciar sesión.'})

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

    @action(detail=False, methods=['get'])
    def mapa_compradores(self, request):
        """Obtiene compradores con ubicación para el mapa interactivo"""
        ciudad = request.query_params.get('ciudad', None)
        
        # Filtrar compradores activos con ubicación
        compradores = Usuario.objects.filter(
            rol=4,  # Solo compradores
            es_activo=True
        ).exclude(
            ciudad__isnull=True
        ).exclude(
            ciudad=''
        )
        
        # Filtrar por ciudad si se especifica
        if ciudad:
            compradores = compradores.filter(ciudad=ciudad)
        
        serializer = CompradorMapaSerializer(compradores, many=True)
        
        # Agrupar por ciudad para el mapa
        ciudades_data = {}
        for comprador_data in serializer.data:
            ciudad_nombre = comprador_data.get('ciudad')
            if ciudad_nombre:
                if ciudad_nombre not in ciudades_data:
                    ciudades_data[ciudad_nombre] = {
                        'ciudad': ciudad_nombre,
                        'total_compradores': 0,
                        'compradores': []
                    }
                ciudades_data[ciudad_nombre]['total_compradores'] += 1
                ciudades_data[ciudad_nombre]['compradores'].append(comprador_data)
        
        return Response({
            'ciudades': list(ciudades_data.values()),
            'total_compradores': compradores.count()
        })
    
    @action(detail=True, methods=['get'])
    def envios_comprador(self, request, pk=None):
        """Obtiene todos los envíos de un comprador específico"""
        comprador = self.get_object()
        
        # Verificar que sea un comprador
        if comprador.rol != 4:
            return Response(
                {'error': 'El usuario especificado no es un comprador'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener envíos del comprador
        from apps.archivos.models import Envio
        from apps.archivos.serializers import EnvioListSerializer
        
        envios = Envio.objects.filter(comprador=comprador).order_by('-fecha_emision')
        
        # Filtros opcionales
        estado = request.query_params.get('estado', None)
        if estado:
            envios = envios.filter(estado=estado)
        
        serializer = EnvioListSerializer(envios, many=True)
        
        return Response({
            'comprador': CompradorSerializer(comprador).data,
            'envios': serializer.data,
            'total_envios': envios.count()
        })
    
    @action(detail=False, methods=['get'])
    def dashboard_usuario(self, request):
        """Dashboard del usuario actual con sus envíos y estadísticas de cupo"""
        from datetime import datetime
        from apps.archivos.models import Envio
        from apps.archivos.serializers import EnvioListSerializer
        
        usuario = request.user
        anio = request.query_params.get('anio', datetime.now().year)
        
        try:
            anio = int(anio)
        except ValueError:
            anio = datetime.now().year
        
        # Obtener estadísticas de envíos
        estadisticas = usuario.obtener_estadisticas_envios(anio)
        
        # Obtener estadísticas de cupo (solo para compradores)
        if usuario.es_comprador:
            peso_usado = usuario.obtener_peso_usado_anual(anio)
            peso_disponible = usuario.obtener_peso_disponible_anual(anio)
            porcentaje_usado = usuario.obtener_porcentaje_cupo_usado(anio)
        else:
            peso_usado = 0
            peso_disponible = 0
            porcentaje_usado = 0
        
        # Datos del dashboard
        dashboard_data = {
            'usuario': usuario,
            'cupo_anual': usuario.cupo_anual,
            'peso_usado': peso_usado,
            'peso_disponible': peso_disponible,
            'porcentaje_usado': porcentaje_usado,
            'anio': anio,
            **estadisticas
        }
        
        # Serializar datos
        serializer = DashboardUsuarioSerializer(dashboard_data)
        
        # Obtener envíos recientes del usuario (últimos 10)
        envios = Envio.objects.filter(
            comprador=usuario
        ).order_by('-fecha_emision')[:10]
        
        envios_serializer = EnvioListSerializer(envios, many=True)
        
        return Response({
            'dashboard': serializer.data,
            'envios_recientes': envios_serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def mis_envios(self, request):
        """Obtiene todos los envíos del usuario actual"""
        from apps.archivos.models import Envio
        from apps.archivos.serializers import EnvioListSerializer
        
        usuario = request.user
        
        # Obtener envíos del usuario
        envios = Envio.objects.filter(comprador=usuario).order_by('-fecha_emision')
        
        # Filtros opcionales
        estado = request.query_params.get('estado', None)
        if estado:
            envios = envios.filter(estado=estado)
        
        # Filtro por fecha
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)
        
        if fecha_desde:
            envios = envios.filter(fecha_emision__gte=fecha_desde)
        if fecha_hasta:
            envios = envios.filter(fecha_emision__lte=fecha_hasta)
        
        serializer = EnvioListSerializer(envios, many=True)
        
        return Response({
            'envios': serializer.data,
            'total_envios': envios.count()
        })
    
    @action(detail=False, methods=['get'])
    def estadisticas_cupo(self, request):
        """Obtiene estadísticas del cupo anual del usuario"""
        from datetime import datetime
        
        usuario = request.user
        anio = request.query_params.get('anio', datetime.now().year)
        
        try:
            anio = int(anio)
        except ValueError:
            anio = datetime.now().year
        
        # Obtener estadísticas de cupo
        peso_usado = usuario.obtener_peso_usado_anual(anio)
        peso_disponible = usuario.obtener_peso_disponible_anual(anio)
        porcentaje_usado = usuario.obtener_porcentaje_cupo_usado(anio)
        
        return Response({
            'cupo_anual': float(usuario.cupo_anual),
            'peso_usado': peso_usado,
            'peso_disponible': peso_disponible,
            'porcentaje_usado': porcentaje_usado,
            'anio': anio,
            'alerta': 'warning' if porcentaje_usado >= 80 else 'info' if porcentaje_usado >= 50 else 'success'
        })