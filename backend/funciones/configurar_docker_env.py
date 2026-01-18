"""
Script simple para configurar .env para Docker local
Agrega las variables DB_* activas al final del archivo
"""
from pathlib import Path
import shutil
from datetime import datetime

def configurar_docker():
    """Configura .env para usar Docker local"""
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print("[ERROR] Archivo .env no encontrado")
        return False
    
    # Crear backup
    backup_path = Path(__file__).parent / f'.env.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    shutil.copy(env_path, backup_path)
    print(f"[OK] Backup creado: {backup_path.name}")
    
    # Leer archivo
    with open(env_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    lineas = contenido.split('\n')
    nuevas_lineas = []
    
    # Comentar todas las líneas DATABASE_URL activas
    for linea in lineas:
        if linea.strip().startswith('DATABASE_URL=') and not linea.strip().startswith('#'):
            nuevas_lineas.append('# ' + linea)
        else:
            nuevas_lineas.append(linea)
    
    # Agregar configuración Docker al final si no existe
    contenido_completo = '\n'.join(nuevas_lineas)
    
    # Verificar si ya existen las variables activas
    if 'DB_HOST=localhost' not in contenido_completo or contenido_completo.count('DB_HOST=localhost') == contenido_completo.count('# DB_HOST=localhost'):
        # Agregar configuración Docker al final
        config_docker = '''
# ============================================
# Configuración Docker Local (ACTIVA)
# ============================================
DB_NAME=UBAppDB
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5435
'''
        nuevas_lineas.append(config_docker)
    
    # Escribir archivo
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(nuevas_lineas))
    
    print("[OK] Configuración actualizada para Docker local")
    print("\n[INFO] Variables activas:")
    print("   DB_HOST=localhost")
    print("   DB_PORT=5435")
    print("   DB_NAME=UBAppDB")
    print("   DB_USER=postgres")
    print("   DB_PASSWORD=admin")
    
    return True

if __name__ == '__main__':
    try:
        configurar_docker()
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

