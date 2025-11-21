"""
Comando para generar embeddings de todos los envíos existentes de forma masiva
"""
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from apps.archivos.models import Envio
from apps.busqueda.models import EnvioEmbedding
from apps.busqueda.utils_embeddings import generar_embedding_envio
from django.conf import settings
import time


class Command(BaseCommand):
    help = 'Genera embeddings para todos los envíos existentes que no los tengan'

    def add_arguments(self, parser):
        parser.add_argument(
            '--forzar',
            action='store_true',
            help='Forzar regeneración de embeddings existentes',
        )
        parser.add_argument(
            '--modelo',
            type=str,
            default=None,
            help='Modelo de OpenAI a usar (text-embedding-3-small, text-embedding-3-large)',
        )
        parser.add_argument(
            '--limite',
            type=int,
            default=None,
            help='Límite de envíos a procesar (útil para pruebas)',
        )
        parser.add_argument(
            '--hawb',
            type=str,
            default=None,
            help='Procesar solo un envío específico por HAWB',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Tamaño de lote para procesamiento (por defecto 50)',
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.1,
            help='Retraso en segundos entre cada embedding (para evitar rate limits)',
        )

    def handle(self, *args, **options):
        forzar = options['forzar']
        modelo = options['modelo'] or getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        limite = options['limite']
        hawb_especifico = options['hawb']
        batch_size = options['batch_size']
        delay = options['delay']

        self.stdout.write(self.style.SUCCESS(f'=== Generación de Embeddings ==='))
        self.stdout.write(f'Modelo: {modelo}')
        self.stdout.write(f'Forzar regeneración: {"Sí" if forzar else "No"}')
        self.stdout.write(f'Batch size: {batch_size}')
        self.stdout.write(f'Delay: {delay}s')
        self.stdout.write('')

        # Obtener envíos a procesar
        if hawb_especifico:
            try:
                envios = Envio.objects.filter(hawb=hawb_especifico).select_related('comprador').prefetch_related('productos')
                self.stdout.write(f'Procesando envío específico: {hawb_especifico}')
            except Envio.DoesNotExist:
                raise CommandError(f'No se encontró el envío con HAWB: {hawb_especifico}')
        else:
            envios = Envio.objects.all().select_related('comprador').prefetch_related('productos')
            
            if not forzar:
                # Excluir envíos que ya tienen embedding con este modelo
                envios_con_embedding = EnvioEmbedding.objects.filter(
                    modelo_usado=modelo
                ).values_list('envio_id', flat=True)
                envios = envios.exclude(id__in=envios_con_embedding)
            
            if limite:
                envios = envios[:limite]

        total_envios = envios.count()
        
        if total_envios == 0:
            self.stdout.write(self.style.WARNING('No hay envíos para procesar.'))
            return

        self.stdout.write(f'Total de envíos a procesar: {total_envios}\n')

        # Estadísticas
        exitosos = 0
        errores = 0
        omitidos = 0
        costo_total = 0.0
        tiempo_inicio = time.time()

        # Procesar en lotes
        for i, envio in enumerate(envios, 1):
            try:
                # Verificar si ya existe (solo si no se fuerza)
                if not forzar:
                    if EnvioEmbedding.objects.filter(envio=envio, modelo_usado=modelo).exists():
                        omitidos += 1
                        self.stdout.write(f'  [{i}/{total_envios}] ⏭️  Omitido: {envio.hawb} (ya existe)')
                        continue

                # Generar embedding
                envio_embedding = generar_embedding_envio(envio, modelo=modelo, forzar_regeneracion=forzar)
                
                exitosos += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  [{i}/{total_envios}] ✅ Generado: {envio.hawb}')
                )

                # Pausa para evitar rate limits de OpenAI
                if delay > 0 and i < total_envios:
                    time.sleep(delay)

                # Mostrar progreso cada batch_size envíos
                if i % batch_size == 0:
                    tiempo_transcurrido = time.time() - tiempo_inicio
                    promedio_por_envio = tiempo_transcurrido / i
                    tiempo_restante = promedio_por_envio * (total_envios - i)
                    
                    self.stdout.write(
                        f'\n📊 Progreso: {i}/{total_envios} ({(i/total_envios)*100:.1f}%)'
                    )
                    self.stdout.write(
                        f'   Tiempo restante estimado: {tiempo_restante/60:.1f} minutos\n'
                    )

            except Exception as e:
                errores += 1
                self.stdout.write(
                    self.style.ERROR(f'  [{i}/{total_envios}] ❌ Error en {envio.hawb}: {str(e)}')
                )
                # Continuar con el siguiente envío

        # Resumen final
        tiempo_total = time.time() - tiempo_inicio
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('=== Resumen de Generación ==='))
        self.stdout.write(f'Total procesados: {total_envios}')
        self.stdout.write(self.style.SUCCESS(f'✅ Exitosos: {exitosos}'))
        if omitidos > 0:
            self.stdout.write(self.style.WARNING(f'⏭️  Omitidos: {omitidos}'))
        if errores > 0:
            self.stdout.write(self.style.ERROR(f'❌ Errores: {errores}'))
        self.stdout.write(f'⏱️  Tiempo total: {tiempo_total/60:.2f} minutos')
        self.stdout.write(f'⚡ Promedio por envío: {tiempo_total/total_envios:.2f} segundos')
        
        # Mostrar estadísticas finales
        total_embeddings = EnvioEmbedding.objects.filter(modelo_usado=modelo).count()
        self.stdout.write(f'\n📈 Total de embeddings en BD (modelo {modelo}): {total_embeddings}')
        self.stdout.write('='*60)

