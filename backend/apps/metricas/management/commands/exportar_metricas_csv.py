"""
Comando de gestión para exportar métricas a CSV.
Uso: python manage.py exportar_metricas_csv --tipo semanticas --fecha-desde 2025-01-01
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.metricas.services import ExportacionMetricasService
import os


class Command(BaseCommand):
    help = 'Exporta métricas a archivos CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            type=str,
            choices=['semanticas', 'rendimiento', 'ambos'],
            default='ambos',
            help='Tipo de métricas a exportar'
        )
        parser.add_argument(
            '--fecha-desde',
            type=str,
            help='Fecha desde (formato: YYYY-MM-DD)'
        )
        parser.add_argument(
            '--fecha-hasta',
            type=str,
            help='Fecha hasta (formato: YYYY-MM-DD)'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='exports',
            help='Directorio de salida para los archivos CSV'
        )

    def handle(self, *args, **options):
        tipo = options['tipo']
        fecha_desde = options.get('fecha_desde')
        fecha_hasta = options.get('fecha_hasta')
        output_dir = options['output_dir']
        
        # Crear directorio de salida si no existe
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Exportar métricas semánticas
        if tipo in ['semanticas', 'ambos']:
            self.stdout.write('Exportando métricas semánticas...')
            csv_content = ExportacionMetricasService.exportar_metricas_semanticas_csv(
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta
            )
            
            filename = os.path.join(output_dir, 'metricas_semanticas.csv')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Métricas semánticas exportadas a: {filename}')
            )
        
        # Exportar métricas de rendimiento
        if tipo in ['rendimiento', 'ambos']:
            self.stdout.write('Exportando métricas de rendimiento...')
            csv_content = ExportacionMetricasService.exportar_metricas_rendimiento_csv(
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta
            )
            
            filename = os.path.join(output_dir, 'metricas_rendimiento.csv')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ Métricas de rendimiento exportadas a: {filename}')
            )
        
        self.stdout.write(self.style.SUCCESS('\n✅ Exportación completada'))

