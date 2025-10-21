from rest_framework import serializers
from django.contrib.auth import get_user_model
import re
from .validators import validar_cedula_ecuatoriana, validar_password_fuerte

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
            'telefono', 'fecha_nacimiento', 'direccion', 
            'provincia', 'canton', 'ciudad', 'latitud', 'longitud',
            'cupo_anual', 'es_activo', 'fecha_creacion', 'fecha_actualizacion', 
            'password', 'password_confirm'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
        extra_kwargs = {
            'nombre': {'allow_null': False, 'required': True},
            'correo': {'allow_null': False, 'required': True},
        }

    def validate(self, attrs):
        """Validaciones generales y de contraseña"""
        if attrs.get('password') and attrs.get('password_confirm'):
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError("Las contraseñas no coinciden")
            
            # Validaciones fuertes centralizadas
            validar_password_fuerte(attrs['password'])
        
        return attrs

    def validate_cedula(self, value):
        """Valida cédula ecuatoriana y unicidad"""
        if value:
            # Validar formato ecuatoriano centralizado
            try:
                validar_cedula_ecuatoriana(value)
            except Exception as e:
                raise serializers.ValidationError(str(e))
            
            # Validar unicidad al actualizar
            usuario_id = self.instance.id if self.instance else None
            
            if Usuario.objects.filter(cedula=value).exclude(id=usuario_id).exists():
                raise serializers.ValidationError("Esta cédula ya está registrada")
        
        return value

    def validate_correo(self, value):
        """Valida que el correo sea único al actualizar"""
        if value:
            # Si estamos actualizando, excluir el usuario actual
            usuario_id = self.instance.id if self.instance else None
            
            if Usuario.objects.filter(correo=value).exclude(id=usuario_id).exists():
                raise serializers.ValidationError("Este correo ya está registrado")
        
        return value

    def validate_telefono(self, value):
        """Valida formato de teléfono ecuatoriano"""
        if value:
            # Formatos válidos: 09XXXXXXXX, 0X-XXXXXXX, 0XXXXXXXXX
            patron = r'^0[2-9]\d{7,8}$'
            valor_limpio = value.replace('-', '').replace(' ', '')
            
            if not re.match(patron, valor_limpio):
                raise serializers.ValidationError(
                    "Formato de teléfono inválido. Use formato ecuatoriano (ej: 0999999999 o 02-3456789)"
                )
        return value

    def validate_username(self, value):
        """Valida formato de username"""
        # Solo letras, números, guiones bajos y puntos, mínimo 3 caracteres
        if not re.match(r'^[a-zA-Z0-9_.]{3,150}$', value):
            raise serializers.ValidationError(
                "El username debe tener entre 3-150 caracteres y solo puede contener letras, números, puntos y guiones bajos"
            )
        
        # No puede empezar ni terminar con punto o guión bajo
        if value[0] in '._' or value[-1] in '._':
            raise serializers.ValidationError(
                "El username no puede comenzar ni terminar con punto o guión bajo"
            )
        
        return value

    # Eliminado: la validación de cédula ahora vive en validators.py

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
    ubicacion_completa = serializers.CharField(source='get_ubicacion_completa', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'correo', 'cedula', 'rol', 'rol_nombre', 
                  'provincia', 'canton', 'ciudad', 'ubicacion_completa',
                  'latitud', 'longitud', 'cupo_anual', 'es_activo', 'fecha_creacion']
        read_only_fields = ['id', 'fecha_creacion']


class DashboardUsuarioSerializer(serializers.Serializer):
    """Serializer para el dashboard de usuario con estadísticas de envíos y cupo"""
    # Información del usuario
    usuario = UsuarioListSerializer(read_only=True)
    
    # Estadísticas de cupo
    cupo_anual = serializers.DecimalField(max_digits=10, decimal_places=2)
    peso_usado = serializers.DecimalField(max_digits=10, decimal_places=2)
    peso_disponible = serializers.DecimalField(max_digits=10, decimal_places=2)
    porcentaje_usado = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Estadísticas de envíos
    total_envios = serializers.IntegerField()
    envios_pendientes = serializers.IntegerField()
    envios_en_transito = serializers.IntegerField()
    envios_entregados = serializers.IntegerField()
    envios_cancelados = serializers.IntegerField()
    peso_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    valor_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    costo_servicio_total = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Información del año
    anio = serializers.IntegerField()

class CompradorSerializer(serializers.ModelSerializer):
    """Serializer específico para compradores"""
    rol_nombre = serializers.CharField(source='get_rol_display_name', read_only=True)
    ubicacion_completa = serializers.CharField(source='get_ubicacion_completa', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'correo', 'cedula', 'rol_nombre', 'telefono', 
                  'provincia', 'canton', 'ciudad', 'ubicacion_completa', 'latitud', 'longitud']
        read_only_fields = ['id']


class CompradorMapaSerializer(serializers.ModelSerializer):
    """Serializer específico para mapa de compradores con conteo de envíos"""
    rol_nombre = serializers.CharField(source='get_rol_display_name', read_only=True)
    ubicacion_completa = serializers.CharField(source='get_ubicacion_completa', read_only=True)
    total_envios = serializers.SerializerMethodField()
    envios_recientes = serializers.SerializerMethodField()
    latitud = serializers.SerializerMethodField()
    longitud = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre', 'correo', 'telefono', 
                  'provincia', 'canton', 'ciudad', 'ubicacion_completa',
                  'latitud', 'longitud', 'rol_nombre', 'total_envios', 'envios_recientes']
        read_only_fields = ['id']
    
    def get_latitud(self, obj):
        """Retorna latitud como float en lugar de Decimal"""
        return float(obj.latitud) if obj.latitud else None
    
    def get_longitud(self, obj):
        """Retorna longitud como float en lugar de Decimal"""
        return float(obj.longitud) if obj.longitud else None
    
    def get_total_envios(self, obj):
        """Retorna el total de envíos del comprador"""
        return obj.envio_set.count()
    
    def get_envios_recientes(self, obj):
        """Retorna los últimos 5 envíos del comprador"""
        envios = obj.envio_set.all()[:5]
        # Importación circular evitada usando serialización manual simple
        return [{
            'id': envio.id,
            'hawb': envio.hawb,
            'estado': envio.estado,
            'fecha_emision': envio.fecha_emision,
            'peso_total': float(envio.peso_total),
            'valor_total': float(envio.valor_total),
            'costo_servicio': float(envio.costo_servicio)
        } for envio in envios]