"""
Menú interactivo para gestionar la base de datos
"""
import os
import sys
import subprocess

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_banner():
    print("=" * 70)
    print("  🗄️  MENÚ DE GESTIÓN DE BASE DE DATOS  🗄️")
    print("=" * 70)
    print()

def mostrar_menu():
    print("📋 OPCIONES DISPONIBLES:")
    print()
    print("  1. 🧪 Probar conexión actual")
    print("  2. 🔄 Cambiar configuración de base de datos")
    print("  3. 🔍 Diagnosticar problemas de PostgreSQL")
    print("  4. 📄 Verificar archivo .env")
    print("  5. 📖 Ver documentación")
    print("  6. 🚀 Aplicar migraciones")
    print("  7. 👤 Crear superusuario")
    print("  8. ⚙️  Ejecutar comandos de Django")
    print("  9. ❌ Salir")
    print()

def ejecutar_script(script, descripcion):
    print(f"\n{'='*70}")
    print(f"  {descripcion}")
    print(f"{'='*70}\n")
    try:
        resultado = subprocess.run(['python', script], check=False)
        return resultado.returncode == 0
    except Exception as e:
        print(f"❌ Error al ejecutar {script}: {e}")
        return False

def menu_django():
    while True:
        print("\n" + "="*70)
        print("  ⚙️  COMANDOS DE DJANGO")
        print("="*70)
        print()
        print("  1. python manage.py check")
        print("  2. python manage.py showmigrations")
        print("  3. python manage.py migrate")
        print("  4. python manage.py createsuperuser")
        print("  5. python manage.py runserver")
        print("  6. python manage.py shell")
        print("  7. Volver al menú principal")
        print()
        
        opcion = input("Selecciona una opción [1-7]: ").strip()
        
        comandos = {
            '1': 'check',
            '2': 'showmigrations',
            '3': 'migrate',
            '4': 'createsuperuser',
            '5': 'runserver',
            '6': 'shell',
        }
        
        if opcion in comandos:
            print(f"\nEjecutando: python manage.py {comandos[opcion]}\n")
            try:
                subprocess.run(['python', 'manage.py', comandos[opcion]])
            except KeyboardInterrupt:
                print("\n\n⚠️ Comando interrumpido")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            if opcion in ['5', '6']:  # runserver o shell
                input("\n\nPresiona Enter para continuar...")
        elif opcion == '7':
            break
        else:
            print("❌ Opción inválida")

def ver_documentacion():
    print("\n" + "="*70)
    print("  📖 DOCUMENTACIÓN DISPONIBLE")
    print("="*70)
    print()
    print("  1. COMO_PROBAR_DB.md - Guía completa de pruebas")
    print("  2. SOLUCION_PASSWORD.md - Solución al problema de contraseña")
    print("  3. ENV_TEMPLATE.md - Plantilla de configuración .env")
    print("  4. Volver")
    print()
    
    opcion = input("Selecciona un documento [1-4]: ").strip()
    
    archivos = {
        '1': 'COMO_PROBAR_DB.md',
        '2': 'SOLUCION_PASSWORD.md',
        '3': 'ENV_TEMPLATE.md',
    }
    
    if opcion in archivos:
        archivo = archivos[opcion]
        if os.path.exists(archivo):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                print("\n" + "="*70)
                print(contenido)
                print("="*70)
            except Exception as e:
                print(f"❌ Error al leer {archivo}: {e}")
        else:
            print(f"❌ Archivo {archivo} no encontrado")
        
        input("\n\nPresiona Enter para continuar...")

def main():
    while True:
        limpiar_pantalla()
        mostrar_banner()
        mostrar_menu()
        
        opcion = input("Selecciona una opción [1-9]: ").strip()
        
        if opcion == '1':
            ejecutar_script('test_db_connection.py', '🧪 PROBANDO CONEXIÓN A LA BASE DE DATOS')
            input("\n\nPresiona Enter para continuar...")
            
        elif opcion == '2':
            ejecutar_script('cambiar_db.py', '🔄 CAMBIAR CONFIGURACIÓN DE BASE DE DATOS')
            input("\n\nPresiona Enter para continuar...")
            
        elif opcion == '3':
            ejecutar_script('test_postgres_direct.py', '🔍 DIAGNÓSTICO DE POSTGRESQL')
            input("\n\nPresiona Enter para continuar...")
            
        elif opcion == '4':
            ejecutar_script('fix_env_encoding.py', '📄 VERIFICANDO ARCHIVO .env')
            input("\n\nPresiona Enter para continuar...")
            
        elif opcion == '5':
            ver_documentacion()
            
        elif opcion == '6':
            print("\n🚀 Aplicando migraciones...")
            try:
                subprocess.run(['python', 'manage.py', 'migrate'])
            except Exception as e:
                print(f"❌ Error: {e}")
            input("\n\nPresiona Enter para continuar...")
            
        elif opcion == '7':
            print("\n👤 Creando superusuario...")
            try:
                subprocess.run(['python', 'manage.py', 'createsuperuser'])
            except Exception as e:
                print(f"❌ Error: {e}")
            input("\n\nPresiona Enter para continuar...")
            
        elif opcion == '8':
            menu_django()
            
        elif opcion == '9':
            print("\n👋 ¡Hasta luego!\n")
            sys.exit(0)
            
        else:
            print("\n❌ Opción inválida")
            input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

