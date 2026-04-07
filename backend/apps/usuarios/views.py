"""
Views para la app de usuarios
Usan la arquitectura en capas (servicios y repositorios)
"""
from rest_framework import viewsets, permissions, status, filters
from apps.core.pagination import CustomPageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
import secrets
import string
import logging

logger = logging.getLogger(__name__)

from .serializers import (
    UsuarioSerializer as MainUsuarioSerializer, 
    UsuarioListSerializer, 
    CompradorSerializer,
    CompradorMapaSerializer,
    DashboardUsuarioSerializer
)
UsuarioSerializer = MainUsuarioSerializer
from .permissions import SoloAdmin
from .services import UsuarioService
from .repositories import usuario_repository
from apps.core.throttling import LoginRateThrottle, RegistroRateThrottle
from .validators import validar_password_fuerte
from .tasks import enviar_bienvenida, enviar_reset_password

Usuario = get_user_model()


@extend_schema(
    summary="Autenticación de usuario",
    description="""
    Autentica un usuario y retorna tokens JWT para acceso a la API.
    
    **Seguridad:**
    - Límite de 5 intentos fallidos
    - Bloqueo temporal de 15 minutos tras superar el límite
    - Retorna tokens de acceso y refresh
    """,
    tags=['autenticacion'],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'description': 'Nombre de usuario'},
                'password': {'type': 'string', 'format': 'password', 'description': 'Contraseña'}
            },
            'required': ['username', 'password']
        }
    },
    responses={
        200: {'description': 'Login exitoso'},
        401: {'description': 'Credenciales inválidas o usuario desactivado'},
        429: {'description': 'Demasiados intentos fallidos'}
    }
)
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """Vista para autenticación de usuarios con límite de intentos"""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [LoginRateThrottle]  # Rate limiting para prevenir ataques de fuerza bruta
    
    MAX_INTENTOS = 5
    TIEMPO_BLOQUEO = 900  # 15 minutos
    
    def get_cache_key(self, username):
        return f'login_intentos_{username}'
    
    def verificar_intentos(self, username):
        try:
            cache_key = self.get_cache_key(username)
            intentos = cache.get(cache_key, 0)
            if intentos >= self.MAX_INTENTOS:
                return False, intentos
            return True, intentos
        except Exception:
            return True, 0  # Si Redis falla, permitir el intento

    def registrar_intento_fallido(self, username):
        try:
            cache_key = self.get_cache_key(username)
            intentos = cache.get(cache_key, 0)
            intentos += 1
            cache.set(cache_key, intentos, self.TIEMPO_BLOQUEO)
            return intentos
        except Exception:
            return 1

    def limpiar_intentos(self, username):
        try:
            cache_key = self.get_cache_key(username)
            cache.delete(cache_key)
        except Exception:
            pass
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Se requieren username y password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            puede_intentar, intentos = self.verificar_intentos(username)
        except Exception as e:
            logger.exception(f"[LOGIN] Error en verificar_intentos: {e}")
            puede_intentar, intentos = True, 0

        if not puede_intentar:
            tiempo_espera = self.TIEMPO_BLOQUEO // 60
            return Response({
                'error': f'Cuenta bloqueada temporalmente. Demasiados intentos fallidos. Intente nuevamente en {tiempo_espera} minutos.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        try:
            user = authenticate(username=username, password=password)
        except Exception as e:
            logger.exception(f"[LOGIN] Error en authenticate(): {e}")
            return Response({'error': 'Error interno al autenticar'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if user is None:
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

        if not user.es_activo:
            return Response({
                'error': 'Usuario desactivado'
            }, status=status.HTTP_401_UNAUTHORIZED)

        self.limpiar_intentos(username)

        try:
            refresh = RefreshToken.for_user(user)
        except Exception as e:
            logger.exception(f"[LOGIN] Error en RefreshToken.for_user(): {e}")
            return Response({'error': 'Error interno al generar token'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            serializer = UsuarioSerializer(user)
            user_data = serializer.data
        except Exception as e:
            logger.exception(f"[LOGIN] Error en UsuarioSerializer: {e}")
            return Response({'error': 'Error interno al serializar usuario'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        is_secure = not settings.DEBUG

        response = Response({
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data,
            'message': 'Login exitoso'
        })
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,
            samesite='Lax',
            secure=is_secure,
            max_age=3600,  # 60 min
        )
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            samesite='Lax',
            secure=is_secure,
            max_age=86400,  # 1 día
        )
        return response


class LogoutView(APIView):
    """Vista para cerrar sesión"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh') or request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass

        response = Response({'message': 'Logout exitoso'})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


@method_decorator(csrf_exempt, name='dispatch')
class VerifyEmailView(APIView):
    """Vista para verificar si un correo electrónico existe"""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'El correo electrónico es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exists = usuario_repository.existe_correo(email)
        return Response({'exists': exists})


@method_decorator(csrf_exempt, name='dispatch')
class ResetPasswordView(APIView):
    """Vista para solicitar restablecimiento de contraseña"""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    def generate_reset_token(self):
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(32))
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'El correo electrónico es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            usuario = usuario_repository.obtener_por_correo(email)
            
            reset_token = self.generate_reset_token()
            cache_key = f'reset_password_{reset_token}'
            cache.set(cache_key, usuario.id, timeout=3600)
            
            new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(12))

            try:
                usuario.set_password(new_password)
                usuario.save()
                enviar_reset_password.delay(
                    nombre=usuario.nombre or usuario.username,
                    username=usuario.username,
                    new_password=new_password,
                    email=email,
                )
                return Response({
                    'message': 'Se ha enviado un correo electrónico con tu nueva contraseña temporal.'
                })
            except Exception:
                return Response({
                    'error': 'Error al procesar la solicitud. Por favor, contacta al administrador.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception:
            return Response({
                'message': 'Si el correo está registrado, recibirás instrucciones para restablecer tu contraseña.'
            })


@method_decorator(csrf_exempt, name='dispatch')
class RegisterCompradorView(APIView):
    """Vista pública para registro de compradores"""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [RegistroRateThrottle]  # Rate limiting para prevenir creación masiva de cuentas
    
    def post(self, request):
        rol = request.data.get('rol', 4)
        if rol != 4:
            return Response({
                'error': 'Solo se permite el registro de compradores'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        password = request.data.get('password')
        if not password:
            return Response({
                'error': 'La contraseña es requerida'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validar_password_fuerte(password)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()
        data['rol'] = 4
        data['es_activo'] = True
        if 'password_confirm' not in data:
            data['password_confirm'] = password
        
        serializer = UsuarioSerializer(data=data)
        if serializer.is_valid():
            usuario = serializer.save()
            
            return Response({
                'message': 'Usuario comprador registrado exitosamente',
                'user': UsuarioSerializer(usuario).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        summary="Listar usuarios",
        description="Obtiene la lista de usuarios según los permisos del usuario autenticado",
        tags=['usuarios']
    ),
    create=extend_schema(
        summary="Crear usuario",
        description="Crea un nuevo usuario (solo administradores)",
        tags=['usuarios']
    ),
    retrieve=extend_schema(
        summary="Obtener usuario por ID",
        description="Obtiene los detalles de un usuario específico",
        tags=['usuarios']
    ),
    update=extend_schema(
        summary="Actualizar usuario completo",
        tags=['usuarios']
    ),
    partial_update=extend_schema(
        summary="Actualizar usuario parcialmente",
        tags=['usuarios']
    ),
    destroy=extend_schema(
        summary="Eliminar usuario",
        description="Elimina un usuario del sistema (solo administradores)",
        tags=['usuarios']
    ),
)
class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios.
    
    **Arquitectura**: Usa servicios y repositorios para separar responsabilidades.
    
    **Permisos:**
    - **Admin**: Puede ver y gestionar todos los usuarios
    - **Gerente**: Puede ver todos excepto administradores
    - **Digitador**: Puede ver digitadores y compradores
    - **Comprador**: Solo puede ver su propio perfil
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # El frontend maneja la paginación en el cliente
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'nombre', 'correo', 'cedula']
    ordering_fields = ['nombre', 'fecha_creacion', 'rol']
    ordering = ['-fecha_creacion']

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [SoloAdmin()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'list':
            return UsuarioListSerializer
        return UsuarioSerializer

    def get_queryset(self):
        """Usa repositorio para filtrar por permisos"""
        return usuario_repository.filtrar_por_permisos_usuario(self.request.user)

    def create(self, request, *args, **kwargs):
        """Crear usuario - delegado al servicio"""
        try:
            usuario = UsuarioService.crear_usuario(
                data=request.data,
                usuario_creador=request.user
            )
            
            # Enviar correo con credenciales si se creó correctamente (async)
            password = request.data.get('password')
            if password and usuario.correo:
                try:
                    enviar_bienvenida.delay(
                        nombre=usuario.nombre or usuario.username,
                        username=usuario.username,
                        password=password,
                        rol=usuario.get_rol_display_name(),
                        correo=usuario.correo,
                        frontend_url=getattr(settings, 'FRONTEND_URL', 'http://localhost:4200'),
                    )
                except Exception:
                    pass  # El email es un efecto secundario; no debe bloquear la creación
            
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """Actualizar usuario - delegado al servicio"""
        try:
            usuario = UsuarioService.actualizar_usuario(
                usuario_id=kwargs.get('pk'),
                data=request.data,
                usuario_actual=request.user
            )
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def perfil(self, request):
        """Obtiene el perfil del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def actualizar_perfil(self, request):
        """Actualiza el perfil - delegado al servicio"""
        try:
            usuario = UsuarioService.actualizar_perfil(
                usuario=request.user,
                data=request.data
            )
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def cambiar_password(self, request):
        """Cambia la contraseña - delegado al servicio"""
        try:
            UsuarioService.cambiar_password(
                usuario=request.user,
                password_actual=request.data.get('password_actual'),
                password_nuevo=request.data.get('password_nuevo'),
                password_confirm=request.data.get('password_confirm')
            )
            return Response({'message': 'Contraseña actualizada correctamente'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def activar_desactivar(self, request, pk=None):
        """Activa o desactiva un usuario - delegado al servicio"""
        try:
            usuario = UsuarioService.activar_desactivar_usuario(
                usuario_id=pk,
                usuario_actual=request.user
            )
            estado = "activado" if usuario.es_activo else "desactivado"
            return Response({'message': f'Usuario {estado} correctamente'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def compradores(self, request):
        """Obtiene compradores activos - usa repositorio"""
        compradores = usuario_repository.obtener_compradores_activos()
        serializer = CompradorSerializer(compradores, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_rol(self, request):
        """Obtiene usuarios por rol - usa repositorio"""
        rol = request.query_params.get('rol')
        if rol:
            usuarios = usuario_repository.obtener_por_rol(int(rol))
            serializer = UsuarioListSerializer(usuarios, many=True)
            return Response(serializer.data)
        return Response({'error': 'Parámetro rol requerido'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas por rol - usa repositorio"""
        if not (request.user.es_admin or request.user.es_gerente):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        stats = usuario_repository.obtener_estadisticas_por_rol()
        return Response(stats)

    @action(detail=False, methods=['get'])
    def mapa_compradores(self, request):
        """Obtiene compradores agrupados por provincia para el mapa"""
        provincia = request.query_params.get('provincia', None)
        
        compradores = usuario_repository.obtener_compradores_con_ubicacion()
        if provincia:
            compradores = compradores.filter(provincia=provincia)
        
        serializer = CompradorMapaSerializer(compradores, many=True)
        
        provincias_data = {}
        for comprador_data in serializer.data:
            provincia_nombre = comprador_data.get('provincia')
            if provincia_nombre:
                if provincia_nombre not in provincias_data:
                    provincias_data[provincia_nombre] = {
                        'provincia': provincia_nombre,
                        'total_compradores': 0,
                        'compradores': []
                    }
                provincias_data[provincia_nombre]['total_compradores'] += 1
                provincias_data[provincia_nombre]['compradores'].append(comprador_data)
        
        return Response({
            'provincias': list(provincias_data.values()),
            'total_compradores': compradores.count()
        })
    
    @action(detail=True, methods=['get'])
    def envios_comprador(self, request, pk=None):
        """Obtiene envíos de un comprador específico"""
        comprador = self.get_object()
        
        if comprador.rol != 4:
            return Response(
                {'error': 'El usuario especificado no es un comprador'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from apps.archivos.repositories import envio_repository
        from apps.archivos.serializers import EnvioListSerializer
        
        envios = envio_repository.filtrar_por_comprador(comprador.id)
        
        estado = request.query_params.get('estado', None)
        if estado:
            envios = envios.filter(estado=estado)
        
        serializer = EnvioListSerializer(envios, many=True)
        
        return Response({
            'comprador': CompradorSerializer(comprador).data,
            'envios': serializer.data,
            'total_envios': envios.count()
        })
    
    @extend_schema(
        summary="Obtener dashboard del usuario",
        description="""
        Obtiene el dashboard completo del usuario con estadísticas y datos relevantes.
        
        Incluye:
        - Estadísticas de envíos por año
        - Información de cupo anual (para compradores)
        - Porcentaje de cupo usado
        - Envíos recientes
        """,
        parameters=[
            OpenApiParameter(
                name='anio',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Año para las estadísticas (default: año actual)',
            ),
        ],
        tags=['usuarios'],
    )
    @action(detail=False, methods=['get'])
    def dashboard_usuario(self, request):
        """Dashboard del usuario - delegado al servicio"""
        from datetime import datetime
        from apps.archivos.serializers import EnvioListSerializer
        from apps.archivos.repositories import envio_repository
        from apps.core.base.base_service import BaseService
        
        anio = request.query_params.get('anio', datetime.now().year)
        try:
            anio = int(anio)
        except ValueError:
            anio = datetime.now().year
        
        # Log para depuración
        BaseService.log_info(
            f"Dashboard solicitado para usuario {request.user.id} ({request.user.username}), "
            f"rol: {request.user.rol}, es_comprador: {request.user.es_comprador}, año: {anio}",
            usuario_id=request.user.id
        )
        
        dashboard_data = UsuarioService.obtener_dashboard_usuario(request.user, anio)
        serializer = DashboardUsuarioSerializer(dashboard_data)
        
        # Filtrar envíos por comprador (solo si es comprador, sino usar filtro por permisos)
        if request.user.es_comprador:
            envios = envio_repository.filtrar_por_comprador(request.user.id).order_by('-fecha_emision')[:10]
        else:
            # Para otros roles, usar filtro por permisos
            envios = envio_repository.filtrar_por_permisos_usuario(request.user).order_by('-fecha_emision')[:10]
        
        envios_serializer = EnvioListSerializer(envios, many=True)
        
        # Log de datos devueltos
        BaseService.log_info(
            f"Dashboard generado - Total envíos: {dashboard_data.get('total_envios', 0)}, "
            f"Envíos recientes: {envios.count()}",
            usuario_id=request.user.id
        )
        
        return Response({
            'dashboard': serializer.data,
            'envios_recientes': envios_serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def mis_envios(self, request):
        """Obtiene envíos del usuario actual"""
        from apps.archivos.repositories import envio_repository
        from apps.archivos.serializers import EnvioListSerializer
        
        envios = envio_repository.filtrar_por_comprador(request.user.id)
        
        estado = request.query_params.get('estado', None)
        if estado:
            envios = envios.filter(estado=estado)
        
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
        """Obtiene estadísticas del cupo anual"""
        from datetime import datetime
        
        anio = request.query_params.get('anio', datetime.now().year)
        try:
            anio = int(anio)
        except ValueError:
            anio = datetime.now().year
        
        peso_usado = UsuarioService.obtener_peso_usado_anual(request.user, anio)
        peso_disponible = UsuarioService.obtener_cupo_disponible(request.user, anio)
        cupo_anual = float(request.user.cupo_anual)
        porcentaje_usado = (peso_usado / cupo_anual) * 100 if cupo_anual > 0 else 0
        
        return Response({
            'cupo_anual': cupo_anual,
            'peso_usado': peso_usado,
            'peso_disponible': peso_disponible,
            'porcentaje_usado': porcentaje_usado,
            'anio': anio,
            'alerta': 'warning' if porcentaje_usado >= 80 else 'info' if porcentaje_usado >= 50 else 'success'
        })
