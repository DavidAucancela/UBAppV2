"""
Script para actualizar .env con configuración de Docker
"""
from pathlib import Path
import shutil

def actualizar_env():
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print("[ERROR] Archivo .env no encontrado")
        return False
    
    # Crear backup
    backup_path = Path(__file__).parent / '.env.supabase'
    if not backup_path.exists():
        shutil.copy(env_path, backup_path)
        print("[OK] Backup creado: .env.supabase")
    
    # Leer y actualizar
    with open(env_path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    lineas = contenido.split('\n')
    nuevas_lineas = []
    
    for linea in lineas:
        if linea.startswith('DB_HOST='):
            nuevas_lineas.append('DB_HOST=localhost')
        elif linea.startswith('DB_PORT='):
            nuevas_lineas.append('DB_PORT=5435')
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
    
    print("[OK] Archivo .env actualizado")
    print("\n[INFO] Configuración:")
    print("   DB_HOST=localhost")
    print("   DB_PORT=5435")
    print("   DB_NAME=UBAppDB")
    print("   DB_USER=postgres")
    print("   DB_PASSWORD=admin")
    
    return True

if __name__ == '__main__':
    actualizar_env()

