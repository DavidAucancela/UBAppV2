from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import re

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
        """Validaciones generales y de contraseña"""
        if attrs.get('password') and attrs.get('password_confirm'):
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError("Las contraseñas no coinciden")
            
            # Validaciones personalizadas de contraseña
            password = attrs['password']
            
            # Mínimo 8 caracteres
            if len(password) < 8:
                raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres")
            
            # Al menos una mayúscula
            if not any(c.isupper() for c in password):
                raise serializers.ValidationError("La contraseña debe contener al menos una letra mayúscula")
            
            # Al menos una minúscula
            if not any(c.islower() for c in password):
                raise serializers.ValidationError("La contraseña debe contener al menos una letra minúscula")
            
            # Al menos un número
            if not any(c.isdigit() for c in password):
                raise serializers.ValidationError("La contraseña debe contener al menos un número")
            
            # Al menos un carácter especial
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise serializers.ValidationError("La contraseña debe contener al menos un carácter especial (!@#$%^&*...)")
            
            # Validación de Django por defecto
            validate_password(attrs['password'])
        
        return attrs

    def validate_cedula(self, value):
        """Valida cédula ecuatoriana y unicidad"""
        if value:
            # Validar formato ecuatoriano
            if not self.validar_cedula_ecuatoriana(value):
                raise serializers.ValidationError("La cédula no es válida")
            
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

    @staticmethod
    def validar_cedula_ecuatoriana(cedula):
        """Valida cédula ecuatoriana usando algoritmo módulo 10"""
        if not cedula or len(cedula) != 10:
            return False
        
        if not cedula.isdigit():
            return False
        
        provincia = int(cedula[0:2])
        if provincia < 1 or provincia > 24:
            return False
        
        if int(cedula[2]) >= 6:
            return False
        
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0
        
        for i in range(9):
            valor = int(cedula[i]) * coeficientes[i]
            if valor >= 10:
                valor -= 9
            suma += valor
        
        resultado = suma % 10
        verificador = 0 if resultado == 0 else 10 - resultado
        
        return verificador == int(cedula[9])

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