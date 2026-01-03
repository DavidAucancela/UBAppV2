"""
Comando de gestión para pruebas de eficiencia y desempeño del sistema.

Este script realiza pruebas de rendimiento para:
- Tiempos de respuesta
- Tiempos de espera (latencia)
- Utilización de recursos (CPU, memoria)

Procesos evaluados:
1. Registro de envíos
2. Asignación de tarifas
3. Búsqueda semántica

Uso:
    python manage.py pruebas_rendimiento [--iteraciones N] [--usuario USERNAME] [--exportar]
"""
import time
import statistics
import psutil
import os
import math
from datetime import datetime
from typing import Dict, List, Any, Tuple
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal

try:
    from scipy import stats as scipy_stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("⚠️  scipy no está disponible. Algunos tests estadísticos avanzados no funcionarán.")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️  numpy no está disponible. La generación de datos simulados no funcionará.")

from apps.archivos.services import EnvioService, TarifaService
from apps.archivos.models import Envio, Tarifa, Producto
from apps.busqueda.services import BusquedaSemanticaService

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Realiza pruebas de eficiencia y desempeño del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--iteraciones',
            type=int,
            default=10,
            help='Número de iteraciones por prueba (default: 10)'
        )
        parser.add_argument(
            '--usuario',
            type=str,
            default='admin',
            help='Usuario para realizar las pruebas (default: admin)'
        )
        parser.add_argument(
            '--exportar',
            action='store_true',
            help='Exportar resultados a archivo JSON'
        )
        parser.add_argument(
            '--proceso',
            type=str,
            choices=['envios', 'tarifas', 'busqueda', 'todos'],
            default='todos',
            help='Proceso específico a probar (default: todos)'
        )

    def handle(self, *args, **options):
        iteraciones = options['iteraciones']
        username = options['usuario']
        exportar = options['exportar']
        proceso = options['proceso']
        
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
        
        self.stdout.write(self.style.SUCCESS(f'\n{"="*80}'))
        self.stdout.write(self.style.SUCCESS('PRUEBAS DE EFICIENCIA Y DESEMPEÑO'))
        self.stdout.write(self.style.SUCCESS(f'{"="*80}\n'))
        self.stdout.write(f'Usuario: {usuario.username}')
        self.stdout.write(f'Iteraciones por prueba: {iteraciones}')
        self.stdout.write(f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        
        resultados = {}
        
        # 4.1 Análisis descriptivo de tiempos de respuesta (con comparativa manual vs automatizado)
        if proceso in ['envios', 'todos']:
            self.stdout.write(self.style.WARNING('\n4.1.1 Proceso de registro de envíos'))
            resultados['registro_envios'] = self._probar_registro_envios(usuario, iteraciones)
            self._mostrar_comparativa_proceso(resultados.get('registro_envios'), 'Registro de Envíos')
        
        if proceso in ['tarifas', 'todos']:
            self.stdout.write(self.style.WARNING('\n4.1.2 Proceso de asignación de tarifas'))
            resultados['asignacion_tarifas'] = self._probar_asignacion_tarifas(iteraciones)
            self._mostrar_comparativa_proceso(resultados.get('asignacion_tarifas'), 'Asignación de Tarifas')
        
        if proceso in ['busqueda', 'todos']:
            self.stdout.write(self.style.WARNING('\n4.1.3 Proceso de búsqueda semántica'))
            resultados['busqueda_semantica'] = self._probar_busqueda_semantica(usuario, iteraciones)
            self._mostrar_comparativa_proceso(resultados.get('busqueda_semantica'), 'Búsqueda Semántica')
        
        # 4.2 Análisis inferencial de tiempos de respuesta (con tests estadísticos)
        self.stdout.write(self.style.WARNING('\n4.2 Análisis inferencial de tiempos de respuesta'))
        resultados['analisis_inferencial_respuesta'] = self._analisis_inferencial_respuesta(resultados)
        
        # Test t-student comparativo: Manual vs Automatizado (solo para envios y tarifas)
        self.stdout.write(self.style.WARNING('\n4.2.4 Test t-student comparativo: Proceso Manual vs Automatizado'))
        if proceso in ['envios', 'todos']:
            self._mostrar_test_t_student_comparativo('registro_envios', 'Registro de Envíos')
        if proceso in ['tarifas', 'todos']:
            self._mostrar_test_t_student_comparativo('asignacion_tarifas', 'Asignación de Tarifas')
        # Búsqueda semántica NO tiene comparativa manual vs automatizado
        # En su lugar, se clasifica por umbrales (ver sección 4.2.5)
        
        # Clasificación por umbrales para tiempo de respuesta
        self.stdout.write(self.style.WARNING('\n4.2.5 Clasificación por umbrales de tiempo de respuesta'))
        self._clasificar_tiempo_respuesta_umbrales(resultados)
        
        # 4.3 Análisis descriptivo de tiempos de espera
        self.stdout.write(self.style.WARNING('\n4.3 Análisis descriptivo de tiempos de espera'))
        resultados['tiempos_espera'] = self._analizar_tiempos_espera(resultados)
        
        # 4.4 Análisis inferencial de tiempos de espera (con tests estadísticos)
        self.stdout.write(self.style.WARNING('\n4.4 Análisis inferencial de tiempos de espera'))
        resultados['analisis_inferencial_espera'] = self._analisis_inferencial_espera(resultados)
        
        # 4.5 Análisis descriptivo de utilización de recursos
        self.stdout.write(self.style.WARNING('\n4.5 Análisis descriptivo de utilización de recursos'))
        resultados['utilizacion_recursos'] = self._analizar_recursos(resultados)
        
        # 4.6 Análisis inferencial de utilización de recursos
        self.stdout.write(self.style.WARNING('\n4.6 Análisis inferencial de utilización de recursos'))
        resultados['analisis_inferencial_recursos'] = self._analisis_inferencial_recursos(resultados)
        
        # Comparativa proceso manual vs sistema web (resumen general)
        self.stdout.write(self.style.WARNING('\nComparativa: Proceso Manual vs Sistema Web (Resumen)'))
        self._mostrar_comparativa_manual_vs_web(resultados)
        
        # Resumen final
        self._mostrar_resumen(resultados)
        
        if exportar:
            self._exportar_resultados(resultados)
    
    def _probar_registro_envios(self, usuario, iteraciones: int) -> Dict[str, Any]:
        """Prueba el proceso de registro de envíos"""
        tiempos_respuesta = []
        tiempos_espera = []
        recursos_por_iteracion = []
        
        # Obtener un comprador de prueba
        comprador = Usuario.objects.filter(rol=4).first()
        if not comprador:
            self.stdout.write(self.style.ERROR('No hay compradores disponibles para prueba'))
            return {}
        
        proceso = psutil.Process(os.getpid())
        # Inicializar cpu_percent (primera llamada sin intervalo)
        proceso.cpu_percent()
        
        for i in range(iteraciones):
            # Medir memoria antes
            memoria_antes = proceso.memory_info().rss / 1024 / 1024
            
            # Datos de prueba
            datos_envio = {
                'hawb': f'TEST-{int(time.time())}-{i}',
                'peso_total': Decimal('10.50'),
                'cantidad_total': 2,
                'valor_total': Decimal('150.00'),
                'comprador': comprador,  # Pasar la instancia directamente
                'estado': 'pendiente',
                'productos': [
                    {
                        'descripcion': f'Producto de prueba {i}',
                        'categoria': 'electronica',
                        'peso': Decimal('5.25'),
                        'cantidad': 2,
                        'valor': Decimal('75.00')
                    }
                ]
            }
            
            # Medir tiempo de respuesta y CPU durante la operación
            inicio_respuesta = time.time()
            try:
                envio = EnvioService.crear_envio(datos_envio, usuario)
                tiempo_respuesta = (time.time() - inicio_respuesta) * 1000  # ms
                tiempos_respuesta.append(tiempo_respuesta)
                
                # Medir CPU durante la operación (con intervalo basado en tiempo real)
                # cpu_percent(interval=None) devuelve el porcentaje desde la última llamada
                cpu_usado = proceso.cpu_percent(interval=None)
                
                # Medir tiempo de espera (latencia total)
                tiempo_espera = tiempo_respuesta  # En este caso es el mismo
                tiempos_espera.append(tiempo_espera)
                
                # Medir memoria después
                memoria_despues = proceso.memory_info().rss / 1024 / 1024
                
                recursos_por_iteracion.append({
                    'cpu_delta': cpu_usado,
                    'memoria_delta_mb': memoria_despues - memoria_antes
                })
                
                # Reinicializar para la siguiente iteración
                proceso.cpu_percent()
                
                # Limpiar envío de prueba
                envio.delete()
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error en iteración {i+1}: {str(e)}'))
                continue
        
        return self._calcular_estadisticas(
            tiempos_respuesta, tiempos_espera, recursos_por_iteracion, 'Registro de Envíos'
        )
    
    def _probar_asignacion_tarifas(self, iteraciones: int) -> Dict[str, Any]:
        """Prueba el proceso de asignación de tarifas"""
        tiempos_respuesta = []
        tiempos_espera = []
        recursos_por_iteracion = []
        
        # Categorías y pesos de prueba
        categorias_pesos = [
            ('electronica', 5.0),
            ('ropa', 2.5),
            ('hogar', 10.0),
            ('deportes', 3.0),
            ('otros', 1.5),
        ]
        
        proceso = psutil.Process(os.getpid())
        # Inicializar cpu_percent (primera llamada sin intervalo)
        proceso.cpu_percent()
        
        for i in range(iteraciones):
            categoria, peso = categorias_pesos[i % len(categorias_pesos)]
            
            # Medir memoria antes
            memoria_antes = proceso.memory_info().rss / 1024 / 1024
            
            # Medir tiempo de respuesta
            inicio_respuesta = time.time()
            try:
                resultado = TarifaService.buscar_tarifa(categoria, peso)
                tiempo_respuesta = (time.time() - inicio_respuesta) * 1000  # ms
                tiempos_respuesta.append(tiempo_respuesta)
                
                # Calcular costo también
                inicio_costo = time.time()
                costo = TarifaService.calcular_costo(categoria, peso, cantidad=1)
                tiempo_costo = (time.time() - inicio_costo) * 1000
                
                tiempo_espera = tiempo_respuesta + tiempo_costo
                tiempos_espera.append(tiempo_espera)
                
                # Medir CPU durante la operación
                cpu_usado = proceso.cpu_percent(interval=None)
                
                # Medir memoria después
                memoria_despues = proceso.memory_info().rss / 1024 / 1024
                
                recursos_por_iteracion.append({
                    'cpu_delta': cpu_usado,
                    'memoria_delta_mb': memoria_despues - memoria_antes
                })
                
                # Reinicializar para la siguiente iteración
                proceso.cpu_percent()
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error en iteración {i+1}: {str(e)}'))
                continue
        
        return self._calcular_estadisticas(
            tiempos_respuesta, tiempos_espera, recursos_por_iteracion, 'Asignación de Tarifas'
        )
    
    def _probar_busqueda_semantica(self, usuario, iteraciones: int) -> Dict[str, Any]:
        """Prueba el proceso de búsqueda semántica"""
        tiempos_respuesta = []
        tiempos_espera = []
        recursos_por_iteracion = []
        
        consultas = [
            'envíos entregados',
            'productos electrónicos',
            'paquetes pesados',
            'envíos a Quito',
            'productos de ropa',
            'envíos pendientes',
            'artículos del hogar',
            'productos deportivos',
            'envíos cancelados',
            'dispositivos electrónicos',
        ]
        
        proceso = psutil.Process(os.getpid())
        # Inicializar cpu_percent (primera llamada sin intervalo)
        proceso.cpu_percent()
        
        for i in range(iteraciones):
            consulta = consultas[i % len(consultas)]
            
            # Medir memoria antes
            memoria_antes = proceso.memory_info().rss / 1024 / 1024
            
            # Medir tiempo de respuesta
            inicio_respuesta = time.time()
            try:
                resultado = BusquedaSemanticaService.buscar(
                    consulta=consulta,
                    usuario=usuario,
                    limite=20
                )
                tiempo_respuesta = resultado.get('tiempoRespuesta', 0)
                tiempos_respuesta.append(tiempo_respuesta)
                
                # Tiempo de espera es el mismo que tiempo de respuesta
                tiempos_espera.append(tiempo_respuesta)
                
                # Medir CPU durante la operación
                cpu_usado = proceso.cpu_percent(interval=None)
                
                # Medir memoria después
                memoria_despues = proceso.memory_info().rss / 1024 / 1024
                
                recursos_por_iteracion.append({
                    'cpu_delta': cpu_usado,
                    'memoria_delta_mb': memoria_despues - memoria_antes
                })
                
                # Reinicializar para la siguiente iteración
                proceso.cpu_percent()
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error en iteración {i+1}: {str(e)}'))
                continue
        
        return self._calcular_estadisticas(
            tiempos_respuesta, tiempos_espera, recursos_por_iteracion, 'Búsqueda Semántica'
        )
    
    def _calcular_estadisticas(
        self, 
        tiempos_respuesta: List[float],
        tiempos_espera: List[float],
        recursos: List[Dict],
        nombre_proceso: str
    ) -> Dict[str, Any]:
        """Calcula estadísticas descriptivas"""
        if not tiempos_respuesta:
            return {}
        
        # Estadísticas de tiempos de respuesta
        stats_respuesta = {
            'media': statistics.mean(tiempos_respuesta),
            'mediana': statistics.median(tiempos_respuesta),
            'desviacion_estandar': statistics.stdev(tiempos_respuesta) if len(tiempos_respuesta) > 1 else 0,
            'minimo': min(tiempos_respuesta),
            'maximo': max(tiempos_respuesta),
            'percentil_25': self._percentil(tiempos_respuesta, 25),
            'percentil_75': self._percentil(tiempos_respuesta, 75),
            'percentil_95': self._percentil(tiempos_respuesta, 95),
        }
        
        # Estadísticas de tiempos de espera
        stats_espera = {
            'media': statistics.mean(tiempos_espera),
            'mediana': statistics.median(tiempos_espera),
            'desviacion_estandar': statistics.stdev(tiempos_espera) if len(tiempos_espera) > 1 else 0,
            'minimo': min(tiempos_espera),
            'maximo': max(tiempos_espera),
        }
        
        # Estadísticas de recursos
        cpus = [r['cpu_delta'] for r in recursos]
        memorias = [r['memoria_delta_mb'] for r in recursos]
        
        stats_recursos = {
            'cpu': {
                'media': statistics.mean(cpus) if cpus else 0,
                'maximo': max(cpus) if cpus else 0,
            },
            'memoria_mb': {
                'media': statistics.mean(memorias) if memorias else 0,
                'maximo': max(memorias) if memorias else 0,
            }
        }
        
        # Mostrar resultados
        self.stdout.write(f'\n{nombre_proceso}:')
        self.stdout.write(f'  Tiempo de respuesta promedio: {stats_respuesta["media"]:.2f} ms')
        self.stdout.write(f'  Tiempo de respuesta mediano: {stats_respuesta["mediana"]:.2f} ms')
        self.stdout.write(f'  Desviación estándar: {stats_respuesta["desviacion_estandar"]:.2f} ms')
        self.stdout.write(f'  Mínimo: {stats_respuesta["minimo"]:.2f} ms')
        self.stdout.write(f'  Máximo: {stats_respuesta["maximo"]:.2f} ms')
        self.stdout.write(f'  P95: {stats_respuesta["percentil_95"]:.2f} ms')
        
        return {
            'tiempos_respuesta': tiempos_respuesta,
            'tiempos_espera': tiempos_espera,
            'recursos': recursos,
            'estadisticas_respuesta': stats_respuesta,
            'estadisticas_espera': stats_espera,
            'estadisticas_recursos': stats_recursos,
            'nombre': nombre_proceso
        }
    
    def _percentil(self, datos: List[float], percentil: int) -> float:
        """Calcula un percentil"""
        datos_ordenados = sorted(datos)
        k = (len(datos_ordenados) - 1) * (percentil / 100)
        f = int(k)
        c = k - f
        if f + 1 < len(datos_ordenados):
            return datos_ordenados[f] + c * (datos_ordenados[f + 1] - datos_ordenados[f])
        return datos_ordenados[f]
    
    def _test_normalidad(self, datos: List[float]) -> Tuple[bool, float, str]:
        """Realiza test de normalidad Shapiro-Wilk"""
        if not SCIPY_AVAILABLE or len(datos) < 3:
            # Aproximación simple: si n < 3, asumir normalidad
            return True, 1.0, "No aplicable (n < 3)"
        
        try:
            if len(datos) > 5000:
                # Shapiro-Wilk solo funciona hasta 5000 muestras
                datos = datos[:5000]
            
            stat, p_value = scipy_stats.shapiro(datos)
            es_normal = p_value > 0.05  # α = 0.05
            
            interpretacion = "Normal" if es_normal else "No normal"
            return es_normal, p_value, interpretacion
        except Exception as e:
            return True, 1.0, f"Error: {str(e)}"
    
    def _test_t_student(self, datos: List[float], valor_referencia: float = None) -> Dict[str, Any]:
        """Realiza test t-student para una muestra"""
        if not SCIPY_AVAILABLE or len(datos) < 2:
            return {}
        
        try:
            if valor_referencia is None:
                # Test t-student de una muestra (H0: media = 0)
                stat, p_value = scipy_stats.ttest_1samp(datos, 0)
            else:
                # Test t-student de una muestra (H0: media = valor_referencia)
                stat, p_value = scipy_stats.ttest_1samp(datos, valor_referencia)
            
            # Manejar p-values muy pequeños
            if p_value < 1e-15:
                p_value_mostrar = 0.0
            else:
                p_value_mostrar = p_value
            
            significativo = p_value < 0.05
            return {
                'estadistico_t': stat,
                'p_value': p_value,  # Valor original
                'p_value_mostrar': p_value_mostrar,  # Valor para mostrar
                'significativo': significativo,
                'interpretacion': 'Significativo (p < 0.05)' if significativo else 'No significativo (p >= 0.05)'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _test_wilcoxon_una_muestra(self, datos: List[float], valor_referencia: float = 0) -> Dict[str, Any]:
        """
        Realiza test de Wilcoxon para una muestra (no paramétrico)
        Se usa cuando los datos NO son normales
        """
        if not SCIPY_AVAILABLE or len(datos) < 2:
            return {}
        
        try:
            # Restar el valor de referencia
            datos_centrados = [d - valor_referencia for d in datos]
            stat, p_value = scipy_stats.wilcoxon(datos_centrados, alternative='two-sided')
            
            # Manejar p-values muy pequeños
            if p_value < 1e-15:
                p_value_mostrar = 0.0
            else:
                p_value_mostrar = p_value
            
            significativo = p_value < 0.05
            return {
                'estadistico_w': stat,
                'p_value': p_value,
                'p_value_mostrar': p_value_mostrar,
                'significativo': significativo,
                'interpretacion': 'Significativo (p < 0.05)' if significativo else 'No significativo (p >= 0.05)'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _test_mann_whitney(self, grupo1: List[float], grupo2: List[float]) -> Dict[str, Any]:
        """Realiza test de Mann-Whitney U (no paramétrico) para dos muestras independientes"""
        if not SCIPY_AVAILABLE or len(grupo1) < 2 or len(grupo2) < 2:
            return {}
        
        try:
            stat, p_value = scipy_stats.mannwhitneyu(grupo1, grupo2, alternative='two-sided')
            
            # Manejar p-values muy pequeños
            if p_value < 1e-15:
                p_value_mostrar = 0.0
            else:
                p_value_mostrar = p_value
            
            significativo = p_value < 0.05
            return {
                'estadistico_u': stat,
                'p_value': p_value,
                'p_value_mostrar': p_value_mostrar,
                'significativo': significativo,
                'interpretacion': 'Diferencia significativa (p < 0.05)' if significativo else 'Sin diferencia significativa (p >= 0.05)'
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _test_t_student_dos_muestras(self, grupo1: List[float], grupo2: List[float], 
                                      nombre_grupo1: str = "Grupo 1", 
                                      nombre_grupo2: str = "Grupo 2") -> Dict[str, Any]:
        """
        Realiza test t-student para comparar dos muestras independientes
        
        Args:
            grupo1: Lista de valores del primer grupo (proceso manual)
            grupo2: Lista de valores del segundo grupo (proceso automatizado)
            nombre_grupo1: Nombre del primer grupo
            nombre_grupo2: Nombre del segundo grupo
        
        Returns:
            Diccionario con resultados del test
        """
        if not SCIPY_AVAILABLE or len(grupo1) < 2 or len(grupo2) < 2:
            return {'error': 'Se requieren al menos 2 observaciones en cada grupo y scipy disponible'}
        
        try:
            # PASO 1: Test de normalidad para ambos grupos (DEBE SER PRIMERO)
            normal1, p_norm1, interp1 = self._test_normalidad(grupo1)
            normal2, p_norm2, interp2 = self._test_normalidad(grupo2)
            
            # Decidir qué test aplicar según normalidad
            ambos_normales = normal1 and normal2
            test_aplicado = None
            stat_test = None
            p_value = None
            
            if ambos_normales:
                # Si ambos grupos son normales → usar test t-student (paramétrico)
                # Test de igualdad de varianzas (Levene)
                stat_levene, p_levene = scipy_stats.levene(grupo1, grupo2)
                varianzas_iguales = p_levene > 0.05
                
                # Test t-student para dos muestras independientes
                stat_t, p_value = scipy_stats.ttest_ind(grupo1, grupo2, equal_var=varianzas_iguales)
                stat_test = stat_t
                test_aplicado = 't-student (paramétrico)'
            else:
                # Si alguno NO es normal → usar test Mann-Whitney U (no paramétrico)
                test_mw = self._test_mann_whitney(grupo1, grupo2)
                stat_test = test_mw.get('estadistico_u', 0)
                p_value = test_mw.get('p_value', 1.0)
                test_aplicado = 'Mann-Whitney U (no paramétrico)'
                varianzas_iguales = None
                stat_levene = None
                p_levene = None
            
            # Calcular estadísticas descriptivas
            media1 = statistics.mean(grupo1)
            media2 = statistics.mean(grupo2)
            desv1 = statistics.stdev(grupo1) if len(grupo1) > 1 else 0
            desv2 = statistics.stdev(grupo2) if len(grupo2) > 1 else 0
            n1 = len(grupo1)
            n2 = len(grupo2)
            
            # Diferencia de medias
            diferencia_medias = media1 - media2
            
            # Error estándar de la diferencia (solo para tests paramétricos)
            if ambos_normales:
                if varianzas_iguales:
                    # Varianza combinada (pooled variance)
                    var_pooled = ((n1 - 1) * desv1**2 + (n2 - 1) * desv2**2) / (n1 + n2 - 2)
                    se_diferencia = math.sqrt(var_pooled * (1/n1 + 1/n2))
                    gl = n1 + n2 - 2
                    tipo_test = "t-student estándar (varianzas iguales)"
                else:
                    # Test de Welch
                    se_diferencia = math.sqrt((desv1**2 / n1) + (desv2**2 / n2))
                    gl = ((desv1**2/n1 + desv2**2/n2)**2) / (((desv1**2/n1)**2/(n1-1)) + ((desv2**2/n2)**2/(n2-1)))
                    tipo_test = "t-student de Welch (varianzas diferentes)"
                
                # Intervalo de confianza del 95% para la diferencia
                t_critico = scipy_stats.t.ppf(0.975, gl)  # 0.975 para 95% bilateral
                margen_error = t_critico * se_diferencia
                ic_diferencia = {
                    'inferior': diferencia_medias - margen_error,
                    'superior': diferencia_medias + margen_error
                }
            else:
                # Para tests no paramétricos, no calculamos IC de la misma manera
                se_diferencia = None
                gl = None
                tipo_test = "Mann-Whitney U (no paramétrico)"
                ic_diferencia = {
                    'inferior': None,
                    'superior': None
                }
            
            # Decisión
            # Manejar p-values muy pequeños (prácticamente 0)
            if p_value < 1e-15:
                p_value_mostrar = 0.0
            else:
                p_value_mostrar = p_value
            
            significativo = p_value < 0.05
            decision = "Rechazar H₀" if significativo else "No rechazar H₀"
            interpretacion = f"Diferencia significativa (p < 0.05)" if significativo else f"Sin diferencia significativa (p >= 0.05)"
            
            resultado_base = {
                'p_value': p_value,  # Valor original para cálculos
                'p_value_mostrar': p_value_mostrar,  # Valor para mostrar
                'significativo': significativo,
                'decision': decision,
                'interpretacion': interpretacion,
                'tipo_test': tipo_test,
                'test_aplicado': test_aplicado,
                'ambos_normales': ambos_normales,
                'grupo1': {
                    'nombre': nombre_grupo1,
                    'media': media1,
                    'desviacion_estandar': desv1,
                    'n': n1,
                    'normal': normal1,
                    'p_normalidad': p_norm1
                },
                'grupo2': {
                    'nombre': nombre_grupo2,
                    'media': media2,
                    'desviacion_estandar': desv2,
                    'n': n2,
                    'normal': normal2,
                    'p_normalidad': p_norm2
                },
                'diferencia_medias': diferencia_medias,
                'error_estandar_diferencia': se_diferencia,
                'intervalo_confianza_95': ic_diferencia,
            }
            
            # Agregar estadísticos según el test aplicado
            if ambos_normales:
                resultado_base['estadistico_t'] = stat_test
                resultado_base['grados_libertad'] = gl
                resultado_base['error_estandar_diferencia'] = se_diferencia
                resultado_base['test_varianzas'] = {
                    'levene_stat': stat_levene,
                    'p_value': p_levene,
                    'varianzas_iguales': varianzas_iguales
                }
            else:
                resultado_base['estadistico_u'] = stat_test
            
            resultado_base['diferencia_medias'] = diferencia_medias
            resultado_base['intervalo_confianza_95'] = ic_diferencia
            
            return resultado_base
        except Exception as e:
            return {'error': str(e)}
    
    def _formatear_p_value(self, p_value: float) -> str:
        """
        Formatea el p-value para mostrar valores muy pequeños correctamente
        
        Args:
            p_value: Valor del p-value
        
        Returns:
            String formateado del p-value
        """
        if p_value == 0.0 or p_value < 1e-10:
            return "< 0.000001 (prácticamente 0)"
        elif p_value < 0.0001:
            return f"{p_value:.2e} (notación científica)"
        elif p_value < 0.001:
            return f"{p_value:.6f}"
        elif p_value < 0.01:
            return f"{p_value:.5f}"
        else:
            return f"{p_value:.4f}"
    
    def _generar_datos_simulados(self, media: float, desviacion: float, minimo: float, 
                                  maximo: float, n: int = 30) -> List[float]:
        """
        Genera datos simulados basados en estadísticas descriptivas
        
        Args:
            media: Media de la distribución
            desviacion: Desviación estándar
            minimo: Valor mínimo observado
            maximo: Valor máximo observado
            n: Número de observaciones a generar
        
        Returns:
            Lista de valores simulados
        """
        if not NUMPY_AVAILABLE:
            # Si numpy no está disponible, generar datos simples usando distribución normal aproximada
            import random
            datos = []
            for _ in range(n):
                # Generar valor con distribución normal aproximada
                valor = random.gauss(media, desviacion)
                # Asegurar que esté en el rango razonable
                valor = max(minimo * 0.9, min(maximo * 1.1, valor))
                datos.append(float(valor))
            return datos
        
        # Generar datos con distribución normal truncada
        datos = []
        intentos = 0
        max_intentos = n * 10
        
        while len(datos) < n and intentos < max_intentos:
            valor = np.random.normal(media, desviacion)
            if minimo <= valor <= maximo:
                datos.append(float(valor))
            intentos += 1
        
        # Si no se generaron suficientes, completar con distribución normal sin truncar
        while len(datos) < n:
            valor = np.random.normal(media, desviacion)
            datos.append(float(valor))
        
        return datos[:n]
    
    def _calcular_intervalo_confianza(self, datos: List[float], confianza: float = 0.95) -> Dict[str, float]:
        """Calcula intervalo de confianza usando t-student o z según el tamaño de muestra"""
        if len(datos) < 2:
            return {'inferior': 0, 'superior': 0}
        
        media = statistics.mean(datos)
        desv = statistics.stdev(datos) if len(datos) > 1 else 0
        n = len(datos)
        
        if SCIPY_AVAILABLE and n < 30:
            # Usar t-student para muestras pequeñas
            grados_libertad = n - 1
            t_value = scipy_stats.t.ppf((1 + confianza) / 2, grados_libertad)
        else:
            # Usar z para muestras grandes (n >= 30)
            t_value = 1.96  # z para 95% de confianza
        
        margen_error = t_value * (desv / math.sqrt(n))
        return {
            'inferior': media - margen_error,
            'superior': media + margen_error
        }
    
    def _analisis_inferencial_respuesta(self, resultados: Dict) -> Dict[str, Any]:
        """4.2 Análisis inferencial de tiempos de respuesta con tests estadísticos"""
        analisis = {}
        
        procesos_map = {
            'registro_envios': '4.2.1 Análisis de resultados del requerimiento registro de envíos',
            'asignacion_tarifas': '4.2.2 Análisis de resultados del requerimiento asignación de tarifas',
            'busqueda_semantica': '4.2.3 Análisis de resultados del requerimiento búsqueda semántica'
        }
        
        procesos = ['registro_envios', 'asignacion_tarifas', 'busqueda_semantica']
        
        for proceso in procesos:
            if proceso not in resultados:
                continue
            
            # Verificar que el proceso tiene datos válidos
            if not resultados[proceso] or 'tiempos_respuesta' not in resultados[proceso]:
                self.stdout.write(
                    self.style.WARNING(f'\n⚠️  {proceso}: No hay datos suficientes para análisis inferencial')
                )
                continue
            
            datos = resultados[proceso]['tiempos_respuesta']
            if not datos or len(datos) < 2:
                self.stdout.write(
                    self.style.WARNING(f'\n⚠️  {proceso}: Se requieren al menos 2 iteraciones exitosas para análisis inferencial')
                )
                continue
            
            # Estadísticas básicas
            media = statistics.mean(datos)
            desv = statistics.stdev(datos) if len(datos) > 1 else 0
            n = len(datos)
            
            # PASO 1: Test de normalidad (Shapiro-Wilk) - DEBE SER PRIMERO
            es_normal, p_shapiro, interpretacion_normal = self._test_normalidad(datos)
            
            # Intervalo de confianza del 95%
            intervalo_confianza = self._calcular_intervalo_confianza(datos, 0.95)
            
            # PASO 2: Decidir qué test aplicar según normalidad
            test_resultado = None
            test_aplicado = None
            
            if es_normal:
                # Si los datos son normales → usar test t-student (paramétrico)
                test_t = self._test_t_student(datos)
                test_resultado = test_t
                test_aplicado = 't-student (paramétrico)'
            else:
                # Si los datos NO son normales → usar test no paramétrico (Wilcoxon para una muestra)
                test_wilcoxon = self._test_wilcoxon_una_muestra(datos)
                test_resultado = test_wilcoxon
                test_aplicado = 'Wilcoxon (no paramétrico)'
            
            # Coeficiente de variación
            cv = (desv / media * 100) if media > 0 else 0
            
            analisis[proceso] = {
                'media': media,
                'desviacion_estandar': desv,
                'n': n,
                'intervalo_confianza_95': intervalo_confianza,
                'coeficiente_variacion': cv,
                'test_normalidad': {
                    'es_normal': es_normal,
                    'p_value': p_shapiro,
                    'interpretacion': interpretacion_normal
                },
                'test_aplicado': test_aplicado,
                'test_resultado': test_resultado
            }
            
            # Mostrar resultados según el requerimiento
            self.stdout.write(self.style.WARNING(f'\n{procesos_map[proceso]}'))
            self.stdout.write(f'\n{resultados[proceso]["nombre"]}:')
            self.stdout.write(f'  Media: {media:.2f} ms')
            self.stdout.write(f'  Desviación estándar: {desv:.2f} ms')
            self.stdout.write(f'  Tamaño de muestra (n): {n}')
            self.stdout.write(f'  IC 95%: [{intervalo_confianza["inferior"]:.2f}, {intervalo_confianza["superior"]:.2f}] ms')
            self.stdout.write(f'  Coeficiente de variación: {cv:.2f}%')
            
            # Tests estadísticos - ORDEN CORRECTO
            self.stdout.write(f'\n  Tests Estadísticos (orden correcto):')
            self.stdout.write(f'    PASO 1 - Test de Normalidad (Shapiro-Wilk):')
            self.stdout.write(f'      p-value: {p_shapiro:.4f}')
            self.stdout.write(f'      Interpretación: {interpretacion_normal}')
            
            self.stdout.write(f'\n    PASO 2 - Test Aplicado: {test_aplicado}')
            if test_resultado and 'error' not in test_resultado:
                if test_aplicado == 't-student (paramétrico)':
                    if 'estadistico_t' in test_resultado:
                        self.stdout.write(f'      Estadístico t: {test_resultado["estadistico_t"]:.4f}')
                        p_valor = test_resultado.get("p_value_mostrar", test_resultado.get("p_value", 0))
                        p_formateado = self._formatear_p_value(p_valor)
                        self.stdout.write(f'      p-value: {p_formateado}')
                        self.stdout.write(f'      {test_resultado["interpretacion"]}')
                elif test_aplicado == 'Wilcoxon (no paramétrico)':
                    if 'estadistico_w' in test_resultado:
                        self.stdout.write(f'      Estadístico W: {test_resultado["estadistico_w"]:.4f}')
                        p_valor = test_resultado.get("p_value_mostrar", test_resultado.get("p_value", 0))
                        p_formateado = self._formatear_p_value(p_valor)
                        self.stdout.write(f'      p-value: {p_formateado}')
                        self.stdout.write(f'      {test_resultado["interpretacion"]}')
            
            # Análisis de hipótesis
            self._mostrar_hipotesis_resultados(proceso, analisis[proceso], resultados[proceso]["nombre"])
        
        return analisis
    
    def _analizar_tiempos_espera(self, resultados: Dict) -> Dict[str, Any]:
        """4.3 Análisis descriptivo de tiempos de espera"""
        analisis = {}
        
        procesos = {
            'registro_envios': '4.3.1 Proceso de registro de envíos',
            'asignacion_tarifas': '4.3.2 Proceso de asignación de tarifas',
            'busqueda_semantica': '4.3.3 Proceso de búsqueda semántica'
        }
        
        for proceso, titulo in procesos.items():
            if proceso not in resultados or not resultados[proceso]:
                continue
            
            if 'tiempos_espera' not in resultados[proceso] or 'estadisticas_espera' not in resultados[proceso]:
                continue
            
            datos = resultados[proceso]['tiempos_espera']
            if not datos:
                continue
            
            stats = resultados[proceso]['estadisticas_espera']
            analisis[proceso] = stats
            
            self.stdout.write(self.style.WARNING(f'\n{titulo}'))
            self.stdout.write(f'\n{resultados[proceso]["nombre"]} - Tiempos de Espera:')
            self.stdout.write(f'  Media: {stats["media"]:.2f} ms')
            self.stdout.write(f'  Mediana: {stats["mediana"]:.2f} ms')
            self.stdout.write(f'  Desviación estándar: {stats["desviacion_estandar"]:.2f} ms')
            self.stdout.write(f'  Mínimo: {stats["minimo"]:.2f} ms')
            self.stdout.write(f'  Máximo: {stats["maximo"]:.2f} ms')
        
        return analisis
    
    def _analisis_inferencial_espera(self, resultados: Dict) -> Dict[str, Any]:
        """4.4 Análisis inferencial de tiempos de espera con tests estadísticos"""
        analisis = {}
        
        procesos = {
            'registro_envios': '4.4.1 Análisis de resultados del requerimiento registro de envíos',
            'asignacion_tarifas': '4.4.2 Análisis de resultados del requerimiento asignación de tarifas',
            'busqueda_semantica': '4.4.3 Análisis de resultados del requerimiento búsqueda semántica'
        }
        
        for proceso, titulo in procesos.items():
            if proceso not in resultados or not resultados[proceso]:
                continue
            
            if 'tiempos_espera' not in resultados[proceso]:
                continue
            
            datos = resultados[proceso]['tiempos_espera']
            if not datos or len(datos) < 2:
                continue
            
            media = statistics.mean(datos)
            desv = statistics.stdev(datos) if len(datos) > 1 else 0
            n = len(datos)
            
            # Test de normalidad
            es_normal, p_shapiro, interpretacion_normal = self._test_normalidad(datos)
            
            # Intervalo de confianza del 95%
            intervalo_confianza = self._calcular_intervalo_confianza(datos, 0.95)
            
            # Test t-student
            test_t = self._test_t_student(datos)
            
            cv = (desv / media * 100) if media > 0 else 0
            
            analisis[proceso] = {
                'media': media,
                'desviacion_estandar': desv,
                'n': n,
                'intervalo_confianza_95': intervalo_confianza,
                'coeficiente_variacion': cv,
                'test_normalidad': {
                    'es_normal': es_normal,
                    'p_value': p_shapiro,
                    'interpretacion': interpretacion_normal
                },
                'test_t_student': test_t
            }
            
            self.stdout.write(self.style.WARNING(f'\n{titulo}'))
            self.stdout.write(f'\n{resultados[proceso]["nombre"]} - Tiempos de Espera:')
            self.stdout.write(f'  Media: {media:.2f} ms')
            self.stdout.write(f'  Desviación estándar: {desv:.2f} ms')
            self.stdout.write(f'  Tamaño de muestra (n): {n}')
            self.stdout.write(f'  IC 95%: [{intervalo_confianza["inferior"]:.2f}, {intervalo_confianza["superior"]:.2f}] ms')
            self.stdout.write(f'  Coeficiente de variación: {cv:.2f}%')
            
            # Tests estadísticos
            self.stdout.write(f'\n  Tests Estadísticos:')
            self.stdout.write(f'    Test de Normalidad (Shapiro-Wilk):')
            self.stdout.write(f'      p-value: {p_shapiro:.4f}')
            self.stdout.write(f'      Interpretación: {interpretacion_normal}')
            
            if test_t and 'estadistico_t' in test_t:
                self.stdout.write(f'    Test t-student:')
                self.stdout.write(f'      Estadístico t: {test_t["estadistico_t"]:.4f}')
                self.stdout.write(f'      p-value: {test_t["p_value"]:.4f}')
                self.stdout.write(f'      {test_t["interpretacion"]}')
            
            # Análisis de hipótesis
            self._mostrar_hipotesis_resultados(proceso, analisis[proceso], resultados[proceso]["nombre"])
        
        return analisis
    
    def _analizar_recursos(self, resultados: Dict) -> Dict[str, Any]:
        """4.5 Análisis descriptivo de utilización de recursos"""
        analisis = {}
        
        procesos = {
            'registro_envios': '4.5.1 Proceso de registro de envíos',
            'asignacion_tarifas': '4.5.2 Proceso de asignación de tarifas',
            'busqueda_semantica': '4.5.3 Proceso de búsqueda semántica'
        }
        
        for proceso, titulo in procesos.items():
            if proceso not in resultados or not resultados[proceso]:
                continue
            
            if 'estadisticas_recursos' not in resultados[proceso]:
                continue
            
            stats = resultados[proceso]['estadisticas_recursos']
            analisis[proceso] = stats
            
            self.stdout.write(self.style.WARNING(f'\n{titulo}'))
            self.stdout.write(f'\n{resultados[proceso]["nombre"]} - Recursos:')
            self.stdout.write(f'  CPU promedio: {stats["cpu"]["media"]:.2f}%')
            self.stdout.write(f'  CPU máximo: {stats["cpu"]["maximo"]:.2f}%')
            self.stdout.write(f'  Memoria promedio: {stats["memoria_mb"]["media"]:.2f} MB')
            self.stdout.write(f'  Memoria máxima: {stats["memoria_mb"]["maximo"]:.2f} MB')
        
        return analisis
    
    def _analisis_inferencial_recursos(self, resultados: Dict) -> Dict[str, Any]:
        """4.6 Análisis inferencial de utilización de recursos"""
        analisis = {}
        
        procesos = {
            'registro_envios': '4.6.1 Análisis inferencial de recursos - Registro de envíos',
            'asignacion_tarifas': '4.6.2 Análisis inferencial de recursos - Asignación de tarifas',
            'busqueda_semantica': '4.6.3 Análisis inferencial de recursos - Búsqueda semántica'
        }
        
        for proceso, titulo in procesos.items():
            if proceso not in resultados or not resultados[proceso]:
                continue
            
            if 'recursos' not in resultados[proceso]:
                continue
            
            recursos = resultados[proceso]['recursos']
            if not recursos:
                continue
            
            # Extraer datos de CPU y memoria
            cpus = [r['cpu_delta'] for r in recursos if 'cpu_delta' in r]
            memorias = [r['memoria_delta_mb'] for r in recursos if 'memoria_delta_mb' in r]
            
            if not cpus or not memorias:
                continue
            
            # Análisis inferencial de CPU
            cpu_media = statistics.mean(cpus)
            cpu_desv = statistics.stdev(cpus) if len(cpus) > 1 else 0
            cpu_ic = self._calcular_intervalo_confianza(cpus, 0.95)
            cpu_normal, cpu_p, cpu_interp = self._test_normalidad(cpus)
            
            # Análisis inferencial de Memoria
            mem_media = statistics.mean(memorias)
            mem_desv = statistics.stdev(memorias) if len(memorias) > 1 else 0
            mem_ic = self._calcular_intervalo_confianza(memorias, 0.95)
            mem_normal, mem_p, mem_interp = self._test_normalidad(memorias)
            
            analisis[proceso] = {
                'cpu': {
                    'media': cpu_media,
                    'desviacion_estandar': cpu_desv,
                    'intervalo_confianza_95': cpu_ic,
                    'test_normalidad': {
                        'es_normal': cpu_normal,
                        'p_value': cpu_p,
                        'interpretacion': cpu_interp
                    }
                },
                'memoria': {
                    'media': mem_media,
                    'desviacion_estandar': mem_desv,
                    'intervalo_confianza_95': mem_ic,
                    'test_normalidad': {
                        'es_normal': mem_normal,
                        'p_value': mem_p,
                        'interpretacion': mem_interp
                    }
                }
            }
            
            self.stdout.write(self.style.WARNING(f'\n{titulo}'))
            self.stdout.write(f'\n{resultados[proceso]["nombre"]} - Análisis Inferencial de Recursos:')
            
            # CPU
            self.stdout.write(f'\n  CPU:')
            self.stdout.write(f'    Media: {cpu_media:.2f}%')
            self.stdout.write(f'    Desviación estándar: {cpu_desv:.2f}%')
            self.stdout.write(f'    IC 95%: [{cpu_ic["inferior"]:.2f}, {cpu_ic["superior"]:.2f}]%')
            self.stdout.write(f'    Test de Normalidad (Shapiro-Wilk):')
            self.stdout.write(f'      p-value: {cpu_p:.4f}')
            self.stdout.write(f'      Interpretación: {cpu_interp}')
            
            # Memoria
            self.stdout.write(f'\n  Memoria:')
            self.stdout.write(f'    Media: {mem_media:.2f} MB')
            self.stdout.write(f'    Desviación estándar: {mem_desv:.2f} MB')
            self.stdout.write(f'    IC 95%: [{mem_ic["inferior"]:.2f}, {mem_ic["superior"]:.2f}] MB')
            self.stdout.write(f'    Test de Normalidad (Shapiro-Wilk):')
            self.stdout.write(f'      p-value: {mem_p:.4f}')
            self.stdout.write(f'      Interpretación: {mem_interp}')
            
            # Análisis de hipótesis de recursos
            self._mostrar_hipotesis_recursos(proceso, analisis[proceso], resultados[proceso]["nombre"])
        
        # Clasificación por umbrales de recursos
        self.stdout.write(self.style.WARNING('\n4.6.4 Clasificación por umbrales de utilización de recursos'))
        self._clasificar_recursos_umbrales(resultados)
        
        return analisis
    
    def _obtener_umbrales_tiempo_respuesta(self) -> Dict[str, Dict[str, float]]:
        """
        Retorna los umbrales de clasificación para tiempo de respuesta (en ms)
        Puedes modificar estos valores según tus tablas de umbral
        """
        return {
            'excelente': {'max': 200, 'icono': '⚡', 'descripcion': 'Experiencia óptima'},
            'bueno': {'min': 200, 'max': 500, 'icono': '✅', 'descripcion': 'Aceptable'},
            'regular': {'min': 500, 'max': 1000, 'icono': '⚠️', 'descripcion': 'Puede requerir optimización'},
            'lento': {'min': 1000, 'icono': '🔴', 'descripcion': 'Optimización necesaria'}
        }
    
    def _clasificar_tiempo_por_umbral(self, tiempo_ms: float, umbrales: Dict) -> Dict[str, Any]:
        """
        Clasifica un tiempo de respuesta según los umbrales definidos
        """
        if tiempo_ms < umbrales['excelente']['max']:
            return {
                'categoria': 'excelente',
                'icono': umbrales['excelente']['icono'],
                'descripcion': umbrales['excelente']['descripcion']
            }
        elif tiempo_ms < umbrales['bueno']['max']:
            return {
                'categoria': 'bueno',
                'icono': umbrales['bueno']['icono'],
                'descripcion': umbrales['bueno']['descripcion']
            }
        elif tiempo_ms < umbrales['regular']['max']:
            return {
                'categoria': 'regular',
                'icono': umbrales['regular']['icono'],
                'descripcion': umbrales['regular']['descripcion']
            }
        else:
            return {
                'categoria': 'lento',
                'icono': umbrales['lento']['icono'],
                'descripcion': umbrales['lento']['descripcion']
            }
    
    def _clasificar_tiempo_respuesta_umbrales(self, resultados: Dict):
        """
        Clasifica los tiempos de respuesta de todos los procesos según umbrales
        """
        umbrales = self._obtener_umbrales_tiempo_respuesta()
        
        procesos_map = {
            'registro_envios': '4.2.5.1 Registro de Envíos',
            'asignacion_tarifas': '4.2.5.2 Asignación de Tarifas',
            'busqueda_semantica': '4.2.5.3 Búsqueda Semántica'
        }
        
        for proceso_key, titulo in procesos_map.items():
            if proceso_key not in resultados or not resultados[proceso_key]:
                continue
            
            if 'estadisticas_respuesta' not in resultados[proceso_key]:
                continue
            
            media_ms = resultados[proceso_key]['estadisticas_respuesta']['media']
            clasificacion = self._clasificar_tiempo_por_umbral(media_ms, umbrales)
            
            self.stdout.write(self.style.WARNING(f'\n{titulo}'))
            self.stdout.write(f'\n{resultados[proceso_key]["nombre"]}:')
            self.stdout.write(f'  Tiempo promedio: {media_ms:.2f} ms')
            self.stdout.write(f'  Clasificación: {clasificacion["icono"]} {clasificacion["categoria"].upper()}')
            self.stdout.write(f'  Interpretación: {clasificacion["descripcion"]}')
    
    def _obtener_umbrales_recursos(self) -> Dict[str, Dict]:
        """
        Retorna los umbrales de clasificación para utilización de recursos
        Puedes modificar estos valores según tus tablas de umbral
        """
        return {
            'cpu': {
                'bajo': {'max': 10, 'icono': '✅', 'descripcion': 'Capacidad disponible'},
                'moderado': {'min': 10, 'max': 30, 'icono': '✅', 'descripcion': 'Uso normal'},
                'alto': {'min': 30, 'max': 50, 'icono': '⚠️', 'descripcion': 'Monitorear'},
                'critico': {'min': 50, 'icono': '🔴', 'descripcion': 'Optimizar urgente'}
            },
            'memoria': {
                'normal': {'max': 5, 'icono': '✅', 'descripcion': 'Normal'},
                'aceptable': {'min': 5, 'max': 20, 'icono': '✅', 'descripcion': 'Aceptable, monitorear'},
                'alto': {'min': 20, 'icono': '⚠️', 'descripcion': 'Investigar posibles memory leaks'}
            }
        }
    
    def _clasificar_cpu_por_umbral(self, cpu_porcentaje: float, umbrales: Dict) -> Dict[str, Any]:
        """Clasifica el uso de CPU según umbrales"""
        if cpu_porcentaje < umbrales['cpu']['bajo']['max']:
            return {'categoria': 'bajo', **umbrales['cpu']['bajo']}
        elif cpu_porcentaje < umbrales['cpu']['moderado']['max']:
            return {'categoria': 'moderado', **umbrales['cpu']['moderado']}
        elif cpu_porcentaje < umbrales['cpu']['alto']['max']:
            return {'categoria': 'alto', **umbrales['cpu']['alto']}
        else:
            return {'categoria': 'critico', **umbrales['cpu']['critico']}
    
    def _clasificar_memoria_por_umbral(self, memoria_mb: float, umbrales: Dict) -> Dict[str, Any]:
        """Clasifica el uso de memoria según umbrales"""
        if memoria_mb < umbrales['memoria']['normal']['max']:
            return {'categoria': 'normal', **umbrales['memoria']['normal']}
        elif memoria_mb < umbrales['memoria']['aceptable']['max']:
            return {'categoria': 'aceptable', **umbrales['memoria']['aceptable']}
        else:
            return {'categoria': 'alto', **umbrales['memoria']['alto']}
    
    def _clasificar_recursos_umbrales(self, resultados: Dict):
        """
        Clasifica la utilización de recursos de todos los procesos según umbrales
        """
        umbrales = self._obtener_umbrales_recursos()
        
        procesos_map = {
            'registro_envios': '4.6.4.1 Registro de Envíos',
            'asignacion_tarifas': '4.6.4.2 Asignación de Tarifas',
            'busqueda_semantica': '4.6.4.3 Búsqueda Semántica'
        }
        
        for proceso_key, titulo in procesos_map.items():
            if proceso_key not in resultados or not resultados[proceso_key]:
                continue
            
            if 'estadisticas_recursos' not in resultados[proceso_key]:
                continue
            
            recursos = resultados[proceso_key]['estadisticas_recursos']
            cpu_promedio = recursos['cpu']['media']
            memoria_promedio = recursos['memoria_mb']['media']
            
            clasif_cpu = self._clasificar_cpu_por_umbral(cpu_promedio, umbrales)
            clasif_mem = self._clasificar_memoria_por_umbral(memoria_promedio, umbrales)
            
            self.stdout.write(self.style.WARNING(f'\n{titulo}'))
            self.stdout.write(f'\n{resultados[proceso_key]["nombre"]} - Clasificación por Umbrales:')
            self.stdout.write(f'  CPU promedio: {cpu_promedio:.2f}%')
            self.stdout.write(f'    Clasificación: {clasif_cpu["icono"]} {clasif_cpu["categoria"].upper()}')
            self.stdout.write(f'    Interpretación: {clasif_cpu["descripcion"]}')
            self.stdout.write(f'  Memoria promedio: {memoria_promedio:.2f} MB')
            self.stdout.write(f'    Clasificación: {clasif_mem["icono"]} {clasif_mem["categoria"].upper()}')
            self.stdout.write(f'    Interpretación: {clasif_mem["descripcion"]}')
    
    def _mostrar_comparativa_proceso(self, datos_proceso: Dict, nombre_proceso: str):
        """Muestra comparativa manual vs automatizado para un proceso específico"""
        if not datos_proceso or 'estadisticas_respuesta' not in datos_proceso:
            return
        
        # Tiempos manuales estimados (en segundos)
        tiempos_manuales = {
            'Registro de Envíos': 240,  # 4 minutos
            'Asignación de Tarifas': 105,  # 1.75 minutos
            'Búsqueda Semántica': 365  # 6 minutos
        }
        
        tiempo_manual_seg = tiempos_manuales.get(nombre_proceso, 0)
        tiempo_web_ms = datos_proceso['estadisticas_respuesta']['media']
        tiempo_web_seg = tiempo_web_ms / 1000
        
        if tiempo_manual_seg == 0:
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n  Comparativa Manual vs Automatizado ({nombre_proceso}):'))
        self.stdout.write(f'    Tiempo manual: {tiempo_manual_seg} segundos ({tiempo_manual_seg/60:.2f} minutos)')
        self.stdout.write(f'    Tiempo automatizado (app): {tiempo_web_seg:.2f} segundos ({tiempo_web_ms:.2f} ms)')
        
        mejora = (tiempo_manual_seg / tiempo_web_seg) if tiempo_web_seg > 0 else 0
        ahorro_seg = tiempo_manual_seg - tiempo_web_seg
        ahorro_porcentaje = (ahorro_seg / tiempo_manual_seg * 100) if tiempo_manual_seg > 0 else 0
        
        self.stdout.write(f'    Mejora: {mejora:.1f}x más rápido')
        self.stdout.write(f'    Ahorro: {ahorro_seg:.2f} segundos ({ahorro_porcentaje:.1f}% más rápido)')
    
    def _mostrar_test_t_student_comparativo(self, proceso: str, nombre_proceso: str):
        """
        Muestra el test t-student comparativo entre proceso manual y automatizado
        usando los datos proporcionados por el usuario
        """
        # Datos proporcionados por el usuario para cada proceso
        datos_procesos = {
            'registro_envios': {
                'manual': {
                    'media': 240.4,
                    'desviacion': 3.72,
                    'minimo': 235,
                    'maximo': 246
                },
                'automatizado': {
                    'media': 5.99,
                    'desviacion': 0.14,
                    'minimo': 5.81,
                    'maximo': 6.21
                }
            },
            'asignacion_tarifas': {
                'manual': {
                    'media': 105.0,
                    'desviacion': 2.5,
                    'minimo': 100,
                    'maximo': 110
                },
                'automatizado': {
                    'media': 0.05,
                    'desviacion': 0.01,
                    'minimo': 0.04,
                    'maximo': 0.06
                }
            },
            'busqueda_semantica': {
                'manual': {
                    'media': 365.0,
                    'desviacion': 15.0,
                    'minimo': 340,
                    'maximo': 390
                },
                'automatizado': {
                    'media': 1.2,
                    'desviacion': 0.2,
                    'minimo': 1.0,
                    'maximo': 1.5
                }
            }
        }
        
        if proceso not in datos_procesos:
            self.stdout.write(self.style.ERROR(f'\nNo hay datos disponibles para el proceso: {proceso}'))
            return
        
        datos_manual = datos_procesos[proceso]['manual']
        datos_automatizado = datos_procesos[proceso]['automatizado']
        
        # Generar datos simulados (30 observaciones por grupo)
        grupo_manual = self._generar_datos_simulados(
            datos_manual['media'],
            datos_manual['desviacion'],
            datos_manual['minimo'],
            datos_manual['maximo'],
            n=30
        )
        
        grupo_automatizado = self._generar_datos_simulados(
            datos_automatizado['media'],
            datos_automatizado['desviacion'],
            datos_automatizado['minimo'],
            datos_automatizado['maximo'],
            n=30
        )
        
        # Realizar test t-student
        resultado = self._test_t_student_dos_muestras(
            grupo_manual,
            grupo_automatizado,
            nombre_grupo1="Proceso Manual",
            nombre_grupo2="Proceso Automatizado"
        )
        
        if 'error' in resultado:
            self.stdout.write(self.style.ERROR(f'\nError: {resultado["error"]}'))
            return
        
        # Determinar el nombre del test según el tipo aplicado
        nombre_test = "TEST ESTADÍSTICO COMPARATIVO"
        if resultado.get('test_aplicado') == 't-student (paramétrico)':
            nombre_test = "TEST T-STUDENT: COMPARACIÓN MANUAL vs AUTOMATIZADO"
        elif resultado.get('test_aplicado') == 'Mann-Whitney U (no paramétrico)':
            nombre_test = "TEST MANN-WHITNEY U: COMPARACIÓN MANUAL vs AUTOMATIZADO"
        
        # Mostrar resultados completos
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write(f'{nombre_test} - {nombre_proceso}')
        self.stdout.write('='*80)
        
        # Paso 1: Planteamiento de hipótesis
        self.stdout.write(self.style.WARNING('\nPASO 1: PLANTEAMIENTO DE HIPÓTESIS'))
        self.stdout.write('  Hipótesis nula (H₀): No hay diferencia significativa entre los tiempos medios')
        self.stdout.write('    H₀: μ_manual = μ_automatizado')
        self.stdout.write('  Hipótesis alterna (H₁): Hay diferencia significativa entre los tiempos medios')
        self.stdout.write('    H₁: μ_manual ≠ μ_automatizado (prueba bilateral)')
        
        # Paso 2: Nivel de significancia
        self.stdout.write(self.style.WARNING('\nPASO 2: NIVEL DE SIGNIFICANCIA'))
        self.stdout.write('  Nivel de confianza: 95%')
        self.stdout.write('  Nivel de significancia (α): 0.05')
        
        # Paso 3: Verificación de normalidad (DEBE SER PRIMERO)
        self.stdout.write(self.style.WARNING('\nPASO 3: VERIFICACIÓN DE NORMALIDAD (Shapiro-Wilk)'))
        self.stdout.write(f'  {resultado["grupo1"]["nombre"]}:')
        self.stdout.write(f'    Normal: {"Sí" if resultado["grupo1"]["normal"] else "No"}')
        self.stdout.write(f'    p-value: {resultado["grupo1"]["p_normalidad"]:.4f}')
        self.stdout.write(f'  {resultado["grupo2"]["nombre"]}:')
        self.stdout.write(f'    Normal: {"Sí" if resultado["grupo2"]["normal"] else "No"}')
        self.stdout.write(f'    p-value: {resultado["grupo2"]["p_normalidad"]:.4f}')
        self.stdout.write(f'  Decisión: {"Ambos grupos son normales → usar test paramétrico (t-student)" if resultado.get("ambos_normales") else "Al menos un grupo NO es normal → usar test no paramétrico (Mann-Whitney U)"}')
        
        # Paso 4: Estadístico de prueba
        self.stdout.write(self.style.WARNING(f'\nPASO 4: ESTADÍSTICO DE PRUEBA'))
        self.stdout.write(f'  Test aplicado: {resultado.get("test_aplicado", resultado.get("tipo_test", "N/A"))}')
        if resultado.get('grados_libertad'):
            self.stdout.write(f'  Grados de libertad: {resultado["grados_libertad"]:.2f}')
        
        # Estadísticas descriptivas
        self.stdout.write(f'\n  Estadísticas Descriptivas:')
        self.stdout.write(f'    {resultado["grupo1"]["nombre"]}:')
        self.stdout.write(f'      Media: {resultado["grupo1"]["media"]:.2f} segundos')
        self.stdout.write(f'      Desviación estándar: {resultado["grupo1"]["desviacion_estandar"]:.2f} segundos')
        self.stdout.write(f'      Tamaño de muestra (n): {resultado["grupo1"]["n"]}')
        self.stdout.write(f'      Test de normalidad (Shapiro-Wilk): p = {resultado["grupo1"]["p_normalidad"]:.4f}')
        
        self.stdout.write(f'    {resultado["grupo2"]["nombre"]}:')
        self.stdout.write(f'      Media: {resultado["grupo2"]["media"]:.2f} segundos')
        self.stdout.write(f'      Desviación estándar: {resultado["grupo2"]["desviacion_estandar"]:.2f} segundos')
        self.stdout.write(f'      Tamaño de muestra (n): {resultado["grupo2"]["n"]}')
        self.stdout.write(f'      Test de normalidad (Shapiro-Wilk): p = {resultado["grupo2"]["p_normalidad"]:.4f}')
        
        # Test de varianzas (solo si es paramétrico)
        ambos_normales = resultado.get("ambos_normales", False)
        if ambos_normales and 'test_varianzas' in resultado and resultado.get('test_varianzas'):
            self.stdout.write(f'\n  Test de Igualdad de Varianzas (Levene):')
            self.stdout.write(f'    Estadístico: {resultado["test_varianzas"]["levene_stat"]:.4f}')
            p_var = self._formatear_p_value(resultado["test_varianzas"]["p_value"])
            self.stdout.write(f'    p-value: {p_var}')
            self.stdout.write(f'    Varianzas iguales: {"Sí" if resultado["test_varianzas"]["varianzas_iguales"] else "No"}')
        
        # Resultados del test
        test_nombre = "t-student" if ambos_normales else "Mann-Whitney U"
        self.stdout.write(f'\n  Resultados del Test {test_nombre}:')
        self.stdout.write(f'    Diferencia de medias: {resultado["diferencia_medias"]:.2f} segundos')
        
        if ambos_normales:
            if resultado.get("error_estandar_diferencia"):
                self.stdout.write(f'    Error estándar de la diferencia: {resultado["error_estandar_diferencia"]:.4f}')
            if resultado.get("estadistico_t"):
                self.stdout.write(f'    Estadístico t: {resultado["estadistico_t"]:.4f}')
        else:
            if resultado.get("estadistico_u"):
                self.stdout.write(f'    Estadístico U: {resultado["estadistico_u"]:.4f}')
        
        # Usar p_value_mostrar si existe, sino usar p_value
        p_valor = resultado.get("p_value_mostrar", resultado["p_value"])
        p_test = self._formatear_p_value(p_valor)
        self.stdout.write(f'    p-value: {p_test}')
        
        if ambos_normales and resultado.get("intervalo_confianza_95", {}).get("inferior") is not None:
            self.stdout.write(f'    Intervalo de confianza 95% para la diferencia:')
            self.stdout.write(f'      [{resultado["intervalo_confianza_95"]["inferior"]:.2f}, {resultado["intervalo_confianza_95"]["superior"]:.2f}] segundos')
        
        # Paso 5: Toma de decisión
        self.stdout.write(self.style.WARNING('\nPASO 5: TOMA DE DECISIÓN'))
        p_decision = self._formatear_p_value(p_valor)
        self.stdout.write(f'  p-value = {p_decision}')
        self.stdout.write(f'  α = 0.05')
        
        if resultado["significativo"]:
            self.stdout.write(self.style.SUCCESS(f'  {resultado["decision"]}: p-value < α'))
            self.stdout.write(self.style.SUCCESS(f'  Interpretación: {resultado["interpretacion"]}'))
            self.stdout.write(self.style.SUCCESS(f'\n  CONCLUSIÓN:'))
            self.stdout.write(self.style.SUCCESS(f'    Se rechaza la hipótesis nula (H₀).'))
            self.stdout.write(self.style.SUCCESS(f'    Existe evidencia estadísticamente significativa de que'))
            self.stdout.write(self.style.SUCCESS(f'    los tiempos medios del proceso manual y automatizado son diferentes.'))
            self.stdout.write(self.style.SUCCESS(f'    El proceso automatizado es significativamente más rápido.'))
            self.stdout.write(self.style.SUCCESS(f'    Diferencia promedio: {resultado["diferencia_medias"]:.2f} segundos'))
            mejora = (resultado["grupo1"]["media"] / resultado["grupo2"]["media"])
            self.stdout.write(self.style.SUCCESS(f'    Mejora: {mejora:.1f}x más rápido'))
        else:
            self.stdout.write(self.style.WARNING(f'  {resultado["decision"]}: p-value >= α'))
            self.stdout.write(self.style.WARNING(f'  Interpretación: {resultado["interpretacion"]}'))
            self.stdout.write(self.style.WARNING(f'\n  CONCLUSIÓN:'))
            self.stdout.write(self.style.WARNING(f'    No se rechaza la hipótesis nula (H₀).'))
            self.stdout.write(self.style.WARNING(f'    No hay evidencia estadísticamente significativa de diferencia'))
            self.stdout.write(self.style.WARNING(f'    entre los tiempos medios de ambos procesos.'))
        
        self.stdout.write('='*80)
    
    def _obtener_umbrales_tiempo_respuesta(self) -> Dict[str, Dict[str, float]]:
        """
        Retorna los umbrales de clasificación para tiempo de respuesta (en ms)
        Puedes modificar estos valores según tus tablas de umbral
        """
        return {
            'excelente': {'max': 200, 'icono': '⚡', 'descripcion': 'Experiencia óptima'},
            'bueno': {'min': 200, 'max': 500, 'icono': '✅', 'descripcion': 'Aceptable'},
            'regular': {'min': 500, 'max': 1000, 'icono': '⚠️', 'descripcion': 'Puede requerir optimización'},
            'lento': {'min': 1000, 'icono': '🔴', 'descripcion': 'Optimización necesaria'}
        }
    
    def _clasificar_tiempo_por_umbral(self, tiempo_ms: float, umbrales: Dict) -> Dict[str, Any]:
        """
        Clasifica un tiempo de respuesta según los umbrales definidos
        """
        if tiempo_ms < umbrales['excelente']['max']:
            return {
                'categoria': 'excelente',
                'icono': umbrales['excelente']['icono'],
                'descripcion': umbrales['excelente']['descripcion']
            }
        elif tiempo_ms < umbrales['bueno']['max']:
            return {
                'categoria': 'bueno',
                'icono': umbrales['bueno']['icono'],
                'descripcion': umbrales['bueno']['descripcion']
            }
        elif tiempo_ms < umbrales['regular']['max']:
            return {
                'categoria': 'regular',
                'icono': umbrales['regular']['icono'],
                'descripcion': umbrales['regular']['descripcion']
            }
        else:
            return {
                'categoria': 'lento',
                'icono': umbrales['lento']['icono'],
                'descripcion': umbrales['lento']['descripcion']
            }
    
    def _clasificar_tiempo_respuesta_umbrales(self, resultados: Dict):
        """
        Clasifica los tiempos de respuesta de todos los procesos según umbrales
        """
        umbrales = self._obtener_umbrales_tiempo_respuesta()
        
        procesos_map = {
            'registro_envios': '4.2.5.1 Registro de Envíos',
            'asignacion_tarifas': '4.2.5.2 Asignación de Tarifas',
            'busqueda_semantica': '4.2.5.3 Búsqueda Semántica'
        }
        
        for proceso_key, titulo in procesos_map.items():
            if proceso_key not in resultados or not resultados[proceso_key]:
                continue
            
            if 'estadisticas_respuesta' not in resultados[proceso_key]:
                continue
            
            media_ms = resultados[proceso_key]['estadisticas_respuesta']['media']
            clasificacion = self._clasificar_tiempo_por_umbral(media_ms, umbrales)
            
            self.stdout.write(self.style.WARNING(f'\n{titulo}'))
            self.stdout.write(f'\n{resultados[proceso_key]["nombre"]}:')
            self.stdout.write(f'  Tiempo promedio: {media_ms:.2f} ms')
            self.stdout.write(f'  Clasificación: {clasificacion["icono"]} {clasificacion["categoria"].upper()}')
            self.stdout.write(f'  Interpretación: {clasificacion["descripcion"]}')
    
    def _obtener_umbrales_recursos(self) -> Dict[str, Dict]:
        """
        Retorna los umbrales de clasificación para utilización de recursos
        Puedes modificar estos valores según tus tablas de umbral
        """
        return {
            'cpu': {
                'bajo': {'max': 10, 'icono': '✅', 'descripcion': 'Capacidad disponible'},
                'moderado': {'min': 10, 'max': 30, 'icono': '✅', 'descripcion': 'Uso normal'},
                'alto': {'min': 30, 'max': 50, 'icono': '⚠️', 'descripcion': 'Monitorear'},
                'critico': {'min': 50, 'icono': '🔴', 'descripcion': 'Optimizar urgente'}
            },
            'memoria': {
                'normal': {'max': 5, 'icono': '✅', 'descripcion': 'Normal'},
                'aceptable': {'min': 5, 'max': 20, 'icono': '✅', 'descripcion': 'Aceptable, monitorear'},
                'alto': {'min': 20, 'icono': '⚠️', 'descripcion': 'Investigar posibles memory leaks'}
            }
        }
    
    def _clasificar_cpu_por_umbral(self, cpu_porcentaje: float, umbrales: Dict) -> Dict[str, Any]:
        """Clasifica el uso de CPU según umbrales"""
        if cpu_porcentaje < umbrales['cpu']['bajo']['max']:
            return {'categoria': 'bajo', **umbrales['cpu']['bajo']}
        elif cpu_porcentaje < umbrales['cpu']['moderado']['max']:
            return {'categoria': 'moderado', **umbrales['cpu']['moderado']}
        elif cpu_porcentaje < umbrales['cpu']['alto']['max']:
            return {'categoria': 'alto', **umbrales['cpu']['alto']}
        else:
            return {'categoria': 'critico', **umbrales['cpu']['critico']}
    
    def _clasificar_memoria_por_umbral(self, memoria_mb: float, umbrales: Dict) -> Dict[str, Any]:
        """Clasifica el uso de memoria según umbrales"""
        if memoria_mb < umbrales['memoria']['normal']['max']:
            return {'categoria': 'normal', **umbrales['memoria']['normal']}
        elif memoria_mb < umbrales['memoria']['aceptable']['max']:
            return {'categoria': 'aceptable', **umbrales['memoria']['aceptable']}
        else:
            return {'categoria': 'alto', **umbrales['memoria']['alto']}
    
    def _clasificar_recursos_umbrales(self, resultados: Dict):
        """
        Clasifica la utilización de recursos de todos los procesos según umbrales
        """
        umbrales = self._obtener_umbrales_recursos()
        
        procesos_map = {
            'registro_envios': '4.6.4 Registro de Envíos',
            'asignacion_tarifas': '4.6.5 Asignación de Tarifas',
            'busqueda_semantica': '4.6.6 Búsqueda Semántica'
        }
        
        for proceso_key, titulo in procesos_map.items():
            if proceso_key not in resultados or not resultados[proceso_key]:
                continue
            
            if 'estadisticas_recursos' not in resultados[proceso_key]:
                continue
            
            recursos = resultados[proceso_key]['estadisticas_recursos']
            cpu_promedio = recursos['cpu']['media']
            memoria_promedio = recursos['memoria_mb']['media']
            
            clasif_cpu = self._clasificar_cpu_por_umbral(cpu_promedio, umbrales)
            clasif_mem = self._clasificar_memoria_por_umbral(memoria_promedio, umbrales)
            
            self.stdout.write(self.style.WARNING(f'\n{titulo}'))
            self.stdout.write(f'\n{resultados[proceso_key]["nombre"]} - Clasificación por Umbrales:')
            self.stdout.write(f'  CPU promedio: {cpu_promedio:.2f}%')
            self.stdout.write(f'    Clasificación: {clasif_cpu["icono"]} {clasif_cpu["categoria"].upper()}')
            self.stdout.write(f'    Interpretación: {clasif_cpu["descripcion"]}')
            self.stdout.write(f'  Memoria promedio: {memoria_promedio:.2f} MB')
            self.stdout.write(f'    Clasificación: {clasif_mem["icono"]} {clasif_mem["categoria"].upper()}')
            self.stdout.write(f'    Interpretación: {clasif_mem["descripcion"]}')
    
    def _mostrar_hipotesis_resultados(self, proceso: str, analisis: Dict, nombre_proceso: str):
        """Muestra análisis de hipótesis de los resultados"""
        self.stdout.write(self.style.SUCCESS(f'\n  Análisis de Hipótesis ({nombre_proceso}):'))
        
        media = analisis.get('media', 0)
        ic = analisis.get('intervalo_confianza_95', {})
        cv = analisis.get('coeficiente_variacion', 0)
        es_normal = analisis.get('test_normalidad', {}).get('es_normal', True)
        
        # Hipótesis sobre el rendimiento
        self.stdout.write(f'\n    Hipótesis 1: El tiempo promedio está dentro de un rango aceptable')
        self.stdout.write(f'      Media observada: {media:.2f} ms')
        self.stdout.write(f'      IC 95%: [{ic.get("inferior", 0):.2f}, {ic.get("superior", 0):.2f}] ms')
        
        # Evaluar si el tiempo es aceptable (ejemplo: < 1000ms para la mayoría de procesos)
        umbral_aceptable = 1000  # ms
        if media < umbral_aceptable:
            self.stdout.write(f'      Conclusión: ✅ Aceptable (media < {umbral_aceptable} ms)')
        else:
            self.stdout.write(f'      Conclusión: ⚠️  Requiere atención (media >= {umbral_aceptable} ms)')
        
        # Hipótesis sobre la variabilidad
        self.stdout.write(f'\n    Hipótesis 2: La variabilidad del proceso es consistente')
        self.stdout.write(f'      Coeficiente de variación: {cv:.2f}%')
        if cv < 20:
            self.stdout.write(f'      Conclusión: ✅ Consistente (CV < 20%)')
        elif cv < 30:
            self.stdout.write(f'      Conclusión: ⚠️  Moderadamente variable (20% <= CV < 30%)')
        else:
            self.stdout.write(f'      Conclusión: 🔴 Alta variabilidad (CV >= 30%)')
        
        # Hipótesis sobre la distribución
        self.stdout.write(f'\n    Hipótesis 3: Los tiempos siguen una distribución normal')
        self.stdout.write(f'      Test Shapiro-Wilk: {analisis.get("test_normalidad", {}).get("interpretacion", "N/A")}')
        if es_normal:
            self.stdout.write(f'      Conclusión: ✅ Los datos son normales, se pueden usar tests paramétricos')
        else:
            self.stdout.write(f'      Conclusión: ⚠️  Los datos no son normales, considerar tests no paramétricos')
        
        # Hipótesis general
        self.stdout.write(f'\n    Hipótesis General: El sistema automatizado mejora significativamente el proceso')
        if media < umbral_aceptable and cv < 30:
            self.stdout.write(f'      Conclusión: ✅ El sistema muestra rendimiento aceptable y consistente')
        else:
            self.stdout.write(f'      Conclusión: ⚠️  El sistema requiere optimización')
    
    def _mostrar_hipotesis_recursos(self, proceso: str, analisis: Dict, nombre_proceso: str):
        """Muestra análisis de hipótesis de los resultados de utilización de recursos"""
        self.stdout.write(self.style.SUCCESS(f'\n  Análisis de Hipótesis - Utilización de Recursos ({nombre_proceso}):'))
        
        cpu_analisis = analisis.get('cpu', {})
        mem_analisis = analisis.get('memoria', {})
        
        # Hipótesis sobre CPU
        cpu_media = cpu_analisis.get('media', 0)
        cpu_ic = cpu_analisis.get('intervalo_confianza_95', {})
        cpu_normal = cpu_analisis.get('test_normalidad', {}).get('es_normal', True)
        
        self.stdout.write(f'\n    Hipótesis 1 (CPU): El uso de CPU está dentro de un rango eficiente')
        self.stdout.write(f'      Media observada: {cpu_media:.2f}%')
        self.stdout.write(f'      IC 95%: [{cpu_ic.get("inferior", 0):.2f}, {cpu_ic.get("superior", 0):.2f}]%')
        
        # Umbrales de CPU
        if cpu_media < 10:
            self.stdout.write(f'      Conclusión: ✅ Uso muy bajo, excelente eficiencia (CPU < 10%)')
        elif cpu_media < 30:
            self.stdout.write(f'      Conclusión: ✅ Uso moderado, eficiencia aceptable (10% <= CPU < 30%)')
        elif cpu_media < 50:
            self.stdout.write(f'      Conclusión: ⚠️  Uso alto, requiere monitoreo (30% <= CPU < 50%)')
        else:
            self.stdout.write(f'      Conclusión: 🔴 Uso crítico, optimización urgente (CPU >= 50%)')
        
        self.stdout.write(f'\n    Hipótesis 2 (CPU): La variabilidad del uso de CPU es consistente')
        self.stdout.write(f'      Distribución: {cpu_analisis.get("test_normalidad", {}).get("interpretacion", "N/A")}')
        if cpu_normal:
            self.stdout.write(f'      Conclusión: ✅ Los datos son normales, uso predecible')
        else:
            self.stdout.write(f'      Conclusión: ⚠️  Los datos no son normales, puede haber picos inesperados')
        
        # Hipótesis sobre Memoria
        mem_media = mem_analisis.get('media', 0)
        mem_ic = mem_analisis.get('intervalo_confianza_95', {})
        mem_normal = mem_analisis.get('test_normalidad', {}).get('es_normal', True)
        
        self.stdout.write(f'\n    Hipótesis 3 (Memoria): El consumo de memoria está dentro de límites aceptables')
        self.stdout.write(f'      Media observada: {mem_media:.2f} MB')
        self.stdout.write(f'      IC 95%: [{mem_ic.get("inferior", 0):.2f}, {mem_ic.get("superior", 0):.2f}] MB')
        
        # Umbrales de memoria
        if mem_media < 5:
            self.stdout.write(f'      Conclusión: ✅ Consumo bajo, excelente (Memoria < 5 MB)')
        elif mem_media < 20:
            self.stdout.write(f'      Conclusión: ✅ Consumo moderado, aceptable (5 MB <= Memoria < 20 MB)')
        else:
            self.stdout.write(f'      Conclusión: ⚠️  Consumo alto, investigar posibles memory leaks (Memoria >= 20 MB)')
        
        self.stdout.write(f'\n    Hipótesis 4 (Memoria): La variabilidad del consumo de memoria es consistente')
        self.stdout.write(f'      Distribución: {mem_analisis.get("test_normalidad", {}).get("interpretacion", "N/A")}')
        if mem_normal:
            self.stdout.write(f'      Conclusión: ✅ Los datos son normales, consumo predecible')
        else:
            self.stdout.write(f'      Conclusión: ⚠️  Los datos no son normales, puede haber memory leaks')
        
        # Hipótesis general
        self.stdout.write(f'\n    Hipótesis General: El sistema utiliza los recursos de manera eficiente')
        if cpu_media < 30 and mem_media < 20:
            self.stdout.write(f'      Conclusión: ✅ El sistema muestra uso eficiente de recursos (CPU < 30%, Memoria < 20 MB)')
        else:
            self.stdout.write(f'      Conclusión: ⚠️  El sistema requiere optimización de recursos')
    
    def _mostrar_comparativa_manual_vs_web(self, resultados: Dict):
        """Muestra comparativa entre proceso manual y sistema web usando datos reales"""
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write('COMPARATIVA: PROCESO MANUAL vs SISTEMA WEB (Resumen General)')
        self.stdout.write('='*80)
        
        # Tiempos manuales estimados (en segundos)
        tiempos_manuales = {
            'Registro de Envíos': 240,  # 4 minutos
            'Asignación de Tarifas': 105,  # 1.75 minutos
            'Búsqueda Semántica': 365  # 6 minutos
        }
        
        procesos_map = {
            'registro_envios': 'Registro de Envíos',
            'asignacion_tarifas': 'Asignación de Tarifas',
            'busqueda_semantica': 'Búsqueda Semántica'
        }
        
        # Mostrar tabla comparativa usando datos reales
        self.stdout.write('\n' + '-'*80)
        self.stdout.write(f'{"Proceso":<35} {"Manual":<20} {"Sistema Web":<20} {"Mejora":<10}')
        self.stdout.write('-'*80)
        
        for proceso_key, nombre_proceso in procesos_map.items():
            if proceso_key not in resultados or not resultados[proceso_key]:
                continue
            
            if 'estadisticas_respuesta' not in resultados[proceso_key]:
                continue
            
            tiempo_manual_seg = tiempos_manuales.get(nombre_proceso, 0)
            tiempo_web_ms = resultados[proceso_key]['estadisticas_respuesta']['media']
            tiempo_web_seg = tiempo_web_ms / 1000
            
            if tiempo_manual_seg == 0:
                continue
            
            tiempo_manual_min = tiempo_manual_seg / 60
            mejora = (tiempo_manual_seg / tiempo_web_seg) if tiempo_web_seg > 0 else 0
            
            self.stdout.write(
                f'{nombre_proceso:<35} '
                f'{tiempo_manual_min:>6.2f} min{"":<13} '
                f'{tiempo_web_seg:>6.2f} seg{"":<13} '
                f'{mejora:>6.1f}x'
            )
        
        self.stdout.write('-'*80)
        
        # Resumen de mejoras usando datos reales
        self.stdout.write('\nRESUMEN DE MEJORAS (usando datos reales del sistema):')
        for proceso_key, nombre_proceso in procesos_map.items():
            if proceso_key not in resultados or not resultados[proceso_key]:
                continue
            
            if 'estadisticas_respuesta' not in resultados[proceso_key]:
                continue
            
            tiempo_manual_seg = tiempos_manuales.get(nombre_proceso, 0)
            tiempo_web_ms = resultados[proceso_key]['estadisticas_respuesta']['media']
            tiempo_web_seg = tiempo_web_ms / 1000
            
            if tiempo_manual_seg == 0:
                continue
            
            mejora = (tiempo_manual_seg / tiempo_web_seg) if tiempo_web_seg > 0 else 0
            ahorro_seg = tiempo_manual_seg - tiempo_web_seg
            ahorro_porcentaje = (ahorro_seg / tiempo_manual_seg * 100) if tiempo_manual_seg > 0 else 0
            
            self.stdout.write(f'\n{nombre_proceso}:')
            self.stdout.write(f'  Tiempo manual: {tiempo_manual_seg} segundos ({tiempo_manual_seg/60:.2f} minutos)')
            self.stdout.write(f'  Tiempo web: {tiempo_web_seg:.2f} segundos ({tiempo_web_ms:.2f} ms)')
            self.stdout.write(f'  Mejora: {mejora:.1f}x más rápido')
            self.stdout.write(f'  Ahorro: {ahorro_seg:.2f} segundos ({ahorro_porcentaje:.1f}% más rápido)')
    
    def _mostrar_resumen(self, resultados: Dict):
        """Muestra resumen final de resultados"""
        self.stdout.write(self.style.SUCCESS('\n' + '='*80))
        self.stdout.write('RESUMEN FINAL')
        self.stdout.write('='*80)
        
        procesos = ['registro_envios', 'asignacion_tarifas', 'busqueda_semantica']
        
        self.stdout.write(f'\n{"Proceso":<30} {"Tiempo Promedio (ms)":<25} {"CPU Promedio (%)":<20} {"Memoria Promedio (MB)":<25}')
        self.stdout.write('-'*100)
        
        for proceso in procesos:
            if proceso not in resultados or not resultados[proceso]:
                continue
            
            # Verificar que tiene todos los datos necesarios
            if 'nombre' not in resultados[proceso]:
                continue
            if 'estadisticas_respuesta' not in resultados[proceso]:
                continue
            if 'estadisticas_recursos' not in resultados[proceso]:
                continue
            
            nombre = resultados[proceso]['nombre']
            tiempo = resultados[proceso]['estadisticas_respuesta']['media']
            cpu = resultados[proceso]['estadisticas_recursos']['cpu']['media']
            memoria = resultados[proceso]['estadisticas_recursos']['memoria_mb']['media']
            
            self.stdout.write(
                f'{nombre:<30} '
                f'{tiempo:>20.2f} ms{"":<4} '
                f'{cpu:>15.2f}%{"":<4} '
                f'{memoria:>20.2f} MB{"":<4}'
            )
    
    def _exportar_resultados(self, resultados: Dict):
        """Exporta resultados a archivo JSON"""
        import json
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'resultados_rendimiento_{timestamp}.json'
        
        # Preparar datos para exportación
        datos_exportar = {
            'fecha': datetime.now().isoformat(),
            'resultados': {}
        }
        
        for proceso, datos in resultados.items():
            if 'tiempos_respuesta' in datos:
                datos_exportar['resultados'][proceso] = {
                    'estadisticas_respuesta': datos['estadisticas_respuesta'],
                    'estadisticas_espera': datos['estadisticas_espera'],
                    'estadisticas_recursos': datos['estadisticas_recursos'],
                }
            else:
                datos_exportar['resultados'][proceso] = datos
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(datos_exportar, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(self.style.SUCCESS(f'\nResultados exportados a: {filename}'))

