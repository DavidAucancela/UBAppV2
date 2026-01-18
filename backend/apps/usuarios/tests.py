"""
Tests completos para la aplicación de usuarios
Incluye tests de autenticación, autorización, roles y permisos
"""
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
import time
import statistics

Usuario = get_user_model()


class UsuarioTestCase(TestCase):
    """Tests básicos de funcionalidad de usuarios"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = Usuario.objects.create(
            username='admin',
            correo='admin@test.com',
            cedula='1234567890',
            nombre='Admin Test',
            rol=1,
            is_active=True
        )
        self.admin.set_password('admin123')
        self.admin.save()
    
    def test_crear_usuario(self):
        """Test creación de usuario"""
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'username': 'nuevouser',
            'correo': 'nuevo@test.com',
            'cedula': '0987654321',
            'nombre': 'Usuario Nuevo',
            'rol': 3,  # Digitador
            'password': 'password123'
        }
        
        response = self.client.post('/api/usuarios/usuarios/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Usuario.objects.filter(username='nuevouser').exists())
    
    def test_correo_unico(self):
        """Test que el correo debe ser único"""
        Usuario.objects.create(
            username='user1',
            correo='test@test.com',
            cedula='1111111111',
            nombre='Usuario 1',
            rol=4
        )
        
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'username': 'user2',
            'correo': 'test@test.com',  # Mismo correo
            'cedula': '2222222222',
            'nombre': 'Usuario 2',
            'rol': 4,
            'password': 'password123'
        }
        
        response = self.client.post('/api/usuarios/usuarios/', data, format='json')
        self.assertNotEqual(response.status_code, 201)
    
    def test_cedula_unica(self):
        """Test que la cédula debe ser única"""
        Usuario.objects.create(
            username='user1',
            correo='user1@test.com',
            cedula='1111111111',
            nombre='Usuario 1',
            rol=4
        )
        
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'username': 'user2',
            'correo': 'user2@test.com',
            'cedula': '1111111111',  # Misma cédula
            'nombre': 'Usuario 2',
            'rol': 4,
            'password': 'password123'
        }
        
        response = self.client.post('/api/usuarios/usuarios/', data, format='json')
        self.assertNotEqual(response.status_code, 201)
    
    def test_actualizar_usuario(self):
        """Test actualización de información de usuario"""
        user = Usuario.objects.create(
            username='testupdate',
            correo='update@test.com',
            cedula='3333333333',
            nombre='Test Update',
            rol=4
        )
        
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'nombre': 'Nombre Actualizado',
            'telefono': '0999999999'
        }
        
        response = self.client.patch(f'/api/usuarios/usuarios/{user.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)
        
        user.refresh_from_db()
        self.assertEqual(user.nombre, 'Nombre Actualizado')
    
    def test_desactivar_usuario(self):
        """Test desactivación de usuario"""
        user = Usuario.objects.create(
            username='testdeactivate',
            correo='deactivate@test.com',
            cedula='4444444444',
            nombre='Test Deactivate',
            rol=4,
            is_active=True
        )
        
        self.client.force_authenticate(user=self.admin)
        
        data = {'es_activo': False}
        response = self.client.patch(f'/api/usuarios/usuarios/{user.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)
        
        user.refresh_from_db()
        self.assertFalse(user.is_active)
    
    def test_eliminar_usuario(self):
        """Test eliminación de usuario"""
        user = Usuario.objects.create(
            username='testdelete',
            correo='delete@test.com',
            cedula='5555555555',
            nombre='Test Delete',
            rol=4
        )
        
        self.client.force_authenticate(user=self.admin)
        
        response = self.client.delete(f'/api/usuarios/usuarios/{user.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Usuario.objects.filter(id=user.id).exists())
    
    def test_listar_usuarios(self):
        """Test listado de usuarios"""
        self.client.force_authenticate(user=self.admin)
        
        response = self.client.get('/api/usuarios/usuarios/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.data)


class AutenticacionTestCase(TestCase):
    """Tests de autenticación JWT"""
    
    def setUp(self):
        self.client = APIClient()
        self.usuario = Usuario.objects.create(
            username='testauth',
            correo='auth@test.com',
            cedula='6666666666',
            nombre='Test Auth',
            rol=1,
            is_active=True
        )
        self.usuario.set_password('testpass123')
        self.usuario.save()
    
    def test_login_exitoso(self):
        """Test login exitoso retorna token"""
        data = {
            'username': 'testauth',
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/token/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_credenciales_invalidas(self):
        """Test login con credenciales inválidas falla"""
        data = {
            'username': 'testauth',
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/api/token/', data, format='json')
        self.assertEqual(response.status_code, 401)
    
    def test_login_usuario_inactivo(self):
        """Test login con usuario inactivo falla"""
        self.usuario.is_active = False
        self.usuario.save()
        
        data = {
            'username': 'testauth',
            'password': 'testpass123'
        }
        
        response = self.client.post('/api/token/', data, format='json')
        self.assertNotEqual(response.status_code, 200)
    
    def test_refresh_token(self):
        """Test refresh token funciona"""
        # Obtener token inicial
        refresh = RefreshToken.for_user(self.usuario)
        
        data = {'refresh': str(refresh)}
        response = self.client.post('/api/token/refresh/', data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
    
    def test_acceso_sin_autenticacion(self):
        """Test que endpoints protegidos requieren autenticación"""
        response = self.client.get('/api/usuarios/usuarios/')
        self.assertEqual(response.status_code, 401)
    
    def test_acceso_con_token_valido(self):
        """Test acceso con token válido"""
        self.client.force_authenticate(user=self.usuario)
        
        response = self.client.get('/api/usuarios/usuarios/')
        self.assertEqual(response.status_code, 200)


class PermisosRolesTestCase(TestCase):
    """Tests de permisos y roles"""
    
    def setUp(self):
        self.client = APIClient()
        
        # Admin
        self.admin = Usuario.objects.create(
            username='admin',
            correo='admin@test.com',
            cedula='1111111111',
            nombre='Admin',
            rol=1,
            is_active=True
        )
        
        # Gerente
        self.gerente = Usuario.objects.create(
            username='gerente',
            correo='gerente@test.com',
            cedula='2222222222',
            nombre='Gerente',
            rol=2,
            is_active=True
        )
        
        # Digitador
        self.digitador = Usuario.objects.create(
            username='digitador',
            correo='digitador@test.com',
            cedula='3333333333',
            nombre='Digitador',
            rol=3,
            is_active=True
        )
        
        # Comprador
        self.comprador = Usuario.objects.create(
            username='comprador',
            correo='comprador@test.com',
            cedula='4444444444',
            nombre='Comprador',
            rol=4,
            is_active=True
        )
    
    def test_admin_puede_crear_usuarios(self):
        """Test que admin puede crear usuarios"""
        self.client.force_authenticate(user=self.admin)
        
        data = {
            'username': 'nuevouser',
            'correo': 'nuevo@test.com',
            'cedula': '9999999999',
            'nombre': 'Usuario Nuevo',
            'rol': 4,
            'password': 'password123'
        }
        
        response = self.client.post('/api/usuarios/usuarios/', data, format='json')
        self.assertEqual(response.status_code, 201)
    
    def test_comprador_no_puede_crear_usuarios(self):
        """Test que comprador no puede crear usuarios"""
        self.client.force_authenticate(user=self.comprador)
        
        data = {
            'username': 'nuevouser',
            'correo': 'nuevo@test.com',
            'cedula': '9999999999',
            'nombre': 'Usuario Nuevo',
            'rol': 4,
            'password': 'password123'
        }
        
        response = self.client.post('/api/usuarios/usuarios/', data, format='json')
        self.assertNotEqual(response.status_code, 201)
    
    def test_gerente_puede_ver_usuarios(self):
        """Test que gerente puede ver usuarios"""
        self.client.force_authenticate(user=self.gerente)
        
        response = self.client.get('/api/usuarios/usuarios/')
        self.assertEqual(response.status_code, 200)
    
    def test_cambiar_rol_requiere_permisos(self):
        """Test que cambiar rol requiere permisos adecuados"""
        # Digitador intenta cambiar su propio rol
        self.client.force_authenticate(user=self.digitador)
        
        data = {'rol': 1}  # Intentar convertirse en admin
        response = self.client.patch(f'/api/usuarios/usuarios/{self.digitador.id}/', data, format='json')
        
        # Debe fallar o ignorar el cambio de rol
        self.digitador.refresh_from_db()
        self.assertNotEqual(self.digitador.rol, 1)


class UsuarioPerformanceTestCase(TransactionTestCase):
    """Tests de rendimiento para operaciones de usuarios"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = Usuario.objects.create(
            username='admin',
            correo='admin@test.com',
            cedula='1234567890',
            nombre='Admin Test',
            rol=1,
            is_active=True
        )
        self.admin.set_password('admin123')
        self.admin.save()
        self.client.force_authenticate(user=self.admin)
    
    def test_login_tiempo_respuesta(self):
        """Test que el login es rápido"""
        tiempos = []
        
        for _ in range(10):
            # Crear cliente nuevo para cada intento
            client = APIClient()
            
            data = {
                'username': 'admin',
                'password': 'admin123'
            }
            
            inicio = time.time()
            response = client.post('/api/token/', data, format='json')
            tiempo = time.time() - inicio
            
            self.assertEqual(response.status_code, 200)
            tiempos.append(tiempo)
        
        tiempo_promedio = statistics.mean(tiempos)
        
        self.assertLess(tiempo_promedio, 0.5,
                       f"Login tomó {tiempo_promedio:.3f}s en promedio, debe ser < 0.5s")
    
    def test_listar_muchos_usuarios(self):
        """Test rendimiento al listar muchos usuarios"""
        # Crear 100 usuarios
        usuarios = []
        for i in range(100):
            usuarios.append(Usuario(
                username=f'user{i}',
                correo=f'user{i}@test.com',
                cedula=f'{i:010d}',
                nombre=f'Usuario {i}',
                rol=4,
                is_active=True
            ))
        Usuario.objects.bulk_create(usuarios)
        
        inicio = time.time()
        response = self.client.get('/api/usuarios/usuarios/')
        tiempo = time.time() - inicio
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(tiempo, 1.0,
                       f"Listar usuarios tomó {tiempo:.3f}s, debe ser < 1.0s")
    
    def test_crear_usuario_tiempo_respuesta(self):
        """Test tiempo de respuesta al crear usuario"""
        tiempos = []
        
        for i in range(10):
            data = {
                'username': f'perfuser{i}',
                'correo': f'perfuser{i}@test.com',
                'cedula': f'{1000+i:010d}',
                'nombre': f'Performance User {i}',
                'rol': 4,
                'password': 'password123'
            }
            
            inicio = time.time()
            response = self.client.post('/api/usuarios/usuarios/', data, format='json')
            tiempo = time.time() - inicio
            
            self.assertEqual(response.status_code, 201)
            tiempos.append(tiempo)
        
        tiempo_promedio = statistics.mean(tiempos)
        
        self.assertLess(tiempo_promedio, 1.0,
                       f"Crear usuario tomó {tiempo_promedio:.3f}s en promedio, debe ser < 1.0s")
    
    def test_buscar_usuario_tiempo_respuesta(self):
        """Test tiempo de búsqueda de usuario"""
        # Crear 50 usuarios
        for i in range(50):
            Usuario.objects.create(
                username=f'searchuser{i}',
                correo=f'searchuser{i}@test.com',
                cedula=f'{2000+i:010d}',
                nombre=f'Search User {i}',
                rol=4
            )
        
        inicio = time.time()
        response = self.client.get('/api/usuarios/usuarios/?search=searchuser25')
        tiempo = time.time() - inicio
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(tiempo, 0.5,
                       f"Búsqueda de usuario tomó {tiempo:.3f}s, debe ser < 0.5s")
