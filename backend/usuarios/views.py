from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .serializers import (
    UsuarioSerializer, 
    UsuarioListSerializer, 
    CompradorSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer
)
from .utils import (
    enviar_email_verificacion,
    enviar_email_recuperacion,
    enviar_notificacion_cambio_password,
    validar_password_seguro,
    validar_datos_obligatorios
)

Usuario = get_user_model()

#vista para comenzar el proceso de ingreso/registro
class LoginView(APIView):
    """Vista para autenticación de usuarios con políticas de seguridad"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Se requieren username y password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar usuario para verificar bloqueo
        try:
            user = Usuario.objects.get(username=username)
            
            # Verificar si está bloqueado
            if user.esta_bloqueado():
                tiempo_restante = (user.bloqueado_hasta - timezone.now()).seconds // 60
                return Response({
                    'error': f'Usuario bloqueado por múltiples intentos fallidos. Intenta de nuevo en {tiempo_restante} minutos.'
                }, status=status.HTTP_403_FORBIDDEN)
                
        except Usuario.DoesNotExist:
            return Response({
                'error': 'Credenciales inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Intentar autenticar
        user = authenticate(username=username, password=password)
        
        if user is None:
            # Incrementar intentos fallidos
            try:
                user_obj = Usuario.objects.get(username=username)
                user_obj.incrementar_intentos_fallidos()
            except Usuario.DoesNotExist:
                pass
            
            return Response({
                'error': 'Credenciales inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active or not user.es_activo:
            return Response({
                'error': 'Usuario desactivado'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar si el email está verificado (solo para nuevos usuarios)
        if not user.email_verificado and user.fecha_creacion > timezone.now() - timedelta(days=7):
            return Response({
                'error': 'Debes verificar tu correo electrónico antes de iniciar sesión',
                'require_email_verification': True
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Login exitoso - resetear intentos fallidos y actualizar actividad
        user.resetear_intentos_fallidos()
        user.actualizar_ultima_actividad()
        
        # Crear o obtener token
        token, created = Token.objects.get_or_create(user=user)
        
        # Serializar datos del usuario
        serializer = UsuarioSerializer(user)
        
        response_data = {
            'token': token.key,
            'user': serializer.data,
            'message': 'Login exitoso'
        }
        
        # Advertir si debe cambiar contraseña
        if user.debe_cambiar_password:
            response_data['warning'] = 'Debes cambiar tu contraseña'
            response_data['must_change_password'] = True
        
        return Response(response_data)

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

class RegisterView(APIView):
    """Vista para registro de nuevos usuarios"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        data = request.data
        
        # Validar datos obligatorios
        es_valido, errores = validar_datos_obligatorios(data)
        if not es_valido:
            return Response({
                'errors': errores
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar contraseña segura
        password = data.get('password')
        if password:
            es_valida, mensaje = validar_password_seguro(password)
            if not es_valida:
                return Response({
                    'error': mensaje
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar confirmación de contraseña
        if data.get('password') != data.get('password_confirm'):
            return Response({
                'error': 'Las contraseñas no coinciden'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si el usuario ya existe
        if Usuario.objects.filter(username=data.get('username')).exists():
            return Response({
                'error': 'El nombre de usuario ya está en uso'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if Usuario.objects.filter(correo=data.get('correo')).exists():
            return Response({
                'error': 'El correo electrónico ya está registrado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if Usuario.objects.filter(cedula=data.get('cedula')).exists():
            return Response({
                'error': 'La cédula ya está registrada'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear usuario
        serializer = UsuarioSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Enviar email de verificación
            enviar_email_verificacion(user, request)
            
            return Response({
                'message': 'Usuario creado exitosamente. Por favor verifica tu correo electrónico.',
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    """Vista para verificar el email del usuario"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        user_id = request.data.get('user_id')
        
        if not token or not user_id:
            return Response({
                'error': 'Token y user_id son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Usuario.objects.get(id=user_id)
            
            if user.verificar_email(token):
                return Response({
                    'message': 'Email verificado exitosamente'
                })
            else:
                return Response({
                    'error': 'Token inválido o expirado'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Usuario.DoesNotExist:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)

class ResendVerificationView(APIView):
    """Vista para reenviar el email de verificación"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': 'Email es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Usuario.objects.get(correo=email)
            
            if user.email_verificado:
                return Response({
                    'message': 'Este email ya está verificado'
                })
            
            enviar_email_verificacion(user, request)
            
            return Response({
                'message': 'Email de verificación reenviado'
            })
            
        except Usuario.DoesNotExist:
            # No revelar si el email existe o no por seguridad
            return Response({
                'message': 'Si el email existe en nuestro sistema, recibirás un correo de verificación'
            })

class PasswordResetRequestView(APIView):
    """Vista para solicitar recuperación de contraseña"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'error': 'Email es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Usuario.objects.get(correo=email)
            enviar_email_recuperacion(user, request)
        except Usuario.DoesNotExist:
            pass  # No revelar si el email existe
        
        return Response({
            'message': 'Si el email existe en nuestro sistema, recibirás instrucciones para restablecer tu contraseña'
        })

class PasswordResetConfirmView(APIView):
    """Vista para confirmar el restablecimiento de contraseña"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        user_id = request.data.get('user_id')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([token, user_id, new_password, confirm_password]):
            return Response({
                'error': 'Todos los campos son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({
                'error': 'Las contraseñas no coinciden'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar contraseña segura
        es_valida, mensaje = validar_password_seguro(new_password)
        if not es_valida:
            return Response({
                'error': mensaje
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Usuario.objects.get(id=user_id)
            
            if user.puede_recuperar_password(token):
                user.set_password(new_password)
                user.token_recuperacion = None
                user.token_recuperacion_expira = None
                user.ultima_cambio_password = timezone.now()
                user.debe_cambiar_password = False
                user.save()
                
                # Enviar notificación de cambio
                enviar_notificacion_cambio_password(user)
                
                return Response({
                    'message': 'Contraseña restablecida exitosamente'
                })
            else:
                return Response({
                    'error': 'Token inválido o expirado'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Usuario.DoesNotExist:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)

class ListUsersView(APIView):
    """Vista para listar usuarios creados"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Verificar permisos - solo admins y gerentes pueden ver todos los usuarios
        user = request.user
        
        if user.es_admin:
            # Los admins pueden ver todos los usuarios
            usuarios = Usuario.objects.all()
        elif user.es_gerente:
            # Los gerentes pueden ver todos excepto admins
            usuarios = Usuario.objects.exclude(rol=1)
        elif user.es_digitador:
            # Los digitadores pueden ver compradores y otros digitadores
            usuarios = Usuario.objects.filter(rol__in=[3, 4])
        else:
            # Los compradores solo pueden ver su propio perfil
            usuarios = Usuario.objects.filter(id=user.id)
        
        # Aplicar filtros opcionales
        rol_filter = request.query_params.get('rol')
        if rol_filter:
            usuarios = usuarios.filter(rol=rol_filter)
        
        activo_filter = request.query_params.get('activo')
        if activo_filter is not None:
            activo_bool = activo_filter.lower() == 'true'
            usuarios = usuarios.filter(es_activo=activo_bool)
        
        verificado_filter = request.query_params.get('verificado')
        if verificado_filter is not None:
            verificado_bool = verificado_filter.lower() == 'true'
            usuarios = usuarios.filter(email_verificado=verificado_bool)
        
        # Búsqueda por nombre o email
        search = request.query_params.get('search')
        if search:
            usuarios = usuarios.filter(
                Q(nombre__icontains=search) |
                Q(username__icontains=search) |
                Q(correo__icontains=search) |
                Q(cedula__icontains=search)
            )
        
        # Ordenar por fecha de creación (más recientes primero)
        usuarios = usuarios.order_by('-fecha_creacion')
        
        # Serializar los datos
        serializer = UsuarioListSerializer(usuarios, many=True)
        
        # Agregar estadísticas para admins y gerentes
        response_data = {
            'usuarios': serializer.data,
            'total': usuarios.count()
        }
        
        if user.es_admin or user.es_gerente:
            response_data['estadisticas'] = {
                'total_usuarios': Usuario.objects.count(),
                'usuarios_activos': Usuario.objects.filter(es_activo=True).count(),
                'usuarios_verificados': Usuario.objects.filter(email_verificado=True).count(),
                'por_rol': {}
            }
            
            for rol_id, rol_nombre in Usuario.ROLES_CHOICES:
                response_data['estadisticas']['por_rol'][rol_nombre] = Usuario.objects.filter(rol=rol_id).count()
        
        return Response(response_data)

class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para el modelo Usuario con funcionalidades extendidas"""
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

    def get_queryset(self):
        """Filtra el queryset según el usuario y su rol"""
        user = self.request.user
        
        # Actualizar última actividad
        user.actualizar_ultima_actividad()
        
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
    
    def create(self, request, *args, **kwargs):
        """Crea un nuevo usuario con validaciones"""
        # Validar permisos
        if not (request.user.es_admin or request.user.es_gerente):
            return Response({
                'error': 'No tienes permisos para crear usuarios'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Validar datos obligatorios
        es_valido, errores = validar_datos_obligatorios(request.data)
        if not es_valido:
            return Response({
                'errors': errores
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar contraseña segura
        password = request.data.get('password')
        if password:
            es_valida, mensaje = validar_password_seguro(password)
            if not es_valida:
                return Response({
                    'error': mensaje
                }, status=status.HTTP_400_BAD_REQUEST)
        
        response = super().create(request, *args, **kwargs)
        
        # Enviar email de verificación al nuevo usuario
        if response.status_code == 201:
            user = Usuario.objects.get(id=response.data['id'])
            enviar_email_verificacion(user, request)
        
        return response
    
    def update(self, request, *args, **kwargs):
        """Actualiza un usuario con validaciones"""
        instance = self.get_object()
        
        # Verificar permisos
        if not (request.user.es_admin or 
                request.user.es_gerente or 
                request.user.id == instance.id):
            return Response({
                'error': 'No tienes permisos para editar este usuario'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Si se está cambiando la contraseña, validar que sea segura
        if 'password' in request.data:
            es_valida, mensaje = validar_password_seguro(request.data['password'])
            if not es_valida:
                return Response({
                    'error': mensaje
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Elimina un usuario (solo admins)"""
        if not request.user.es_admin:
            return Response({
                'error': 'Solo los administradores pueden eliminar usuarios'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def perfil(self, request):
        """Obtiene el perfil del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def actualizar_perfil(self, request):
        """Actualiza el perfil del usuario actual"""
        # Validar que no intente cambiar su propio rol
        if 'rol' in request.data and not request.user.es_admin:
            return Response({
                'error': 'No puedes cambiar tu propio rol'
            }, status=status.HTTP_403_FORBIDDEN)
        
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
        
        # Validar contraseña segura
        es_valida, mensaje = validar_password_seguro(password_nuevo)
        if not es_valida:
            return Response({'error': mensaje}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password_nuevo)
        user.ultima_cambio_password = timezone.now()
        user.debe_cambiar_password = False
        user.save()
        
        # Enviar notificación
        enviar_notificacion_cambio_password(user)
        
        return Response({'message': 'Contraseña actualizada correctamente'})

    @action(detail=True, methods=['post'])
    def activar_desactivar(self, request, pk=None):
        """Activa o desactiva un usuario (solo para admin y gerente)"""
        if not (request.user.es_admin or request.user.es_gerente):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)

        usuario = self.get_object()
        
        # No permitir desactivar el propio usuario
        if usuario.id == request.user.id:
            return Response({'error': 'No puedes desactivarte a ti mismo'}, status=status.HTTP_400_BAD_REQUEST)
        
        usuario.es_activo = not usuario.es_activo
        usuario.save()
        
        estado = "activado" if usuario.es_activo else "desactivado"
        return Response({'message': f'Usuario {estado} correctamente'})
    
    @action(detail=True, methods=['post'])
    def forzar_cambio_password(self, request, pk=None):
        """Fuerza a un usuario a cambiar su contraseña en el próximo login"""
        if not (request.user.es_admin or request.user.es_gerente):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        usuario = self.get_object()
        usuario.debe_cambiar_password = True
        usuario.save()
        
        return Response({'message': 'El usuario deberá cambiar su contraseña en el próximo inicio de sesión'})
    
    @action(detail=True, methods=['post'])
    def desbloquear(self, request, pk=None):
        """Desbloquea un usuario bloqueado por intentos fallidos"""
        if not (request.user.es_admin or request.user.es_gerente):
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        usuario = self.get_object()
        usuario.resetear_intentos_fallidos()
        
        return Response({'message': 'Usuario desbloqueado correctamente'})

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
        
        stats = {
            'por_rol': {},
            'total_usuarios': Usuario.objects.count(),
            'usuarios_activos': Usuario.objects.filter(es_activo=True).count(),
            'usuarios_verificados': Usuario.objects.filter(email_verificado=True).count(),
            'usuarios_bloqueados': Usuario.objects.filter(bloqueado_hasta__isnull=False).count(),
        }
        
        for rol_id, rol_nombre in Usuario.ROLES_CHOICES:
            stats['por_rol'][rol_nombre] = Usuario.objects.filter(rol=rol_id, es_activo=True).count()
        
        # Usuarios activos en las últimas 24 horas
        hace_24h = timezone.now() - timedelta(hours=24)
        stats['activos_ultimas_24h'] = Usuario.objects.filter(
            ultima_actividad__gte=hace_24h
        ).count()
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def check_session(self, request):
        """Verifica si la sesión del usuario sigue activa"""
        user = request.user
        
        # Verificar inactividad (30 minutos)
        tiempo_inactividad = timezone.now() - user.ultima_actividad
        if tiempo_inactividad > timedelta(minutes=30):
            # Cerrar sesión automáticamente
            try:
                user.auth_token.delete()
            except:
                pass
            
            return Response({
                'active': False,
                'message': 'Sesión expirada por inactividad'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Actualizar última actividad
        user.actualizar_ultima_actividad()
        
        return Response({
            'active': True,
            'last_activity': user.ultima_actividad,
            'must_change_password': user.debe_cambiar_password
        })