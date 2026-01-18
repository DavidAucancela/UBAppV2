"""
Comando de Django para generar embeddings de envíos usando OpenAI
Uso: python manage.py generar_embeddings [--regenerar] [--limite N] [--modelo MODELO]
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.archivos.models import Envio
from apps.busqueda.models import EnvioEmbedding
from apps.busqueda.semantic.embedding_service import EmbeddingService
from apps.busqueda.repositories import embedding_repository
import time


class Command(BaseCommand):
    help = 'Genera embeddings para envíos usando OpenAI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--regenerar',
            action='store_true',
            help='Regenera embeddings existentes',
        )
        parser.add_argument(
            '--limite',
            type=int,
            default=None,
            help='Límite de envíos a procesar',
        )
        parser.add_argument(
            '--modelo',
            type=str,
            default=None,
            help='Modelo de embedding a usar (text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002). Por defecto usa el configurado en settings.',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Tamaño del lote para procesar',
        )

    def handle(self, *args, **options):
        regenerar = options['regenerar']
        limite = options['limite']
        batch_size = options['batch_size']
        modelo = options['modelo']
        
        # Determinar modelo a usar
        if modelo:
            modelo = EmbeddingService.validar_modelo(modelo)
        else:
            modelo = EmbeddingService.get_modelo_default()
        
        self.stdout.write(
            self.style.SUCCESS(f'Usando modelo: {modelo}')
        )
        
        # Obtener envíos a procesar
        if regenerar:
            self.stdout.write(
                self.style.WARNING('Modo regenerar activado: se recrearán todos los embeddings')
            )
            # Eliminar embeddings existentes para este modelo
            EnvioEmbedding.objects.filter(modelo_usado=modelo).delete()
            self.stdout.write(self.style.SUCCESS(f'Embeddings existentes para {modelo} eliminados'))
            envios = Envio.objects.all()
        else:
            # Solo procesar envíos sin embedding para este modelo específico
            envios_con_embedding = EnvioEmbedding.objects.filter(
                modelo_usado=modelo
            ).values_list('envio_id', flat=True)
            envios = Envio.objects.exclude(id__in=envios_con_embedding)
        
        if limite:
            envios = envios[:limite]
        
        total_envios = envios.count()
        
        if total_envios == 0:
            self.stdout.write(
                self.style.SUCCESS(f'No hay envíos para procesar. Todos tienen embeddings para {modelo}.')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Procesando {total_envios} envíos con modelo {modelo}...')
        )
        
        # Procesar envíos usando el servicio de embeddings
        procesados = 0
        errores = 0
        tokens_total = 0
        costo_total = 0.0
        tiempo_inicio = time.time()
        
        for i, envio in enumerate(envios, 1):
            try:
                # Usar el servicio de embeddings que maneja todo correctamente
                embedding = EmbeddingService.generar_embedding_envio(
                    envio=envio,
                    modelo=modelo,
                    forzar_regeneracion=regenerar,
                    tipo_proceso='masivo'
                )
                
                procesados += 1
                
                # Mostrar progreso cada batch_size envíos
                if i % batch_size == 0:
                    porcentaje = (i / total_envios) * 100
                    self.stdout.write(
                        f'Progreso: {i}/{total_envios} ({porcentaje:.1f}%) - '
                        f'Procesados: {procesados}, Errores: {errores}'
                    )
                    # Pequeña pausa para no saturar la API
                    time.sleep(0.1)
                
            except Exception as e:
                errores += 1
                self.stdout.write(
                    self.style.ERROR(f'Error procesando envío {envio.hawb}: {str(e)}')
                )
                continue
        
        # Resumen final
        tiempo_total = time.time() - tiempo_inicio
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('PROCESO COMPLETADO'))
        self.stdout.write('='*60)
        self.stdout.write(f'Modelo usado: {modelo}')
        self.stdout.write(f'Total procesados: {procesados}')
        self.stdout.write(f'Errores: {errores}')
        self.stdout.write(f'Tiempo total: {tiempo_total:.2f} segundos')
        if total_envios > 0:
            self.stdout.write(f'Tiempo promedio por envío: {tiempo_total/total_envios:.2f}s')
        self.stdout.write('='*60)


























