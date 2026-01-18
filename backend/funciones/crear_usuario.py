"""
Script para crear usuarios fácilmente
Útil cuando la base de datos está vacía o necesitas crear usuarios de prueba
"""
import sys
import os
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def crear_usuario_interactivo():
    """Crea un usuario de forma interactiva"""
    print("=" * 70)
    print("CREAR NUEVO USUARIO")
    print("=" * 70)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        import django
        django.setup()
        
        from django.contrib.auth import get_user_model
        from django.core.exceptions import ValidationError
        
        Usuario = get_user_model()
        
        print("\n[INFO] Ingresa los datos del usuario:")
        print("(Presiona Enter para usar valores por defecto)\n")
        
        # Solicitar datos
        username = input("Username: ").strip()
        if not username:
            print("[ERROR] El username es requerido")
            return False
        
        # Verificar si ya existe
        if Usuario.objects.filter(username=username).exists():
            print(f"[ERROR] El usuario '{username}' ya existe")
            respuesta = input("¿Deseas actualizar la contraseña? (s/n): ").strip().lower()
            if respuesta == 's':
                password = input("Nueva contraseña: ").strip()
                if password:
                    usuario = Usuario.objects.get(username=username)
                    usuario.set_password(password)
                    usuario.is_active = True
                    usuario.save()
                    print(f"[OK] Contraseña actualizada para '{username}'")
                    return True
            return False
        
        password = input("Contraseña: ").strip()
        if not password:
            print("[ERROR] La contraseña es requerida")
            return False
        
        nombre = input("Nombre completo: ").strip()
        if not nombre:
            nombre = username
        
        correo = input("Correo electrónico: ").strip()
        if not correo:
            correo = f"{username}@ubapp.com"
        
        cedula = input("Cédula (10 dígitos): ").strip()
        if not cedula:
            print("[ERROR] La cédula es requerida")
            return False
        
        print("\n[INFO] Roles disponibles:")
        print("   1 - Admin")
        print("   2 - Gerente")
        print("   3 - Digitador")
        print("   4 - Comprador")
        
        rol_input = input("Rol (1-4, default=4): ").strip()
        rol = int(rol_input) if rol_input and rol_input.isdigit() else 4
        
        if rol not in [1, 2, 3, 4]:
            print("[ADVERTENCIA] Rol inválido, usando 4 (Comprador)")
            rol = 4
        
        es_superuser_input = input("¿Es superusuario? (s/n, default=n): ").strip().lower()
        es_superuser = es_superuser_input == 's'
        
        es_staff_input = input("¿Es staff (acceso admin)? (s/n, default=n): ").strip().lower()
        es_staff = es_staff_input == 's'
        
        # Crear usuario
        try:
            # Usar create_superuser si es superusuario, sino create_user
            if es_superuser:
                usuario = Usuario.objects.create_superuser(
                    username=username,
                    password=password,
                    correo=correo,
                    nombre=nombre,
                    cedula=cedula,
                    rol=rol,
                    is_staff=es_staff,
                    is_active=True
                )
            else:
                usuario = Usuario.objects.create_user(
                    username=username,
                    password=password,
                    correo=correo,
                    nombre=nombre,
                    cedula=cedula,
                    rol=rol,
                    is_staff=es_staff,
                    is_active=True
                )
            
            print("\n" + "=" * 70)
            print("[OK] USUARIO CREADO EXITOSAMENTE")
            print("=" * 70)
            print(f"\n[INFO] Usuario: {username}")
            print(f"[INFO] Nombre: {nombre}")
            print(f"[INFO] Correo: {correo}")
            print(f"[INFO] Rol: {usuario.get_rol_display_name()}")
            print(f"[INFO] Superusuario: {'Sí' if es_superuser else 'No'}")
            print(f"[INFO] Staff: {'Sí' if es_staff else 'No'}")
            print(f"[INFO] Activo: Sí")
            
            return True
            
        except ValidationError as e:
            print(f"\n[ERROR] Error de validación: {e}")
            return False
        except Exception as e:
            print(f"\n[ERROR] Error al crear usuario: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def crear_usuario_rapido():
    """Crea un usuario con valores por defecto para pruebas"""
    print("=" * 70)
    print("CREAR USUARIO RÁPIDO (MODO PRUEBA)")
    print("=" * 70)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        import django
        django.setup()
        
        from django.contrib.auth import get_user_model
        
        Usuario = get_user_model()
        
        # Valores por defecto
        username = "admin"
        password = "admin123"
        nombre = "Administrador"
        correo = "admin@ubapp.com"
        cedula = "1234567890"
        rol = 1  # Admin
        es_superuser = True
        es_staff = True
        
        # Verificar si ya existe
        if Usuario.objects.filter(username=username).exists():
            print(f"\n[ADVERTENCIA] El usuario '{username}' ya existe")
            respuesta = input("¿Deseas actualizar la contraseña? (s/n): ").strip().lower()
            if respuesta == 's':
                usuario = Usuario.objects.get(username=username)
                usuario.set_password(password)
                usuario.is_active = True
                usuario.save()
                print(f"[OK] Contraseña actualizada para '{username}'")
                print(f"[INFO] Username: {username}")
                print(f"[INFO] Password: {password}")
                return True
            return False
        
        # Crear usuario (es superusuario)
        usuario = Usuario.objects.create_superuser(
            username=username,
            password=password,
            correo=correo,
            nombre=nombre,
            cedula=cedula,
            rol=rol,
            is_staff=es_staff,
            is_active=True
        )
        
        print("\n" + "=" * 70)
        print("[OK] USUARIO CREADO EXITOSAMENTE")
        print("=" * 70)
        print(f"\n[INFO] Credenciales:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Nombre: {nombre}")
        print(f"   Rol: {usuario.get_rol_display_name()}")
        print(f"   Superusuario: Sí")
        print(f"   Staff: Sí")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error al crear usuario: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("CREAR USUARIO")
    print("=" * 70)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--rapido':
        # Modo rápido
        return 0 if crear_usuario_rapido() else 1
    else:
        # Modo interactivo
        print("\n[INFO] Modo interactivo")
        print("[INFO] Para modo rápido: python funciones/crear_usuario.py --rapido\n")
        return 0 if crear_usuario_interactivo() else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[ADVERTENCIA] Operación interrumpida")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
