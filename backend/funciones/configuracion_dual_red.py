"""
Script para configurar automáticamente entre Supabase y base de datos local
Detecta si Supabase está disponible y cambia la configuración según corresponda
"""
import sys
import os
from pathlib import Path
import shutil
from datetime import datetime

# Agregar funciones al path
sys.path.insert(0, str(Path(__file__).parent / 'funciones'))

try:
    from verificar_conexion_supabase import verificar_supabase
except ImportError:
    # Si no se puede importar, crear función básica
    def verificar_supabase():
        return {'disponible': False, 'error': 'IMPORT', 'mensaje': 'No se pudo importar módulo de verificación'}

def leer_env():
    """Lee el archivo .env y retorna su contenido como lista de líneas"""
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print("[ERROR] Archivo .env no encontrado")
        return None
    
    with open(env_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def escribir_env(lineas):
    """Escribe las líneas al archivo .env"""
    env_path = Path(__file__).parent / '.env'
    
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lineas)

def crear_backup():
    """Crea un backup del archivo .env"""
    env_path = Path(__file__).parent / '.env'
    backup_path = Path(__file__).parent / f'.env.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    
    if env_path.exists():
        shutil.copy(env_path, backup_path)
        print(f"[OK] Backup creado: {backup_path.name}")
        return backup_path
    return None

def configurar_supabase():
    """Configura .env para usar Supabase"""
    print("\n" + "=" * 70)
    print("CONFIGURANDO PARA SUPABASE")
    print("=" * 70)
    
    lineas = leer_env()
    if lineas is None:
        return False
    
    crear_backup()
    
    nuevas_lineas = []
    encontrado_db_config = False
    
    for linea in lineas:
        linea_stripped = linea.strip()
        
        # Activar DATABASE_URL de Supabase si está comentada
        if linea_stripped.startswith('# DATABASE_URL=') and 'supabase.co' in linea_stripped:
            nuevas_lineas.append(linea.replace('# ', ''))
            encontrado_db_config = True
            continue
        elif linea_stripped.startswith('DATABASE_URL=') and 'supabase.co' in linea_stripped:
            nuevas_lineas.append(linea)
            encontrado_db_config = True
            continue
        
        # Comentar variables individuales de Docker
        if linea_stripped.startswith('DB_HOST=') and 'localhost' in linea_stripped:
            nuevas_lineas.append('# ' + linea)
            continue
        elif linea_stripped.startswith('DB_PORT=') and '5435' in linea_stripped:
            nuevas_lineas.append('# ' + linea)
            continue
        elif linea_stripped.startswith('DB_NAME=') and 'UBAppDB' in linea_stripped:
            nuevas_lineas.append('# ' + linea)
            continue
        
        nuevas_lineas.append(linea)
    
    # Si no se encontró DATABASE_URL, agregarla
    if not encontrado_db_config:
        # Buscar dónde insertar
        insert_index = len(nuevas_lineas)
        for i, linea in enumerate(nuevas_lineas):
            if 'database' in linea.lower() or 'db_' in linea.lower():
                insert_index = i + 1
                break
        
        nuevas_lineas.insert(insert_index, '\n# Configuración Supabase (activada)\n')
        nuevas_lineas.insert(insert_index + 1, 'DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres\n')
        nuevas_lineas.insert(insert_index + 2, '\n# Configuración Docker Local (comentada)\n')
        nuevas_lineas.insert(insert_index + 3, '# DB_HOST=localhost\n')
        nuevas_lineas.insert(insert_index + 4, '# DB_PORT=5435\n')
        nuevas_lineas.insert(insert_index + 5, '# DB_NAME=UBAppDB\n')
        nuevas_lineas.insert(insert_index + 6, '# DB_USER=postgres\n')
        nuevas_lineas.insert(insert_index + 7, '# DB_PASSWORD=admin\n')
    
    escribir_env(nuevas_lineas)
    
    print("\n[OK] Configuración cambiada a Supabase")
    print("\n[INFO] Configuración activa:")
    print("   DATABASE_URL=postgresql://postgres:...@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres")
    print("\n[ADVERTENCIA] Asegúrate de que DATABASE_URL tenga la contraseña correcta")
    
    return True

