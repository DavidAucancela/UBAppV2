"""
Comando de Django para generar embeddings de envíos usando OpenAI
Uso: python manage.py generar_embeddings [--regenerar] [--limite N]
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.archivos.models import Envio
from apps.busqueda.models import EnvioEmbedding
from openai import OpenAI
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
            '--batch-size',
            type=int,
            default=10,
            help='Tamaño del lote para procesar',
        )

    def handle(self, *args, **options):
        regenerar = options['regenerar']
        limite = options['limite']
        batch_size = options['batch_size']
        
        # Inicializar cliente OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Obtener envíos a procesar
        if regenerar:
            self.stdout.write(
                self.style.WARNING('Modo regenerar activado: se recrearán todos los embeddings')
            )
            envios = Envio.objects.all()
            # Eliminar embeddings existentes si se regenera
            EnvioEmbedding.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Embeddings existentes eliminados'))
        else:
            # Solo procesar envíos sin embedding
            envios_con_embedding = EnvioEmbedding.objects.values_list('envio_id', flat=True)
            envios = Envio.objects.exclude(id__in=envios_con_embedding)
        
        if limite:
            envios = envios[:limite]
        
        total_envios = envios.count()
        
        if total_envios == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ No hay envíos para procesar. Todos tienen embeddings.')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'📦 Procesando {total_envios} envíos...')
        )
        
        # Procesar envíos
        procesados = 0
        errores = 0
        tiempo_inicio = time.time()
        
        for i, envio in enumerate(envios, 1):
            try:
                # Generar texto descriptivo
                texto = self._generar_texto_envio(envio)
                
                # Generar embedding
                response = client.embeddings.create(
                    model=settings.OPENAI_EMBEDDING_MODEL,
                    input=texto,
                    encoding_format="float"
                )
                
                vector = response.data[0].embedding
                
                # Guardar embedding
                envio_embedding = EnvioEmbedding.objects.create(
                    envio=envio,
                    texto_indexado=texto,
                    modelo_usado=settings.OPENAI_EMBEDDING_MODEL
                )
                envio_embedding.set_vector(vector)
                envio_embedding.save()
                
                procesados += 1
                
                # Mostrar progreso cada batch_size envíos
                if i % batch_size == 0:
                    porcentaje = (i / total_envios) * 100
                    self.stdout.write(
                        f'Progreso: {i}/{total_envios} ({porcentaje:.1f}%) - '
                        f'Procesados: {procesados}, Errores: {errores}'
                    )
                    # Pequeña pausa para no saturar la API
                    time.sleep(0.5)
                
            except Exception as e:
                errores += 1
                self.stdout.write(
                    self.style.ERROR(f'❌ Error procesando envío {envio.hawb}: {str(e)}')
                )
                continue
        
        # Resumen final
        tiempo_total = time.time() - tiempo_inicio
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ PROCESO COMPLETADO'))
        self.stdout.write('='*60)
        self.stdout.write(f'Total procesados: {procesados}')
        self.stdout.write(f'Errores: {errores}')
        self.stdout.write(f'Tiempo total: {tiempo_total:.2f} segundos')
        self.stdout.write(f'Tiempo promedio por envío: {tiempo_total/total_envios:.2f}s')
        self.stdout.write('='*60)

    def _generar_texto_envio(self, envio):
        """Genera texto descriptivo del envío para indexación"""
        partes = [
            f"HAWB: {envio.hawb}",
            f"Comprador: {envio.comprador.nombre}",
            f"Ciudad: {envio.comprador.ciudad or 'No especificada'}",
            f"Estado: {envio.get_estado_display()}",
            f"Fecha: {envio.fecha_emision.strftime('%Y-%m-%d')}",
            f"Peso: {envio.peso_total} kg",
            f"Valor: ${envio.valor_total}",
        ]
        
        # Agregar información de productos
        productos = envio.productos.all()
        if productos:
            descripciones = [p.descripcion for p in productos[:5]]
            partes.append(f"Productos: {', '.join(descripciones)}")
        
        # Agregar observaciones si existen
        if envio.observaciones:
            partes.append(f"Observaciones: {envio.observaciones}")
        
        return " | ".join(partes)
























