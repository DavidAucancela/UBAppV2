"""
Script para limpiar contenedor Docker de PostgreSQL anterior
"""
import subprocess
import sys

def limpiar_contenedor():
    """Elimina el contenedor postgres_local si existe"""
    print("=" * 70)
    print("LIMPIANDO CONTENEDOR DOCKER ANTERIOR")
    print("=" * 70)
    
    print("\n[INFO] Buscando contenedor postgres_local...")
    
    # Detener contenedor si está corriendo
    try:
        print("[INFO] Deteniendo contenedor...")
        subprocess.run(
            ['docker', 'stop', 'postgres_local'],
            capture_output=True,
            timeout=30
        )
        print("[OK] Contenedor detenido")
    except:
        print("[INFO] Contenedor no estaba corriendo")
    
    # Eliminar contenedor
    try:
        print("[INFO] Eliminando contenedor...")
        subprocess.run(
            ['docker', 'rm', 'postgres_local'],
            capture_output=True,
            timeout=30
        )
        print("[OK] Contenedor eliminado")
    except:
        print("[INFO] Contenedor no existía")
    
    print("\n[OK] Limpieza completada")
    print("[INFO] Ahora puedes ejecutar: python setup_docker_postgres.py")

if __name__ == '__main__':
    try:
        limpiar_contenedor()
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)

