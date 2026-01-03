from rest_framework import serializers
from .models import Envio, Producto, Tarifa, ImportacionExcel
from apps.usuarios.serializers import CompradorSerializer

class ProductoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Producto"""
    categoria_nombre = serializers.CharField(source='get_categoria_display', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id', 'descripcion', 'peso', 'cantidad', 'valor', 'categoria', 
            'categoria_nombre', 'costo_envio', 'envio', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'costo_envio', 'fecha_creacion', 'fecha_actualizacion']

class ProductoListSerializer(serializers.ModelSerializer):
    """Serializer para listar productos (versión simplificada)"""
    categoria_nombre = serializers.CharField(source='get_categoria_display', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id', 'descripcion', 'peso', 'cantidad', 'valor', 'categoria_nombre', 'costo_envio'
        ]
        read_only_fields = ['id', 'costo_envio']

class ProductoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear productos anidados (sin campo envio)"""
    
    class Meta:
        model = Producto
        fields = [
            'descripcion', 'peso', 'cantidad', 'valor', 'categoria'
        ]

class EnvioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Envío"""
    comprador_info = CompradorSerializer(source='comprador', read_only=True)
    estado_nombre = serializers.CharField(source='get_estado_display', read_only=True)
    productos = ProductoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Envio
        fields = [
            'id', 'hawb', 'peso_total', 'cantidad_total', 'valor_total', 'costo_servicio',
            'fecha_emision', 'comprador', 'comprador_info', 'estado', 'estado_nombre',
            'observaciones', 'productos', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'costo_servicio', 'fecha_emision', 'fecha_creacion', 'fecha_actualizacion']
    
    def update(self, instance, validated_data):
        """Actualiza el envío incluyendo observaciones"""
        # Actualizar todos los campos permitidos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class EnvioListSerializer(serializers.ModelSerializer):
    """Serializer para listar envíos (versión simplificada)"""
    comprador_info = CompradorSerializer(source='comprador', read_only=True)
    estado_nombre = serializers.CharField(source='get_estado_display', read_only=True)
    cantidad_productos = serializers.SerializerMethodField()
    
    class Meta:
        model = Envio
        fields = [
            'id', 'hawb', 'peso_total', 'cantidad_total', 'valor_total', 'costo_servicio',
            'fecha_emision', 'comprador', 'comprador_info', 'estado', 'estado_nombre', 
            'cantidad_productos', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'costo_servicio', 'fecha_emision', 'fecha_creacion']
    
    def get_cantidad_productos(self, obj):
        return obj.productos.count()

class EnvioCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear envíos con productos"""
    productos = ProductoCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Envio
        fields = [
            'id', 'hawb', 'comprador', 'estado', 'observaciones', 'productos'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        productos_data = validated_data.pop('productos', [])
        
        # Establecer valores por defecto para totales
        validated_data['peso_total'] = 0
        validated_data['cantidad_total'] = 0
        validated_data['valor_total'] = 0
        validated_data['costo_servicio'] = 0
        
        # Crear el envío
        envio = Envio.objects.create(**validated_data)
        
        # Crear productos asociados
        for producto_data in productos_data:
            Producto.objects.create(envio=envio, **producto_data)
        
        # Recalcular totales basados en productos
        if productos_data:
            envio.calcular_totales()
        
        return envio

class TarifaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Tarifa"""
    categoria_nombre = serializers.CharField(source='get_categoria_display', read_only=True)
    
    class Meta:
        model = Tarifa
        fields = [
            'id', 'categoria', 'categoria_nombre', 'peso_minimo', 'peso_maximo',
            'precio_por_kg', 'cargo_base', 'activa', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

class ImportacionExcelSerializer(serializers.ModelSerializer):
    """Serializer para el modelo ImportacionExcel"""
    estado_nombre = serializers.CharField(source='get_estado_display', read_only=True)
    nombre_usuario = serializers.CharField(source='usuario.nombre', read_only=True)
    porcentaje_exito = serializers.SerializerMethodField()
    
    class Meta:
        model = ImportacionExcel
        fields = [
            'id', 'archivo', 'nombre_original', 'estado', 'estado_nombre',
            'usuario', 'nombre_usuario', 'total_registros', 'registros_validos',
            'registros_errores', 'registros_duplicados', 'registros_procesados',
            'errores_validacion', 'columnas_mapeadas', 'registros_seleccionados',
            'mensaje_resultado', 'fecha_creacion', 'fecha_actualizacion',
            'fecha_completado', 'porcentaje_exito'
        ]
        read_only_fields = [
            'id', 'usuario', 'estado', 'total_registros', 'registros_validos',
            'registros_errores', 'registros_duplicados', 'registros_procesados',
            'fecha_creacion', 'fecha_actualizacion', 'fecha_completado'
        ]
    
    def get_porcentaje_exito(self, obj):
        """Calcula el porcentaje de registros válidos"""
        if obj.total_registros > 0:
            return round((obj.registros_validos / obj.total_registros) * 100, 2)
        return 0

class ImportacionExcelCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear importaciones de Excel"""
    
    class Meta:
        model = ImportacionExcel
        fields = ['archivo', 'nombre_original']
    
    def validate_archivo(self, value):
        """Valida que el archivo sea Excel"""
        nombre_archivo = value.name.lower()
        if not (nombre_archivo.endswith('.xlsx') or nombre_archivo.endswith('.xls')):
            raise serializers.ValidationError(
                "El archivo debe ser formato Excel (.xlsx o .xls)"
            )
        return value

class PreviewExcelSerializer(serializers.Serializer):
    """Serializer para la vista previa de datos del Excel"""
    columnas = serializers.ListField(child=serializers.CharField())
    filas = serializers.ListField(child=serializers.DictField())
    total_filas = serializers.IntegerField()
    errores_detectados = serializers.ListField(child=serializers.DictField(), required=False)
    duplicados = serializers.ListField(child=serializers.IntegerField(), required=False)

class ProcesarExcelSerializer(serializers.Serializer):
    """Serializer para procesar datos del Excel"""
    importacion_id = serializers.IntegerField()
    columnas_mapeadas = serializers.DictField(
        child=serializers.CharField(),
        help_text="Mapeo entre columnas del Excel y campos del modelo"
    )
    registros_seleccionados = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Índices de registros a importar (vacío = todos)"
    ) 