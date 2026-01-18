"""
Script para cambiar .env a configuración de Docker local
Esto comenta DATABASE_URL y activa las variables individuales para Docker
"""
from pathlib import Path
import shutil
from datetime import datetime

def cambiar_a_docker():
    """Cambia .env para usar Docker local"""
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
        lineas = f.readlines()
    
    nuevas_lineas = []
    encontrado_configuracion = False
    
    for i, linea in enumerate(lineas):
        linea_stripped = linea.strip()
        
        # Comentar DATABASE_URL si está activa
        if linea_stripped.startswith('DATABASE_URL=') and not linea_stripped.startswith('#'):
            nuevas_lineas.append('# ' + linea)
            encontrado_configuracion = True
            continue
        
        # Si encontramos el comentario de configuración, activar variables Docker
        if 'configuración con supabase' in linea_stripped.lower() or 'opcion1' in linea_stripped.lower():
            # Activar variables Docker (descomentar)
            nuevas_lineas.append(linea)
            # Buscar las siguientes líneas de DB_* y activarlas
            for j in range(i+1, min(i+6, len(lineas))):
                siguiente = lineas[j].strip()
                if siguiente.startswith('# DB_NAME=') or siguiente.startswith('DB_NAME='):
                    if siguiente.startswith('#'):
                        nuevas_lineas.append(siguiente.replace('# ', ''))
                    else:
                        nuevas_lineas.append(lineas[j])
                elif siguiente.startswith('# DB_USER=') or siguiente.startswith('DB_USER='):
                    if siguiente.startswith('#'):
                        nuevas_lineas.append(siguiente.replace('# ', ''))
                    else:
                        nuevas_lineas.append(lineas[j])
                elif siguiente.startswith('# DB_PASSWORD=') or siguiente.startswith('DB_PASSWORD='):
                    if siguiente.startswith('#'):
                        nuevas_lineas.append(siguiente.replace('# ', ''))
                    else:
                        nuevas_lineas.append(lineas[j])
                elif siguiente.startswith('# DB_HOST=') or siguiente.startswith('DB_HOST='):
                    if 'localhost' in siguiente:
                        if siguiente.startswith('#'):
                            nuevas_lineas.append(siguiente.replace('# ', ''))
                        else:
                            nuevas_lineas.append(lineas[j])
                    else:
                        nuevas_lineas.append(lineas[j])
                elif siguiente.startswith('# DB_PORT=') or siguiente.startswith('DB_PORT='):
                    if '5435' in siguiente:
                        if siguiente.startswith('#'):
                            nuevas_lineas.append(siguiente.replace('# ', ''))
                        else:
                            nuevas_lineas.append(lineas[j])
                    else:
                        nuevas_lineas.append(lineas[j])
                else:
                    nuevas_lineas.append(lineas[j])
            continue
        
        nuevas_lineas.append(linea)
    
    # Si no se encontró la sección de configuración, agregarla
    if not encontrado_configuracion:
        # Buscar dónde insertar
        insert_index = len(nuevas_lineas)
        for i, linea in enumerate(nuevas_lineas):
            if 'database' in linea.lower() or 'db_' in linea.lower():
                insert_index = i
                break
        
        # Insertar configuración Docker
        config_docker = [
            '# configuración con supabase - opcion1\n',
            'DB_NAME=UBAppDB\n',
            'DB_USER=postgres\n',
            'DB_PASSWORD=admin\n',
            'DB_HOST=localhost\n',
            'DB_PORT=5435\n',
            '# supabase - opcion2\n',
            '# DATABASE_URL=postgresql://postgres:TU_CONTRASEÑA@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres\n',
            '# Docker Local:\n',
            '# DATABASE_URL=postgresql://postgres:admin@localhost:5435/UBAppDB\n',
            '\n'
        ]
        nuevas_lineas[insert_index:insert_index] = config_docker
    
    # Escribir archivo
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(nuevas_lineas)
    
    print("[OK] Configuración cambiada a Docker local")
    print("\n[INFO] Configuración activa:")
    print("   DB_HOST=localhost")
    print("   DB_PORT=5435")
    print("   DB_NAME=UBAppDB")
    print("   DB_USER=postgres")
    print("   DB_PASSWORD=admin")
    print("\n[INFO] DATABASE_URL está comentada")
    
    return True

if __name__ == '__main__':
    try:
        cambiar_a_docker()
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

