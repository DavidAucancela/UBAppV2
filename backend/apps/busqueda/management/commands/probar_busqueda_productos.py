"""
Comando de gestión para probar búsquedas semánticas sobre productos.

Este script prueba diferentes tipos de consultas sobre productos para identificar
qué funciona y qué no funciona en el sistema de búsqueda semántica.

Uso:
    python manage.py probar_busqueda_productos [--usuario USERNAME]
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.busqueda.services import BusquedaSemanticaService
import json

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Prueba diferentes consultas de búsqueda semántica sobre productos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            default='admin',
            help='Usuario para realizar las búsquedas (default: admin)'
        )
        parser.add_argument(
            '--limite',
            type=int,
            default=5,
            help='Límite de resultados por búsqueda (default: 5)'
        )

    def handle(self, *args, **options):
        username = options['usuario']
        limite = options['limite']
        
        try:
            usuario = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuario "{username}" no encontrado')
            )
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*80}'))
        self.stdout.write(self.style.SUCCESS('PRUEBAS DE BÚSQUEDA SEMÁNTICA - PRODUCTOS'))
        self.stdout.write(self.style.SUCCESS(f'{"="*80}\n'))
        self.stdout.write(f'Usuario: {usuario.username}')
        self.stdout.write(f'Límite de resultados: {limite}\n')
        
        # Lista de consultas de prueba organizadas por categoría
        consultas_prueba = {
            'Consultas básicas de productos': [
                'productos electrónicos',
                'ropa',
                'artículos para el hogar',
                'productos deportivos',
                'dispositivos',
            ],
            'Consultas con descripción específica': [
                'laptop',
                'camiseta',
                'muebles',
                'zapatos deportivos',
                'smartphone',
            ],
            'Consultas con características numéricas': [
                'productos con peso mayor a 5kg',
                'productos de valor alto',
                'productos pesados',
                'productos costosos',
            ],
            'Consultas combinadas (producto + ubicación)': [
                'productos electrónicos en Quito',
                'ropa entregada',
                'artículos del hogar en Guayaquil',
            ],
            'Consultas con sinónimos': [
                'electrónica',
                'vestimenta',
                'artículos domésticos',
                'equipamiento deportivo',
            ],
            'Consultas con preguntas': [
                '¿qué productos hay?',
                'muéstrame productos de electrónica',
                'envíos con productos de ropa',
                'qué envíos contienen dispositivos',
            ],
            'Consultas complejas': [
                'productos electrónicos entregados la semana pasada',
                'ropa de alto valor',
                'artículos pesados para el hogar',
                'productos tecnológicos en Quito',
            ],
        }
        
        resultados_totales = {
            'exitosas': [],
            'sin_resultados': [],
            'con_resultados_bajos': [],
        }
        
        # Ejecutar pruebas
        for categoria, consultas in consultas_prueba.items():
            self.stdout.write(self.style.WARNING(f'\n{categoria}'))
            self.stdout.write('-' * 80)
            
            for consulta in consultas:
                try:
                    resultado = BusquedaSemanticaService.buscar(
                        consulta=consulta,
                        usuario=usuario,
                        limite=limite,
                        modelo_embedding='text-embedding-3-small'
                    )
                    
                    total = resultado.get('totalEncontrados', 0)
                    tiempo = resultado.get('tiempoRespuesta', 0)
                    
                    # Clasificar resultado
                    if total == 0:
                        estado = self.style.ERROR('❌ SIN RESULTADOS')
                        resultados_totales['sin_resultados'].append({
                            'consulta': consulta,
                            'categoria': categoria
                        })
                    elif total > 0:
                        # Verificar puntuación de similitud del primer resultado
                        resultados = resultado.get('resultados', [])
                        if resultados:
                            primera_puntuacion = resultados[0].get('puntuacionSimilitud', 0)
                            if primera_puntuacion < 0.4:
                                estado = self.style.WARNING('⚠️  RESULTADOS BAJOS')
                                resultados_totales['con_resultados_bajos'].append({
                                    'consulta': consulta,
                                    'categoria': categoria,
                                    'puntuacion': primera_puntuacion,
                                    'total': total
                                })
                            else:
                                estado = self.style.SUCCESS('✅ EXITOSA')
                                resultados_totales['exitosas'].append({
                                    'consulta': consulta,
                                    'categoria': categoria,
                                    'puntuacion': primera_puntuacion,
                                    'total': total
                                })
                        else:
                            estado = self.style.SUCCESS('✅ EXITOSA')
                            resultados_totales['exitosas'].append({
                                'consulta': consulta,
                                'categoria': categoria,
                                'total': total
                            })
                    
                    # Mostrar resultado
                    self.stdout.write(f'{estado} | "{consulta}"')
                    self.stdout.write(f'   → Resultados: {total} | Tiempo: {tiempo}ms')
                    
                    # Mostrar detalles del primer resultado si existe
                    if resultados and len(resultados) > 0:
                        primer_resultado = resultados[0]
                        puntuacion = primer_resultado.get('puntuacionSimilitud', 0)
                        hawb = primer_resultado.get('envio', {}).get('hawb', 'N/A')
                        razon = primer_resultado.get('razonRelevancia', 'N/A')
                        
                        self.stdout.write(
                            f'   → Mejor resultado: HAWB {hawb} '
                            f'(Similitud: {puntuacion:.2%})'
                        )
                        self.stdout.write(f'   → Razón: {razon}')
                        
                        # Mostrar productos del envío si existen
                        envio_data = primer_resultado.get('envio', {})
                        productos = envio_data.get('productos', [])
                        if productos:
                            productos_str = ', '.join([
                                p.get('descripcion', '')[:30] 
                                for p in productos[:3]
                            ])
                            self.stdout.write(f'   → Productos: {productos_str}')
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ ERROR | "{consulta}" → {str(e)}')
                    )
        
        # Resumen final
        self.stdout.write(self.style.SUCCESS(f'\n{"="*80}'))
        self.stdout.write(self.style.SUCCESS('RESUMEN DE PRUEBAS'))
        self.stdout.write(self.style.SUCCESS(f'{"="*80}\n'))
        
        total_pruebas = (
            len(resultados_totales['exitosas']) +
            len(resultados_totales['sin_resultados']) +
            len(resultados_totales['con_resultados_bajos'])
        )
        
        self.stdout.write(f'Total de pruebas: {total_pruebas}')
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Exitosas: {len(resultados_totales["exitosas"])} '
                f'({len(resultados_totales["exitosas"])/total_pruebas*100:.1f}%)'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                f'⚠️  Con resultados bajos: {len(resultados_totales["con_resultados_bajos"])} '
                f'({len(resultados_totales["con_resultados_bajos"])/total_pruebas*100:.1f}%)'
            )
        )
        self.stdout.write(
            self.style.ERROR(
                f'❌ Sin resultados: {len(resultados_totales["sin_resultados"])} '
                f'({len(resultados_totales["sin_resultados"])/total_pruebas*100:.1f}%)'
            )
        )
        
        # Detalles de consultas sin resultados
        if resultados_totales['sin_resultados']:
            self.stdout.write(self.style.ERROR(f'\n{"="*80}'))
            self.stdout.write(self.style.ERROR('CONSULTAS SIN RESULTADOS:'))
            self.stdout.write(self.style.ERROR(f'{"="*80}\n'))
            for item in resultados_totales['sin_resultados']:
                self.stdout.write(f'  - "{item["consulta"]}" ({item["categoria"]})')
        
        # Detalles de consultas con resultados bajos
        if resultados_totales['con_resultados_bajos']:
            self.stdout.write(self.style.WARNING(f'\n{"="*80}'))
            self.stdout.write(self.style.WARNING('CONSULTAS CON RESULTADOS BAJOS:'))
            self.stdout.write(self.style.WARNING(f'{"="*80}\n'))
            for item in resultados_totales['con_resultados_bajos']:
                self.stdout.write(
                    f'  - "{item["consulta"]}" '
                    f'(Similitud: {item["puntuacion"]:.2%}, '
                    f'Resultados: {item["total"]})'
                )
        
        # Recomendaciones
        self.stdout.write(self.style.SUCCESS(f'\n{"="*80}'))
        self.stdout.write(self.style.SUCCESS('RECOMENDACIONES:'))
        self.stdout.write(self.style.SUCCESS(f'{"="*80}\n'))
        
        if len(resultados_totales['sin_resultados']) > total_pruebas * 0.3:
            self.stdout.write(
                '⚠️  Más del 30% de las consultas no tienen resultados. '
                'Considera mejorar la indexación de productos.'
            )
        
        if len(resultados_totales['con_resultados_bajos']) > total_pruebas * 0.2:
            self.stdout.write(
                '⚠️  Más del 20% de las consultas tienen resultados con baja similitud. '
                'Considera mejorar el texto indexado o ajustar el umbral.'
            )
        
        if len(resultados_totales['exitosas']) / total_pruebas >= 0.7:
            self.stdout.write(
                '✅ Más del 70% de las consultas son exitosas. '
                'El sistema funciona bien para la mayoría de casos.'
            )
        
        self.stdout.write('\n')

