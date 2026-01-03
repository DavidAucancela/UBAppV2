"""
Comando de gestión para mostrar métricas detalladas de similitud.

Muestra las 4 métricas de similitud para cada resultado de una búsqueda:
- Cosine Similarity (Similitud Coseno) [RECOMENDADO]
- Dot Product (Producto Punto)
- Euclidean Distance (Distancia Euclidiana)
- Manhattan Distance (Distancia Manhattan)

Uso:
    python manage.py mostrar_metricas_similitud "consulta" [opciones]

Opciones:
    --usuario USERNAME     Usuario para realizar la búsqueda (default: admin)
    --limite N             Límite de resultados a mostrar (default: 10)
    --ordenar METRICA      Métrica para ordenar resultados:
                           - cosine: Similitud coseno
                           - dot_product: Producto punto
                           - euclidean: Distancia euclidiana
                           - manhattan: Distancia Manhattan
                           - score_combinado: Score combinado (default)
    --formato FORMATO      Formato de salida:
                           - tabla: Tabla con métricas (default)
                           - json: Formato JSON
                           - detallado: Información completa por resultado
                           - comparativo: Compara ordenamientos por diferentes métricas
    --comparar             Compara ordenamientos por diferentes métricas

Ejemplos:
    # Mostrar métricas ordenadas por cosine similarity
    python manage.py mostrar_metricas_similitud "envíos pesados" --ordenar cosine

    # Comparar ordenamientos por diferentes métricas
    python manage.py mostrar_metricas_similitud "productos electrónicos" --formato comparativo

    # Formato detallado ordenado por euclidean distance
    python manage.py mostrar_metricas_similitud "envíos a Quito" --ordenar euclidean --formato detallado
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q
from apps.busqueda.services import BusquedaSemanticaService
from apps.busqueda.semantic.vector_search import VectorSearchService
import numpy as np

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Muestra las métricas detalladas de similitud para una búsqueda semántica'

    def add_arguments(self, parser):
        parser.add_argument(
            'consulta',
            type=str,
            help='Texto de la consulta a buscar'
        )
        parser.add_argument(
            '--usuario',
            type=str,
            default='admin',
            help='Usuario para realizar la búsqueda (default: admin)'
        )
        parser.add_argument(
            '--limite',
            type=int,
            default=10,
            help='Límite de resultados a mostrar (default: 10)'
        )
        parser.add_argument(
            '--formato',
            type=str,
            choices=['tabla', 'json', 'detallado', 'comparativo'],
            default='tabla',
            help='Formato de salida (default: tabla)'
        )
        parser.add_argument(
            '--ordenar',
            type=str,
            choices=['cosine', 'dot_product', 'euclidean', 'manhattan', 'score_combinado'],
            default='score_combinado',
            help='Métrica para ordenar resultados (default: score_combinado)'
        )
        parser.add_argument(
            '--comparar',
            action='store_true',
            help='Comparar ordenamientos por diferentes métricas'
        )

    def handle(self, *args, **options):
        consulta = options['consulta']
        username = options['usuario']
        limite = options['limite']
        formato = options['formato']
        ordenar_por = options['ordenar']
        comparar = options['comparar']
        
        # Intentar obtener el usuario especificado
        usuario = None
        try:
            usuario = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            # Si no existe, buscar un usuario admin o superuser
            usuario = Usuario.objects.filter(
                Q(rol=1) | Q(is_superuser=True)
            ).first()
            
            if not usuario:
                # Si no hay admin, buscar gerente o digitador
                usuario = Usuario.objects.filter(
                    Q(rol=2) | Q(rol=3)
                ).first()
            
            if not usuario:
                # Si no hay ninguno, buscar cualquier usuario activo
                usuario = Usuario.objects.filter(es_activo=True).first()
            
            if not usuario:
                # Mostrar usuarios disponibles
                usuarios_disponibles = Usuario.objects.all()[:10]
                self.stdout.write(
                    self.style.ERROR(f'\nUsuario "{username}" no encontrado.')
                )
                if usuarios_disponibles.exists():
                    self.stdout.write(self.style.WARNING('\nUsuarios disponibles:'))
                    for u in usuarios_disponibles:
                        rol_nombre = dict(Usuario.ROLES_CHOICES).get(u.rol, 'Desconocido')
                        self.stdout.write(f'  - {u.username} (Rol: {rol_nombre})')
                    self.stdout.write(f'\nEjecute con: --usuario {usuarios_disponibles.first().username}')
                else:
                    self.stdout.write(
                        self.style.ERROR('No hay usuarios en el sistema. Cree un usuario primero.')
                    )
                return
            
            # Mostrar que se usó un usuario diferente
            self.stdout.write(
                self.style.WARNING(
                    f'Usuario "{username}" no encontrado. Usando usuario: {usuario.username} (Rol: {dict(Usuario.ROLES_CHOICES).get(usuario.rol, "Desconocido")})'
                )
            )
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*100}'))
        self.stdout.write(self.style.SUCCESS('MÉTRICAS DE SIMILITUD - BÚSQUEDA SEMÁNTICA'))
        self.stdout.write(self.style.SUCCESS(f'{"="*100}\n'))
        self.stdout.write(f'Consulta: "{consulta}"')
        self.stdout.write(f'Usuario: {usuario.username}')
        self.stdout.write(f'Límite de resultados: {limite}')
        self.stdout.write(f'Ordenar por: {ordenar_por}\n')
        
        try:
            # Mapear métrica de ordenamiento para el servicio
            mapeo_metricas_servicio = {
                'cosine': 'cosine_similarity',
                'dot_product': 'dot_product',
                'euclidean': 'euclidean_distance',
                'manhattan': 'manhattan_distance',
                'score_combinado': 'score_combinado'
            }
            metrica_servicio = mapeo_metricas_servicio.get(ordenar_por, 'score_combinado')
            
            # Realizar búsqueda con límite mayor para tener más datos para comparar
            limite_busqueda = limite * 2 if comparar else limite
            resultado = BusquedaSemanticaService.buscar(
                consulta=consulta,
                usuario=usuario,
                limite=limite_busqueda,
                modelo_embedding='text-embedding-3-small',
                metrica_ordenamiento=metrica_servicio
            )
            
            resultados_raw = resultado.get('resultados', [])
            total_encontrados = resultado.get('totalEncontrados', 0)
            tiempo_respuesta = resultado.get('tiempoRespuesta', 0)
            costo_consulta = resultado.get('costoConsulta', 0)
            
            # Mostrar información general
            self.stdout.write(self.style.SUCCESS(f'[OK] Busqueda completada'))
            self.stdout.write(f'   Resultados encontrados: {total_encontrados}')
            self.stdout.write(f'   Tiempo de respuesta: {tiempo_respuesta} ms')
            self.stdout.write(f'   Costo: ${costo_consulta:.6f} USD\n')
            
            if not resultados_raw:
                self.stdout.write(
                    self.style.WARNING('[ADVERTENCIA] No se encontraron resultados')
                )
                return
            
            # Convertir resultados a formato interno para ordenamiento
            resultados_internos = self._convertir_a_formato_interno(resultados_raw)
            
            # Ordenar por la métrica especificada
            vector_search = VectorSearchService()
            mapeo_metricas = {
                'cosine': 'cosine_similarity',
                'dot_product': 'dot_product',
                'euclidean': 'euclidean_distance',
                'manhattan': 'manhattan_distance',
                'score_combinado': 'score_combinado'
            }
            metrica_ordenar = mapeo_metricas.get(ordenar_por, 'score_combinado')
            
            resultados_ordenados = vector_search.ordenar_por_metrica(
                resultados_internos,
                metrica=metrica_ordenar,
                limite=limite
            )
            
            # Convertir de vuelta al formato de salida
            resultados = self._convertir_a_formato_salida(resultados_ordenados)
            
            # Mostrar métricas según formato
            if formato == 'tabla':
                self._mostrar_tabla(resultados, ordenar_por)
            elif formato == 'json':
                self._mostrar_json(resultados)
            elif formato == 'detallado':
                self._mostrar_detallado(resultados, consulta, ordenar_por)
            elif formato == 'comparativo':
                self._mostrar_comparativo(resultados_internos, limite, consulta)
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'[ERROR] Error ejecutando busqueda: {str(e)}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())
    
    def _convertir_a_formato_interno(self, resultados_raw):
        """Convierte resultados del formato de salida al formato interno"""
        resultados_internos = []
        for resultado in resultados_raw:
            envio_obj = resultado.get('envio', {})
            envio_id = envio_obj.get('id') if isinstance(envio_obj, dict) else (envio_obj.id if hasattr(envio_obj, 'id') else None)
            
            resultados_internos.append({
                'envio_id': envio_id,
                'envio': envio_obj,
                'cosine_similarity': resultado.get('cosineSimilarity', 0),
                'dot_product': resultado.get('dotProduct', 0),
                'euclidean_distance': resultado.get('euclideanDistance', 0),
                'manhattan_distance': resultado.get('manhattanDistance', 0),
                'score_combinado': resultado.get('scoreCombinado', resultado.get('puntuacionSimilitud', 0)),
                'boost_exactas': resultado.get('boostExactas', 0),
                'coincidencias_exactas': 0,  # No disponible en formato salida
                'razonRelevancia': resultado.get('razonRelevancia', ''),
                'fragmentosRelevantes': resultado.get('fragmentosRelevantes', []),
                'norma_envio': resultado.get('normaEnvio', 1.0),
                'norma_consulta': resultado.get('normaConsulta', 1.0)
            })
        return resultados_internos
    
    def _convertir_a_formato_salida(self, resultados_internos):
        """Convierte resultados del formato interno al formato de salida"""
        resultados = []
        for resultado in resultados_internos:
            envio_obj = resultado.get('envio', {})
            
            resultados.append({
                'envio': envio_obj if isinstance(envio_obj, dict) else {
                    'id': envio_obj.id if hasattr(envio_obj, 'id') else None,
                    'hawb': envio_obj.hawb if hasattr(envio_obj, 'hawb') else 'N/A',
                    'comprador': envio_obj.comprador if hasattr(envio_obj, 'comprador') else {},
                    'estado': envio_obj.estado if hasattr(envio_obj, 'estado') else 'N/A'
                },
                'cosineSimilarity': resultado.get('cosine_similarity', 0),
                'dotProduct': resultado.get('dot_product', 0),
                'euclideanDistance': resultado.get('euclidean_distance', 0),
                'manhattanDistance': resultado.get('manhattan_distance', 0),
                'scoreCombinado': resultado.get('score_combinado', 0),
                'puntuacionSimilitud': resultado.get('score_combinado', 0),
                'boostExactas': resultado.get('boost_exactas', 0),
                'razonRelevancia': resultado.get('razonRelevancia', ''),
                'fragmentosRelevantes': resultado.get('fragmentosRelevantes', []),
                'normaEnvio': resultado.get('norma_envio', 1.0),
                'normaConsulta': resultado.get('norma_consulta', 1.0)
            })
        return resultados
    
    def _mostrar_tabla(self, resultados, ordenar_por='score_combinado'):
        """Muestra resultados en formato tabla"""
        self.stdout.write(self.style.SUCCESS(f'\n{"="*100}'))
        self.stdout.write(self.style.SUCCESS('RESULTADOS CON MÉTRICAS DE SIMILITUD'))
        self.stdout.write(self.style.SUCCESS(f'{"="*100}\n'))
        self.stdout.write(self.style.WARNING(f'[METRICAS] Ordenado por: {ordenar_por.upper()}\n'))
        
        # Nota sobre Dot Product
        if resultados:
            primer_resultado = resultados[0]
            norma_envio = primer_resultado.get('normaEnvio', 1.0)
            norma_consulta = primer_resultado.get('normaConsulta', 1.0)
            if abs(norma_envio - 1.0) < 0.1 and abs(norma_consulta - 1.0) < 0.1:
                self.stdout.write(
                    self.style.WARNING(
                        '[NOTA] Los embeddings estan normalizados (norma ~ 1.0). '
                        'Por esto, Dot Product ~ Cosine Similarity es esperado y correcto.\n'
                    )
                )
        
        # Encabezado de tabla con indicador de ordenamiento
        header = (
            f"{'#':<4} | "
            f"{'HAWB':<12} | "
            f"{'Cosine':<10} | "
            f"{'Dot Prod':<12} | "
            f"{'Euclidean':<12} | "
            f"{'Manhattan':<12} | "
            f"{'Score Comb':<12}"
        )
        self.stdout.write(header)
        self.stdout.write('-' * 100)
        
        # Filas de datos
        for i, resultado in enumerate(resultados, 1):
            envio = resultado.get('envio', {})
            hawb = envio.get('hawb', 'N/A')
            
            cosine = resultado.get('cosineSimilarity', 0)
            dot_product = resultado.get('dotProduct', 0)
            euclidean = resultado.get('euclideanDistance', 0)
            manhattan = resultado.get('manhattanDistance', 0)
            score_combinado = resultado.get('scoreCombinado', resultado.get('puntuacionSimilitud', 0))
            
            # Resaltar la métrica por la que se ordena
            cosine_str = f"{cosine:<10.4f}"
            dot_str = f"{dot_product:<12.4f}"
            euclidean_str = f"{euclidean:<12.4f}"
            manhattan_str = f"{manhattan:<12.4f}"
            score_str = f"{score_combinado:<12.4f}"
            
            if ordenar_por == 'cosine':
                cosine_str = self.style.SUCCESS(cosine_str)
            elif ordenar_por == 'dot_product':
                dot_str = self.style.SUCCESS(dot_str)
            elif ordenar_por == 'euclidean':
                euclidean_str = self.style.SUCCESS(euclidean_str)
            elif ordenar_por == 'manhattan':
                manhattan_str = self.style.SUCCESS(manhattan_str)
            elif ordenar_por == 'score_combinado':
                score_str = self.style.SUCCESS(score_str)
            
            fila = (
                f"{i:<4} | "
                f"{hawb:<12} | "
                f"{cosine_str} | "
                f"{dot_str} | "
                f"{euclidean_str} | "
                f"{manhattan_str} | "
                f"{score_str}"
            )
            self.stdout.write(fila)
        
        self.stdout.write('-' * 100)
        
        # Mostrar estadísticas de métricas
        self._mostrar_estadisticas(resultados)
    
    def _mostrar_json(self, resultados):
        """Muestra resultados en formato JSON"""
        import json
        
        datos_json = []
        for resultado in resultados:
            envio = resultado.get('envio', {})
            datos_json.append({
                'hawb': envio.get('hawb', 'N/A'),
                'metricas': {
                    'cosineSimilarity': resultado.get('cosineSimilarity', 0),
                    'dotProduct': resultado.get('dotProduct', 0),
                    'euclideanDistance': resultado.get('euclideanDistance', 0),
                    'manhattanDistance': resultado.get('manhattanDistance', 0),
                    'scoreCombinado': resultado.get('scoreCombinado', resultado.get('puntuacionSimilitud', 0)),
                    'boostExactas': resultado.get('boostExactas', 0),
                },
                'razonRelevancia': resultado.get('razonRelevancia', 'N/A')
            })
        
        self.stdout.write(json.dumps(datos_json, indent=2, ensure_ascii=False))
    
    def _mostrar_detallado(self, resultados, consulta, ordenar_por='score_combinado'):
        """Muestra resultados con información detallada"""
        self.stdout.write(self.style.SUCCESS(f'\n{"="*100}'))
        self.stdout.write(self.style.SUCCESS('RESULTADOS DETALLADOS CON MÉTRICAS'))
        self.stdout.write(self.style.SUCCESS(f'{"="*100}\n'))
        self.stdout.write(self.style.WARNING(f'[METRICAS] Ordenado por: {ordenar_por.upper()}\n'))
        
        for i, resultado in enumerate(resultados, 1):
            envio = resultado.get('envio', {})
            hawb = envio.get('hawb', 'N/A')
            comprador = envio.get('comprador', {})
            nombre_comprador = comprador.get('nombre', 'N/A') if isinstance(comprador, dict) else 'N/A'
            ciudad = comprador.get('ciudad', 'N/A') if isinstance(comprador, dict) else 'N/A'
            estado = envio.get('estado', 'N/A')
            
            # Métricas
            cosine = resultado.get('cosineSimilarity', 0)
            dot_product = resultado.get('dotProduct', 0)
            euclidean = resultado.get('euclideanDistance', 0)
            manhattan = resultado.get('manhattanDistance', 0)
            score_combinado = resultado.get('scoreCombinado', resultado.get('puntuacionSimilitud', 0))
            boost_exactas = resultado.get('boostExactas', 0)
            
            # Información adicional
            razon = resultado.get('razonRelevancia', 'N/A')
            fragmentos = resultado.get('fragmentosRelevantes', [])
            
            self.stdout.write(self.style.SUCCESS(f'\n[{i}] Envío: {hawb}'))
            self.stdout.write('-' * 100)
            self.stdout.write(f'Comprador: {nombre_comprador} | Ciudad: {ciudad} | Estado: {estado}')
            self.stdout.write('')
            
            # Métricas con indicador de ordenamiento
            self.stdout.write(self.style.WARNING('[METRICAS] METRICAS DE SIMILITUD:'))
            
            # Cosine
            cosine_str = f'   Cosine Similarity:      {cosine:>10.6f}  (Rango: [-1, 1], Mayor = Más similar)'
            if ordenar_por == 'cosine':
                cosine_str = self.style.SUCCESS(cosine_str + ' [ORDENADO POR ESTA METRICA]')
            self.stdout.write(cosine_str)
            
            # Dot Product con información adicional
            norma_envio = resultado.get('normaEnvio', 1.0)
            norma_consulta = resultado.get('normaConsulta', 1.0)
            
            # Nota sobre normalización
            nota_dot = ""
            if abs(norma_envio - 1.0) < 0.1 and abs(norma_consulta - 1.0) < 0.1:
                nota_dot = " (Vectores normalizados: Dot Product ~ Cosine)"
            
            dot_str = f'   Dot Product:            {dot_product:>10.6f}  (Rango: [0, inf], Mayor = Mas similar){nota_dot}'
            if ordenar_por == 'dot_product':
                dot_str = self.style.SUCCESS(dot_str + ' [ORDENADO POR ESTA METRICA]')
            self.stdout.write(dot_str)
            
            # Mostrar normas si están disponibles
            if norma_envio and norma_consulta:
                self.stdout.write(f'   Normas (Envío: {norma_envio:.4f}, Consulta: {norma_consulta:.4f})')
            
            # Euclidean
            euclidean_str = f'   Euclidean Distance:     {euclidean:>10.6f}  (Rango: [0, inf], Menor = Mas similar)'
            if ordenar_por == 'euclidean':
                euclidean_str = self.style.SUCCESS(euclidean_str + ' [ORDENADO POR ESTA METRICA]')
            self.stdout.write(euclidean_str)
            
            # Manhattan
            manhattan_str = f'   Manhattan Distance:     {manhattan:>10.6f}  (Rango: [0, inf], Menor = Mas similar)'
            if ordenar_por == 'manhattan':
                manhattan_str = self.style.SUCCESS(manhattan_str + ' [ORDENADO POR ESTA METRICA]')
            self.stdout.write(manhattan_str)
            
            self.stdout.write('')
            
            # Score Combinado
            score_str = f'   Score Combinado:       {score_combinado:>10.6f}  (Métrica final para ordenamiento)'
            if ordenar_por == 'score_combinado':
                score_str = self.style.SUCCESS(score_str + ' [ORDENADO POR ESTA METRICA]')
            self.stdout.write(score_str)
            self.stdout.write(f'   Boost por Exactas:      {boost_exactas:>10.6f}  (Boost aplicado)')
            self.stdout.write('')
            
            # Interpretación de métricas
            self._mostrar_interpretacion_metricas(cosine, dot_product, euclidean, manhattan, score_combinado)
            
            # Información de relevancia
            self.stdout.write(self.style.WARNING('🔍 INFORMACIÓN DE RELEVANCIA:'))
            self.stdout.write(f'   Razón: {razon}')
            if fragmentos:
                self.stdout.write('   Fragmentos relevantes:')
                for fragmento in fragmentos[:3]:
                    self.stdout.write(f'      - {fragmento[:80]}...')
            
            self.stdout.write('')
    
    def _mostrar_interpretacion_metricas(self, cosine, dot_product, euclidean, manhattan, score_combinado):
        """Muestra interpretación de las métricas"""
        self.stdout.write(self.style.WARNING('📈 INTERPRETACIÓN:'))
        
        # Interpretar Cosine
        if cosine >= 0.8:
            interp_cosine = "Excelente similitud semántica"
        elif cosine >= 0.6:
            interp_cosine = "Buena similitud semántica"
        elif cosine >= 0.4:
            interp_cosine = "Similitud moderada"
        elif cosine >= 0.2:
            interp_cosine = "Similitud baja"
        else:
            interp_cosine = "Muy poca similitud"
        self.stdout.write(f'   Cosine ({cosine:.4f}): {interp_cosine}')
        
        # Interpretar Dot Product (si es diferente de cosine)
        if abs(dot_product - cosine) > 0.01:
            if dot_product > 10:
                interp_dot = "Producto punto alto (vectores con magnitud significativa)"
            elif dot_product > 5:
                interp_dot = "Producto punto moderado"
            else:
                interp_dot = "Producto punto bajo"
            self.stdout.write(f'   Dot Product ({dot_product:.4f}): {interp_dot}')
        
        # Interpretar Euclidean
        if euclidean < 0.5:
            interp_euclidean = "Muy cercanos en el espacio vectorial"
        elif euclidean < 1.0:
            interp_euclidean = "Cercanos en el espacio vectorial"
        elif euclidean < 2.0:
            interp_euclidean = "Distancia moderada"
        else:
            interp_euclidean = "Distantes en el espacio vectorial"
        self.stdout.write(f'   Euclidean ({euclidean:.4f}): {interp_euclidean}')
        
        # Interpretar Score Combinado
        porcentaje = score_combinado * 100
        if porcentaje >= 80:
            interp_score = "Alta relevancia"
        elif porcentaje >= 60:
            interp_score = "Relevancia moderada-alta"
        elif porcentaje >= 40:
            interp_score = "Relevancia moderada"
        else:
            interp_score = "Baja relevancia"
        self.stdout.write(f'   Score Combinado ({score_combinado:.4f} = {porcentaje:.1f}%): {interp_score}')
        self.stdout.write('')
    
    def _mostrar_estadisticas(self, resultados):
        """Muestra estadísticas de las métricas"""
        if not resultados:
            return
        
        cosines = [r.get('cosineSimilarity', 0) for r in resultados]
        dot_products = [r.get('dotProduct', 0) for r in resultados]
        euclideans = [r.get('euclideanDistance', 0) for r in resultados]
        manhattans = [r.get('manhattanDistance', 0) for r in resultados]
        scores = [r.get('scoreCombinado', 0) for r in resultados]
        
        self.stdout.write(self.style.WARNING(f'\n[METRICAS] ESTADISTICAS DE METRICAS:'))
        self.stdout.write('-' * 100)
        
        # Cosine
        self.stdout.write(f'Cosine Similarity:')
        self.stdout.write(f'   Media: {np.mean(cosines):.4f} | Min: {min(cosines):.4f} | Max: {max(cosines):.4f} | Std: {np.std(cosines):.4f}')
        
        # Dot Product
        if len(set(dot_products)) > 1:  # Solo mostrar si hay variación
            self.stdout.write(f'Dot Product:')
            self.stdout.write(f'   Media: {np.mean(dot_products):.4f} | Min: {min(dot_products):.4f} | Max: {max(dot_products):.4f} | Std: {np.std(dot_products):.4f}')
        
        # Euclidean
        self.stdout.write(f'Euclidean Distance:')
        self.stdout.write(f'   Media: {np.mean(euclideans):.4f} | Min: {min(euclideans):.4f} | Max: {max(euclideans):.4f} | Std: {np.std(euclideans):.4f}')
        
        # Manhattan
        self.stdout.write(f'Manhattan Distance:')
        self.stdout.write(f'   Media: {np.mean(manhattans):.4f} | Min: {min(manhattans):.4f} | Max: {max(manhattans):.4f} | Std: {np.std(manhattans):.4f}')
        
        # Score Combinado
        self.stdout.write(f'Score Combinado:')
        self.stdout.write(f'   Media: {np.mean(scores):.4f} | Min: {min(scores):.4f} | Max: {max(scores):.4f} | Std: {np.std(scores):.4f}')
        self.stdout.write('-' * 100)
    
    def _mostrar_comparativo(self, resultados_internos, limite, consulta):
        """Muestra comparación de ordenamientos por diferentes métricas"""
        self.stdout.write(self.style.SUCCESS(f'\n{"="*100}'))
        self.stdout.write(self.style.SUCCESS('COMPARACIÓN DE ORDENAMIENTOS POR DIFERENTES MÉTRICAS'))
        self.stdout.write(self.style.SUCCESS(f'{"="*100}\n'))
        
        vector_search = VectorSearchService()
        metricas = ['cosine_similarity', 'dot_product', 'euclidean_distance', 'manhattan_distance', 'score_combinado']
        nombres_metricas = {
            'cosine_similarity': 'Cosine Similarity',
            'dot_product': 'Dot Product',
            'euclidean_distance': 'Euclidean Distance',
            'manhattan_distance': 'Manhattan Distance',
            'score_combinado': 'Score Combinado'
        }
        
        ordenamientos = {}
        for metrica in metricas:
            ordenados = vector_search.ordenar_por_metrica(
                resultados_internos.copy(),
                metrica=metrica,
                limite=limite
            )
            # Extraer HAWBs de forma segura
            hawbs_list = []
            for r in ordenados:
                envio = r.get('envio', {})
                if hasattr(envio, 'hawb'):
                    hawbs_list.append(envio.hawb)
                elif isinstance(envio, dict):
                    hawbs_list.append(envio.get('hawb', 'N/A'))
                else:
                    hawbs_list.append('N/A')
            ordenamientos[metrica] = hawbs_list
        
        # Mostrar comparación
        self.stdout.write(f'\n{"Métrica":<25} | Top {limite} HAWBs')
        self.stdout.write('-' * 100)
        
        for metrica, hawbs in ordenamientos.items():
            nombre = nombres_metricas[metrica]
            hawbs_str = ', '.join(hawbs[:10])  # Mostrar primeros 10
            if len(hawbs) > 10:
                hawbs_str += f' ... (+{len(hawbs)-10} más)'
            self.stdout.write(f'{nombre:<25} | {hawbs_str}')
        
        # Análisis de diferencias
        self.stdout.write('\n' + self.style.WARNING('[METRICAS] ANALISIS DE DIFERENCIAS:'))
        
        # Comparar con score_combinado (referencia)
        referencia = ordenamientos['score_combinado']
        for metrica, hawbs in ordenamientos.items():
            if metrica == 'score_combinado':
                continue
            
            # Calcular diferencia usando índice de posición
            diferencias = []
            for i, hawb in enumerate(referencia[:limite]):
                try:
                    pos_otra = hawbs.index(hawb)
                    diferencia = abs(i - pos_otra)
                    diferencias.append(diferencia)
                except ValueError:
                    diferencias.append(limite)  # No está en el top
            
            diferencia_promedio = np.mean(diferencias) if diferencias else 0
            nombre = nombres_metricas[metrica]
            
            if diferencia_promedio < 2:
                estado = self.style.SUCCESS('[OK] Similar')
            elif diferencia_promedio < 5:
                estado = self.style.WARNING('[ADV] Moderadamente diferente')
            else:
                estado = self.style.ERROR('[ERR] Muy diferente')
            
            self.stdout.write(f'   {nombre}: Diferencia promedio de posición = {diferencia_promedio:.2f} {estado}')
        
        self.stdout.write('\n' + self.style.SUCCESS('[RECOMENDACION]:'))
        self.stdout.write('   Cosine Similarity y Score Combinado suelen dar resultados más consistentes.')
        self.stdout.write('   Las distancias (Euclidean, Manhattan) pueden variar más según la distribución de los datos.')