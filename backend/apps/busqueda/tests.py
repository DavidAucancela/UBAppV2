"""
Tests completos para la aplicación de búsqueda semántica
Incluye tests de funcionalidad, precisión, rendimiento y métricas
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from decimal import Decimal
import time
import statistics
from unittest.mock import patch, MagicMock

from apps.archivos.models import Envio, Producto
from .services import BusquedaSemanticaService
from .models import HistorialBusqueda

Usuario = get_user_model()


class BusquedaSemanticaTestCase(TestCase):
    """Tests básicos de funcionalidad de búsqueda semántica"""
    
    def setUp(self):
        self.client = APIClient()
        self.usuario = Usuario.objects.create(
            username='testuser',
            correo='testuser@test.com',
            cedula='1234567890',
            nombre='Usuario Test',
            rol=1,
            is_active=True
        )
        self.usuario.set_password('testpass123')
        self.usuario.save()
        self.client.force_authenticate(user=self.usuario)
        
        # Crear comprador
        self.comprador = Usuario.objects.create(
            username='comprador1',
            correo='comprador1@test.com',
            cedula='0987654321',
            nombre='Juan Pérez',
            rol=4,
            is_active=True
        )
        
        # Crear envíos de prueba con productos
        self.envio1 = Envio.objects.create(
            hawb='HAW001',
            comprador=self.comprador,
            peso_total=Decimal('5.0'),
            cantidad_total=1,
            valor_total=Decimal('150.0'),
            estado='entregado',
            ciudad_destino='Quito'
        )
        Producto.objects.create(
            envio=self.envio1,
            descripcion='Laptop Dell Inspiron',
            peso=Decimal('2.5'),
            cantidad=1,
            valor=Decimal('150.0'),
            categoria='electronica'
        )
        
        self.envio2 = Envio.objects.create(
            hawb='HAW002',
            comprador=self.comprador,
            peso_total=Decimal('10.0'),
            cantidad_total=2,
            valor_total=Decimal('300.0'),
            estado='en_transito',
            ciudad_destino='Guayaquil'
        )
        Producto.objects.create(
            envio=self.envio2,
            descripcion='Camiseta deportiva Nike',
            peso=Decimal('0.3'),
            cantidad=5,
            valor=Decimal('100.0'),
            categoria='ropa'
        )
        Producto.objects.create(
            envio=self.envio2,
            descripcion='Pantalón deportivo Adidas',
            peso=Decimal('0.4'),
            cantidad=3,
            valor=Decimal('200.0'),
            categoria='ropa'
        )
        
        self.envio3 = Envio.objects.create(
            hawb='HAW003',
            comprador=self.comprador,
            peso_total=Decimal('15.0'),
            cantidad_total=1,
            valor_total=Decimal('500.0'),
            estado='pendiente',
            ciudad_destino='Cuenca'
        )
        Producto.objects.create(
            envio=self.envio3,
            descripcion='Televisor Samsung 55 pulgadas',
            peso=Decimal('15.0'),
            cantidad=1,
            valor=Decimal('500.0'),
            categoria='electronica'
        )
    
    def test_busqueda_basica_funciona(self):
        """Test que la búsqueda básica retorna resultados"""
        response = self.client.get('/api/busqueda/buscar/?q=laptop')
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.data)
    
    @patch('apps.busqueda.services.openai_client')
    def test_busqueda_semantica_funciona(self, mock_openai):
        """Test que la búsqueda semántica funciona correctamente"""
        # Mock del embedding de OpenAI
        mock_embedding = MagicMock()
        mock_embedding.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_openai.embeddings.create.return_value = mock_embedding
        
        response = self.client.post('/api/busqueda/semantica/', {
            'consulta': 'computadoras portátiles',
            'limite': 10
        }, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('resultados', response.data)
        self.assertIn('tiempoRespuesta', response.data)
    
    def test_busqueda_guarda_historial(self):
        """Test que la búsqueda guarda el historial"""
        count_inicial = HistorialBusqueda.objects.count()
        
        response = self.client.get('/api/busqueda/buscar/?q=laptop')
        self.assertEqual(response.status_code, 200)
        
        count_final = HistorialBusqueda.objects.count()
        self.assertEqual(count_final, count_inicial + 1)
    
    def test_filtros_fecha_funcionan(self):
        """Test que los filtros de fecha funcionan correctamente"""
        # Crear envío con fecha específica
        fecha_especifica = timezone.now() - timezone.timedelta(days=10)
        Envio.objects.create(
            hawb='HAW004',
            comprador=self.comprador,
            peso_total=Decimal('5.0'),
            cantidad_total=1,
            valor_total=Decimal('100.0'),
            estado='pendiente',
            fecha_emision=fecha_especifica
        )
        
        # Buscar con filtro de fecha
        fecha_desde = (timezone.now() - timezone.timedelta(days=15)).date().isoformat()
        fecha_hasta = timezone.now().date().isoformat()
        
        response = self.client.get(
            f'/api/busqueda/buscar/?q=HAW004&fecha_desde={fecha_desde}&fecha_hasta={fecha_hasta}'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_filtro_estado_funciona(self):
        """Test que el filtro de estado funciona"""
        response = self.client.get('/api/busqueda/buscar/?q=&estado=entregado')
        self.assertEqual(response.status_code, 200)
        
        # Verificar que todos los resultados son entregados
        for resultado in response.data.get('resultados', []):
            self.assertEqual(resultado.get('estado'), 'entregado')
    
    def test_filtro_ciudad_funciona(self):
        """Test que el filtro de ciudad funciona"""
        response = self.client.get('/api/busqueda/buscar/?q=&ciudad_destino=Quito')
        self.assertEqual(response.status_code, 200)
        
        # Verificar que todos los resultados son de Quito
        for resultado in response.data.get('resultados', []):
            self.assertEqual(resultado.get('ciudad_destino'), 'Quito')
    
    def test_busqueda_vacia_retorna_todos(self):
        """Test que búsqueda vacía retorna todos los envíos"""
        response = self.client.get('/api/busqueda/buscar/?q=')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data.get('resultados', [])), 0)
    
    def test_busqueda_sin_resultados(self):
        """Test búsqueda que no retorna resultados"""
        response = self.client.get('/api/busqueda/buscar/?q=ZZZZZZZZZ')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('resultados', [])), 0)
    
    def test_historial_busqueda_usuario(self):
        """Test que el historial se filtra por usuario"""
        # Realizar búsquedas
        self.client.get('/api/busqueda/buscar/?q=laptop')
        self.client.get('/api/busqueda/buscar/?q=televisor')
        
        # Obtener historial
        response = self.client.get('/api/busqueda/historial/')
        self.assertEqual(response.status_code, 200)
        
        # Verificar que solo muestra del usuario actual
        for busqueda in response.data.get('results', []):
            self.assertEqual(busqueda['usuario'], self.usuario.id)


class BusquedaSemanticaPerformanceTestCase(TransactionTestCase):
    """Tests de rendimiento para búsqueda semántica"""
    
    def setUp(self):
        self.client = APIClient()
        self.usuario = Usuario.objects.create(
            username='testuser',
            correo='testuser@test.com',
            cedula='1234567890',
            nombre='Usuario Test',
            rol=1,
            is_active=True
        )
        self.usuario.set_password('testpass123')
        self.usuario.save()
        self.client.force_authenticate(user=self.usuario)
        
        # Crear comprador
        self.comprador = Usuario.objects.create(
            username='comprador1',
            correo='comprador1@test.com',
            cedula='0987654321',
            nombre='Comprador Test',
            rol=4,
            is_active=True
        )
        
        # Crear 100 envíos de prueba
        envios = []
        for i in range(100):
            envios.append(Envio(
                hawb=f'HAWPERF{i:05d}',
                comprador=self.comprador,
                peso_total=Decimal('10.0'),
                cantidad_total=1,
                valor_total=Decimal('100.0'),
                estado='pendiente',
                ciudad_destino='Quito'
            ))
        Envio.objects.bulk_create(envios)
        
        # Crear productos para algunos envíos
        productos = []
        for i in range(0, 100, 10):
            envio = Envio.objects.get(hawb=f'HAWPERF{i:05d}')
            productos.append(Producto(
                envio=envio,
                descripcion=f'Producto Test {i}',
                peso=Decimal('5.0'),
                cantidad=1,
                valor=Decimal('100.0'),
                categoria='electronica'
            ))
        Producto.objects.bulk_create(productos)
    
    def test_busqueda_basica_tiempo_respuesta(self):
        """Test tiempo de respuesta de búsqueda básica"""
        tiempos = []
        
        for _ in range(10):
            inicio = time.time()
            response = self.client.get('/api/busqueda/buscar/?q=producto')
            tiempo = time.time() - inicio
            
            self.assertEqual(response.status_code, 200)
            tiempos.append(tiempo)
        
        tiempo_promedio = statistics.mean(tiempos)
        tiempo_maximo = max(tiempos)
        
        self.assertLess(tiempo_promedio, 0.5,
                       f"Tiempo promedio {tiempo_promedio:.3f}s debe ser < 0.5s")
        self.assertLess(tiempo_maximo, 1.0,
                       f"Tiempo máximo {tiempo_maximo:.3f}s debe ser < 1.0s")
    
    @patch('apps.busqueda.services.openai_client')
    def test_busqueda_semantica_tiempo_respuesta(self, mock_openai):
        """Test tiempo de respuesta de búsqueda semántica"""
        # Mock del embedding
        mock_embedding = MagicMock()
        mock_embedding.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_openai.embeddings.create.return_value = mock_embedding
        
        tiempos = []
        
        for _ in range(5):
            inicio = time.time()
            response = self.client.post('/api/busqueda/semantica/', {
                'consulta': 'productos electrónicos',
                'limite': 20
            }, format='json')
            tiempo = time.time() - inicio
            
            self.assertEqual(response.status_code, 200)
            tiempos.append(tiempo)
        
        tiempo_promedio = statistics.mean(tiempos)
        
        # La búsqueda semántica puede ser más lenta
        self.assertLess(tiempo_promedio, 2.0,
                       f"Tiempo promedio {tiempo_promedio:.3f}s debe ser < 2.0s")
    
    def test_busqueda_con_multiples_filtros(self):
        """Test rendimiento de búsqueda con múltiples filtros"""
        inicio = time.time()
        response = self.client.get(
            '/api/busqueda/buscar/?q=HAWPERF&estado=pendiente&ciudad_destino=Quito'
        )
        tiempo = time.time() - inicio
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(tiempo, 0.5,
                       f"Búsqueda con filtros tomó {tiempo:.3f}s, debe ser < 0.5s")
    
    def test_paginacion_rendimiento(self):
        """Test que la paginación no afecta rendimiento"""
        # Primera página
        inicio = time.time()
        response1 = self.client.get('/api/busqueda/buscar/?q=&page=1&page_size=20')
        tiempo1 = time.time() - inicio
        
        # Página intermedia
        inicio = time.time()
        response2 = self.client.get('/api/busqueda/buscar/?q=&page=3&page_size=20')
        tiempo2 = time.time() - inicio
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        # Los tiempos deben ser similares
        self.assertLess(abs(tiempo1 - tiempo2), 0.2,
                       "La paginación no debe afectar significativamente el rendimiento")


class BusquedaSemanticaPrecisionTestCase(TestCase):
    """Tests de precisión y relevancia de búsqueda semántica"""
    
    def setUp(self):
        self.client = APIClient()
        self.usuario = Usuario.objects.create(
            username='testuser',
            correo='testuser@test.com',
            cedula='1234567890',
            nombre='Usuario Test',
            rol=1,
            is_active=True
        )
        self.usuario.set_password('testpass123')
        self.usuario.save()
        self.client.force_authenticate(user=self.usuario)
        
        self.comprador = Usuario.objects.create(
            username='comprador1',
            correo='comprador1@test.com',
            cedula='0987654321',
            nombre='Comprador Test',
            rol=4,
            is_active=True
        )
    
    def test_busqueda_exacta_hawb(self):
        """Test búsqueda exacta por HAWB"""
        Envio.objects.create(
            hawb='HAW12345',
            comprador=self.comprador,
            peso_total=Decimal('10.0'),
            cantidad_total=1,
            valor_total=Decimal('100.0'),
            estado='pendiente'
        )
        
        response = self.client.get('/api/busqueda/buscar/?q=HAW12345')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data.get('resultados', [])), 0)
        
        # El primer resultado debe ser el envío buscado
        primer_resultado = response.data['resultados'][0]
        self.assertEqual(primer_resultado['hawb'], 'HAW12345')
    
    def test_busqueda_por_nombre_comprador(self):
        """Test búsqueda por nombre de comprador"""
        comprador_especial = Usuario.objects.create(
            username='comprador_especial',
            correo='especial@test.com',
            cedula='1111111111',
            nombre='María Rodríguez',
            rol=4,
            is_active=True
        )
        
        Envio.objects.create(
            hawb='HAW99999',
            comprador=comprador_especial,
            peso_total=Decimal('10.0'),
            cantidad_total=1,
            valor_total=Decimal('100.0'),
            estado='pendiente'
        )
        
        response = self.client.get('/api/busqueda/buscar/?q=María')
        self.assertEqual(response.status_code, 200)
        
        # Debe encontrar el envío de María
        hawbs = [r['hawb'] for r in response.data.get('resultados', [])]
        self.assertIn('HAW99999', hawbs)
    
    def test_busqueda_por_descripcion_producto(self):
        """Test búsqueda por descripción de producto"""
        envio = Envio.objects.create(
            hawb='HAW88888',
            comprador=self.comprador,
            peso_total=Decimal('10.0'),
            cantidad_total=1,
            valor_total=Decimal('100.0'),
            estado='pendiente'
        )
        
        Producto.objects.create(
            envio=envio,
            descripcion='iPhone 15 Pro Max',
            peso=Decimal('0.3'),
            cantidad=1,
            valor=Decimal('1200.0'),
            categoria='electronica'
        )
        
        response = self.client.get('/api/busqueda/buscar/?q=iPhone')
        self.assertEqual(response.status_code, 200)
        
        # Debe encontrar el envío con el iPhone
        hawbs = [r['hawb'] for r in response.data.get('resultados', [])]
        self.assertIn('HAW88888', hawbs)
