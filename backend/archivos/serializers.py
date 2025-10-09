from rest_framework import serializers
from .models import Envio, Producto
from usuarios.serializers import CompradorSerializer

class ProductoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Producto"""
    categoria_nombre = serializers.CharField(source='get_categoria_display', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id', 'descripcion', 'peso', 'cantidad', 'valor', 'categoria', 
            'categoria_nombre', 'envio', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer para listar productos (versión simplificada)"""
    categoria_nombre = serializers.CharField(source='get_categoria_display', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id', 'descripcion', 'peso', 'cantidad', 'valor', 'categoria_nombre'
        ]
        read_only_fields = ['id']

class EnvioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Envío"""
    comprador_info = CompradorSerializer(source='comprador', read_only=True)
    estado_nombre = serializers.CharField(source='get_estado_display', read_only=True)
    productos = ProductoSerializer(many=True, read_only=True)
    archivado = serializers.BooleanField(read_only=True)
    marcado = serializers.BooleanField(read_only=True)
    fecha_archivo = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Envio
        fields = [
            'id', 'hawb', 'peso_total', 'cantidad_total', 'valor_total',
            'fecha_emision', 'comprador', 'comprador_info', 'estado', 'estado_nombre',
            'observaciones', 'marcado', 'archivado', 'fecha_archivo',
            'productos', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_emision', 'fecha_creacion', 'fecha_actualizacion']

class EnvioListSerializer(serializers.ModelSerializer):
    """Serializer para listar envíos (versión simplificada)"""
    comprador_nombre = serializers.CharField(source='comprador.nombre', read_only=True)
    estado_nombre = serializers.CharField(source='get_estado_display', read_only=True)
    cantidad_productos = serializers.SerializerMethodField()
    
    class Meta:
        model = Envio
        fields = [
            'id', 'hawb', 'peso_total', 'cantidad_total', 'valor_total',
            'fecha_emision', 'comprador_nombre', 'estado_nombre', 'cantidad_productos'
        ]
        read_only_fields = ['id', 'fecha_emision']
    
    def get_cantidad_productos(self, obj):
        return obj.productos.count()

class EnvioCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear envíos con productos"""
    productos = ProductoSerializer(many=True, required=False)
    
    class Meta:
        model = Envio
        fields = [
            'hawb', 'comprador', 'estado', 'observaciones', 'productos'
        ]
    
    def create(self, validated_data):
        productos_data = validated_data.pop('productos', [])
        envio = Envio.objects.create(**validated_data)
        
        for producto_data in productos_data:
            Producto.objects.create(envio=envio, **producto_data)
        
        return envio 