"""
Script de diagnóstico completo para problemas de conexión a la base de datos
Verifica configuración, DNS, conectividad y sugiere soluciones
"""
import sys
import os
import socket
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def verificar_env():
    """Verifica que el archivo .env exista y tenga configuración"""
    print("=" * 70)
    print("1. VERIFICACIÓN DE ARCHIVO .ENV")
    print("=" * 70)
    
    env_path = Path(__file__).parent.parent / '.env'
    
    if not env_path.exists():
        print("\n[ERROR] Archivo .env no encontrado")
        print("[SOLUCIÓN] Crea un archivo .env en el directorio backend/")
        return False, None
    
    print(f"\n[OK] Archivo .env encontrado: {env_path}")
    
    # Leer configuración
    config = {
        'DATABASE_URL': None,
        'DB_HOST': None,
        'DB_PORT': None,
        'DB_NAME': None,
        'DB_USER': None,
        'DB_PASSWORD': None
    }
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            if linea.startswith('DATABASE_URL=') and not linea.startswith('#'):
                config['DATABASE_URL'] = linea.split('=', 1)[1].strip()
            elif linea.startswith('DB_HOST=') and not linea.startswith('#'):
                config['DB_HOST'] = linea.split('=', 1)[1].strip()
            elif linea.startswith('DB_PORT=') and not linea.startswith('#'):
                config['DB_PORT'] = linea.split('=', 1)[1].strip()
            elif linea.startswith('DB_NAME=') and not linea.startswith('#'):
                config['DB_NAME'] = linea.split('=', 1)[1].strip()
            elif linea.startswith('DB_USER=') and not linea.startswith('#'):
                config['DB_USER'] = linea.split('=', 1)[1].strip()
            elif linea.startswith('DB_PASSWORD=') and not linea.startswith('#'):
                config['DB_PASSWORD'] = linea.split('=', 1)[1].strip()
    
    print("\n[INFO] Configuración encontrada:")
    if config['DATABASE_URL']:
        # Ocultar contraseña
        url_oculta = config['DATABASE_URL'].split('@')[0] + '@***'
        print(f"   DATABASE_URL: {url_oculta}...")
    else:
        print("   DATABASE_URL: No configurada")
    
    if config['DB_HOST']:
        print(f"   DB_HOST: {config['DB_HOST']}")
    if config['DB_PORT']:
        print(f"   DB_PORT: {config['DB_PORT']}")
    if config['DB_NAME']:
        print(f"   DB_NAME: {config['DB_NAME']}")
    if config['DB_USER']:
        print(f"   DB_USER: {config['DB_USER']}")
    if config['DB_PASSWORD']:
        print(f"   DB_PASSWORD: {'*' * len(config['DB_PASSWORD'])}")
    
    # Determinar qué configuración está activa
    if config['DATABASE_URL']:
        print("\n[INFO] Configuración activa: DATABASE_URL (Supabase)")
        es_supabase = 'supabase.co' in config['DATABASE_URL']
        es_local = 'localhost' in config['DATABASE_URL'] or '127.0.0.1' in config['DATABASE_URL']
    elif config['DB_HOST']:
        print("\n[INFO] Configuración activa: Variables individuales")
        es_supabase = 'supabase.co' in config['DB_HOST']
        es_local = config['DB_HOST'] in ('localhost', '127.0.0.1')
    else:
        print("\n[ERROR] No se encontró configuración de base de datos")
        print("[SOLUCIÓN] Configura DATABASE_URL o DB_HOST en .env")
        return False, None
    
    if es_supabase:
        print("   Tipo: Supabase (remoto)")
    elif es_local:
        print("   Tipo: Local (Docker o PostgreSQL local)")
    else:
        print("   Tipo: Desconocido")
    
    return True, config

def verificar_dns(hostname, timeout=5):
    """Verifica resolución DNS"""
    try:
        ip = socket.gethostbyname(hostname)
        return True, ip, None
    except socket.gaierror as e:
        return False, None, str(e)
    except Exception as e:
        return False, None, str(e)