def configurar_local():
    """Configura .env para usar base de datos local (Docker)"""
    print("\n" + "=" * 70)
    print("CONFIGURANDO PARA BASE DE DATOS LOCAL (DOCKER)")
    print("=" * 70)
    
    lineas = leer_env()
    if lineas is None:
        return False
    
    crear_backup()
    
    nuevas_lineas = []
    encontrado_db_config = False
    
    for linea in lineas:
        linea_stripped = linea.strip()
        
        # Comentar DATABASE_URL de Supabase
        if linea_stripped.startswith('DATABASE_URL=') and 'supabase.co' in linea_stripped:
            nuevas_lineas.append('# ' + linea)
            encontrado_db_config = True
            continue
        
        # Activar variables individuales de Docker
        if linea_stripped.startswith('# DB_HOST=') and 'localhost' in linea_stripped:
            nuevas_lineas.append(linea.replace('# ', ''))
            encontrado_db_config = True
            continue
        elif linea_stripped.startswith('DB_HOST=') and 'localhost' in linea_stripped:
            nuevas_lineas.append(linea)
            encontrado_db_config = True
            continue
        
        if linea_stripped.startswith('# DB_PORT=') and '5435' in linea_stripped:
            nuevas_lineas.append(linea.replace('# ', ''))
            continue
        elif linea_stripped.startswith('DB_PORT=') and '5435' in linea_stripped:
            nuevas_lineas.append(linea)
            continue
        
        if linea_stripped.startswith('# DB_NAME=') and 'UBAppDB' in linea_stripped:
            nuevas_lineas.append(linea.replace('# ', ''))
            continue
        elif linea_stripped.startswith('DB_NAME=') and 'UBAppDB' in linea_stripped:
            nuevas_lineas.append(linea)
            continue
        
        if linea_stripped.startswith('# DB_USER='):
            nuevas_lineas.append(linea.replace('# ', ''))
            continue
        
        if linea_stripped.startswith('# DB_PASSWORD='):
            nuevas_lineas.append(linea.replace('# ', ''))
            continue
        
        nuevas_lineas.append(linea)
    
    # Si no se encontró configuración, agregarla
    if not encontrado_db_config:
        insert_index = len(nuevas_lineas)
        for i, linea in enumerate(nuevas_lineas):
            if 'database' in linea.lower() or 'db_' in linea.lower():
                insert_index = i + 1
                break
        
        nuevas_lineas.insert(insert_index, '\n# Configuración Docker Local (activada)\n')
        nuevas_lineas.insert(insert_index + 1, 'DB_HOST=localhost\n')
        nuevas_lineas.insert(insert_index + 2, 'DB_PORT=5435\n')
        nuevas_lineas.insert(insert_index + 3, 'DB_NAME=UBAppDB\n')
        nuevas_lineas.insert(insert_index + 4, 'DB_USER=postgres\n')
        nuevas_lineas.insert(insert_index + 5, 'DB_PASSWORD=admin\n')
        nuevas_lineas.insert(insert_index + 6, '\n# Configuración Supabase (comentada)\n')
        nuevas_lineas.insert(insert_index + 7, '# DATABASE_URL=postgresql://postgres:...@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres\n')
    
    escribir_env(nuevas_lineas)
    
    print("\n[OK] Configuración cambiada a base de datos local")
    print("\n[INFO] Configuración activa:")
    print("   DB_HOST=localhost")
    print("   DB_PORT=5435")
    print("   DB_NAME=UBAppDB")
    print("   DB_USER=postgres")
    print("   DB_PASSWORD=admin")
    print("\n[INFO] Asegúrate de que Docker esté corriendo:")
    print("   docker start postgres_local")
    
    return True

def main():
    """Función principal con menú interactivo"""
    print("\n" + "=" * 70)
    print("CONFIGURACIÓN DUAL: SUPABASE ↔️ LOCAL")
    print("=" * 70)
    
    # Verificar disponibilidad de Supabase
    print("\n[INFO] Verificando conectividad a Supabase...")
    resultado = verificar_supabase()
    
    print("\n" + "=" * 70)
    print("OPCIONES")
    print("=" * 70)
    
    if resultado['disponible']:
        print("\n[1] Usar Supabase (recomendado - está disponible)")
        print("[2] Usar base de datos local (Docker)")
        print("[3] Salir sin cambios")
    else:
        print("\n[1] Usar base de datos local (Docker) - RECOMENDADO")
        print("[2] Usar Supabase (no disponible actualmente)")
        print("[3] Salir sin cambios")
    
    opcion = input("\nSelecciona una opción (1-3): ").strip()
    
    if opcion == '1':
        if resultado['disponible']:
            configurar_supabase()
        else:
            configurar_local()
    elif opcion == '2':
        if resultado['disponible']:
            configurar_local()
        else:
            print("\n[ADVERTENCIA] Supabase no está disponible actualmente")
            respuesta = input("¿Deseas configurarlo de todas formas? (s/n): ").strip().lower()
            if respuesta == 's':
                configurar_supabase()
            else:
                print("\n[INFO] No se realizaron cambios")
    elif opcion == '3':
        print("\n[INFO] No se realizaron cambios")
    else:
        print("\n[ERROR] Opción inválida")
        return 1
    
    print("\n" + "=" * 70)
    print("[OK] CONFIGURACIÓN COMPLETADA")
    print("=" * 70)
    print("\n[INFO] Próximos pasos:")
    print("   1. Verifica la configuración en .env")
    print("   2. Si usas Docker, asegúrate de que esté corriendo:")
    print("      docker start postgres_local")
    print("   3. Inicia Django: python manage.py runserver")
    
    return 0

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
