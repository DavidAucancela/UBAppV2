from rest_framework import serializers
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from .models import Envio, Producto, Tarifa, ImportacionExcel
from apps.usuarios.serializers import CompradorSerializer


class DecimalFieldNormalizado(serializers.DecimalField):
    """Campo DecimalField que normaliza valores antes de la validación"""
    
    def to_internal_value(self, data):
        """Normalizar el valor antes de la validación automática"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[DecimalFieldNormalizado] Recibido: {data} (tipo: {type(data)})")
        
        if data is None:
            return None
        
        # Normalizar el valor (convertir coma a punto, etc.)
        valor_str = self._normalizar_decimal_campo(data)
        logger.info(f"[DecimalFieldNormalizado] Después de normalizar: {valor_str}")
        
        try:
            # Convertir directamente a Decimal desde el string normalizado
            # Esto evita problemas de precisión de punto flotante
            if valor_str:
                # Si el string tiene más decimales de los necesarios, redondearlo
                valor_decimal = Decimal(valor_str).quantize(
                    Decimal('0.01'), 
                    rounding=ROUND_HALF_UP
                )
            else:
                valor_decimal = Decimal('0')
            
            logger.info(f"[DecimalFieldNormalizado] Decimal después de quantize: {valor_decimal}")
            
            # Convertir a string con exactamente 2 decimales para evitar problemas de precisión
            # Esto asegura que cuando DRF lo valide, tenga exactamente 2 decimales
            valor_str_normalizado = format(valor_decimal, '.2f')
            logger.info(f"[DecimalFieldNormalizado] String normalizado final: {valor_str_normalizado}")
            
            # Llamar al método padre con el string normalizado (DRF acepta strings para DecimalField)
            resultado = super().to_internal_value(valor_str_normalizado)
            logger.info(f"[DecimalFieldNormalizado] Resultado del padre: {resultado} (tipo: {type(resultado)})")
            return resultado
            
        except (ValueError, TypeError, InvalidOperation) as e:
            logger.error(f"[DecimalFieldNormalizado] Error en normalización: {str(e)}")
            # Si hay error, intentar con el valor original
            try:
                return super().to_internal_value(data)
            except Exception as e2:
                logger.error(f"[DecimalFieldNormalizado] Error también con valor original: {str(e2)}")
                # Si también falla, re-lanzar el error original
                raise serializers.ValidationError(f"Valor decimal inválido: {str(e)}")
    
    @staticmethod
    def _normalizar_decimal_campo(valor):
        """Normaliza valores decimales: convierte coma a punto"""
        if valor is None:
            return None
        if isinstance(valor, (int, float)):
            return str(valor)
        # Convertir a string y reemplazar coma por punto
        valor_str = str(valor).strip()
        # Si tiene coma y punto, asumir formato europeo (1.234,56 -> 1234.56)
        if '.' in valor_str and ',' in valor_str:
            # Eliminar puntos (separadores de miles) y convertir coma a punto
            valor_str = valor_str.replace('.', '').replace(',', '.')
        # Si solo tiene coma, convertir a punto
        elif ',' in valor_str:
            valor_str = valor_str.replace(',', '.')
        return valor_str

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
            'id', 'descripcion', 'peso', 'cantidad', 'valor', 'categoria', 'categoria_nombre', 'costo_envio'
        ]
        read_only_fields = ['id', 'costo_envio']

class ProductoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear productos anidados (sin campo envio)"""
    
    # Usar campos personalizados que normalizan antes de la validación
    peso = DecimalFieldNormalizado(max_digits=8, decimal_places=2, required=True)
    valor = DecimalFieldNormalizado(max_digits=10, decimal_places=2, required=True)
    
    def to_internal_value(self, data):
        """Normalizar valores decimales antes de la validación de campos"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[ProductoCreateSerializer] Recibido data: {data}")
        
        # Crear una copia mutable de data
        if isinstance(data, dict):
            data = dict(data)
        else:
            data = dict(data.items()) if hasattr(data, 'items') else data
        
        logger.info(f"[ProductoCreateSerializer] Data después de copiar: {data}")
        
        # Normalizar peso si existe
        if 'peso' in data and data['peso'] is not None:
            logger.info(f"[ProductoCreateSerializer] Normalizando peso: {data['peso']} (tipo: {type(data['peso'])})")
            try:
                peso_str = self._normalizar_decimal_serializer(data['peso'])
                logger.info(f"[ProductoCreateSerializer] Peso después de normalizar string: {peso_str}")
                if peso_str:
                    peso_decimal = Decimal(peso_str).quantize(
                        Decimal('0.01'), 
                        rounding=ROUND_HALF_UP
                    )
                    logger.info(f"[ProductoCreateSerializer] Peso Decimal: {peso_decimal}")
                    # Convertir a string con exactamente 2 decimales
                    data['peso'] = format(peso_decimal, '.2f')
                    logger.info(f"[ProductoCreateSerializer] Peso final normalizado: {data['peso']}")
            except (ValueError, TypeError, InvalidOperation) as e:
                logger.error(f"[ProductoCreateSerializer] Error normalizando peso: {str(e)}")
                pass  # Dejar que el campo maneje el error
        
        # Normalizar valor si existe
        if 'valor' in data and data['valor'] is not None:
            logger.info(f"[ProductoCreateSerializer] Normalizando valor: {data['valor']} (tipo: {type(data['valor'])})")
            try:
                valor_str = self._normalizar_decimal_serializer(data['valor'])
                logger.info(f"[ProductoCreateSerializer] Valor después de normalizar string: {valor_str}")
                if valor_str:
                    valor_decimal = Decimal(valor_str).quantize(
                        Decimal('0.01'), 
                        rounding=ROUND_HALF_UP
                    )
                    logger.info(f"[ProductoCreateSerializer] Valor Decimal: {valor_decimal}")
                    # Convertir a string con exactamente 2 decimales
                    data['valor'] = format(valor_decimal, '.2f')
                    logger.info(f"[ProductoCreateSerializer] Valor final normalizado: {data['valor']}")
            except (ValueError, TypeError, InvalidOperation) as e:
                logger.error(f"[ProductoCreateSerializer] Error normalizando valor: {str(e)}")
                pass  # Dejar que el campo maneje el error
        
        logger.info(f"[ProductoCreateSerializer] Data final antes de llamar al padre: {data}")
        
        # Llamar al método padre con los datos normalizados
        resultado = super().to_internal_value(data)
        logger.info(f"[ProductoCreateSerializer] Resultado del padre: {resultado}")
        return resultado
    
    @staticmethod
    def _normalizar_decimal_serializer(valor):
        """Normaliza valores decimales: convierte coma a punto"""
        if valor is None:
            return None
        if isinstance(valor, (int, float)):
            # Convertir float a string, pero primero redondear para evitar problemas de precisión
            if isinstance(valor, float):
                # Redondear a 2 decimales antes de convertir a string
                valor = round(valor, 2)
            return str(valor)
        # Convertir a string y reemplazar coma por punto
        valor_str = str(valor).strip()
        # Si tiene coma y punto, asumir formato europeo (1.234,56 -> 1234.56)
        if '.' in valor_str and ',' in valor_str:
            # Eliminar puntos (separadores de miles) y convertir coma a punto
            valor_str = valor_str.replace('.', '').replace(',', '.')
        # Si solo tiene coma, convertir a punto
        elif ',' in valor_str:
            valor_str = valor_str.replace(',', '.')
        return valor_str
    
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
    
    def to_internal_value(self, data):
        """Normalizar valores decimales de productos antes de la validación"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[EnvioCreateSerializer] Recibido data completo: {data}")
        
        # Crear una copia mutable de data
        if isinstance(data, dict):
            data = dict(data)
        else:
            data = dict(data.items()) if hasattr(data, 'items') else data
        
        # Normalizar productos si existen
        if 'productos' in data and data['productos']:
            logger.info(f"[EnvioCreateSerializer] Productos encontrados: {data['productos']}")
            productos_normalizados = []
            for idx, producto in enumerate(data['productos']):
                logger.info(f"[EnvioCreateSerializer] Procesando producto {idx}: {producto}")
                producto_normalizado = dict(producto) if isinstance(producto, dict) else producto
                
                # Normalizar peso
                if 'peso' in producto_normalizado and producto_normalizado['peso'] is not None:
                    logger.info(f"[EnvioCreateSerializer] Producto {idx} - Peso original: {producto_normalizado['peso']} (tipo: {type(producto_normalizado['peso'])})")
                    try:
                        peso_str = self._normalizar_decimal(producto_normalizado['peso'])
                        logger.info(f"[EnvioCreateSerializer] Producto {idx} - Peso string normalizado: {peso_str}")
                        if peso_str:
                            peso_decimal = Decimal(str(peso_str)).quantize(
                                Decimal('0.01'), 
                                rounding=ROUND_HALF_UP
                            )
                            logger.info(f"[EnvioCreateSerializer] Producto {idx} - Peso Decimal: {peso_decimal}")
                            producto_normalizado['peso'] = format(peso_decimal, '.2f')
                            logger.info(f"[EnvioCreateSerializer] Producto {idx} - Peso final: {producto_normalizado['peso']}")
                    except (ValueError, TypeError, InvalidOperation) as e:
                        logger.error(f"[EnvioCreateSerializer] Producto {idx} - Error normalizando peso: {str(e)}")
                        pass
                
                # Normalizar valor
                if 'valor' in producto_normalizado and producto_normalizado['valor'] is not None:
                    logger.info(f"[EnvioCreateSerializer] Producto {idx} - Valor original: {producto_normalizado['valor']} (tipo: {type(producto_normalizado['valor'])})")
                    try:
                        valor_str = self._normalizar_decimal(producto_normalizado['valor'])
                        logger.info(f"[EnvioCreateSerializer] Producto {idx} - Valor string normalizado: {valor_str}")
                        if valor_str:
                            valor_decimal = Decimal(str(valor_str)).quantize(
                                Decimal('0.01'), 
                                rounding=ROUND_HALF_UP
                            )
                            logger.info(f"[EnvioCreateSerializer] Producto {idx} - Valor Decimal: {valor_decimal}")
                            producto_normalizado['valor'] = format(valor_decimal, '.2f')
                            logger.info(f"[EnvioCreateSerializer] Producto {idx} - Valor final: {producto_normalizado['valor']}")
                    except (ValueError, TypeError, InvalidOperation) as e:
                        logger.error(f"[EnvioCreateSerializer] Producto {idx} - Error normalizando valor: {str(e)}")
                        pass
                
                productos_normalizados.append(producto_normalizado)
                logger.info(f"[EnvioCreateSerializer] Producto {idx} normalizado: {producto_normalizado}")
            
            data['productos'] = productos_normalizados
            logger.info(f"[EnvioCreateSerializer] Productos normalizados finales: {data['productos']}")
        
        # Llamar al método padre
        logger.info(f"[EnvioCreateSerializer] Llamando al método padre con data: {data}")
        resultado = super().to_internal_value(data)
        logger.info(f"[EnvioCreateSerializer] Resultado del padre: {resultado}")
        return resultado
    
    class Meta:
        model = Envio
        fields = [
            'id', 'hawb', 'comprador', 'estado', 'observaciones', 'productos'
        ]
        read_only_fields = ['id']
    
    @staticmethod
    def _normalizar_decimal(valor):
        """Normaliza valores decimales: convierte coma a punto y redondea floats"""
        if valor is None:
            return None
        if isinstance(valor, float):
            # Redondear float a 2 decimales antes de convertir a string para evitar problemas de precisión
            valor_redondeado = round(valor, 2)
            return str(valor_redondeado)
        if isinstance(valor, int):
            return str(valor)
        # Convertir a string y reemplazar coma por punto
        valor_str = str(valor).strip()
        # Si tiene coma y punto, asumir formato europeo (1.234,56 -> 1234.56)
        if '.' in valor_str and ',' in valor_str:
            # Eliminar puntos (separadores de miles) y convertir coma a punto
            valor_str = valor_str.replace('.', '').replace(',', '.')
        # Si solo tiene coma, convertir a punto
        elif ',' in valor_str:
            valor_str = valor_str.replace(',', '.')
        return valor_str
    
    def validate_productos(self, value):
        """Validar productos si se proporcionan"""
        # Los productos son opcionales en el serializer, pero si se proporcionan deben ser válidos
        if value:
            if len(value) == 0:
                raise serializers.ValidationError("Si se proporcionan productos, debe haber al menos uno")
            
            # Validar cada producto
            for producto in value:
                if not producto.get('descripcion') or not producto.get('descripcion').strip():
                    raise serializers.ValidationError("Cada producto debe tener una descripción")
                if not producto.get('categoria'):
                    raise serializers.ValidationError("Cada producto debe tener una categoría")
                
                # Normalizar peso (aceptar coma o punto como separador decimal)
                peso_str = self._normalizar_decimal(producto.get('peso', 0))
                try:
                    peso_float = float(peso_str) if peso_str else 0
                    # Convertir a Decimal y redondear a exactamente 2 decimales para evitar problemas de precisión
                    peso_decimal = Decimal(str(peso_float)).quantize(
                        Decimal('0.01'), 
                        rounding=ROUND_HALF_UP
                    )
                    # Validar que no exceda max_digits=8 (6 enteros + 2 decimales)
                    # Contar solo los dígitos significativos (sin el punto decimal)
                    digitos = [d for d in peso_decimal.as_tuple().digits if d is not None]
                    if len(digitos) > 8:
                        raise serializers.ValidationError("El peso no puede tener más de 8 dígitos en total (6 enteros + 2 decimales)")
                    # Convertir de vuelta a float para el serializer (DRF espera float)
                    peso = float(peso_decimal)
                except (ValueError, TypeError) as e:
                    raise serializers.ValidationError(f"El peso debe ser un número válido: {str(e)}")
                except Exception as e:
                    raise serializers.ValidationError(f"Error al procesar el peso: {str(e)}")
                if peso <= 0:
                    raise serializers.ValidationError("Cada producto debe tener un peso mayor a 0")
                producto['peso'] = peso
                
                cantidad = int(producto.get('cantidad', 0))
                if cantidad <= 0:
                    raise serializers.ValidationError("Cada producto debe tener una cantidad mayor a 0")
                
                # Normalizar valor (aceptar coma o punto como separador decimal)
                valor_str = self._normalizar_decimal(producto.get('valor', -1))
                try:
                    valor_float = float(valor_str) if valor_str else -1
                    # Convertir a Decimal y redondear a exactamente 2 decimales para evitar problemas de precisión
                    valor_decimal = Decimal(str(valor_float)).quantize(
                        Decimal('0.01'), 
                        rounding=ROUND_HALF_UP
                    )
                    # Validar que no exceda max_digits=10 (8 enteros + 2 decimales)
                    # Contar solo los dígitos significativos (sin el punto decimal)
                    digitos = [d for d in valor_decimal.as_tuple().digits if d is not None]
                    if len(digitos) > 10:
                        raise serializers.ValidationError("El valor no puede tener más de 10 dígitos en total (8 enteros + 2 decimales)")
                    # Convertir de vuelta a float para el serializer (DRF espera float)
                    valor = float(valor_decimal)
                except (ValueError, TypeError) as e:
                    raise serializers.ValidationError(f"El valor debe ser un número válido: {str(e)}")
                except Exception as e:
                    raise serializers.ValidationError(f"Error al procesar el valor: {str(e)}")
                if valor < 0:
                    raise serializers.ValidationError("Cada producto debe tener un valor válido (>= 0)")
                producto['valor'] = valor
        
        return value
    
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
            # Asegurar que peso y valor sean Decimal con exactamente 2 decimales
            if 'peso' in producto_data:
                producto_data['peso'] = Decimal(str(producto_data['peso'])).quantize(
                    Decimal('0.01'), 
                    rounding=ROUND_HALF_UP
                )
            if 'valor' in producto_data:
                producto_data['valor'] = Decimal(str(producto_data['valor'])).quantize(
                    Decimal('0.01'), 
                    rounding=ROUND_HALF_UP
                )
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