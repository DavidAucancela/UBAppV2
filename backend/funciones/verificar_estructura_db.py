"""
Script para verificar la estructura de la base de datos
Especialmente útil para verificar si las columnas first_name y last_name existen
"""
import sys
import os
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def verificar_estructura_usuarios():
    """Verifica la estructura de la tabla usuarios"""
    print("=" * 70)
    print("VERIFICACIÓN DE ESTRUCTURA DE BASE DE DATOS")
    print("=" * 70)
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
        import django
        django.setup()
        
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Verificar si la tabla existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'usuarios'
                );
            """)
            tabla_existe = cursor.fetchone()[0]
            
            if not tabla_existe:
                print("\n[ERROR] La tabla 'usuarios' no existe")
                return False
            
            print("\n[OK] La tabla 'usuarios' existe")
            
            # Obtener todas las columnas
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'usuarios'
                ORDER BY ordinal_position;
            """)
            
            columnas = cursor.fetchall()
            
            print("\n[INFO] Columnas en la tabla 'usuarios':")
            print("-" * 70)
            print(f"{'Columna':<25} {'Tipo':<20} {'Nullable':<10} {'Default'}")
            print("-" * 70)
            
            tiene_first_name = False
            tiene_last_name = False
            tiene_email = False
            
            for columna in columnas:
                nombre, tipo, nullable, default = columna
                nullable_str = "Sí" if nullable == "YES" else "No"
                default_str = str(default) if default else "None"
                print(f"{nombre:<25} {tipo:<20} {nullable_str:<10} {default_str}")
                
                if nombre == 'first_name':
                    tiene_first_name = True
                elif nombre == 'last_name':
                    tiene_last_name = True
                elif nombre == 'email':
                    tiene_email = True
            
            print("-" * 70)
            
            # Verificar problemas
            problemas = []
            
            if tiene_first_name:
                problemas.append("La columna 'first_name' todavía existe (debería eliminarse)")
            if tiene_last_name:
                problemas.append("La columna 'last_name' todavía existe (debería eliminarse)")
            if tiene_email:
                problemas.append("La columna 'email' todavía existe (debería eliminarse)")
            
            if problemas:
                print("\n[ADVERTENCIA] Se encontraron problemas:")
                for problema in problemas:
                    print(f"   - {problema}")
                
                print("\n[SOLUCIÓN]")
                print("   1. Ejecuta: python manage.py migrate usuarios")
                print("   2. O ejecuta el script: python funciones/aplicar_migracion_first_name.py")
                return False
            else:
                print("\n[OK] La estructura de la tabla está correcta")
                print("   - No hay columnas first_name, last_name o email")
            
            # Verificar datos
            cursor.execute("SELECT COUNT(*) FROM usuarios;")
            total_usuarios = cursor.fetchone()[0]
            
            print(f"\n[INFO] Total de usuarios en la base de datos: {total_usuarios}")
            
            if total_usuarios > 0:
                cursor.execute("""
                    SELECT id, username, nombre, correo, cedula, rol
                    FROM usuarios
                    LIMIT 5;
                """)
                usuarios = cursor.fetchall()
                
                print("\n[INFO] Primeros usuarios:")
                print("-" * 70)
                print(f"{'ID':<5} {'Username':<15} {'Nombre':<20} {'Correo':<25} {'Cédula':<12} {'Rol'}")
                print("-" * 70)
                for usuario in usuarios:
                    id, username, nombre, correo, cedula, rol = usuario
                    print(f"{id:<5} {str(username):<15} {str(nombre):<20} {str(correo):<25} {str(cedula):<12} {rol}")
                print("-" * 70)
            
            return True
            
    except Exception as e:
        print(f"\n[ERROR] Error al verificar la base de datos: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    try:
        exito = verificar_estructura_usuarios()
        return 0 if exito else 1
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
