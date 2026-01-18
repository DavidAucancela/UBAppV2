"""
Script para restablecer la contraseña de un usuario.
Permite buscar usuarios por username, correo o cédula y establecer una nueva contraseña.

¿Cómo ejecuto este script?
----------------------------------------
1. Asegúrate de tener el entorno de Django configurado correctamente y la base de datos accesible.
2. Abre una terminal y navega a la carpeta donde se encuentra este script.
3. Ejecuta el script con el siguiente comando:

    python restablecer_password.py

El script te guiará paso a paso para buscar al usuario y establecer la nueva contraseña.
"""
import os
import sys
import getpass
import django
from pathlib import Path

# Configurar Django
# Agregar el directorio padre (backend) al path para encontrar settings.py
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from apps.usuarios.validators import validar_password_fuerte

Usuario = get_user_model()


def verificar_conexion():
    """Verifica la conexión a la base de datos"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"[OK] Conectado a PostgreSQL: {version[0][:50]}...")
            return True
    except Exception as e:
        print(f"\n[ERROR] No se puede conectar a la base de datos: {e}")
        print("\n[INFO] Asegúrate de:")
        print("   1. Tener PostgreSQL corriendo (local o remoto)")
        print("   2. Tener configurado correctamente DB_HOST en .env")
        print("   3. Que las credenciales sean correctas")
        return False


def buscar_usuario():
    """Busca un usuario por username, correo o cédula"""
    print("\n" + "=" * 70)
    print("BUSCAR USUARIO")
    print("=" * 70)
    print("\n[INFO] Puedes buscar por:")
    print("   1. Username")
    print("   2. Correo electrónico")
    print("   3. Cédula")
    
    try:
        criterio = input("\nIngresa el username, correo o cédula: ").strip()
        
        if not criterio:
            print("[ERROR] Debes ingresar un criterio de búsqueda")
            return None
        
        # Intentar buscar por username
        usuario = Usuario.objects.filter(username=criterio).first()
        
        # Si no se encuentra, buscar por correo
        if not usuario:
            usuario = Usuario.objects.filter(correo=criterio).first()
        
        # Si no se encuentra, buscar por cédula
        if not usuario:
            usuario = Usuario.objects.filter(cedula=criterio).first()
        
        if not usuario:
            print(f"\n[ERROR] No se encontró ningún usuario con: {criterio}")
            return None
        
        # Mostrar información del usuario encontrado
        print("\n" + "=" * 70)
        print("[OK] USUARIO ENCONTRADO")
        print("=" * 70)
        print(f"   ID: {usuario.id}")
        print(f"   Username: {usuario.username}")
        print(f"   Nombre: {usuario.nombre}")
        print(f"   Correo: {usuario.correo}")
        print(f"   Cédula: {usuario.cedula}")
        print(f"   Rol: {usuario.get_rol_display_name()}")
        print(f"   Activo: {'Sí' if usuario.is_active else 'No'}")
        
        return usuario
        
    except KeyboardInterrupt:
        print("\n\n[ADVERTENCIA] Búsqueda cancelada")
        return None
    except Exception as e:
        print(f"\n[ERROR] Error al buscar usuario: {e}")
        return None


def obtener_nueva_password():
    """Solicita y valida una nueva contraseña"""
    print("\n" + "=" * 70)
    print("NUEVA CONTRASEÑA")
    print("=" * 70)
    print("\n[INFO] Requisitos de contraseña:")
    print("   - Mínimo 8 caracteres")
    print("   - Al menos una letra mayúscula")
    print("   - Al menos una letra minúscula")
    print("   - Al menos un número")
    print("   - Al menos un carácter especial (!@#$%^&*...)")
    
    try:
        while True:
            password = getpass.getpass("\nIngresa la nueva contraseña: ")
            
            if not password:
                print("[ERROR] La contraseña no puede estar vacía")
                continue
            
            # Validar contraseña
            try:
                validar_password_fuerte(password)
            except Exception as e:
                print(f"[ERROR] {e}")
                continue
            
            # Confirmar contraseña
            password_confirm = getpass.getpass("Confirma la nueva contraseña: ")
            
            if password != password_confirm:
                print("[ERROR] Las contraseñas no coinciden")
                continue
            
            return password
            
    except KeyboardInterrupt:
        print("\n\n[ADVERTENCIA] Operación cancelada")
        return None
    except Exception as e:
        print(f"\n[ERROR] Error al obtener contraseña: {e}")
        return None


def restablecer_password(usuario, nueva_password):
    """Restablece la contraseña del usuario"""
    try:
        # Confirmar operación
        print("\n" + "=" * 70)
        print("CONFIRMAR OPERACIÓN")
        print("=" * 70)
        print(f"\n[ADVERTENCIA] Se cambiará la contraseña de:")
        print(f"   Usuario: {usuario.username} ({usuario.nombre})")
        print(f"   Correo: {usuario.correo}")
        
        respuesta = input("\n¿Deseas continuar? (s/n): ").strip().lower()
        
        if respuesta != 's':
            print("[INFO] Operación cancelada")
            return False
        
        # Actualizar contraseña
        usuario.set_password(nueva_password)
        usuario.save()
        
        print("\n" + "=" * 70)
        print("[OK] CONTRASEÑA RESTABLECIDA EXITOSAMENTE")
        print("=" * 70)
        print(f"\n[INFO] La contraseña del usuario '{usuario.username}' ha sido actualizada")
        print(f"[INFO] El usuario puede iniciar sesión con la nueva contraseña")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error al restablecer contraseña: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal"""
    print("=" * 70)
    print("RESTABLECER CONTRASEÑA DE USUARIO")
    print("=" * 70)
    
    # Verificar conexión
    print("\n[INFO] Verificando conexión a la base de datos...")
    if not verificar_conexion():
        return
    
    # Buscar usuario
    usuario = buscar_usuario()
    if not usuario:
        return
    
    # Obtener nueva contraseña
    nueva_password = obtener_nueva_password()
    if not nueva_password:
        return
    
    # Restablecer contraseña
    restablecer_password(usuario, nueva_password)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[ADVERTENCIA] Operación interrumpida")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

