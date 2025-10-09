"""
Script para probar la conexión directa a PostgreSQL
"""
from decouple import config

def test_direct_connection():
    print("=" * 60)
    print("PRUEBA DIRECTA DE CONEXIÓN A POSTGRESQL")
    print("=" * 60)
    
    # Obtener credenciales
    db_name = config('DB_NAME', default='')
    db_user = config('DB_USER', default='')
    db_password = config('DB_PASSWORD', default='')
    db_host = config('DB_HOST', default='localhost')
    db_port = config('DB_PORT', default='5432')
    
    print(f"\n📋 Credenciales:")
    print(f"   Base de datos: {db_name}")
    print(f"   Usuario: {db_user}")
    print(f"   Host: {db_host}")
    print(f"   Puerto: {db_port}")
    print(f"   Longitud de contraseña: {len(db_password)} caracteres")
    
    # Verificar si hay caracteres especiales problemáticos
    special_chars = []
    for char in db_password:
        if ord(char) > 127:  # Caracteres no-ASCII
            special_chars.append(f"{char} (código: {ord(char)})")
    
    if special_chars:
        print(f"\n⚠️ Caracteres especiales detectados en la contraseña:")
        for char in special_chars:
            print(f"   - {char}")
        print("\n   Estos caracteres pueden causar problemas en Windows.")
    
    # Intentar diferentes formas de conectar
    print("\n🔌 Probando conexión...")
    
    try:
        import psycopg2
        print("   ✅ psycopg2 está instalado")
    except ImportError:
        print("   ❌ psycopg2 NO está instalado")
        print("\n💡 Instala psycopg2 con:")
        print("   pip install psycopg2-binary")
        return False
    
    # Método 1: Conexión con parámetros separados
    print("\n1️⃣ Intentando con parámetros separados...")
    try:
        # Intentar codificar la contraseña correctamente
        password_bytes = db_password.encode('utf-8')
        password_decoded = password_bytes.decode('utf-8')
        
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=password_decoded,
            host=db_host,
            port=db_port
        )
        print("   ✅ Conexión exitosa!")
        
        # Probar una consulta
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        print(f"   📊 PostgreSQL: {version[:50]}...")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"   ❌ Error operacional: {str(e)[:100]}")
    except UnicodeDecodeError as e:
        print(f"   ❌ Error de codificación: {e}")
        print("\n   💡 SOLUCIÓN:")
        print("   La contraseña tiene caracteres especiales problemáticos.")
        print("   Opciones:")
        print("   a) Cambia la contraseña de PostgreSQL a solo ASCII")
        print("   b) Usa pgAdmin para cambiar la contraseña del usuario postgres")
        print()
        print("   Ejemplo en SQL:")
        print(f"   ALTER USER {db_user} PASSWORD 'NuevaPass123';")
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {str(e)[:100]}")
    
    # Método 2: Conexión con DSN
    print("\n2️⃣ Intentando con cadena de conexión DSN...")
    try:
        # Escapar caracteres especiales en la contraseña para URL
        from urllib.parse import quote_plus
        password_escaped = quote_plus(db_password)
        
        dsn = f"postgresql://{db_user}:{password_escaped}@{db_host}:{db_port}/{db_name}"
        
        import psycopg2
        conn = psycopg2.connect(dsn)
        print("   ✅ Conexión exitosa con DSN!")
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {str(e)[:100]}")
    
    print("\n" + "=" * 60)
    print("❌ NO SE PUDO CONECTAR")
    print("=" * 60)
    print("\n💡 SOLUCIONES RECOMENDADAS:")
    print()
    print("1. CAMBIAR LA CONTRASEÑA DE POSTGRESQL (Más fácil):")
    print("   - Abre pgAdmin o psql")
    print("   - Ejecuta: ALTER USER postgres PASSWORD 'Admin123';")
    print("   - Actualiza DB_PASSWORD en el archivo .env")
    print("   - Usa solo letras, números y símbolos básicos: !@#$%")
    print()
    print("2. VERIFICAR QUE POSTGRESQL ESTÉ CORRIENDO:")
    print("   - Abre 'Servicios' de Windows")
    print("   - Busca 'postgresql-x64-XX'")
    print("   - Verifica que esté 'Iniciado'")
    print()
    print("3. VERIFICAR LA BASE DE DATOS:")
    print("   - Verifica que la base de datos 'DB_UniversalBox' exista")
    print("   - Puedes crearla con: CREATE DATABASE DB_UniversalBox;")
    print()
    print("=" * 60)
    
    return False

if __name__ == "__main__":
    import sys
    success = test_direct_connection()
    sys.exit(0 if success else 1)

