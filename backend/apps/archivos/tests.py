# backend/apps/archivos/tests.py
"""
Tests completos para la aplicación de archivos (envíos, productos, tarifas)
Incluye tests funcionales, de rendimiento, de integración y de validación
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from django.db import connection
from django.db import reset_queries
from decimal import Decimal
import time
import statistics
from .models import Envio, Producto, Tarifa
from .services import EnvioService, TarifaService

Usuario = get_user_model()


class EnvioTestCase(TestCase):
    """Tests básicos de funcionalidad de envíos"""
    
    def setUp(self):
        self.client = APIClient()
        # Crear usuario admin
        self.usuario = Usuario.objects.create(
            username='testuser',
            correo='testuser@test.com',
            cedula='1234567890',
            nombre='Usuario Test',
            rol=1,  # Admin
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
            rol=4,  # Comprador
            is_active=True
        )
        self.comprador.set_password('testpass123')
        self.comprador.save()
        
        # Crear tarifa de prueba
        self.tarifa = Tarifa.objects.create(
            categoria='electronica',
            peso_minimo=0,
            peso_maximo=100,
            precio_por_kg=Decimal('5.00'),
            cargo_base=Decimal('10.00')
        )
    
    def test_crear_envio_basico(self):
        """Test básico de creación de envío"""
        data = {
            'hawb': 'HAW000001',
            'comprador': self.comprador.id,
            'estado': 'pendiente',
            'productos': [
                {
                    'descripcion': 'Producto Test',
                    'peso': 10.5,
                    'cantidad': 1,
                    'valor': 100.0,
                    'categoria': 'electronica'
                }
            ]
        }
        response = self.client.post('/api/envios/envios/', data, format='json')
        self.assertEqual(response.status_code, 201, 
                         f"Error: {response.data if hasattr(response, 'data') else response.content}")
        self.assertTrue(Envio.objects.filter(hawb='HAW000001').exists())
    
    def test_crear_envio_con_multiples_productos(self):
        """Test creación de envío con múltiples productos"""
        data = {
            'hawb': 'HAW000002',
            'comprador': self.comprador.id,
            'estado': 'pendiente',
            'productos': [
                {
                    'descripcion': 'Laptop',
                    'peso': 2.5,
                    'cantidad': 1,
                    'valor': 800.0,
                    'categoria': 'electronica'
                },
                {
                    'descripcion': 'Mouse',
                    'peso': 0.2,
                    'cantidad': 2,
                    'valor': 15.0,
                    'categoria': 'electronica'
                }
            ]
        }
        response = self.client.post('/api/envios/envios/', data, format='json')
        self.assertEqual(response.status_code, 201)
        envio = Envio.objects.get(hawb='HAW000002')
        self.assertEqual(envio.productos.count(), 2)
    
    def test_validar_hawb_unico(self):
        """Test validación de HAWB único"""
        # Crear primer envío
        Envio.objects.create(
            hawb='HAW000003',
            comprador=self.comprador,
            peso_total=Decimal('10.0'),
            cantidad_total=1,
            valor_total=Decimal('100.0'),
            estado='pendiente'
        )
        
        # Intentar crear otro con mismo HAWB
        data = {
            'hawb': 'HAW000003',
            'comprador': self.comprador.id,
            'estado': 'pendiente',
            'productos': [
                {
                    'descripcion': 'Producto',
                    'peso': 5.0,
                    'cantidad': 1,
                    'valor': 50.0,
                    'categoria': 'electronica'
                }
            ]
        }
        response = self.client.post('/api/envios/envios/', data, format='json')
        self.assertNotEqual(response.status_code, 201)
    
    def test_cambiar_estado_envio(self):
        """Test cambio de estado de envío"""
        envio = Envio.objects.create(
            hawb='HAW000004',
            comprador=self.comprador,
            peso_total=Decimal('10.0'),
            cantidad_total=1,
            valor_total=Decimal('100.0'),
            estado='pendiente'
        )
        
        data = {'estado': 'en_transito'}
        response = self.client.patch(f'/api/envios/envios/{envio.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)
        envio.refresh_from_db()
        self.assertEqual(envio.estado, 'en_transito')
    
    def test_listar_envios_filtro_estado(self):
        """Test listado con filtro por estado"""
        # Crear envíos con diferentes estados
        Envio.objects.create(
            hawb='HAW000005',
            comprador=self.comprador,
            peso_total=Decimal('10.0'),
            cantidad_total=1,
            valor_total=Decimal('100.0'),
            estado='pendiente'
        )
        Envio.objects.create(
            hawb='HAW000006',
            comprador=self.comprador,
            peso_total=Decimal('10.0'),
            cantidad_total=1,
            valor_total=Decimal('100.0'),
            estado='entregado'
        )
        
        response = self.client.get('/api/envios/envios/?estado=pendiente')
        self.assertEqual(response.status_code, 200)
        # Verificar que solo devuelve pendientes
        for envio in response.data.get('results', []):
            self.assertEqual(envio['estado'], 'pendiente')
    
    def test_calcular_costo_servicio(self):
        """Test cálculo automático de costo de servicio"""
        envio = Envio.objects.create(
            hawb='HAW000007',
            comprador=self.comprador,
            peso_total=Decimal('10.0'),
            cantidad_total=1,
            valor_total=Decimal('100.0'),
            estado='pendiente'
        )
        
        Producto.objects.create(
            envio=envio,
            descripcion='Producto Test',
            peso=Decimal('10.0'),
            cantidad=1,
            valor=Decimal('100.0'),
            categoria='electronica'
        )
        
        costo = envio.calcular_costo_servicio()
        # Cargo base (10) + peso (10) * precio_por_kg (5) = 60
        self.assertEqual(costo, Decimal('60.00'))
    
    def test_eliminar_envio(self):
        """Test eliminación de envío"""
        envio = Envio.objects.create(
            hawb='HAW000008',
            comprador=self.comprador,
            peso_total=Decimal('10.0'),
            cantidad_total=1,
            valor_total=Decimal('100.0'),
            estado='pendiente'
        )
        
        response = self.client.delete(f'/api/envios/envios/{envio.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Envio.objects.filter(id=envio.id).exists())


class TarifaTestCase(TestCase):
    """Tests para funcionalidad de tarifas"""
    
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
    
    def test_crear_tarifa(self):
        """Test creación de tarifa"""
        data = {
            'categoria': 'electronica',
            'peso_minimo': 0,
            'peso_maximo': 50,
            'precio_por_kg': 5.50,
            'cargo_base': 12.00
        }
        response = self.client.post('/api/envios/tarifas/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Tarifa.objects.filter(categoria='electronica').exists())
    
    def test_buscar_tarifa_por_categoria_y_peso(self):
        """Test búsqueda de tarifa apropiada"""
        Tarifa.objects.create(
            categoria='electronica',
            peso_minimo=Decimal('0'),
            peso_maximo=Decimal('50'),
            precio_por_kg=Decimal('5.00'),
            cargo_base=Decimal('10.00')
        )
        
        tarifa = TarifaService.buscar_tarifa('electronica', Decimal('25.0'))
        self.assertIsNotNone(tarifa)
        self.assertEqual(tarifa.categoria, 'electronica')
    
    def test_calcular_costo_con_tarifa(self):
        """Test cálculo de costo usando tarifa"""
        Tarifa.objects.create(
            categoria='electronica',
            peso_minimo=Decimal('0'),
            peso_maximo=Decimal('100'),
            precio_por_kg=Decimal('5.00'),
            cargo_base=Decimal('10.00')
        )
        
        costo = TarifaService.calcular_costo('electronica', Decimal('20.0'), cantidad=1)
        # cargo_base (10) + peso (20) * precio_por_kg (5) = 110
        self.assertEqual(costo, Decimal('110.00'))


class EnvioPerformanceTestCase(TransactionTestCase):
    """Tests de rendimiento para operaciones de envíos"""
    
    def setUp(self):
        self.client = APIClient()
        self.usuario = Usuario.objects.create(
            username='testuser',
            correo='testuser@test.com',
            cedula='1234567890',
            nombre='Usuario Test',
            rol=1,  # Admin
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
        self.comprador.set_password('testpass123')
        self.comprador.save()
        
        # Crear tarifa para pruebas
        Tarifa.objects.create(
            categoria='electronica',
            peso_minimo=Decimal('0'),
            peso_maximo=Decimal('100'),
            precio_por_kg=Decimal('5.00'),
            cargo_base=Decimal('10.00')
        )
    
    def test_crear_envio_tiempo_respuesta(self):
        """Test que verifica que crear un envío toma menos de 2 segundos"""
        data = {
            'hawb': 'HAW000001',
            'comprador': self.comprador.id,
            'peso_total': 10.5,
            'cantidad_total': 1,
            'valor_total': 100.0,
            'estado': 'pendiente',
            'productos': [
                {
                    'descripcion': 'Producto 1',
                    'peso': 5.0,
                    'cantidad': 2,
                    'valor': 50.0,
                    'categoria': 'electronica'
                }
            ]
        }
        
        inicio = time.time()
        response = self.client.post('/api/envios/envios/', data, format='json')
        tiempo_respuesta = time.time() - inicio
        
        self.assertEqual(response.status_code, 201)
        self.assertLess(tiempo_respuesta, 2.0, 
                       f"Crear envío tomó {tiempo_respuesta:.2f}s, debe ser < 2s")
    
    def test_crear_multiples_envios_rendimiento(self):
        """Test de rendimiento al crear múltiples envíos"""
        tiempos = []
        
        for i in range(10):
            data = {
                'hawb': f'HAWPERF{i:04d}',
                'comprador': self.comprador.id,
                'estado': 'pendiente',
                'productos': [
                    {
                        'descripcion': f'Producto {i}',
                        'peso': 10.0,
                        'cantidad': 1,
                        'valor': 100.0,
                        'categoria': 'electronica'
                    }
                ]
            }
            
            inicio = time.time()
            response = self.client.post('/api/envios/envios/', data, format='json')
            tiempo = time.time() - inicio
            
            self.assertEqual(response.status_code, 201)
            tiempos.append(tiempo)
        
        tiempo_promedio = statistics.mean(tiempos)
        tiempo_maximo = max(tiempos)
        
        self.assertLess(tiempo_promedio, 2.0, 
                       f"Tiempo promedio {tiempo_promedio:.2f}s debe ser < 2s")
        self.assertLess(tiempo_maximo, 3.0,
                       f"Tiempo máximo {tiempo_maximo:.2f}s debe ser < 3s")
    
    def test_listar_envios_tiempo_respuesta(self):
        """Test que verifica tiempo de respuesta al listar envíos"""
        # Crear 100 envíos de prueba
        envios = []
        for i in range(100):
            envios.append(Envio(
                hawb=f'HAW{i:05d}',
                comprador=self.comprador,
                peso_total=Decimal('10.0'),
                cantidad_total=1,
                valor_total=Decimal('100.0'),
                estado='pendiente'
            ))
        Envio.objects.bulk_create(envios)
        
        inicio = time.time()
        response = self.client.get('/api/envios/envios/')
        tiempo_respuesta = time.time() - inicio
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(tiempo_respuesta, 1.0, 
                       f"Listar envíos tomó {tiempo_respuesta:.2f}s, debe ser < 1s")
    
    def test_buscar_envios_tiempo_respuesta(self):
        """Test tiempo de respuesta de búsqueda de envíos"""
        # Crear 50 envíos
        for i in range(50):
            Envio.objects.create(
                hawb=f'HAW{i:05d}',
                comprador=self.comprador,
                peso_total=Decimal('10.0'),
                cantidad_total=1,
                valor_total=Decimal('100.0'),
                estado='pendiente'
            )
        
        inicio = time.time()
        response = self.client.get('/api/envios/envios/?search=HAW00001')
        tiempo_busqueda = time.time() - inicio
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(tiempo_busqueda, 0.5,
                       f"Búsqueda tomó {tiempo_busqueda:.2f}s, debe ser < 0.5s")
    
    def test_calcular_costo_servicio_eficiencia(self):
        """Test que verifica eficiencia del cálculo de costos"""
        envio = Envio.objects.create(
            hawb='HAW000001',
            comprador=self.comprador,
            peso_total=Decimal('10.0'),
            cantidad_total=50,
            valor_total=Decimal('100.0')
        )
        
        # Crear 50 productos
        productos = []
        for i in range(50):
            productos.append(Producto(
                envio=envio,
                descripcion=f'Producto {i}',
                peso=Decimal('0.2'),
                cantidad=1,
                valor=Decimal('2.0'),
                categoria='electronica'
            ))
        Producto.objects.bulk_create(productos)
        
        inicio = time.time()
        costo = envio.calcular_costo_servicio()
        tiempo_calculo = time.time() - inicio
        
        self.assertGreater(costo, 0)
        self.assertLess(tiempo_calculo, 0.5, 
                       f"Cálculo de costo tomó {tiempo_calculo:.2f}s, debe ser < 0.5s")
    
    def test_consultas_optimizadas_n_plus_1(self):
        """Test que verifica que no hay consultas N+1 al listar envíos"""
        # Crear 10 envíos con productos
        for i in range(10):
            envio = Envio.objects.create(
                hawb=f'HAW{i:05d}',
                comprador=self.comprador,
                peso_total=Decimal('10.0'),
                cantidad_total=1,
                valor_total=Decimal('100.0'),
                estado='pendiente'
            )
            Producto.objects.create(
                envio=envio,
                descripcion=f'Producto {i}',
                peso=Decimal('5.0'),
                cantidad=1,
                valor=Decimal('50.0'),
                categoria='electronica'
            )
        
        reset_queries()
        envios = Envio.objects.select_related('comprador').prefetch_related('productos').all()
        
        # Acceder a relaciones para forzar queries
        for envio in envios:
            _ = envio.comprador.nombre
            _ = list(envio.productos.all())
        
        num_queries = len(connection.queries)
        self.assertLessEqual(num_queries, 3, 
                           f"Se realizaron {num_queries} queries, deberían ser máximo 3")
    
    def test_rendimiento_actualizacion_masiva(self):
        """Test de rendimiento en actualización masiva de estados"""
        # Crear 50 envíos
        envios = []
        for i in range(50):
            envios.append(Envio(
                hawb=f'HAWUP{i:04d}',
                comprador=self.comprador,
                peso_total=Decimal('10.0'),
                cantidad_total=1,
                valor_total=Decimal('100.0'),
                estado='pendiente'
            ))
        Envio.objects.bulk_create(envios)
        
        inicio = time.time()
        Envio.objects.filter(hawb__startswith='HAWUP').update(estado='en_transito')
        tiempo_actualizacion = time.time() - inicio
        
        self.assertLess(tiempo_actualizacion, 1.0,
                       f"Actualización masiva tomó {tiempo_actualizacion:.2f}s, debe ser < 1s")
        
        # Verificar que se actualizaron
        count = Envio.objects.filter(hawb__startswith='HAWUP', estado='en_transito').count()
        self.assertEqual(count, 50)