"""
Comando para evaluar la eficiencia del panel semántico.
Ejecuta pruebas controladas (opcional), calcula MRR, NDCG@10, Precision@5 y muestra tabla comparativa.
Uso:
  python manage.py evaluar_panel_semantico
  python manage.py evaluar_panel_semantico --ejecutar
  python manage.py evaluar_panel_semantico --ejecutar --exportar reporte.csv
"""
import csv
import io
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.metricas.models import PruebaControladaSemantica
from apps.metricas.repositories import prueba_controlada_repository, metrica_semantica_repository
from apps.metricas.services import MetricaSemanticaService

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Evalúa la eficiencia del panel semántico (MRR, NDCG@10, Precision@5) y muestra tabla comparativa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--ejecutar',
            action='store_true',
            help='Ejecutar todas las pruebas controladas activas antes de mostrar el reporte'
        )
        parser.add_argument(
            '--exportar',
            type=str,
            metavar='ARCHIVO',
            help='Exportar tabla comparativa a CSV (ej: reporte.csv)'
        )
        parser.add_argument(
            '--limite',
            type=int,
            default=20,
            help='Límite de resultados por búsqueda al ejecutar pruebas (default: 20)'
        )

    def handle(self, *args, **options):
        ejecutar = options['ejecutar']
        exportar = options.get('exportar')
        limite = options['limite']

        usuario = Usuario.objects.filter(is_superuser=True).first()
        if not usuario:
            usuario = Usuario.objects.first()
        if not usuario and ejecutar:
            self.stdout.write(self.style.ERROR('No hay usuarios en el sistema. Cree uno para ejecutar pruebas.'))
            return

        if ejecutar:
            self._ejecutar_pruebas(usuario, limite)

        reporte = MetricaSemanticaService.obtener_reporte_comparativo()
        self._imprimir_tabla(reporte)

        if exportar:
            self._exportar_csv(reporte, exportar)
            self.stdout.write(self.style.SUCCESS(f'\nReporte exportado a: {exportar}'))

    def _ejecutar_pruebas(self, usuario, limite):
        pruebas = prueba_controlada_repository.obtener_activas()
        total = pruebas.count()
        if total == 0:
            self.stdout.write(self.style.WARNING('No hay pruebas controladas activas. Cree algunas en el dashboard.'))
            return
        self.stdout.write(self.style.NOTICE(f'Ejecutando {total} prueba(s) controlada(s)...'))
        for i, prueba in enumerate(pruebas, 1):
            try:
                MetricaSemanticaService.ejecutar_prueba_controlada(
                    prueba=prueba,
                    usuario=usuario,
                    filtros=None,
                    limite=limite
                )
                self.stdout.write(f'  [{i}/{total}] OK: {prueba.nombre or prueba.consulta[:50]}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  [{i}/{total}] Error: {prueba.nombre or prueba.consulta[:50]} - {e}'))
        self.stdout.write(self.style.SUCCESS(f'Pruebas ejecutadas: {total}.\n'))

    def _imprimir_tabla(self, reporte):
        filas = reporte.get('filas', [])
        resumen = reporte.get('resumen', {})

        self.stdout.write('\n' + '=' * 100)
        self.stdout.write(self.style.SUCCESS('  REPORTE COMPARATIVO - EFICIENCIA DEL PANEL SEMÁNTICO'))
        self.stdout.write('  Métricas: MRR (Mean Reciprocal Rank) | nDCG@10 | Precision@5')
        self.stdout.write('=' * 100 + '\n')

        if not filas:
            self.stdout.write(self.style.WARNING('No hay evaluaciones en el período. Ejecute pruebas controladas con --ejecutar.'))
            self._imprimir_resumen(resumen, sin_datos=True)
            return

        # Encabezado
        self.stdout.write(f"{'ID':<6} {'Consulta':<42} {'MRR':<8} {'nDCG@10':<10} {'P@5':<8} {'Interpretación':<12}")
        self.stdout.write('-' * 100)
        for r in filas[:50]:  # límite 50 filas en consola
            consulta = (r.get('consulta') or '')[:40]
            mrr = f"{r.get('mrr') or 0:.4f}" if r.get('mrr') is not None else '-'
            ndcg = f"{r.get('ndcg_10') or 0:.4f}" if r.get('ndcg_10') is not None else '-'
            p5 = f"{r.get('precision_5') or 0:.4f}" if r.get('precision_5') is not None else '-'
            interp = (r.get('interpretacion_mrr') or {}).get('etiqueta', '-')
            self.stdout.write(f"{r.get('id', ''):<6} {consulta:<42} {mrr:<8} {ndcg:<10} {p5:<8} {interp:<12}")
        if len(filas) > 50:
            self.stdout.write(f'  ... y {len(filas) - 50} filas más (ver API o exportar CSV)')

        self._imprimir_resumen(resumen)

    def _imprimir_resumen(self, resumen, sin_datos=False):
        self.stdout.write('\n' + '-' * 100)
        self.stdout.write(self.style.HTTP_INFO('  RESUMEN'))
        self.stdout.write('-' * 100)
        if sin_datos:
            self.stdout.write('  Total evaluaciones: 0')
            return
        self.stdout.write(f"  Total evaluaciones: {resumen.get('total_evaluaciones', 0)}")
        self.stdout.write(f"  MRR  - Promedio: {resumen.get('mrr_promedio', 0):.4f}  |  Máx: {resumen.get('mrr_maximo', 0):.4f}  |  Mín: {resumen.get('mrr_minimo', 0):.4f}")
        self.stdout.write(f"  nDCG@10 - Promedio: {resumen.get('ndcg_10_promedio', 0):.4f}")
        self.stdout.write(f"  Precision@5 - Promedio: {resumen.get('precision_5_promedio', 0):.4f}")
        interp = resumen.get('interpretacion_global') or {}
        self.stdout.write(self.style.SUCCESS(f"  Interpretación global: {interp.get('etiqueta', '-')} - {interp.get('descripcion', '')}"))
        self.stdout.write('=' * 100 + '\n')

    def _exportar_csv(self, reporte, path):
        filas = reporte.get('filas', [])
        resumen = reporte.get('resumen', {})
        with io.open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['ID', 'Consulta', 'Fecha', 'MRR', 'nDCG@10', 'Precision@5', 'Total resultados', 'Relevantes encontrados', 'Interpretación MRR', 'Interpretación nDCG', 'Interpretación P@5'])
            for r in filas:
                w.writerow([
                    r.get('id'),
                    r.get('consulta_completa') or r.get('consulta'),
                    r.get('fecha_calculo'),
                    r.get('mrr'),
                    r.get('ndcg_10'),
                    r.get('precision_5'),
                    r.get('total_resultados'),
                    r.get('total_relevantes_encontrados'),
                    (r.get('interpretacion_mrr') or {}).get('etiqueta'),
                    (r.get('interpretacion_ndcg') or {}).get('etiqueta'),
                    (r.get('interpretacion_precision') or {}).get('etiqueta'),
                ])
            w.writerow([])
            w.writerow(['RESUMEN', '', '', '', '', '', '', '', '', '', ''])
            w.writerow(['Total evaluaciones', resumen.get('total_evaluaciones'), '', '', '', '', '', '', '', '', ''])
            w.writerow(['MRR promedio', resumen.get('mrr_promedio'), 'MRR máx', resumen.get('mrr_maximo'), 'MRR mín', resumen.get('mrr_minimo'), '', '', '', '', ''])
            w.writerow(['nDCG@10 promedio', resumen.get('ndcg_10_promedio'), '', '', '', '', '', '', '', '', ''])
            w.writerow(['Precision@5 promedio', resumen.get('precision_5_promedio'), '', '', '', '', '', '', '', '', ''])
            w.writerow(['Interpretación global', (resumen.get('interpretacion_global') or {}).get('etiqueta'), (resumen.get('interpretacion_global') or {}).get('descripcion'), '', '', '', '', '', '', '', ''])
