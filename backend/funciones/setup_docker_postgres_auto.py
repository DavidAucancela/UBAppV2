"""
Script para configurar PostgreSQL con pgvector usando Docker
Con detección automática de puerto libre
"""
import os
import sys
import subprocess
import time
import socket

def encontrar_puerto_libre(puerto_inicial=5435, max_intentos=20):
    """Encuentra un puerto libre empezando desde puerto_inicial"""
    for puerto in range(puerto_inicial, puerto_inicial + max_intentos):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', puerto))
                return puerto
            except OSError:
                continue
    return None

def verificar_docker():
    """Verifica si Docker está instalado y corriendo"""
    print("=" * 70)
    print("VERIFICANDO DOCKER")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"\n[OK] Docker instalado: {result.stdout.strip()}")
            return True
        else:
            print("\n[ERROR] Docker no está instalado o no funciona")
            return False
            
    except FileNotFoundError:
        print("\n[ERROR] Docker no está instalado")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error al verificar Docker: {e}")
        return False

def limpiar_contenedor_existente():
    """Limpia contenedor postgres_local si existe"""
    try:
        # Detener
        subprocess.run(
            ['docker', 'stop', 'postgres_local'],
            capture_output=True,
            timeout=30
        )
        
        # Eliminar
        subprocess.run(
            ['docker', 'rm', 'postgres_local'],
            capture_output=True,
            timeout=30
        )
    except:
        pass

def crear_contenedor(puerto):
    """Crea y ejecuta el contenedor PostgreSQL con pgvector"""
    print("\n" + "=" * 70)
    print("CREANDO CONTENEDOR POSTGRESQL + PGVECTOR")
    print("=" * 70)
    
    print(f"\n[INFO] Usando puerto: {puerto}")
    print("[INFO] Descargando imagen ankane/pgvector...")
    
    cmd = [
        'docker', 'run', '-d',
        '--name', 'postgres_local',
        '-e', 'POSTGRES_DB=UBAppDB',
        '-e', 'POSTGRES_USER=postgres',
        '-e', 'POSTGRES_PASSWORD=admin',
        '-p', f'{puerto}:5432',
        '-v', 'pgdata:/var/lib/postgresql/data',
        'ankane/pgvector'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("\n[OK] Contenedor creado exitosamente")
            print(f"[INFO] ID del contenedor: {result.stdout.strip()[:12]}")
            return True, puerto
        else:
            print(f"\n[ERROR] Error al crear contenedor: {result.stderr}")
            return False, None
            
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return False, None

def esperar_postgres():
    """Espera a que PostgreSQL esté listo"""
    print("\n[INFO] Esperando a que PostgreSQL esté listo...")
    
    for i in range(30):
        try:
            result = subprocess.run(
                ['docker', 'exec', 'postgres_local', 'pg_isready', '-U', 'postgres'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                print("[OK] PostgreSQL está listo")
                return True
        except:
            pass
        
        time.sleep(1)
        if (i + 1) % 5 == 0:
            print(f"[INFO] Esperando... ({i + 1}/30 segundos)")
    
    print("[ERROR] PostgreSQL no respondió a tiempo")
    return False

def habilitar_pgvector():
    """Habilita la extensión pgvector"""
    print("\n[INFO] Habilitando extensión pgvector...")
    
    cmd = [
        'docker', 'exec', 'postgres_local',
        'psql', '-U', 'postgres', '-d', 'UBAppDB',
        '-c', 'CREATE EXTENSION IF NOT EXISTS vector;'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("[OK] Extensión pgvector habilitada")
            
            # Verificar
            cmd_verify = [
                'docker', 'exec', 'postgres_local',
                'psql', '-U', 'postgres', '-d', 'UBAppDB',
                '-c', "SELECT * FROM pg_extension WHERE extname = 'vector';"
            ]
            
            result = subprocess.run(cmd_verify, capture_output=True, text=True, timeout=10)
            if 'vector' in result.stdout:
                print("[OK] pgvector verificado correctamente")
                return True
        
        print(f"[ERROR] Error al habilitar pgvector: {result.stderr}")
        return False
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def actualizar_env(puerto):
    """Actualiza .env para usar base de datos local"""
    from pathlib import Path
    import shutil
    
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print("\n[ERROR] Archivo .env no encontrado")
        return False
    
    # Crear backup
    backup_path = Path(__file__).parent / '.env.supabase'
    if not backup_path.exists():
        shutil.copy(env_path, backup_path)
        print(f"\n[OK] Backup creado: .env.supabase")
    
    # Leer y actualizar
    with open(env_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    lineas = contenido.split('\n')
    nuevas_lineas = []
    
    for linea in lineas:
        if linea.startswith('DB_HOST='):
            nuevas_lineas.append('DB_HOST=localhost')
        elif linea.startswith('DB_PORT='):
            nuevas_lineas.append(f'DB_PORT={puerto}')
        elif linea.startswith('DB_NAME='):
            nuevas_lineas.append('DB_NAME=UBAppDB')
        elif linea.startswith('DB_USER='):
            nuevas_lineas.append('DB_USER=postgres')
        elif linea.startswith('DB_PASSWORD='):
            nuevas_lineas.append('DB_PASSWORD=admin')
        else:
            nuevas_lineas.append(linea)
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(nuevas_lineas))
    
    print(f"[OK] Archivo .env actualizado con puerto {puerto}")
    return True

def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("CONFIGURACION AUTOMATICA DE POSTGRESQL + PGVECTOR")
    print("=" * 70)
    
    # Verificar Docker
    if not verificar_docker():
        return
    
    # Encontrar puerto libre
    print("\n[INFO] Buscando puerto libre...")
    puerto = encontrar_puerto_libre(5435)
    
    if not puerto:
        print("\n[ERROR] No se encontró puerto libre entre 5435-5455")
        print("[INFO] Verifica qué servicios están usando esos puertos")
        return
    
    print(f"[OK] Puerto libre encontrado: {puerto}")
    
    # Limpiar contenedor existente
    print("\n[INFO] Limpiando contenedor existente...")
    limpiar_contenedor_existente()
    
    # Crear contenedor
    exito, puerto_usado = crear_contenedor(puerto)
    if not exito:
        return
    
    # Esperar a que esté listo
    if not esperar_postgres():
        return
    
    # Habilitar pgvector
    if not habilitar_pgvector():
        return
    
    # Actualizar .env
    actualizar_env(puerto_usado)
    
    # Resumen final
    print("\n" + "=" * 70)
    print("[OK] CONFIGURACION COMPLETADA")
    print("=" * 70)
    
    print("\n[INFO] Detalles de conexión:")
    print("   Host: localhost")
    print(f"   Port: {puerto_usado}  (externo, internamente usa 5432)")
    print("   Database: UBAppDB")
    print("   User: postgres")
    print("   Password: admin")
    
    print("\n[INFO] Comandos útiles:")
    print("   Detener: docker stop postgres_local")
    print("   Iniciar: docker start postgres_local")
    print("   Ver logs: docker logs postgres_local")
    print("   Acceder: docker exec -it postgres_local psql -U postgres -d UBAppDB")
    
    print("\n[INFO] Próximos pasos:")
    print("   1. Ejecutar migraciones: python manage.py migrate")
    print("   2. Importar datos: python importar_datos_local.py")
    print("   3. Iniciar Django: python manage.py runserver")

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

