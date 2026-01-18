"""
Comando para probar las 10 consultas de ejemplo del usuario
Verifica que el sistema de búsqueda semántica responda correctamente
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.busqueda.services import BusquedaSemanticaService
from apps.busqueda.semantic import QueryExpander
import json
import time

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Prueba las 10 consultas de ejemplo del usuario para verificar precisión'
    
    # Las 10 consultas de ejemplo proporcionadas por el usuario
    CONSULTAS_PRUEBA = [
        "Buscar envíos que pendientes y sean de Quito.",
        "Envíos registrados este mes con un peso mayor a 5 kilogramos.",
        "Paquetes enviados por Juan Pérez que aún no han sido entregados.",
        "Mostrar envíos con valor total alto que requieran revisión.",
        "Paquetes con productos electrónicos enviados a Cuenca.",
        "Envíos con más de un producto en el mismo paquete.",
        "Buscar envíos del cliente con cédula 1718606043.",
        "Envíos recientes que todavía están pendientes de entrega.",
        "Paquetes livianos enviados la última semana.",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario-id',
            type=int,
            default=None,
            help='ID del usuario para realizar las búsquedas (por defecto usa el primero disponible)',
        )
        parser.add_argument(
            '--mostrar-expansion',
            action='store_true',
            help='Muestra la expansión de cada consulta',
        )
        parser.add_argument(
            '--mostrar-detalles',
            action='store_true',
            help='Muestra detalles completos de cada resultado',
        )
        parser.add_argument(
            '--limite',
            type=int,
            default=5,
            help='Cantidad de resultados a mostrar por consulta (default: 5)',
        )

    def handle(self, *args, **options):
        usuario_id = options['usuario_id']
        mostrar_expansion = options['mostrar_expansion']
        mostrar_detalles = options['mostrar_detalles']
        limite = options['limite']
        
        # Obtener usuario
        try:
            if usuario_id:
                usuario = Usuario.objects.get(id=usuario_id)
            else:
                usuario = Usuario.objects.first()
                if not usuario:
                    self.stdout.write(
                        self.style.ERROR('No hay usuarios en la base de datos')
                    )
                    return
            
            self.stdout.write(
                self.style.SUCCESS(f'Usando usuario: {usuario.nombre} (ID: {usuario.id})')
            )
        except Usuario.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuario con ID {usuario_id} no encontrado')
            )
            return
        
        # Ejecutar pruebas
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('🧪 PRUEBA DE CONSULTAS DE BÚSQUEDA SEMÁNTICA'))
        self.stdout.write('='*80 + '\n')
        
        resultados_totales = []
        tiempo_total = 0
        
        for i, consulta in enumerate(self.CONSULTAS_PRUEBA, 1):
            self.stdout.write(f'\n{"-"*80}')
            self.stdout.write(self.style.WARNING(f'📝 CONSULTA {i}/9'))
            self.stdout.write(f'{"-"*80}')
            self.stdout.write(f'💬 "{consulta}"\n')
            
            # Mostrar expansión si se solicita
            if mostrar_expansion:
                expansion = QueryExpander.expandir_consulta(consulta)
                self.stdout.write(self.style.HTTP_INFO('🔍 Expansión de consulta:'))
                self.stdout.write(f'  • Consulta expandida: {expansion["consulta_expandida"][:100]}...')
                self.stdout.write(f'  • Términos originales: {", ".join(expansion["terminos_originales"][:5])}')
                self.stdout.write(f'  • Sinónimos agregados: {len(expansion["sinonimos_agregados"])} términos')
                if expansion['filtros_sugeridos']:
                    self.stdout.write(f'  • Filtros sugeridos: {expansion["filtros_sugeridos"]}')
                if expansion['contexto_adicional']:
                    self.stdout.write(f'  • Contexto: {", ".join(expansion["contexto_adicional"])}')
                self.stdout.write('')
            
            # Ejecutar búsqueda
            try:
                tiempo_inicio = time.time()
                resultado = BusquedaSemanticaService.buscar(
                    consulta=consulta,
                    usuario=usuario,
                    limite=limite
                )
                tiempo_busqueda = (time.time() - tiempo_inicio) * 1000
                tiempo_total += tiempo_busqueda
                
                # Mostrar resumen
                total_encontrados = resultado['totalEncontrados']
                modelo = resultado['modeloUtilizado']
                costo = resultado['costoConsulta']
                
                if total_encontrados > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Encontrados: {total_encontrados} resultados')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Sin resultados')
                    )
                
                self.stdout.write(f'⏱️  Tiempo: {tiempo_busqueda:.2f}ms')
                self.stdout.write(f'🤖 Modelo: {modelo}')
                self.stdout.write(f'💰 Costo: ${costo:.6f}')
                
                # Mostrar resultados
                if total_encontrados > 0:
                    self.stdout.write(f'\n📊 Top {min(limite, total_encontrados)} resultados:')
                    
                    for j, res in enumerate(resultado['resultados'][:limite], 1):
                        envio = res['envio']
                        similitud = res['puntuacionSimilitud']
                        
                        if mostrar_detalles:
                            self.stdout.write(f'\n  {j}. HAWB: {envio["hawb"]} | Similitud: {similitud:.3f}')
                            self.stdout.write(f'     Estado: {envio.get("estado_display", "N/A")}')
                            self.stdout.write(f'     Comprador: {envio.get("comprador_nombre", "N/A")}')
                            if 'comprador_ciudad' in envio:
                                self.stdout.write(f'     Ciudad: {envio["comprador_ciudad"]}')
                            self.stdout.write(f'     Peso: {envio.get("peso_total", 0)} kg | Valor: ${envio.get("valor_total", 0)}')
                            if res.get('razonRelevancia'):
                                self.stdout.write(f'     ℹ️  {res["razonRelevancia"]}')
                        else:
                            # Vista compacta
                            ciudad = envio.get('comprador_ciudad', 'N/A')
                            estado = envio.get('estado_display', 'N/A')
                            self.stdout.write(
                                f'  {j}. {envio["hawb"]} | {similitud:.3f} | '
                                f'{estado} | {ciudad}'
                            )
                
                # Guardar para resumen
                resultados_totales.append({
                    'consulta': consulta,
                    'encontrados': total_encontrados,
                    'tiempo_ms': tiempo_busqueda,
                    'exitosa': total_encontrados > 0
                })
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error: {str(e)}')
                )
                resultados_totales.append({
                    'consulta': consulta,
                    'encontrados': 0,
                    'tiempo_ms': 0,
                    'exitosa': False,
                    'error': str(e)
                })
        
        # Resumen final
        self.stdout.write('\n\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('📈 RESUMEN DE PRUEBAS'))
        self.stdout.write('='*80)
        
        exitosas = sum(1 for r in resultados_totales if r['exitosa'])
        total_resultados = sum(r['encontrados'] for r in resultados_totales)
        tiempo_promedio = tiempo_total / len(self.CONSULTAS_PRUEBA)
        
        self.stdout.write(f'✅ Consultas exitosas: {exitosas}/{len(self.CONSULTAS_PRUEBA)} ({exitosas/len(self.CONSULTAS_PRUEBA)*100:.1f}%)')
        self.stdout.write(f'📊 Total de resultados encontrados: {total_resultados}')
        self.stdout.write(f'⏱️  Tiempo promedio por consulta: {tiempo_promedio:.2f}ms')
        self.stdout.write(f'⏱️  Tiempo total: {tiempo_total:.2f}ms')
        
        # Tabla detallada
        self.stdout.write(f'\n{"Consulta":<60} {"Resultados":>10} {"Tiempo (ms)":>12}')
        self.stdout.write('-'*85)
        for r in resultados_totales:
            consulta_corta = r['consulta'][:57] + '...' if len(r['consulta']) > 60 else r['consulta']
            estado = '✅' if r['exitosa'] else '❌'
            self.stdout.write(
                f'{estado} {consulta_corta:<58} {r["encontrados"]:>10} {r["tiempo_ms"]:>12.2f}'
            )
        
        # Recomendaciones
        self.stdout.write('\n' + '='*80)
        if exitosas == len(self.CONSULTAS_PRUEBA):
            self.stdout.write(
                self.style.SUCCESS('🎉 ¡Perfecto! Todas las consultas retornaron resultados.')
            )
        elif exitosas >= len(self.CONSULTAS_PRUEBA) * 0.7:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  La mayoría de consultas funcionan, pero algunas no retornan resultados.\n'
                    '   Considera regenerar embeddings o ajustar umbrales.'
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Pocas consultas retornan resultados.\n'
                    '   Es necesario regenerar los embeddings con:\n'
                    '   python manage.py generar_embeddings --regenerar'
                )
            )
        
        self.stdout.write('='*80 + '\n')
