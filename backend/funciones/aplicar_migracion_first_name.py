"""
Script para aplicar la migración que elimina first_name y last_name
Si las columnas todavía existen, las elimina directamente
"""
import sys
import os
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def eliminar_columnas_problematicas():
    """Elimina las columnas first_name, last_name y email si existen"""
    print("=" * 70)
    print("ELIMINACIÓN DE COLUMNAS PROBLEMÁTICAS")
    print("=" * 70)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        import django
        django.setup()
        
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Verificar qué columnas existen
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'usuarios'
                AND column_name IN ('first_name', 'last_name', 'email');
            """)
            
            columnas_existentes = [row[0] for row in cursor.fetchall()]
            
            if not columnas_existentes:
                print("\n[OK] No hay columnas problemáticas que eliminar")
                print("   - first_name: No existe")
                print("   - last_name: No existe")
                print("   - email: No existe")
                return True
            
            print(f"\n[INFO] Columnas a eliminar: {', '.join(columnas_existentes)}")
            
            # Eliminar cada columna
            for columna in columnas_existentes:
                try:
                    print(f"\n[INFO] Eliminando columna '{columna}'...")
                    cursor.execute(f"ALTER TABLE usuarios DROP COLUMN IF EXISTS {columna};")
                    print(f"[OK] Columna '{columna}' eliminada")
                except Exception as e:
                    print(f"[ERROR] No se pudo eliminar '{columna}': {e}")
                    return False
            
            print("\n" + "=" * 70)
            print("[OK] COLUMNAS ELIMINADAS EXITOSAMENTE")
            print("=" * 70)
            
            # Verificar que se eliminaron
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'usuarios'
                AND column_name IN ('first_name', 'last_name', 'email');
            """)
            
            columnas_restantes = cursor.fetchall()
            
            if columnas_restantes:
                print("\n[ADVERTENCIA] Algunas columnas todavía existen:")
                for columna in columnas_restantes:
                    print(f"   - {columna[0]}")
                return False
            else:
                print("\n[OK] Verificación: Todas las columnas problemáticas fueron eliminadas")
                return True
            
    except Exception as e:
        print(f"\n[ERROR] Error al eliminar columnas: {e}")
        import traceback
        traceback.print_exc()
        return False

def aplicar_migraciones():
    """Aplica las migraciones de usuarios"""
    print("\n" + "=" * 70)
    print("APLICANDO MIGRACIONES")
    print("=" * 70)
    
    try:
        import subprocess
        result = subprocess.run(
            ['python', 'manage.py', 'migrate', 'usuarios'],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n[OK] Migraciones aplicadas exitosamente")
            return True
        else:
            print("\n[ERROR] Error al aplicar migraciones")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return False

def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("SOLUCIÓN PARA ERROR DE first_name")
    print("=" * 70)
    
    # Paso 1: Eliminar columnas problemáticas
    if not eliminar_columnas_problematicas():
        print("\n[ERROR] No se pudieron eliminar las columnas")
        return 1
    
    # Paso 2: Aplicar migraciones
    if not aplicar_migraciones():
        print("\n[ADVERTENCIA] Hubo problemas al aplicar migraciones")
        print("[INFO] Las columnas ya fueron eliminadas, puedes continuar")
    
    print("\n" + "=" * 70)
    print("[OK] PROCESO COMPLETADO")
    print("=" * 70)
    print("\n[INFO] Próximos pasos:")
    print("   1. Reinicia el servidor Django")
    print("   2. Intenta crear el usuario nuevamente")
    print("   3. Si persisten problemas, ejecuta: python funciones/verificar_estructura_db.py")
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n[ADVERTENCIA] Proceso interrumpido")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
