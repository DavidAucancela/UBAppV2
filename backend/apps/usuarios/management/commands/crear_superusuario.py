"""
Comando personalizado para crear superusuarios.
Usa 'correo' en lugar de 'email' que fue eliminado del modelo.
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import IntegrityError
import getpass

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea un superusuario personalizado para el modelo Usuario'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nombre de usuario para el superusuario',
        )
        parser.add_argument(
            '--correo',
            type=str,
            help='Correo electrónico para el superusuario',
        )
        parser.add_argument(
            '--cedula',
            type=str,
            help='Cédula ecuatoriana (10 dígitos)',
        )
        parser.add_argument(
            '--nombre',
            type=str,
            help='Nombre completo del usuario',
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='No solicita entrada del usuario (para scripts)',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        correo = options.get('correo')
        cedula = options.get('cedula')
        nombre = options.get('nombre')
        noinput = options.get('noinput')

        self.stdout.write(self.style.SUCCESS('\n=== Crear Superusuario ===\n'))

        # Obtener datos interactivamente si no se proporcionaron
        try:
            if not username and not noinput:
                username = input('Nombre de usuario: ').strip()
            
            if not correo and not noinput:
                correo = input('Correo electrónico: ').strip()
            
            if not cedula and not noinput:
                cedula = input('Cédula (10 dígitos): ').strip()
            
            if not nombre and not noinput:
                nombre = input('Nombre completo: ').strip()

            # Validaciones básicas
            if not username:
                self.stdout.write(self.style.ERROR('Error: Se requiere nombre de usuario'))
                return
            
            if not correo:
                self.stdout.write(self.style.ERROR('Error: Se requiere correo electrónico'))
                return
            
            if not cedula or len(cedula) != 10:
                self.stdout.write(self.style.ERROR('Error: Se requiere cédula válida de 10 dígitos'))
                return

            # Obtener contraseña
            if not noinput:
                password = getpass.getpass('Contraseña: ')
                password_confirm = getpass.getpass('Contraseña (confirmación): ')
                
                if password != password_confirm:
                    self.stdout.write(self.style.ERROR('Error: Las contraseñas no coinciden'))
                    return
                
                if len(password) < 8:
                    self.stdout.write(self.style.ERROR('Error: La contraseña debe tener al menos 8 caracteres'))
                    return
            else:
                # En modo noinput, generar contraseña temporal o requerirla como argumento
                password = None
                self.stdout.write(self.style.WARNING('Modo noinput: No se puede solicitar contraseña interactivamente'))
                self.stdout.write(self.style.WARNING('Use el shell de Django o establezca la contraseña después'))
        except (EOFError, KeyboardInterrupt):
            self.stdout.write(self.style.ERROR('\nOperación cancelada'))
            return

        try:
            # Verificar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'El usuario "{username}" ya existe'))
                response = input('¿Desea actualizarlo a superusuario? (s/n): ').strip().lower()
                if response == 's':
                    user = User.objects.get(username=username)
                    user.is_superuser = True
                    user.is_staff = True
                    if password:
                        user.set_password(password)
                    if nombre:
                        user.nombre = nombre
                    if correo:
                        user.correo = correo
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'✓ Usuario "{username}" actualizado a superusuario'))
                return

            # Crear nuevo superusuario
            # No usar create_user porque intenta usar 'email' que no existe
            user = User(
                username=username,
                correo=correo,
                cedula=cedula,
                nombre=nombre,
                is_superuser=True,
                is_staff=True,
                is_active=True,
            )
            if password:
                user.set_password(password)
            user.save()

            self.stdout.write(self.style.SUCCESS(f'\n✓ Superusuario "{username}" creado exitosamente'))
            self.stdout.write(self.style.SUCCESS(f'  - Username: {username}'))
            self.stdout.write(self.style.SUCCESS(f'  - Correo: {correo}'))
            self.stdout.write(self.style.SUCCESS(f'  - Cédula: {cedula}'))
            if nombre:
                self.stdout.write(self.style.SUCCESS(f'  - Nombre: {nombre}'))

        except IntegrityError as e:
            if 'cedula' in str(e).lower() or 'unique constraint' in str(e).lower():
                self.stdout.write(self.style.ERROR(f'Error: Ya existe un usuario con esa cédula o correo'))
            else:
                self.stdout.write(self.style.ERROR(f'Error al crear usuario: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error inesperado: {e}'))

