from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

Usuario = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Usuario"""
    password = serializers.CharField(write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)
    rol_nombre = serializers.CharField(source='get_rol_display_name', read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'nombre', 'correo', 'cedula', 'rol', 'rol_nombre',
            'telefono', 'fecha_nacimiento', 'direccion', 'es_activo',
            'fecha_creacion', 'fecha_actualizacion', 'password', 'password_confirm'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def validate(self, attrs):
        if attrs.get('password') and attrs.get('password_confirm'):
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError("Las contraseñas no coinciden")
            validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        user = Usuario.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('password_confirm', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance

class UsuarioListSerializer(serializers.ModelSerializer):
    """Serializer para listar usuarios (sin información sensible)"""
    rol_nombre = serializers.CharField(source='get_rol_display_name', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'correo', 'cedula', 'rol', 'rol_nombre', 'es_activo', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']

class CompradorSerializer(serializers.ModelSerializer):
    """Serializer específico para compradores"""
    rol_nombre = serializers.CharField(source='get_rol_display_name', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'correo', 'cedula', 'rol_nombre', 'telefono']
        read_only_fields = ['id'] 