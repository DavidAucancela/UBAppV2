"""
Script para probar la conexión a la base de datos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DRF_APP_BACKEND.settings')
django.setup()

from django.db import connection
from django.conf import settings
from decouple import config

def test_database_connection():
    """Prueba la conexión a la base de datos"""
    
    print("=" * 60)
    print("PRUEBA DE CONEXIÓN A LA BASE DE DATOS")
    print("=" * 60)
    
    # Mostrar configuración actual (sin contraseña)
    print("\n📋 Configuración actual:")
    db_config = settings.DATABASES['default']
    print(f"  Motor: {db_config['ENGINE']}")
    print(f"  Base de datos: {db_config['NAME']}")
    print(f"  Usuario: {db_config['USER']}")
    print(f"  Host: {db_config['HOST']}")
    print(f"  Puerto: {db_config['PORT']}")
    
    # Mostrar valores del .env
    print("\n🔧 Valores desde .env:")
    print(f"  DB_ENGINE: {config('DB_ENGINE', default='No configurado')}")
    print(f"  DB_NAME: {config('DB_NAME', default='No configurado')}")
    print(f"  DB_USER: {config('DB_USER', default='No configurado')}")
    print(f"  DB_HOST: {config('DB_HOST', default='No configurado')}")
    print(f"  DB_PORT: {config('DB_PORT', default='No configurado')}")
    
    # Intentar conectar
    print("\n🔌 Intentando conectar a la base de datos...")
    try:
        with connection.cursor() as cursor:
            # Ejecutar una consulta simple
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        print("✅ ¡CONEXIÓN EXITOSA!")
        print(f"   Resultado de prueba: {result[0]}")
        
        # Información adicional según el motor
        if 'postgresql' in db_config['ENGINE']:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"   Versión de PostgreSQL: {version[0]}")
                
        elif 'mysql' in db_config['ENGINE']:
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION();")
                version = cursor.fetchone()
                print(f"   Versión de MySQL: {version[0]}")
                
        elif 'sqlite3' in db_config['ENGINE']:
            with connection.cursor() as cursor:
                cursor.execute("SELECT sqlite_version();")
                version = cursor.fetchone()
                print(f"   Versión de SQLite: {version[0]}")
        
        # Mostrar tablas existentes
        print("\n📊 Tablas en la base de datos:")
        tables = connection.introspection.table_names()
        if tables:
            for table in sorted(tables):
                print(f"   - {table}")
        else:
            print("   (No hay tablas creadas aún)")
            
        return True
        
    except Exception as e:
        print("❌ ERROR DE CONEXIÓN:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        
        # Sugerencias según el tipo de error
        if 'psycopg2' in str(type(e).__module__):
            print("\n💡 Sugerencias para PostgreSQL:")
            print("   1. Verifica que PostgreSQL esté corriendo")
            print("   2. Verifica usuario y contraseña")
            print("   3. Verifica que la base de datos exista")
            print("   4. Verifica el puerto (5432 por defecto)")
            print("   5. Si hay caracteres especiales en la contraseña,")
            print("      asegúrate de que el archivo .env esté en UTF-8")
            
        elif 'MySQLdb' in str(type(e).__module__) or 'mysql' in str(type(e).__module__):
            print("\n💡 Sugerencias para MySQL:")
            print("   1. Verifica que MySQL esté corriendo")
            print("   2. Verifica usuario y contraseña")
            print("   3. Verifica que la base de datos exista")
            print("   4. Verifica el puerto (3306 por defecto)")
            
        elif 'sqlite3' in db_config['ENGINE']:
            print("\n💡 Sugerencias para SQLite:")
            print("   1. Verifica que la ruta del archivo sea correcta")
            print("   2. Verifica permisos de escritura en el directorio")
            
        return False
    
    finally:
        print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        success = test_database_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Prueba interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

