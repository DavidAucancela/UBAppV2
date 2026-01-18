"""
Script para diagnosticar problemas con migraciones
Verifica el estado de las migraciones y las tablas en la base de datos
"""
import sys
import os
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def verificar_migraciones_aplicadas():
    """Verifica qué migraciones están aplicadas"""
    print("=" * 70)
    print("ESTADO DE MIGRACIONES")
    print("=" * 70)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        import django
        django.setup()
        
        from django.db import connection
        from django.apps import apps
        
        with connection.cursor() as cursor:
            # Verificar tabla de migraciones
            cursor.execute("""
                SELECT app, name, applied
                FROM django_migrations
                ORDER BY app, id;
            """)
            
            migraciones = cursor.fetchall()
            
            print("\n[INFO] Migraciones aplicadas:")
            print("-" * 70)
            print(f"{'App':<20} {'Migración':<40} {'Aplicada'}")
            print("-" * 70)
            
            apps_migraciones = {}
            for app, name, applied in migraciones:
                if app not in apps_migraciones:
                    apps_migraciones[app] = []
                apps_migraciones[app].append((name, applied))
                estado = "✅" if applied else "❌"
                print(f"{app:<20} {name:<40} {estado}")
            
            print("-" * 70)
            
            # Verificar migraciones de busqueda
            print("\n[INFO] Migraciones de 'busqueda':")
            if 'busqueda' in apps_migraciones:
                for name, applied in apps_migraciones['busqueda']:
                    estado = "✅ Aplicada" if applied else "❌ No aplicada"
                    print(f"   {name}: {estado}")
            else:
                print("   [ADVERTENCIA] No se encontraron migraciones de 'busqueda'")
            
            # Verificar migraciones de metricas
            print("\n[INFO] Migraciones de 'metricas':")
            if 'metricas' in apps_migraciones:
                for name, applied in apps_migraciones['metricas']:
                    estado = "✅ Aplicada" if applied else "❌ No aplicada"
                    print(f"   {name}: {estado}")
            else:
                print("   [ADVERTENCIA] No se encontraron migraciones de 'metricas'")
            
            return apps_migraciones
            
    except Exception as e:
        print(f"\n[ERROR] Error al verificar migraciones: {e}")
        import traceback
        traceback.print_exc()
        return None

def verificar_tablas():
    """Verifica qué tablas existen en la base de datos"""
    print("\n" + "=" * 70)
    print("TABLAS EN LA BASE DE DATOS")
    print("=" * 70)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        import django
        django.setup()
        
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Obtener todas las tablas
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            
            tablas = [row[0] for row in cursor.fetchall()]
            
            print(f"\n[INFO] Total de tablas: {len(tablas)}")
            print("\n[INFO] Tablas relacionadas con busqueda y metricas:")
            print("-" * 70)
            
            tablas_busqueda = [t for t in tablas if 'busqueda' in t.lower() or 'embedding' in t.lower()]
            tablas_metricas = [t for t in tablas if 'metrica' in t.lower() or 'prueba' in t.lower()]
            
            print("\nTablas de búsqueda:")
            if tablas_busqueda:
                for tabla in tablas_busqueda:
                    print(f"   ✅ {tabla}")
            else:
                print("   ❌ No se encontraron tablas de búsqueda")
            
            print("\nTablas de métricas:")
            if tablas_metricas:
                for tabla in tablas_metricas:
                    print(f"   ✅ {tabla}")
            else:
                print("   ❌ No se encontraron tablas de métricas")
            
            # Verificar tabla específica
            print("\n[INFO] Verificación de tabla 'embedding_busqueda':")
            if 'embedding_busqueda' in tablas:
                print("   ✅ La tabla 'embedding_busqueda' existe")
                
                # Verificar estructura
                cursor.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = 'embedding_busqueda'
                    ORDER BY ordinal_position;
                """)
                columnas = cursor.fetchall()
                print(f"   [INFO] Columnas: {len(columnas)}")
                for col, tipo in columnas[:5]:  # Mostrar primeras 5
                    print(f"      - {col} ({tipo})")
                if len(columnas) > 5:
                    print(f"      ... y {len(columnas) - 5} más")
            else:
                print("   ❌ La tabla 'embedding_busqueda' NO existe")
                print("   [PROBLEMA] Esta es la causa del error")
            
            return tablas
            
    except Exception as e:
        print(f"\n[ERROR] Error al verificar tablas: {e}")
        import traceback
        traceback.print_exc()
        return None

def sugerir_solucion(tablas, migraciones):
    """Sugiere una solución basada en el diagnóstico"""
    print("\n" + "=" * 70)
    print("DIAGNÓSTICO Y SOLUCIÓN")
    print("=" * 70)
    
    tiene_embedding_busqueda = tablas and 'embedding_busqueda' in tablas
    
    # Verificar migraciones de busqueda
    busqueda_aplicadas = []
    if migraciones and 'busqueda' in migraciones:
        busqueda_aplicadas = [name for name, applied in migraciones['busqueda'] if applied]
    
    # Verificar migraciones de metricas
    metricas_aplicadas = []
    if migraciones and 'metricas' in migraciones:
        metricas_aplicadas = [name for name, applied in migraciones['metricas'] if applied]
    
    print("\n[ANÁLISIS]")
    
    if not tiene_embedding_busqueda:
        print("   ❌ La tabla 'embedding_busqueda' no existe")
        print("   [CAUSA] Las migraciones de 'busqueda' no se han aplicado correctamente")
        
        print("\n[SOLUCIÓN]")
        print("   1. Aplicar migraciones de busqueda primero:")
        print("      python manage.py migrate busqueda")
        print("\n   2. Luego aplicar migraciones de metricas:")
        print("      python manage.py migrate metricas")
        print("\n   3. O aplicar todas las migraciones:")
        print("      python manage.py migrate")
        
    elif '0001_initial' not in metricas_aplicadas:
        print("   ✅ La tabla 'embedding_busqueda' existe")
        print("   ❌ La migración 'metricas.0001_initial' no está aplicada")
        
        print("\n[SOLUCIÓN]")
        print("   1. Aplicar migraciones de metricas:")
        print("      python manage.py migrate metricas")
        print("\n   2. Si falla, verificar dependencias:")
        print("      python manage.py showmigrations metricas")
        
    else:
        print("   ✅ Todo parece estar correcto")
        print("   [INFO] Si aún hay errores, puede ser un problema de dependencias")

def main():
    """Función principal"""
    print("\n" + "=" * 70)
    print("DIAGNÓSTICO DE MIGRACIONES")
    print("=" * 70)
    
    # Verificar migraciones
    migraciones = verificar_migraciones_aplicadas()
    
    # Verificar tablas
    tablas = verificar_tablas()
    
    # Sugerir solución
    if tablas is not None and migraciones is not None:
        sugerir_solucion(tablas, migraciones)
    
    print("\n" + "=" * 70)
    print("[OK] DIAGNÓSTICO COMPLETADO")
    print("=" * 70)
    
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
