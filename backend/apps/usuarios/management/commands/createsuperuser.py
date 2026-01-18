"""
Comando personalizado para crear superusuario
Adaptado para usar 'correo' en lugar de 'email'
"""
from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from django.core.exceptions import ValidationError


class Command(BaseCommand):
    """Comando personalizado para crear superusuario con campo 'correo'"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Reemplazar 'email' con 'correo' en los campos requeridos
        if hasattr(self, 'REQUIRED_FIELDS'):
            # Si REQUIRED_FIELDS tiene 'email', reemplazarlo con 'correo'
            if 'email' in self.UserModel.REQUIRED_FIELDS:
                # No podemos modificar REQUIRED_FIELDS directamente, así que lo manejamos en add_arguments
                pass
    
    def add_arguments(self, parser):
        """Agregar argumentos personalizados"""
        super().add_arguments(parser)
        
        # Reemplazar 'email' con 'correo' en los argumentos
        for action in parser._actions:
            if hasattr(action, 'dest') and action.dest == 'email':
                action.dest = 'correo'
                action.option_strings = ['--correo']
                action.help = 'Correo electrónico del superusuario'
    
    def handle(self, *args, **options):
        """Manejar la creación del superusuario"""
        # Convertir 'email' a 'correo' si viene en options
        if 'email' in options and 'correo' not in options:
            options['correo'] = options.pop('email')
        
        # Llamar al método padre pero con 'correo'
        try:
            # Obtener datos interactivamente si no se proporcionaron
            username = options.get('username') or self.get_input_data('username', 'Username')
            
            # Verificar si el usuario ya existe
            if self.UserModel.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.ERROR(f'El usuario "{username}" ya existe.')
                )
                return
            
            # Obtener correo
            correo = options.get('correo')
            if not correo:
                correo = self.get_input_data('correo', 'Correo electrónico')
            
            # Obtener contraseña
            password = options.get('password')
            if not password:
                password = self.get_password()
            
            # Crear el usuario
            usuario = self.UserModel.objects.create_superuser(
                username=username,
                password=password,
                correo=correo,
                nombre=username,  # Usar username como nombre por defecto
                cedula='0000000000',  # Cédula temporal, se puede cambiar después
                rol=1,  # Admin
                is_active=True,
                is_staff=True,
                is_superuser=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Superusuario "{username}" creado exitosamente.')
            )
            
        except KeyboardInterrupt:
            self.stdout.write('\nOperación cancelada.')
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'Error de validación: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
    
    def get_input_data(self, field, prompt):
        """Obtener datos de entrada del usuario"""
        import getpass
        
        if field == 'password':
            return getpass.getpass(f'{prompt}: ')
        else:
            return input(f'{prompt}: ').strip()
    
    def get_password(self):
        """Obtener contraseña de forma segura"""
        import getpass
        
        password = getpass.getpass('Password: ')
        password_confirm = getpass.getpass('Password (again): ')
        
        if password != password_confirm:
            self.stdout.write(self.style.ERROR('Las contraseñas no coinciden.'))
            return self.get_password()
        
        return password
