"""
Script para cambiar fácilmente entre SQLite y PostgreSQL
"""
import os
import sys

def mostrar_menu():
    print("=" * 60)
    print("CAMBIAR CONFIGURACIÓN DE BASE DE DATOS")
    print("=" * 60)
    print()
    print("1. SQLite (sin contraseña, para desarrollo)")
    print("2. PostgreSQL (requiere configuración)")
    print("3. Salir")
    print()

def cambiar_a_sqlite():
    config = """# Django Settings
SECRET_KEY=django-insecure-@dugr*6&xxk8zuen9g2hn^zb9rbdae_t8sc@lsdhd)=5l3@i*i
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration - SQLite
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(config)
    
    print("✅ Configuración cambiada a SQLite")
    print("📝 Ahora ejecuta: python manage.py migrate")

def cambiar_a_postgresql():
    print()
    print("Ingresa los datos de PostgreSQL:")
    db_name = input("Nombre de la base de datos [DB_UniversalBox]: ").strip() or "DB_UniversalBox"
    db_user = input("Usuario [postgres]: ").strip() or "postgres"
    db_password = input("Contraseña (sin acentos): ").strip()
    db_host = input("Host [localhost]: ").strip() or "localhost"
    db_port = input("Puerto [5432]: ").strip() or "5432"
    
    config = f"""# Django Settings
SECRET_KEY=django-insecure-@dugr*6&xxk8zuen9g2hn^zb9rbdae_t8sc@lsdhd)=5l3@i*i
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration - PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST={db_host}
DB_PORT={db_port}
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(config)
    
    print("\n✅ Configuración cambiada a PostgreSQL")
    print("🧪 Ahora ejecuta: python test_db_connection.py")

def main():
    if not os.path.exists('.env'):
        print("⚠️ No se encontró el archivo .env")
        print("Creando archivo .env con SQLite por defecto...")
        cambiar_a_sqlite()
        return
    
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción [1-3]: ").strip()
        
        if opcion == '1':
            cambiar_a_sqlite()
            break
        elif opcion == '2':
            cambiar_a_postgresql()
            break
        elif opcion == '3':
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")
            print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operación cancelada")
        sys.exit(0)