def verificar_conectividad(hostname, port, timeout=5):
    """Verifica conectividad TCP"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((hostname, port))
        sock.close()
        return result == 0, None if result == 0 else f"Puerto {port} no accesible"
    except socket.gaierror as e:
        return False, f"Error DNS: {str(e)}"
    except Exception as e:
        return False, str(e)

def verificar_docker():
    """Verifica si Docker está corriendo y el contenedor está activo"""
    print("\n" + "=" * 70)
    print("3. VERIFICACIÓN DE DOCKER")
    print("=" * 70)
    
    try:
        import subprocess
        result = subprocess.run(
            ['docker', 'ps'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print("\n[ERROR] Docker no está corriendo o no está instalado")
            print("[SOLUCIÓN] Inicia Docker Desktop")
            return False
        
        if 'postgres_local' in result.stdout:
            print("\n[OK] Contenedor postgres_local está corriendo")
            return True
        else:
            print("\n[ADVERTENCIA] Contenedor postgres_local no está corriendo")
            print("[SOLUCIÓN] Ejecuta: docker start postgres_local")
            return False
            
    except FileNotFoundError:
        print("\n[ERROR] Docker no está instalado")
        print("[SOLUCIÓN] Instala Docker Desktop desde https://www.docker.com/products/docker-desktop/")
        return False
    except Exception as e:
        print(f"\n[ADVERTENCIA] No se pudo verificar Docker: {e}")
        return None

def diagnosticar_conexion(config):
    """Diagnostica problemas de conexión según la configuración"""
    print("\n" + "=" * 70)
    print("2. DIAGNÓSTICO DE CONECTIVIDAD")
    print("=" * 70)
    
    # Determinar hostname y puerto
    if config['DATABASE_URL']:
        # Extraer de DATABASE_URL
        url = config['DATABASE_URL']
        if 'supabase.co' in url:
            # Formato: postgresql://user:pass@host:port/db
            try:
                host_part = url.split('@')[1].split('/')[0]
                hostname = host_part.split(':')[0]
                port = int(host_part.split(':')[1]) if ':' in host_part else 5432
            except:
                print("\n[ERROR] No se pudo parsear DATABASE_URL")
                return False
        else:
            print("\n[INFO] DATABASE_URL apunta a base de datos local")
            return True
    elif config['DB_HOST']:
        hostname = config['DB_HOST']
        port = int(config['DB_PORT']) if config['DB_PORT'] else 5432
    else:
        print("\n[ERROR] No hay configuración de host")
        return False
    
    print(f"\n[INFO] Verificando: {hostname}:{port}")
    
    # Verificar DNS
    print("\n[1/2] Verificando resolución DNS...")
    dns_ok, ip, dns_error = verificar_dns(hostname, timeout=5)
    
    if dns_ok:
        print(f"[OK] DNS resuelto: {ip}")
    else:
        print(f"[ERROR] No se pudo resolver DNS: {dns_error}")
        
        if 'supabase.co' in hostname:
            print("\n[DIAGNÓSTICO] Problema de IPv6 detectado")
            print("   - Supabase gratis solo tiene IPv6")
            print("   - Tu red actual no soporta IPv6")
            print("\n[SOLUCIÓN]")
            print("   1. Ejecuta: python configuracion_dual_red.py")
            print("   2. Selecciona: Usar base de datos local")
            print("   3. O cambia a una red que soporte IPv6")
        else:
            print("\n[SOLUCIÓN] Verifica que el hostname sea correcto")
        
        return False
    
    # Verificar conectividad
    print("\n[2/2] Verificando conectividad TCP...")
    conn_ok, conn_error = verificar_conectividad(hostname, port, timeout=10)
    
    if conn_ok:
        print(f"[OK] Conexión TCP exitosa")
        return True
    else:
        print(f"[ERROR] No se pudo conectar: {conn_error}")
        
        if 'supabase.co' in hostname:
            print("\n[SOLUCIÓN]")
            print("   1. Verifica tu firewall")
            print("   2. Usa base de datos local: python configuracion_dual_red.py")
        else:
            print("\n[SOLUCIÓN]")
            print("   1. Verifica que el servicio esté corriendo")
            print("   2. Si es Docker: docker start postgres_local")
            print("   3. Si es PostgreSQL local: verifica el servicio")
        
        return False

def verificar_django():
    """Intenta conectar usando Django"""
    print("\n" + "=" * 70)
    print("4. VERIFICACIÓN CON DJANGO")
    print("=" * 70)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        import django
        django.setup()
        
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print(f"\n[OK] Conexión exitosa con Django")
        print(f"[INFO] PostgreSQL version: {version}")
        return True
        
    except Exception as e:
        error_str = str(e)
        print(f"\n[ERROR] No se pudo conectar con Django: {error_str}")
        
        if 'could not translate host name' in error_str.lower() or 'host desconocido' in error_str.lower():
            print("\n[DIAGNÓSTICO] Error de DNS/IPv6")
            print("[SOLUCIÓN] Ejecuta: python configuracion_dual_red.py")
        elif 'connection refused' in error_str.lower():
            print("\n[DIAGNÓSTICO] El servicio no está corriendo")
            print("[SOLUCIÓN] Si usas Docker: docker start postgres_local")
        elif 'password authentication failed' in error_str.lower():
            print("\n[DIAGNÓSTICO] Credenciales incorrectas")
            print("[SOLUCIÓN] Verifica DB_PASSWORD o DATABASE_URL en .env")
        elif 'timeout' in error_str.lower():
            print("\n[DIAGNÓSTICO] Timeout de conexión")
            print("[SOLUCIÓN] Verifica tu conexión a internet o usa base de datos local")
        
        return False

def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("DIAGNÓSTICO COMPLETO DE CONEXIÓN A BASE DE DATOS")
    print("=" * 70)
    
    # 1. Verificar .env
    env_ok, config = verificar_env()
    if not env_ok:
        return 1
    
    # 2. Diagnosticar conexión
    if config['DB_HOST'] and 'supabase.co' in config['DB_HOST']:
        diagnosticar_conexion(config)
    elif config['DATABASE_URL'] and 'supabase.co' in config['DATABASE_URL']:
        diagnosticar_conexion(config)
    elif config['DB_HOST'] and config['DB_HOST'] in ('localhost', '127.0.0.1'):
        # Verificar Docker si es local
        verificar_docker()
    
    # 3. Verificar con Django
    verificar_django()
    
    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print("\n[INFO] Si hay errores, ejecuta:")
    print("   python configuracion_dual_red.py")
    print("\n[INFO] Para más información, consulta:")
    print("   backend/documentacion/docker/PROBLEMA_IPV6_REDES.md")
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[ADVERTENCIA] Diagnóstico interrumpido")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
