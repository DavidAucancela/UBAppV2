"""
Comando de gestión para verificar el proceso de generar_texto_envio.

Este script permite verificar cómo se genera el texto descriptivo de un envío
para la indexación semántica, mostrando toda la información relevante y
comparándola con el texto guardado en los embeddings existentes.

Uso:
    python manage.py verificar_texto_envio [--hawb HAWB] [--todos] [--limite N] [--interactivo]
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from datetime import datetime
from apps.archivos.models import Envio, Producto
from apps.busqueda.semantic.text_processor import TextProcessor
from apps.busqueda.models import EnvioEmbedding
from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Verifica el proceso de generar_texto_envio para obtener la descripción del envío'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hawb',
            type=str,
            help='Código HAWB del envío específico a verificar'
        )
        parser.add_argument(
            '--todos',
            action='store_true',
            help='Verificar todos los envíos (limitado por --limite)'
        )
        parser.add_argument(
            '--limite',
            type=int,
            default=5,
            help='Límite de envíos a verificar cuando se usa --todos (default: 5)'
        )
        parser.add_argument(
            '--comparar',
            action='store_true',
            help='Comparar texto generado con texto guardado en embeddings'
        )
        parser.add_argument(
            '--detallado',
            action='store_true',
            help='Mostrar información detallada de cada parte del texto'
        )
        parser.add_argument(
            '--interactivo',
            action='store_true',
            help='Solicitar información del envío de forma interactiva para generar su texto descriptivo'
        )

    def handle(self, *args, **options):
        hawb = options.get('hawb')
        todos = options.get('todos', False)
        limite = options.get('limite', 5)
        comparar = options.get('comparar', False)
        detallado = options.get('detallado', False)
        interactivo = options.get('interactivo', False)
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*80}'))
        self.stdout.write(self.style.SUCCESS('VERIFICACIÓN DE generar_texto_envio'))
        self.stdout.write(self.style.SUCCESS(f'{"="*80}\n'))
        
        # Modo interactivo: solicitar información del envío
        if interactivo:
            envio = self._solicitar_envio_interactivo()
            if envio:
                self._verificar_envio(envio, comparar, detallado)
            return
        
        # Obtener envíos a verificar
        if hawb:
            try:
                envios = [Envio.objects.get(hawb=hawb)]
            except Envio.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ No se encontró envío con HAWB: {hawb}')
                )
                return
        elif todos:
            envios = Envio.objects.all()[:limite]
            if not envios.exists():
                self.stdout.write(
                    self.style.ERROR('❌ No hay envíos en la base de datos')
                )
                return
            self.stdout.write(f'Verificando {envios.count()} envío(s)...\n')
        else:
            # Por defecto, mostrar el primero
            envio = Envio.objects.first()
            if not envio:
                self.stdout.write(
                    self.style.ERROR('❌ No hay envíos en la base de datos')
                )
                return
            envios = [envio]
        
        # Verificar cada envío
        for idx, envio in enumerate(envios, 1):
            if len(envios) > 1:
                self.stdout.write(self.style.SUCCESS(f'\n{"="*80}'))
                self.stdout.write(self.style.SUCCESS(f'ENVÍO {idx} de {len(envios)}'))
                self.stdout.write(self.style.SUCCESS(f'{"="*80}\n'))
            
            self._verificar_envio(envio, comparar, detallado)
    
    def _verificar_envio(self, envio, comparar, detallado):
        """Verifica un envío individual"""
        
        # Información básica del envío
        self.stdout.write(self.style.SUCCESS(f'\n📦 INFORMACIÓN DEL ENVÍO'))
        self.stdout.write('-' * 80)
        self.stdout.write(f'   HAWB: {envio.hawb}')
        self.stdout.write(f'   Estado: {envio.get_estado_display()}')
        self.stdout.write(f'   Comprador: {envio.comprador.nombre}')
        
        # Información de ubicación
        ubicacion_parts = []
        if envio.comprador.ciudad:
            ubicacion_parts.append(f'Ciudad: {envio.comprador.ciudad}')
        if envio.comprador.provincia:
            ubicacion_parts.append(f'Provincia: {envio.comprador.provincia}')
        if envio.comprador.canton:
            ubicacion_parts.append(f'Cantón: {envio.comprador.canton}')
        
        if ubicacion_parts:
            self.stdout.write(f'   Ubicación: {" | ".join(ubicacion_parts)}')
        else:
            self.stdout.write('   Ubicación: No especificada')
        
        # Información numérica
        self.stdout.write(f'   Peso Total: {envio.peso_total} kg')
        self.stdout.write(f'   Valor Total: ${envio.valor_total}')
        self.stdout.write(f'   Costo Servicio: ${envio.costo_servicio}')
        self.stdout.write(f'   Fecha Emisión: {envio.fecha_emision.strftime("%Y-%m-%d %H:%M")}')
        self.stdout.write(f'   Cantidad Total Productos: {envio.cantidad_total}')
        
        # Productos - Manejar tanto objetos reales como mock
        if hasattr(envio.productos, 'all'):
            productos = envio.productos.all()
        else:
            productos = envio.productos
        
        # Obtener el conteo de productos de forma segura
        # Verificar si tiene método count() que no requiera argumentos (QuerySet o Mock)
        try:
            if hasattr(productos, 'count') and callable(getattr(productos, 'count')):
                # Verificar si es el método count() de QuerySet (sin argumentos) o de lista (con argumentos)
                import inspect
                try:
                    sig = inspect.signature(productos.count)
                    # Si count() no requiere argumentos, es QuerySet o Mock
                    if len(sig.parameters) == 0:
                        num_productos = productos.count()
                    else:
                        # Es el count() de lista, usar len() en su lugar
                        num_productos = len(productos) if hasattr(productos, '__len__') else 0
                except (ValueError, TypeError):
                    # Si no se puede inspeccionar, intentar llamar count() y capturar error
                    try:
                        num_productos = productos.count()
                    except TypeError:
                        # count() requiere argumentos (es lista), usar len()
                        num_productos = len(productos) if hasattr(productos, '__len__') else 0
            elif hasattr(productos, '__len__'):
                num_productos = len(productos)
            else:
                num_productos = 0
        except Exception:
            # Si todo falla, usar len() como respaldo
            num_productos = len(productos) if hasattr(productos, '__len__') else 0
        
        self.stdout.write(f'\n📦 PRODUCTOS ({num_productos}):')
        self.stdout.write('-' * 80)
        
        # Verificar si hay productos
        if hasattr(productos, 'exists'):
            tiene_productos = productos.exists()
        else:
            tiene_productos = num_productos > 0
        
        if tiene_productos:
            for producto in productos:
                self.stdout.write(
                    f'   • {producto.descripcion} '
                    f'[{producto.get_categoria_display()}] - '
                    f'{producto.peso}kg x{producto.cantidad} = '
                    f'${producto.valor}'
                )
        else:
            self.stdout.write('   ⚠️  No hay productos asociados')
        
        # Observaciones
        if envio.observaciones:
            self.stdout.write(f'\n📝 OBSERVACIONES:')
            self.stdout.write('-' * 80)
            self.stdout.write(f'   {envio.observaciones}')
        
        # Generar texto
        self.stdout.write(f'\n📝 TEXTO GENERADO POR generar_texto_envio:')
        self.stdout.write('-' * 80)
        texto_generado = TextProcessor.generar_texto_envio(envio)
        
        # Mostrar texto completo en una línea
        self.stdout.write('Texto completo (una línea):')
        self.stdout.write(texto_generado)
        self.stdout.write('-' * 80)
        
        # Mostrar texto formateado por partes
        # Nota: El separador " | " se elimina durante la normalización, 
        # así que dividimos por patrones comunes que identifican el inicio de cada parte
        self.stdout.write('\n📋 TEXTO FORMATEADO (por partes):')
        self.stdout.write('-' * 80)
        
        # Dividir por patrones que identifican el inicio de cada parte
        # Ordenados por especificidad (más específicos primero)
        patrones = [
            'envi ',  # "envió" normalizado
            'estado del envo ',  # Más específico que solo "estado"
            'estado ',
            'cdigo hawb ',
            'comprador ',
            'ciudad destino ',
            'ubicacin ',
            'provincia ',
            'cantn ',
            'fecha de emisin ',
            'fecha ',
            'peso total ',
            'peso ',
            'valor total ',
            'valor ',
            'costo del servicio ',
            'productos incluidos ',
            'contiene ',
            'productos con detalles ',
            'producto ',
            'categoras de productos ',
            'tipos de productos ',
            'cantidad total de productos ',
            'total de artculos ',
            'peso total productos ',
            'valor total productos ',
            'observaciones ',
            'envo '  # "envío" al final del resumen
        ]
        
        # Dividir el texto por estos patrones
        partes = []
        texto_restante = texto_generado
        ultimo_indice = 0
        
        for patron in patrones:
            if patron in texto_restante:
                idx = texto_restante.find(patron, ultimo_indice)
                if idx >= ultimo_indice:
                    # Si hay texto antes del patrón, agregarlo como parte anterior
                    if idx > ultimo_indice:
                        parte_anterior = texto_restante[ultimo_indice:idx].strip()
                        if parte_anterior:
                            partes.append(parte_anterior)
                    # El patrón marca el inicio de una nueva parte
                    ultimo_indice = idx
        
        # Agregar el texto restante como última parte
        if ultimo_indice < len(texto_restante):
            parte_final = texto_restante[ultimo_indice:].strip()
            if parte_final:
                partes.append(parte_final)
        
        # Si no se pudo dividir, mostrar como una sola parte
        if not partes:
            partes = [texto_generado]
        
        for i, parte in enumerate(partes, 1):
            # Mostrar toda la información de la parte sin truncar
            self.stdout.write(f'{i:2d}. {parte}')
        self.stdout.write('-' * 80)
        
        # Análisis del texto (partes ya calculadas arriba)
        self.stdout.write(f'\n📊 ANÁLISIS DEL TEXTO:')
        self.stdout.write('-' * 80)
        self.stdout.write(f'   Longitud total: {len(texto_generado)} caracteres')
        self.stdout.write(f'   Número de partes detectadas: {len(partes)}')
        if partes and len(partes) > 1:
            self.stdout.write(f'   Promedio por parte: {len(texto_generado) // len(partes)} caracteres')
            longitudes = [len(p) for p in partes]
            self.stdout.write(f'   Parte más corta: {min(longitudes)} caracteres')
            self.stdout.write(f'   Parte más larga: {max(longitudes)} caracteres')
        else:
            self.stdout.write('   ⚠️  Nota: El separador " | " se eliminó durante la normalización del texto')
            self.stdout.write('   El texto está normalizado (minúsculas, sin acentos, sin caracteres especiales)')
        
        # Verificación de campos
        # Normalizar valores antes de buscar (el texto generado está normalizado)
        self.stdout.write(f'\n✅ VERIFICACIÓN DE CAMPOS:')
        self.stdout.write('-' * 80)
        
        # Función auxiliar para normalizar valores de búsqueda
        def normalizar_para_busqueda(valor):
            """Normaliza un valor para buscarlo en el texto normalizado"""
            if valor is None:
                return ""
            return TextProcessor.procesar_texto(str(valor))
        
        hawb_normalizado = normalizar_para_busqueda(envio.hawb)
        estado_normalizado = normalizar_para_busqueda(envio.get_estado_display())
        comprador_normalizado = normalizar_para_busqueda(envio.comprador.nombre)
        
        verificaciones = {
            'HAWB': hawb_normalizado in texto_generado if hawb_normalizado else False,
            'Estado': estado_normalizado in texto_generado if estado_normalizado else False,
            'Comprador': comprador_normalizado in texto_generado if comprador_normalizado else False,
            'Peso Total': normalizar_para_busqueda(envio.peso_total) in texto_generado,
            'Valor Total': normalizar_para_busqueda(envio.valor_total) in texto_generado,
            'Costo Servicio': normalizar_para_busqueda(envio.costo_servicio) in texto_generado,
            'Cantidad Productos': normalizar_para_busqueda(envio.cantidad_total) in texto_generado,
        }
        
        if envio.comprador.ciudad:
            verificaciones['Ciudad'] = normalizar_para_busqueda(envio.comprador.ciudad) in texto_generado
        if envio.comprador.provincia:
            verificaciones['Provincia'] = normalizar_para_busqueda(envio.comprador.provincia) in texto_generado
        if envio.observaciones:
            verificaciones['Observaciones'] = normalizar_para_busqueda(envio.observaciones) in texto_generado
        
        for campo, presente in verificaciones.items():
            estado = self.style.SUCCESS('✅') if presente else self.style.ERROR('❌')
            self.stdout.write(f'   {estado} {campo}: {"Presente" if presente else "FALTA"}')
        
        # Verificación de productos
        if tiene_productos:
            self.stdout.write(f'\n📦 VERIFICACIÓN DE PRODUCTOS:')
            self.stdout.write('-' * 80)
            productos_presentes = 0
            
            # Función auxiliar para normalizar valores de búsqueda
            def normalizar_para_busqueda(valor):
                """Normaliza un valor para buscarlo en el texto normalizado"""
                if valor is None:
                    return ""
                return TextProcessor.procesar_texto(str(valor))
            
            for producto in productos:
                descripcion_normalizada = normalizar_para_busqueda(producto.descripcion)
                categoria_normalizada = normalizar_para_busqueda(producto.get_categoria_display())
                
                presente = descripcion_normalizada in texto_generado if descripcion_normalizada else False
                categoria_presente = categoria_normalizada in texto_generado if categoria_normalizada else False
                
                estado = self.style.SUCCESS('✅') if presente else self.style.WARNING('⚠️')
                estado_cat = self.style.SUCCESS('✅') if categoria_presente else self.style.WARNING('⚠️')
                
                if presente:
                    productos_presentes += 1
                
                self.stdout.write(
                    f'   {estado} Descripción "{producto.descripcion[:40]}..." '
                    f'| {estado_cat} Categoría'
                )
            
            porcentaje = (productos_presentes / num_productos * 100) if num_productos > 0 else 0
            self.stdout.write(
                f'\n   Resumen: {productos_presentes}/{num_productos} productos presentes '
                f'({porcentaje:.1f}%)'
            )
        
        # Mostrar partes detalladas si se solicita
        if detallado:
            self.stdout.write(f'\n🔎 PARTES DETALLADAS DEL TEXTO:')
            self.stdout.write('-' * 80)
            for i, parte in enumerate(partes, 1):
                self.stdout.write(f'   {i:2d}. [{len(parte):3d} chars] {parte}')
        
        # Comparar con embedding guardado si existe
        if comparar:
            self.stdout.write(f'\n💾 COMPARACIÓN CON EMBEDDING GUARDADO:')
            self.stdout.write('-' * 80)
            try:
                # Solo comparar si es un envío real (no mock)
                if hasattr(envio, 'id') and envio.id:
                    embeddings = EnvioEmbedding.objects.filter(envio=envio)
                    if embeddings.exists():
                        for embedding in embeddings:
                            texto_guardado = embedding.texto_indexado
                            modelo = embedding.modelo_usado
                            
                            self.stdout.write(f'\n   Modelo: {modelo}')
                            self.stdout.write(f'   Longitud guardada: {len(texto_guardado)} caracteres')
                            self.stdout.write(f'   Longitud generada: {len(texto_generado)} caracteres')
                            
                            if texto_guardado == texto_generado:
                                self.stdout.write(self.style.SUCCESS('   ✅ Los textos son IDÉNTICOS'))
                            else:
                                self.stdout.write(self.style.WARNING('   ⚠️  Los textos son DIFERENTES'))
                                
                                # Mostrar diferencias
                                if detallado:
                                    self.stdout.write('\n   Diferencias encontradas:')
                                    partes_guardadas = texto_guardado.split(' | ')
                                    partes_generadas = texto_generado.split(' | ')
                                    
                                    # Partes que están en guardado pero no en generado
                                    faltantes = set(partes_guardadas) - set(partes_generadas)
                                    if faltantes:
                                        self.stdout.write('   • Partes en guardado pero no en generado:')
                                        for parte in list(faltantes)[:5]:
                                            self.stdout.write(f'     - {parte[:60]}...')
                                    
                                    # Partes que están en generado pero no en guardado
                                    nuevas = set(partes_generadas) - set(partes_guardadas)
                                    if nuevas:
                                        self.stdout.write('   • Partes en generado pero no en guardado:')
                                        for parte in list(nuevas)[:5]:
                                            self.stdout.write(f'     - {parte[:60]}...')
                    else:
                        self.stdout.write('   ⚠️  No hay embedding guardado para este envío')
                else:
                    self.stdout.write('   ℹ️  No se puede comparar con embeddings (envío mock)')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'   ❌ Error al comparar: {str(e)}')
                )
        
        self.stdout.write('\n')
    
    def _solicitar_envio_interactivo(self):
        """
        Solicita información del envío de forma interactiva y crea un objeto mock
        para generar el texto descriptivo completo.
        """
        self.stdout.write(self.style.SUCCESS('\n📝 MODO INTERACTIVO'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('Ingrese la información del envío para generar su texto descriptivo completo\n')
        
        try:
            # Información básica del envío
            hawb = input('HAWB (código del envío): ').strip()
            if not hawb:
                self.stdout.write(self.style.ERROR('❌ HAWB es requerido'))
                return None
            
            estado_input = input('Estado [pendiente/en_transito/entregado/cancelado] (default: pendiente): ').strip().lower()
            estados_validos = ['pendiente', 'en_transito', 'entregado', 'cancelado']
            estado = estado_input if estado_input in estados_validos else 'pendiente'
            
            # Información del comprador
            self.stdout.write('\n--- INFORMACIÓN DEL COMPRADOR ---')
            nombre_comprador = input('Nombre del comprador: ').strip()
            if not nombre_comprador:
                self.stdout.write(self.style.ERROR('❌ Nombre del comprador es requerido'))
                return None
            
            ciudad = input('Ciudad (opcional): ').strip() or None
            provincia = input('Provincia (opcional): ').strip() or None
            canton = input('Cantón (opcional): ').strip() or None
            
            # Información numérica del envío
            self.stdout.write('\n--- INFORMACIÓN NUMÉRICA DEL ENVÍO ---')
            try:
                peso_total = Decimal(input('Peso total (kg): ').strip() or '0')
                valor_total = Decimal(input('Valor total ($): ').strip() or '0')
                costo_servicio = Decimal(input('Costo del servicio ($) (opcional, default: 0): ').strip() or '0')
                cantidad_total = int(input('Cantidad total de productos: ').strip() or '0')
            except (ValueError, InvalidOperation) as e:
                self.stdout.write(self.style.ERROR(f'❌ Error en valores numéricos: {str(e)}'))
                return None
            
            # Fecha de emisión
            fecha_input = input('Fecha de emisión (YYYY-MM-DD) (opcional, default: hoy): ').strip()
            if fecha_input:
                try:
                    fecha_emision = datetime.strptime(fecha_input, '%Y-%m-%d')
                    fecha_emision = timezone.make_aware(fecha_emision)
                except ValueError:
                    self.stdout.write(self.style.WARNING('⚠️  Formato de fecha inválido, usando fecha actual'))
                    fecha_emision = timezone.now()
            else:
                fecha_emision = timezone.now()
            
            # Observaciones
            observaciones = input('Observaciones (opcional): ').strip() or None
            
            # Productos
            productos_data = []
            self.stdout.write('\n--- PRODUCTOS ---')
            agregar_productos = input('¿Desea agregar productos? (s/n): ').strip().lower() == 's'
            
            if agregar_productos:
                categorias_validas = ['electronica', 'ropa', 'hogar', 'deportes', 'otros']
                while True:
                    self.stdout.write(f'\nProducto {len(productos_data) + 1}:')
                    descripcion = input('  Descripción: ').strip()
                    if not descripcion:
                        break
                    
                    try:
                        peso = Decimal(input('  Peso (kg): ').strip() or '0')
                        cantidad = int(input('  Cantidad: ').strip() or '1')
                        valor = Decimal(input('  Valor ($): ').strip() or '0')
                        
                        categoria_input = input('  Categoría [electronica/ropa/hogar/deportes/otros] (default: otros): ').strip().lower()
                        categoria = categoria_input if categoria_input in categorias_validas else 'otros'
                        
                        productos_data.append({
                            'descripcion': descripcion,
                            'peso': peso,
                            'cantidad': cantidad,
                            'valor': valor,
                            'categoria': categoria
                        })
                        
                        continuar = input('  ¿Agregar otro producto? (s/n): ').strip().lower()
                        if continuar != 's':
                            break
                    except (ValueError, InvalidOperation) as e:
                        self.stdout.write(self.style.ERROR(f'  ❌ Error en valores del producto: {str(e)}'))
                        continue
            
            # Crear objeto mock del comprador
            class MockComprador:
                def __init__(self, nombre, ciudad, provincia, canton):
                    self.nombre = nombre
                    self.ciudad = ciudad
                    self.provincia = provincia
                    self.canton = canton
            
            comprador_mock = MockComprador(nombre_comprador, ciudad, provincia, canton)
            
            # Crear objeto mock del producto
            class MockProducto:
                def __init__(self, data):
                    self.descripcion = data['descripcion']
                    self.peso = data['peso']
                    self.cantidad = data['cantidad']
                    self.valor = data['valor']
                    self.categoria = data['categoria']
                
                def get_categoria_display(self):
                    categorias_display = {
                        'electronica': 'Electrónica',
                        'ropa': 'Ropa',
                        'hogar': 'Hogar',
                        'deportes': 'Deportes',
                        'otros': 'Otros'
                    }
                    return categorias_display.get(self.categoria, 'Otros')
            
            # Crear objeto mock del QuerySet de productos
            class MockProductosQuerySet:
                def __init__(self, productos_data):
                    self._productos_data = productos_data
                    self._productos = [MockProducto(p) for p in productos_data]
                
                def all(self):
                    # Devolver self para mantener la interfaz del QuerySet
                    return self
                
                def __iter__(self):
                    return iter(self._productos)
                
                def __len__(self):
                    return len(self._productos_data)
                
                def exists(self):
                    return len(self._productos_data) > 0
                
                def count(self):
                    return len(self._productos_data)
            
            # Crear objeto mock del envío
            class MockEnvio:
                def __init__(self, hawb, estado, comprador, peso_total, valor_total, 
                           costo_servicio, cantidad_total, fecha_emision, observaciones, productos_data):
                    self.hawb = hawb
                    self.estado = estado
                    self.comprador = comprador
                    self.peso_total = peso_total
                    self.valor_total = valor_total
                    self.costo_servicio = costo_servicio
                    self.cantidad_total = cantidad_total
                    self.fecha_emision = fecha_emision
                    self.observaciones = observaciones
                    self.productos = MockProductosQuerySet(productos_data)
                
                def get_estado_display(self):
                    estados_display = {
                        'pendiente': 'Pendiente',
                        'en_transito': 'En Tránsito',
                        'entregado': 'Entregado',
                        'cancelado': 'Cancelado'
                    }
                    return estados_display.get(self.estado, 'Pendiente')
            
            envio_mock = MockEnvio(
                hawb, estado, comprador_mock, peso_total, valor_total,
                costo_servicio, cantidad_total, fecha_emision, observaciones, productos_data
            )
            
            return envio_mock
            
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('\n\n⚠️  Operación cancelada por el usuario'))
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error al solicitar información: {str(e)}'))
            return None
