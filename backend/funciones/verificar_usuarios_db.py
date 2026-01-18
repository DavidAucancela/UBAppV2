"""
Script para verificar usuarios en la base de datos
Útil para diagnosticar problemas de autenticación
"""
import sys
import os
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def verificar_usuarios():
    """Verifica qué usuarios existen en la base de datos"""
    print("=" * 70)
    print("VERIFICACIÓN DE USUARIOS EN LA BASE DE DATOS")
    print("=" * 70)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        import django
        django.setup()
        
        from django.db import connection
        from django.contrib.auth import get_user_model
        
        Usuario = get_user_model()
        
        # Contar usuarios
        total_usuarios = Usuario.objects.count()
        
        print(f"\n[INFO] Total de usuarios en la base de datos: {total_usuarios}")
        
        if total_usuarios == 0:
            print("\n[ADVERTENCIA] No hay usuarios en la base de datos")
            print("[SOLUCIÓN] Necesitas crear un usuario:")
            print("   python manage.py createsuperuser")
            return False
        
        # Mostrar usuarios
        print("\n[INFO] Usuarios encontrados:")
        print("-" * 70)
        print(f"{'ID':<5} {'Username':<20} {'Nombre':<25} {'Correo':<30} {'Rol':<15} {'Activo'}")
        print("-" * 70)
        
        usuarios = Usuario.objects.all().order_by('id')
        for usuario in usuarios:
            nombre = usuario.nombre if hasattr(usuario, 'nombre') and usuario.nombre else 'N/A'
            correo = usuario.correo if hasattr(usuario, 'correo') and usuario.correo else 'N/A'
            rol = usuario.get_rol_display_name() if hasattr(usuario, 'get_rol_display_name') else 'N/A'
            activo = "✅" if usuario.is_active else "❌"
            
            print(f"{usuario.id:<5} {usuario.username:<20} {str(nombre):<25} {str(correo):<30} {str(rol):<15} {activo}")
        
        print("-" * 70)
        
        # Verificar usuarios activos
        usuarios_activos = Usuario.objects.filter(is_active=True).count()
        print(f"\n[INFO] Usuarios activos: {usuarios_activos} de {total_usuarios}")
        
        # Verificar superusuarios
        superusuarios = Usuario.objects.filter(is_superuser=True).count()
        print(f"[INFO] Superusuarios: {superusuarios}")
        
        # Verificar estructura de la tabla
        print("\n[INFO] Verificando estructura de la tabla 'usuarios'...")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'usuarios'
                AND column_name IN ('username', 'password', 'is_active', 'nombre', 'correo', 'cedula')
                ORDER BY column_name;
            """)
            
            columnas = cursor.fetchall()
            
            if columnas:
                print("\n[INFO] Columnas importantes:")
                for col, tipo, nullable in columnas:
                    nullable_str = "Sí" if nullable == "YES" else "No"
                    print(f"   - {col}: {tipo} (nullable: {nullable_str})")
            else:
                print("\n[ADVERTENCIA] No se encontraron algunas columnas esperadas")
        
        # Verificar si hay problemas comunes
        print("\n[INFO] Verificando problemas comunes...")
        
        usuarios_sin_password = []
        usuarios_inactivos = []
        
        for usuario in usuarios:
            # Verificar si tiene password (no se puede verificar directamente, pero podemos intentar)
            if not usuario.is_active:
                usuarios_inactivos.append(usuario.username)
        
        if usuarios_inactivos:
            print(f"\n[ADVERTENCIA] Usuarios inactivos encontrados: {len(usuarios_inactivos)}")
            print("   Estos usuarios no pueden iniciar sesión aunque tengan la contraseña correcta")
            for username in usuarios_inactivos[:5]:  # Mostrar primeros 5
                print(f"   - {username}")
            if len(usuarios_inactivos) > 5:
                print(f"   ... y {len(usuarios_inactivos) - 5} más")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error al verificar usuarios: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_credenciales(username):
    """Verifica si un usuario existe y está activo"""
    print("\n" + "=" * 70)
    print(f"VERIFICACIÓN DE CREDENCIALES: {username}")
    print("=" * 70)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        import django
        django.setup()
        
        from django.contrib.auth import get_user_model
        
        Usuario = get_user_model()
        
        # Buscar usuario
        try:
            usuario = Usuario.objects.get(username=username)
            
            print(f"\n[OK] Usuario encontrado: {username}")
            print(f"[INFO] ID: {usuario.id}")
            print(f"[INFO] Nombre: {usuario.nombre if hasattr(usuario, 'nombre') and usuario.nombre else 'N/A'}")
            print(f"[INFO] Correo: {usuario.correo if hasattr(usuario, 'correo') and usuario.correo else 'N/A'}")
            print(f"[INFO] Activo: {'✅ Sí' if usuario.is_active else '❌ No'}")
            print(f"[INFO] Superusuario: {'✅ Sí' if usuario.is_superuser else '❌ No'}")
            print(f"[INFO] Staff: {'✅ Sí' if usuario.is_staff else '❌ No'}")
            
            if not usuario.is_active:
                print("\n[PROBLEMA] El usuario está INACTIVO")
                print("[SOLUCIÓN] Activa el usuario:")
                print(f"   python manage.py shell")
                print(f"   >>> from apps.usuarios.models import Usuario")
                print(f"   >>> u = Usuario.objects.get(username='{username}')")
                print(f"   >>> u.is_active = True")
                print(f"   >>> u.save()")
            
            # Verificar si tiene password
            if not usuario.has_usable_password():
                print("\n[PROBLEMA] El usuario no tiene contraseña configurada")
                print("[SOLUCIÓN] Establece una contraseña:")
                print(f"   python manage.py changepassword {username}")
            
            return usuario
            
        except Usuario.DoesNotExist:
            print(f"\n[ERROR] Usuario '{username}' NO existe")
            print("\n[INFO] Usuarios disponibles:")
            usuarios = Usuario.objects.all()[:10]
            for u in usuarios:
                print(f"   - {u.username}")
            return None
            
    except Exception as e:
        print(f"\n[ERROR] Error al verificar credenciales: {e}")
        import traceback
        traceback.print_exc()
        return None

def crear_superusuario_interactivo():
    """Guía para crear un superusuario"""
    print("\n" + "=" * 70)
    print("CREAR SUPERUSUARIO")
    print("=" * 70)
    
    print("\n[INFO] Para crear un superusuario, ejecuta:")
    print("   python manage.py createsuperuser")
    print("\n[INFO] O desde el shell de Django:")
    print("   python manage.py shell")
    print("   >>> from apps.usuarios.models import Usuario")
    print("   >>> u = Usuario.objects.create_user(")
    print("   ...     username='tu_usuario',")
    print("   ...     password='tu_contraseña',")
    print("   ...     nombre='Tu Nombre',")
    print("   ...     correo='tu@email.com',")
    print("   ...     cedula='1234567890',")
    print("   ...     rol=1,")
    print("   ...     is_superuser=True,")
    print("   ...     is_staff=True")
    print("   ... )")

def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("DIAGNÓSTICO DE USUARIOS Y AUTENTICACIÓN")
    print("=" * 70)
    
    # Verificar usuarios
    if not verificar_usuarios():
        print("\n[SOLUCIÓN] No hay usuarios en la base de datos")
        crear_superusuario_interactivo()
        return 1
    
    # Si se proporciona un username como argumento, verificar ese usuario específico
    if len(sys.argv) > 1:
        username = sys.argv[1]
        usuario = verificar_credenciales(username)
        
        if usuario and not usuario.is_active:
            print("\n[SOLUCIÓN] El usuario existe pero está inactivo")
            return 1
        elif usuario:
            print("\n[OK] El usuario existe y está activo")
            print("[INFO] Si no puedes iniciar sesión, verifica la contraseña")
            return 0
        else:
            return 1
    
    print("\n" + "=" * 70)
    print("[OK] VERIFICACIÓN COMPLETADA")
    print("=" * 70)
    print("\n[INFO] Para verificar un usuario específico:")
    print("   python funciones/verificar_usuarios_db.py <username>")
    print("\n[INFO] Para crear un nuevo usuario:")
    print("   python manage.py createsuperuser")
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[ADVERTENCIA] Verificación interrumpida")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
