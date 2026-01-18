"""
Comando de gestión para poblar datos de prueba en el dashboard de métricas.
Uso: python manage.py poblar_datos_prueba
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from apps.metricas.models import (
    PruebaControladaSemantica,
    MetricaSemantica,
    RegistroGeneracionEmbedding,
    PruebaCarga,
    MetricaRendimiento,
    RegistroManualEnvio
)
from apps.busqueda.models import EmbeddingBusqueda
from apps.archivos.models import Envio
from apps.busqueda.models import EnvioEmbedding

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de prueba para el dashboard de métricas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpiar',
            action='store_true',
            help='Elimina todos los datos existentes antes de poblar'
        )
        parser.add_argument(
            '--cantidad-metricas',
            type=int,
            default=50,
            help='Cantidad de métricas semánticas a crear (default: 50)'
        )
        parser.add_argument(
            '--cantidad-pruebas-carga',
            type=int,
            default=10,
            help='Cantidad de pruebas de carga a crear (default: 10)'
        )

    def handle(self, *args, **options):
        limpiar = options['limpiar']
        cantidad_metricas = options['cantidad_metricas']
        cantidad_pruebas_carga = options['cantidad_pruebas_carga']

        if limpiar:
            self.stdout.write(self.style.WARNING('Eliminando datos existentes...'))
            MetricaSemantica.objects.all().delete()
            PruebaCarga.objects.all().delete()
            MetricaRendimiento.objects.all().delete()
            RegistroManualEnvio.objects.all().delete()
            PruebaControladaSemantica.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Datos eliminados'))

        # Obtener o crear usuario admin
        admin = Usuario.objects.filter(is_superuser=True).first()
        if not admin:
            self.stdout.write(self.style.ERROR('No se encontró usuario administrador. Cree uno primero.'))
            return

        self.stdout.write(self.style.SUCCESS('\n=== POBLANDO DATOS DE PRUEBA ===\n'))

        # 1. Crear pruebas controladas semánticas
        self.crear_pruebas_controladas(admin)

        # 2. Crear métricas semánticas
        self.crear_metricas_semanticas(admin, cantidad_metricas)

        # 3. Crear registros de generación de embeddings
        self.crear_registros_embedding(admin)

        # 4. Crear pruebas de carga
        self.crear_pruebas_carga(admin, cantidad_pruebas_carga)

        # 5. Crear métricas de rendimiento
        self.crear_metricas_rendimiento(admin)

        # 6. Crear registros manuales de envíos
        self.crear_registros_manuales(admin)

        self.stdout.write(self.style.SUCCESS('\n✅ Poblado de datos completado exitosamente'))

    def crear_pruebas_controladas(self, usuario):
        """Crea pruebas controladas semánticas de ejemplo"""
        self.stdout.write('Creando pruebas controladas semánticas...')

        pruebas = [
            {
                'nombre': 'Prueba: Envíos a Quito',
                'descripcion': 'Evaluar búsqueda de envíos destinados a Quito',
                'consulta': 'envíos entregados en Quito',
                'resultados_relevantes': []
            },
            {
                'nombre': 'Prueba: Productos Electrónicos',
                'descripcion': 'Evaluar búsqueda de envíos con productos electrónicos',
                'consulta': 'envíos con celulares y laptops',
                'resultados_relevantes': []
            },
            {
                'nombre': 'Prueba: Envíos del Mes Pasado',
                'descripcion': 'Evaluar búsqueda temporal de envíos',
                'consulta': 'envíos del mes anterior',
                'resultados_relevantes': []
            },
            {
                'nombre': 'Prueba: Envíos Entregados',
                'descripcion': 'Evaluar búsqueda por estado entregado',
                'consulta': 'envíos que ya fueron entregados',
                'resultados_relevantes': []
            },
            {
                'nombre': 'Prueba: Envíos de Alta Prioridad',
                'descripcion': 'Evaluar búsqueda de envíos urgentes',
                'consulta': 'envíos urgentes o de alta prioridad',
                'resultados_relevantes': []
            }
        ]

        # Obtener algunos IDs de envíos reales para resultados relevantes
        envios = Envio.objects.all()[:20]
        envio_ids = list(envios.values_list('id', flat=True))

        for prueba_data in pruebas:
            # Asignar algunos envíos como relevantes aleatoriamente
            prueba_data['resultados_relevantes'] = random.sample(
                envio_ids, 
                min(random.randint(3, 8), len(envio_ids))
            ) if envio_ids else []

            PruebaControladaSemantica.objects.create(
                nombre=prueba_data['nombre'],
                descripcion=prueba_data['descripcion'],
                consulta=prueba_data['consulta'],
                resultados_relevantes=prueba_data['resultados_relevantes'],
                activa=True,
                creado_por=usuario
            )

        self.stdout.write(self.style.SUCCESS(f'✓ {len(pruebas)} pruebas controladas creadas'))

    def crear_metricas_semanticas(self, usuario, cantidad):
        """Crea métricas semánticas de ejemplo"""
        self.stdout.write(f'Creando {cantidad} métricas semánticas...')

        consultas = [
            'envíos a Quito',
            'productos electrónicos',
            'envíos entregados',
            'envíos pendientes',
            'celulares y tablets',
            'ropa y accesorios',
            'envíos del último mes',
            'envíos urgentes',
            'productos deportivos',
            'envíos a Guayaquil'
        ]

        busquedas = EmbeddingBusqueda.objects.all()[:cantidad]
        
        for i in range(cantidad):
            consulta = random.choice(consultas)
            fecha = timezone.now() - timedelta(days=random.randint(0, 30))
            
            # Generar resultados rankeados simulados
            resultados_rankeados = []
            envios = Envio.objects.all()[:random.randint(5, 20)]
            for j, envio in enumerate(envios):
                resultados_rankeados.append({
                    'envio_id': envio.id,
                    'envio': {'id': envio.id, 'hawb': envio.hawb},
                    'puntuacionSimilitud': round(random.uniform(0.3, 0.95), 4),
                    'cosineSimilarity': round(random.uniform(0.3, 0.95), 4),
                    'scoreCombinado': round(random.uniform(0.3, 0.95), 4)
                })

            # Calcular métricas simuladas
            resultados_relevantes = random.sample(
                list(envios.values_list('id', flat=True)),
                min(random.randint(2, len(envios)), len(envios))
            ) if envios.exists() else []

            # Calcular MRR
            mrr = 0.0
            for pos, resultado in enumerate(resultados_rankeados[:10], 1):
                if resultado['envio_id'] in resultados_relevantes:
                    mrr = 1.0 / pos
                    break

            # Calcular nDCG@10 y Precision@5
            ndcg_10 = round(random.uniform(0.4, 0.9), 4)
            precision_5 = round(random.uniform(0.3, 0.8), 4)

            busqueda = busquedas[i] if i < len(busquedas) else None

            MetricaSemantica.objects.create(
                busqueda_semantica=busqueda,
                consulta=consulta,
                resultados_rankeados=resultados_rankeados,
                mrr=mrr,
                ndcg_10=ndcg_10,
                precision_5=precision_5,
                total_resultados=len(resultados_rankeados),
                total_relevantes_encontrados=len([r for r in resultados_rankeados if r['envio_id'] in resultados_relevantes]),
                tiempo_procesamiento_ms=random.randint(100, 2000),
                modelo_embedding='text-embedding-3-small',
                metrica_ordenamiento='score_combinado',
                fecha_calculo=fecha
            )

        self.stdout.write(self.style.SUCCESS(f'✓ {cantidad} métricas semánticas creadas'))

    def crear_registros_embedding(self, usuario):
        """Crea registros de generación de embeddings"""
        self.stdout.write('Creando registros de generación de embeddings...')

        envios = Envio.objects.all()[:100]
        estados = ['generado', 'error', 'omitido']
        tipos_proceso = ['automatico', 'manual', 'masivo']
        
        embeddings_usados = set()  # Rastrear embeddings ya usados
        registros_creados = 0

        for envio in envios:
            estado = random.choice(estados)
            tipo_proceso = random.choice(tipos_proceso)
            
            embedding = None
            mensaje_error = None
            
            if estado == 'generado':
                # Buscar un embedding que no haya sido usado
                embedding = EnvioEmbedding.objects.filter(
                    envio=envio
                ).exclude(
                    id__in=embeddings_usados
                ).first()
                
                # Si no hay embedding disponible, cambiar a 'error'
                if not embedding:
                    estado = 'error'
                    mensaje_error = 'Error al generar embedding: No se encontró embedding disponible'
                else:
                    embeddings_usados.add(embedding.id)
            elif estado == 'error':
                mensaje_error = 'Error al generar embedding: Timeout en API de OpenAI'
            
            fecha = timezone.now() - timedelta(days=random.randint(0, 60))

            try:
                registro = RegistroGeneracionEmbedding.objects.create(
                    envio=envio,
                    estado=estado,
                    dimension_embedding=1536,
                    tiempo_generacion_ms=random.randint(200, 3000),
                    modelo_usado='text-embedding-3-small',
                    tipo_proceso=tipo_proceso,
                    mensaje_error=mensaje_error,
                    embedding=embedding,
                    fecha_generacion=fecha
                )
                registros_creados += 1
            except Exception as e:
                # Si hay error de duplicado, continuar con el siguiente
                self.stdout.write(self.style.WARNING(f'  ⚠️  Error creando registro para envío {envio.hawb}: {str(e)}'))
                continue

        self.stdout.write(self.style.SUCCESS(f'✓ {registros_creados} registros de embedding creados'))

    def crear_pruebas_carga(self, usuario, cantidad):
        """Crea pruebas de carga de ejemplo"""
        self.stdout.write(f'Creando {cantidad} pruebas de carga...')

        niveles_carga = [1, 10, 30]
        tipos_prueba = ['busqueda_semantica', 'registro_envio']

        for i in range(cantidad):
            nivel = random.choice(niveles_carga)
            tipo = random.choice(tipos_prueba)
            fecha = timezone.now() - timedelta(days=random.randint(0, 15))

            prueba = PruebaCarga.objects.create(
                nombre=f'Prueba de Carga {i+1} - {nivel} operaciones',
                tipo_prueba=tipo,
                nivel_carga=nivel,
                tipo_registro='automatico' if tipo == 'registro_envio' else None,
                ejecutado_por=usuario,
                tiempo_promedio_ms=random.randint(500, 5000),
                tiempo_minimo_ms=random.randint(200, 2000),
                tiempo_maximo_ms=random.randint(3000, 10000),
                cpu_promedio=round(random.uniform(10, 50), 2),
                cpu_maximo=round(random.uniform(50, 80), 2),
                ram_promedio_mb=round(random.uniform(100, 500), 2),
                ram_maximo_mb=round(random.uniform(500, 1000), 2),
                total_exitosos=random.randint(nivel - 2, nivel),
                total_errores=random.randint(0, 2),
                datos_prueba={'consultas': [f'consulta {j+1}' for j in range(nivel)]},
                fecha_ejecucion=fecha
            )

        self.stdout.write(self.style.SUCCESS(f'✓ {cantidad} pruebas de carga creadas'))

    def crear_metricas_rendimiento(self, usuario):
        """Crea métricas de rendimiento individuales"""
        self.stdout.write('Creando métricas de rendimiento...')

        procesos = [
            'registro_envio_manual',
            'registro_envio_automatico',
            'busqueda_semantica'
        ]
        niveles_carga = [1, 10, 30, None]

        pruebas_carga = PruebaCarga.objects.all()

        for i in range(200):
            proceso = random.choice(procesos)
            nivel = random.choice(niveles_carga)
            prueba = random.choice(pruebas_carga) if pruebas_carga.exists() else None
            fecha = timezone.now() - timedelta(days=random.randint(0, 20))

            MetricaRendimiento.objects.create(
                prueba_carga=prueba,
                proceso=proceso,
                tiempo_respuesta_ms=random.randint(100, 5000),
                uso_cpu=round(random.uniform(5, 70), 2),
                uso_ram_mb=round(random.uniform(50, 800), 2),
                nivel_carga=nivel,
                exito=random.choice([True, True, True, False]),  # 75% éxito
                detalles={'operacion': f'operacion_{i+1}'},
                fecha_medicion=fecha
            )

        self.stdout.write(self.style.SUCCESS('✓ 200 métricas de rendimiento creadas'))

    def crear_registros_manuales(self, usuario):
        """Crea registros manuales de envíos"""
        self.stdout.write('Creando registros manuales de envíos...')

        # Simular tiempos de registro manual (más lentos que automáticos)
        for i in range(30):
            fecha = timezone.now() - timedelta(days=random.randint(0, 30))
            
            RegistroManualEnvio.objects.create(
                hawb=f'MANUAL{i+1:03d}',
                tiempo_registro_segundos=round(random.uniform(120, 300), 2),  # 2-5 minutos
                registrado_por=usuario,
                datos_envio={
                    'peso_total': round(random.uniform(1, 50), 2),
                    'valor_total': round(random.uniform(10, 1000), 2)
                },
                notas=f'Registro manual simulado {i+1}',
                fecha_registro=fecha
            )

        self.stdout.write(self.style.SUCCESS('✓ 30 registros manuales creados'))

