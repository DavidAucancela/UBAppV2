"""
Script para verificar si Supabase está disponible
Detecta problemas de DNS/IPv6 y sugiere usar base de datos local
"""
import socket
import sys
import os
from pathlib import Path

# Agregar el directorio padre al path para importar settings
sys.path.insert(0, str(Path(__file__).parent.parent))

def verificar_dns(hostname, timeout=5):
    """
    Verifica si se puede resolver el DNS de un hostname
    Retorna (exito, ip, error)
    """
    try:
        # Intentar resolver DNS
        ip = socket.gethostbyname(hostname)
        return True, ip, None
    except socket.gaierror as e:
        # Error de DNS (host desconocido)
        return False, None, str(e)
    except Exception as e:
        return False, None, str(e)

def verificar_conectividad(hostname, port, timeout=5):
    """
    Verifica si se puede conectar a un host:puerto
    Retorna (exito, error)
    """
    try:
        # Intentar conexión TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((hostname, port))
        sock.close()
        
        if result == 0:
            return True, None
        else:
            return False, f"No se pudo conectar al puerto {port}"
    except socket.gaierror as e:
        return False, f"Error DNS: {str(e)}"
    except Exception as e:
        return False, str(e)

def verificar_supabase():
    """
    Verifica si Supabase está disponible
    Retorna dict con información de la verificación
    """
    # Obtener hostname de Supabase desde .env
    env_path = Path(__file__).parent.parent / '.env'
    supabase_host = None
    
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                if linea.startswith('DB_HOST=') and 'supabase.co' in linea:
                    supabase_host = linea.split('=', 1)[1].strip()
                    break
                elif linea.startswith('DATABASE_URL=') and 'supabase.co' in linea:
                    # Extraer hostname de la URL
                    try:
                        url = linea.split('=', 1)[1].strip()
                        if url.startswith('postgresql://'):
                            # Formato: postgresql://user:pass@host:port/db
                            host_part = url.split('@')[1].split('/')[0]
                            supabase_host = host_part.split(':')[0]
                    except:
                        pass
    
    # Si no se encontró en .env, usar el hostname conocido
    if not supabase_host:
        supabase_host = "db.gybrifikqkibwqpzjuxm.supabase.co"
    
    print("=" * 70)
    print("VERIFICACIÓN DE CONECTIVIDAD A SUPABASE")
    print("=" * 70)
    print(f"\n[INFO] Hostname: {supabase_host}")
    print(f"[INFO] Puerto: 5432")
    
    # Verificar DNS
    print("\n[1/3] Verificando resolución DNS...")
    dns_ok, ip, dns_error = verificar_dns(supabase_host, timeout=5)
    
    if dns_ok:
        print(f"[OK] DNS resuelto correctamente: {ip}")
    else:
        print(f"[ERROR] No se pudo resolver DNS: {dns_error}")
        print("\n[DIAGNÓSTICO]")
        print("   - El proveedor de red no puede resolver el hostname")
        print("   - Esto generalmente indica que la red no soporta IPv6")
        print("   - Supabase gratis solo tiene IPv6 disponible")
        print("\n[SOLUCIÓN]")
        print("   - Usa base de datos local (Docker)")
        print("   - O cambia a una red que soporte IPv6")
        return {
            'disponible': False,
            'error': 'DNS',
            'mensaje': 'No se pudo resolver el hostname (problema de IPv6)',
            'hostname': supabase_host,
            'ip': None
        }
    
    # Verificar conectividad
    print("\n[2/3] Verificando conectividad TCP...")
    conn_ok, conn_error = verificar_conectividad(supabase_host, 5432, timeout=10)
    
    if conn_ok:
        print("[OK] Conexión TCP exitosa")
    else:
        print(f"[ERROR] No se pudo conectar: {conn_error}")
        print("\n[DIAGNÓSTICO]")
        print("   - El hostname se resolvió pero no se puede conectar")
        print("   - Puede ser un problema de firewall o red")
        print("\n[SOLUCIÓN]")
        print("   - Verifica tu firewall")
        print("   - Usa base de datos local como alternativa")
        return {
            'disponible': False,
            'error': 'CONEXION',
            'mensaje': f'No se pudo conectar al puerto 5432: {conn_error}',
            'hostname': supabase_host,
            'ip': ip
        }
    
    # Verificar soporte IPv6
    print("\n[3/3] Verificando soporte IPv6...")
    try:
        # Intentar resolver IPv6
        ipv6_info = socket.getaddrinfo(supabase_host, 5432, socket.AF_INET6)
        if ipv6_info:
            print("[OK] Soporte IPv6 detectado")
            ipv6_ok = True
        else:
            ipv6_ok = False
    except:
        # Si falla, puede ser que la red no soporte IPv6
        print("[ADVERTENCIA] No se pudo verificar IPv6 directamente")
        ipv6_ok = True  # Asumimos que está bien si llegamos aquí
    
    print("\n" + "=" * 70)
    print("[OK] SUPABASE ESTÁ DISPONIBLE")
    print("=" * 70)
    print(f"\n[INFO] Puedes usar Supabase normalmente")
    print(f"[INFO] IP: {ip}")
    
    return {
        'disponible': True,
        'error': None,
        'mensaje': 'Supabase está disponible y accesible',
        'hostname': supabase_host,
        'ip': ip,
        'ipv6_ok': ipv6_ok
    }

def main():
    """Función principal"""
    try:
        resultado = verificar_supabase()
        
        if resultado['disponible']:
            print("\n[RECOMENDACIÓN] Usa Supabase para trabajar")
            return 0
        else:
            print("\n[RECOMENDACIÓN] Usa base de datos local (Docker)")
            print("\n[ACCIÓN] Ejecuta: python configuracion_dual_red.py")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n[ADVERTENCIA] Verificación interrumpida")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
