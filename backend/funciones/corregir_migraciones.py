"""
Script para corregir problemas con migraciones
Aplica las migraciones en el orden correcto y maneja dependencias
"""
import sys
import os
import subprocess
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def aplicar_migraciones_ordenadas():
    """Aplica migraciones en el orden correcto"""
    print("=" * 70)
    print("CORRECCIÓN DE MIGRACIONES")
    print("=" * 70)
    
    # Orden de aplicación (respetando dependencias)
    apps_orden = [
        'contenttypes',
        'auth',
        'admin',
        'sessions',
        'usuarios',
        'archivos',
        'busqueda',  # Debe ir antes de metricas
        'metricas',  # Depende de busqueda
        'notificaciones',
    ]
    
    print("\n[INFO] Aplicando migraciones en orden:")
    print("   1. Apps base (contenttypes, auth, admin, sessions)")
    print("   2. Usuarios")
    print("   3. Archivos")
    print("   4. Búsqueda (requerida para métricas)")
    print("   5. Métricas")
    print("   6. Notificaciones")
    
    exito_total = True
    
    for app in apps_orden:
        print(f"\n[INFO] Aplicando migraciones de '{app}'...")
        try:
            result = subprocess.run(
                ['python', 'manage.py', 'migrate', app],
                cwd=Path(__file__).parent.parent,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"[OK] Migraciones de '{app}' aplicadas")
                if result.stdout:
                    # Mostrar solo las líneas importantes
                    for linea in result.stdout.split('\n'):
                        if 'Applying' in linea or 'OK' in linea or 'No migrations' in linea:
                            print(f"   {linea}")
            else:
                print(f"[ERROR] Error al aplicar migraciones de '{app}'")
                print(result.stderr)
                exito_total = False
                
                # Si es busqueda y falla, es crítico
                if app == 'busqueda':
                    print("\n[ADVERTENCIA] Error crítico: busqueda debe aplicarse antes de metricas")
                    print("[SOLUCIÓN] Verifica que la tabla embedding_busqueda exista")
                    return False
                    
        except subprocess.TimeoutExpired:
            print(f"[ERROR] Timeout al aplicar migraciones de '{app}'")
            exito_total = False
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            exito_total = False
    
    return exito_total

def verificar_tabla_embedding_busqueda():
    """Verifica si la tabla embedding_busqueda existe"""
    print("\n" + "=" * 70)
    print("VERIFICACIÓN DE TABLA embedding_busqueda")
    print("=" * 70)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        import django
        django.setup()
        
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'embedding_busqueda'
                );
            """)
            existe = cursor.fetchone()[0]
            
            if existe:
                print("\n[OK] La tabla 'embedding_busqueda' existe")
                return True
            else:
                print("\n[ERROR] La tabla 'embedding_busqueda' NO existe")
                print("[SOLUCIÓN] Aplicar migraciones de busqueda primero")
                return False
                
    except Exception as e:
        print(f"\n[ERROR] Error al verificar: {e}")
        return False

def crear_tabla_embedding_busqueda_manual():
    """Crea la tabla embedding_busqueda manualmente si no existe"""
    print("\n" + "=" * 70)
    print("CREACIÓN MANUAL DE TABLA embedding_busqueda")
    print("=" * 70)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        import django
        django.setup()
        
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Verificar si existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'embedding_busqueda'
                );
            """)
            existe = cursor.fetchone()[0]
            
            if existe:
                print("\n[OK] La tabla ya existe, no es necesario crearla")
                return True
            
            print("\n[INFO] Creando tabla 'embedding_busqueda'...")
            
            # Crear tabla
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS embedding_busqueda (
                    id BIGSERIAL PRIMARY KEY,
                    consulta TEXT NOT NULL,
                    resultados_encontrados INTEGER NOT NULL DEFAULT 0,
                    tiempo_respuesta INTEGER NOT NULL DEFAULT 0,
                    fecha_busqueda TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    filtros_aplicados JSONB,
                    usuario_id BIGINT NOT NULL,
                    modelo_utilizado VARCHAR(100) NOT NULL DEFAULT 'text-embedding-3-small',
                    costo_consulta NUMERIC(10,8) NOT NULL DEFAULT 0.0,
                    tokens_utilizados INTEGER NOT NULL DEFAULT 0,
                    resultados_json JSONB,
                    embedding_vector vector(1536),
                    CONSTRAINT embedding_busqueda_usuario_id_fk 
                        FOREIGN KEY (usuario_id) 
                        REFERENCES usuarios(id) 
                        ON DELETE CASCADE
                );
            """)
            
            print("[OK] Tabla 'embedding_busqueda' creada")
            
            # Crear índices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS embedding_busqueda_usuario_id_idx 
                ON embedding_busqueda(usuario_id);
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS embedding_busqueda_fecha_busqueda_idx 
                ON embedding_busqueda(fecha_busqueda DESC);
            """)
            
            print("[OK] Índices creados")
            
            return True
            
    except Exception as e:
        print(f"\n[ERROR] Error al crear tabla: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("CORRECCIÓN AUTOMÁTICA DE MIGRACIONES")
    print("=" * 70)
    
    # Paso 1: Verificar tabla embedding_busqueda
    if not verificar_tabla_embedding_busqueda():
        print("\n[INFO] Intentando crear tabla manualmente...")
        if crear_tabla_embedding_busqueda_manual():
            print("[OK] Tabla creada, continuando con migraciones...")
        else:
            print("[ERROR] No se pudo crear la tabla")
            print("[SOLUCIÓN] Aplica migraciones de busqueda primero:")
            print("   python manage.py migrate busqueda")
            return 1
    
    # Paso 2: Aplicar migraciones en orden
    if aplicar_migraciones_ordenadas():
        print("\n" + "=" * 70)
        print("[OK] MIGRACIONES APLICADAS EXITOSAMENTE")
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print("[ERROR] HUBO PROBLEMAS AL APLICAR MIGRACIONES")
        print("=" * 70)
        print("\n[SOLUCIÓN MANUAL]")
        print("   1. Aplica migraciones de busqueda:")
        print("      python manage.py migrate busqueda")
        print("\n   2. Luego aplica migraciones de metricas:")
        print("      python manage.py migrate metricas")
        print("\n   3. Finalmente aplica todas las demás:")
        print("      python manage.py migrate")
        return 1

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
