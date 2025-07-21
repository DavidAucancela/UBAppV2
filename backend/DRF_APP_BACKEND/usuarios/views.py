from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from .serializers import UsuarioSerializer, UsuarioListSerializer, CompradorSerializer

Usuario = get_user_model()

class LoginView(APIView):
    """Vista para autenticación de usuarios"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Se requieren username y password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({
                'error': 'Credenciales inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'error': 'Usuario desactivado'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
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
