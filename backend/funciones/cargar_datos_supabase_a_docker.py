"""
Script simple para cargar datos de Supabase a Docker local

INSTRUCCIONES:
1. Asegúrate de estar conectado a Supabase (configura .env para usar Supabase)
2. Ejecuta este script
3. El script exportará desde Supabase e importará a Docker

NOTA: Este script asume que ya tienes Docker configurado y corriendo.
"""
import os
import sys
import subprocess

def verificar_docker():
    """Verifica que Docker esté corriendo"""
    try:
        result = subprocess.run(
            ['docker', 'ps'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if 'postgres_local' in result.stdout:
            print("[OK] Contenedor Docker postgres_local está corriendo")
            return True
        else:
            print("[ADVERTENCIA] Contenedor Docker postgres_local no está corriendo")
            respuesta = input("¿Deseas iniciarlo ahora? (s/n): ").strip().lower()
            if respuesta == 's':
                result = subprocess.run(['docker', 'start', 'postgres_local'], timeout=30)
                if result.returncode == 0:
                    print("[OK] Contenedor iniciado")
                    return True
            print("[ERROR] Necesitas que Docker esté corriendo")
            return False
    except Exception as e:
        print(f"[ERROR] No se puede verificar Docker: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 70)
    print("CARGAR DATOS DE SUPABASE A DOCKER LOCAL")
    print("=" * 70)
    
    print("\n[INFO] Este script realizará:")
    print("   1. Exportar datos desde Supabase (necesitas estar conectado)")
    print("   2. Cambiar configuración a Docker local")
    print("   3. Importar datos a Docker")
    
    print("\n[IMPORTANTE] Asegúrate de que:")
    print("   - Estás conectado a Supabase (configura .env con DATABASE_URL de Supabase)")
    print("   - Docker Desktop está corriendo")
    print("   - El contenedor postgres_local está iniciado")
    
    respuesta = input("\n¿Deseas continuar? (s/n): ").strip().lower()
    if respuesta != 's':
        print("[INFO] Operación cancelada")
        return
    
    # Verificar Docker
    if not verificar_docker():
        print("\n[ERROR] Por favor inicia Docker manualmente:")
        print("   docker start postgres_local")
        return
    
    # Paso 1: Exportar desde Supabase
    print("\n" + "=" * 70)
    print("PASO 1: EXPORTAR DATOS DESDE SUPABASE")
    print("=" * 70)
    print("\n[INFO] Ejecutando exportar_datos_supabase.py...")
    print("[INFO] Asegúrate de que .env esté configurado para Supabase\n")
    
    try:
        result = subprocess.run(
            [sys.executable, 'exportar_datos_supabase.py'],
            cwd=os.path.dirname(__file__)
        )
        if result.returncode != 0:
            print("\n[ERROR] Error al exportar datos desde Supabase")
            print("[INFO] Verifica que:")
            print("   1. Estés conectado a una red que soporte IPv6 (tu casa)")
            print("   2. .env esté configurado para usar Supabase (DATABASE_URL)")
            print("   3. La contraseña de Supabase sea correcta")
            return
    except Exception as e:
        print(f"\n[ERROR] Error al ejecutar exportar_datos_supabase.py: {e}")
        return
    
    # Paso 2: Informar sobre cambio de configuración
    print("\n" + "=" * 70)
    print("PASO 2: CAMBIAR CONFIGURACIÓN A DOCKER")
    print("=" * 70)
    print("\n[INFO] Ahora necesitas cambiar .env para usar Docker local")
    print("\n[INFO] En tu archivo .env, asegúrate de tener:")
    print("   # Comenta la línea DATABASE_URL de Supabase:")
    print("   # DATABASE_URL=postgresql://postgres:[admin]@db.gybrifikqkibwqpzjuxm.supabase.co:5432/postgres")
    print("\n   # Descomenta las variables de Docker:")
    print("   DB_NAME=UBAppDB")
    print("   DB_USER=postgres")
    print("   DB_PASSWORD=admin")
    print("   DB_HOST=localhost")
    print("   DB_PORT=5435")
    
    respuesta = input("\n¿Ya cambiaste la configuración en .env? (s/n): ").strip().lower()
    if respuesta != 's':
        print("\n[INFO] Por favor cambia la configuración manualmente y ejecuta:")
        print("   python importar_datos_local.py")
        return
    
    # Paso 3: Importar a Docker
    print("\n" + "=" * 70)
    print("PASO 3: IMPORTAR DATOS A DOCKER")
    print("=" * 70)
    print("\n[INFO] Ejecutando importar_datos_local.py...\n")
    
    try:
        result = subprocess.run(
            [sys.executable, 'importar_datos_local.py'],
            cwd=os.path.dirname(__file__)
        )
        if result.returncode != 0:
            print("\n[ERROR] Error al importar datos a Docker")
            return
    except Exception as e:
        print(f"\n[ERROR] Error al ejecutar importar_datos_local.py: {e}")
        return
    
    # Resumen final
    print("\n" + "=" * 70)
    print("[OK] CARGA DE DATOS COMPLETADA")
    print("=" * 70)
    print("\n[INFO] Tu base de datos Docker local ahora tiene los datos de Supabase")
    print("\n[INFO] Puedes trabajar con Docker local en cualquier red")
    print("\n[INFO] Para volver a usar Supabase, cambia la configuración en .env")

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

