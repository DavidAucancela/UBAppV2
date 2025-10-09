from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .utils import validar_password_seguro

Usuario = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer completo para el modelo Usuario"""
    password = serializers.CharField(write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)
    rol_nombre = serializers.CharField(source='get_rol_display_name', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'nombre', 'correo', 'cedula', 'rol', 'rol_nombre',
            'telefono', 'fecha_nacimiento', 'direccion',
            'tiene_discapacidad', 'tipo_discapacidad', 'notas_accesibilidad',
            'es_activo', 'email_verificado', 'ultima_actividad',
            'debe_cambiar_password', 'ultima_cambio_password',
            'intentos_login_fallidos', 'bloqueado_hasta',
            'fecha_creacion', 'fecha_actualizacion', 
            'password', 'password_confirm'
        ]
        read_only_fields = [
            'id', 'fecha_creacion', 'fecha_actualizacion', 
            'email_verificado', 'ultima_actividad', 
            'intentos_login_fallidos', 'bloqueado_hasta',
            'ultima_cambio_password'
        ]
    
    def validate(self, attrs):
        """Validaciones personalizadas"""
        # Validar contraseñas si se proporcionan
        if attrs.get('password'):
            if not attrs.get('password_confirm'):
                raise serializers.ValidationError("Se requiere confirmación de contraseña")
            
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError("Las contraseñas no coinciden")
            
            # Validar seguridad de la contraseña
            es_valida, mensaje = validar_password_seguro(attrs['password'])
            if not es_valida:
                raise serializers.ValidationError(mensaje)
        
        # Validar rol según permisos del usuario actual
        if 'rol' in attrs:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                user = request.user
                if not user.es_admin and attrs['rol'] == 1:
                    raise serializers.ValidationError("Solo los administradores pueden crear otros administradores")
                if not (user.es_admin or user.es_gerente) and attrs['rol'] in [1, 2]:
                    raise serializers.ValidationError("No tienes permisos para asignar este rol")
        
        return attrs
    
    def create(self, validated_data):
        """Crea un nuevo usuario"""
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        
        # Crear usuario
        user = Usuario.objects.create(**validated_data)
        
        # Establecer contraseña si se proporciona
        if password:
            user.set_password(password)
            user.save()
        
        return user
    
    def update(self, instance, validated_data):
        """Actualiza un usuario existente"""
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        
        # Actualizar campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Actualizar contraseña si se proporciona
        if password:
            instance.set_password(password)
            instance.ultima_cambio_password = instance.fecha_actualizacion
            instance.debe_cambiar_password = False
        
        instance.save()
        return instance

class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializer para listar usuarios (información limitada)"""
    rol_nombre = serializers.CharField(source='get_rol_display_name', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'nombre', 'correo', 'cedula', 
            'rol', 'rol_nombre', 'telefono',
            'tiene_discapacidad', 'es_activo', 'email_verificado',
            'ultima_actividad', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion']

class CompradorSerializer(serializers.ModelSerializer):
    """Serializer específico para compradores"""
    rol_nombre = serializers.CharField(source='get_rol_display_name', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'correo', 'cedula', 'rol_nombre', 'telefono']
        read_only_fields = ['id']

class PerfilSerializer(serializers.ModelSerializer):
    """Serializer para el perfil del usuario actual"""
    rol_nombre = serializers.CharField(source='get_rol_display_name', read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'nombre', 'correo', 'cedula', 
            'rol', 'rol_nombre', 'telefono', 'fecha_nacimiento', 'direccion',
            'tiene_discapacidad', 'tipo_discapacidad', 'notas_accesibilidad',
            'email_verificado', 'ultima_actividad', 'debe_cambiar_password',
            'fecha_creacion'
        ]
        read_only_fields = [
            'id', 'username', 'rol', 'email_verificado', 
            'ultima_actividad', 'debe_cambiar_password', 'fecha_creacion'
        ]

class CambiarPasswordSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña"""
    password_actual = serializers.CharField(required=True, write_only=True)
    password_nuevo = serializers.CharField(required=True, write_only=True)
    password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['password_nuevo'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        
        # Validar seguridad de la nueva contraseña
        es_valida, mensaje = validar_password_seguro(attrs['password_nuevo'])
        if not es_valida:
            raise serializers.ValidationError(mensaje)
        
        return attrs

class PasswordResetSerializer(serializers.Serializer):
    """Serializer para solicitud de recuperación de contraseña"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Valida que el email exista"""
        if not Usuario.objects.filter(correo=value).exists():
            # Por seguridad, no revelamos si el email existe o no
            pass
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer para confirmar recuperación de contraseña"""
    token = serializers.CharField(required=True)
    user_id = serializers.IntegerField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden")
        
        # Validar seguridad de la nueva contraseña
        es_valida, mensaje = validar_password_seguro(attrs['new_password'])
        if not es_valida:
            raise serializers.ValidationError(mensaje)
        
        return attrs

class EmailVerificationSerializer(serializers.Serializer):
    """Serializer para verificación de email"""
    token = serializers.CharField(required=True)
    user_id = serializers.IntegerField(required=True)