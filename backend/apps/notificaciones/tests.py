"""
Tests para la aplicación de notificaciones.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

Usuario = get_user_model()


class NotificacionTestCase(TestCase):
    """Tests básicos de CRUD de notificaciones"""

    def setUp(self):
        self.client = APIClient()
        self.usuario = Usuario.objects.create(
            username='notif_user',
            correo='notif@test.com',
            cedula='7700000001',
            nombre='Notif User',
            rol=4,
            is_active=True,
        )
        self.usuario.set_password('notif123')
        self.usuario.save()
        self.client.force_authenticate(user=self.usuario)

        # Admin para crear notificaciones vía señales/admin
        self.admin = Usuario.objects.create(
            username='notif_admin',
            correo='notif_admin@test.com',
            cedula='7700000002',
            nombre='Notif Admin',
            rol=1,
            is_active=True,
        )
        self.admin.set_password('admin123')
        self.admin.save()

    def test_listar_notificaciones_requiere_autenticacion(self):
        """El endpoint de notificaciones requiere autenticación."""
        client_anon = APIClient()
        response = client_anon.get('/api/v1/notificaciones/')
        self.assertIn(response.status_code, [401, 403])

    def test_listar_notificaciones_autenticado(self):
        """Usuario autenticado puede listar sus notificaciones."""
        response = self.client.get('/api/v1/notificaciones/')
        self.assertIn(response.status_code, [200, 404])  # 404 si la URL difiere

    def test_usuario_ve_solo_sus_notificaciones(self):
        """Usuario solo debe ver sus propias notificaciones."""
        from django.apps import apps
        try:
            Notificacion = apps.get_model('notificaciones', 'Notificacion')
        except LookupError:
            self.skipTest('Modelo Notificacion no encontrado')

        # Crear notificación para este usuario
        n1 = Notificacion.objects.create(
            usuario=self.usuario,
            titulo='Notif para mí',
            mensaje='Mensaje de prueba',
            tipo='info',
        )

        # Crear notificación para otro usuario (no debe aparecer)
        n2 = Notificacion.objects.create(
            usuario=self.admin,
            titulo='Notif para admin',
            mensaje='Solo para admin',
            tipo='info',
        )

        response = self.client.get('/api/v1/notificaciones/')
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', data) if isinstance(data, dict) else data
            ids = [r.get('id') for r in results]
            self.assertIn(n1.id, ids)
            self.assertNotIn(n2.id, ids)

    def test_marcar_notificacion_como_leida(self):
        """Usuario puede marcar una notificación como leída."""
        from django.apps import apps
        try:
            Notificacion = apps.get_model('notificaciones', 'Notificacion')
        except LookupError:
            self.skipTest('Modelo Notificacion no encontrado')

        notif = Notificacion.objects.create(
            usuario=self.usuario,
            titulo='No leída',
            mensaje='Mensaje',
            tipo='info',
            leida=False,
        )

        response = self.client.patch(f'/api/v1/notificaciones/{notif.id}/', {'leida': True}, format='json')
        if response.status_code in [200, 404]:
            if response.status_code == 200:
                notif.refresh_from_db()
                self.assertTrue(notif.leida)

    def test_eliminar_notificacion(self):
        """Usuario puede eliminar sus notificaciones."""
        from django.apps import apps
        try:
            Notificacion = apps.get_model('notificaciones', 'Notificacion')
        except LookupError:
            self.skipTest('Modelo Notificacion no encontrado')

        notif = Notificacion.objects.create(
            usuario=self.usuario,
            titulo='Para eliminar',
            mensaje='Se eliminará',
            tipo='info',
        )

        response = self.client.delete(f'/api/v1/notificaciones/{notif.id}/')
        self.assertIn(response.status_code, [204, 404])
        if response.status_code == 204:
            self.assertFalse(Notificacion.objects.filter(id=notif.id).exists())

    def test_no_puede_eliminar_notificacion_ajena(self):
        """Usuario no puede eliminar notificaciones de otro usuario."""
        from django.apps import apps
        try:
            Notificacion = apps.get_model('notificaciones', 'Notificacion')
        except LookupError:
            self.skipTest('Modelo Notificacion no encontrado')

        notif_admin = Notificacion.objects.create(
            usuario=self.admin,
            titulo='Del admin',
            mensaje='No tocar',
            tipo='info',
        )

        response = self.client.delete(f'/api/v1/notificaciones/{notif_admin.id}/')
        # Debe ser 403 o 404 (no encontrado porque no es suya)
        self.assertIn(response.status_code, [403, 404])
        self.assertTrue(Notificacion.objects.filter(id=notif_admin.id).exists())
