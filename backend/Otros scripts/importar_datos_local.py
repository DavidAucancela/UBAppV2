"""
Script para importar datos a base de datos local
Ejecuta este script cuando estés en cualquier red con base de datos local
"""
import os
import sys
import json
import django
from pathlib import Path
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.core import serializers
from django.db import connection, transaction
from apps.usuarios.models import Usuario
from apps.archivos.models import Envio, Producto
from apps.busqueda.models import EnvioEmbedding

def verificar_archivos_backup():
    """Verifica que existan los archivos de backup"""
    backup_dir = Path(__file__).parent / 'backup'
    
    if not backup_dir.exists():
        print("[ERROR] Directorio backup no encontrado")
        print("\n[SOLUCION]:")
        print("   1. Primero debes exportar datos desde Supabase")
        print("   2. Ejecuta (cuando estés en casa):")
        print("      python exportar_datos_supabase.py")
        return False, None
    
    archivos_requeridos = [
        'usuarios.json',
        'envios.json',
        'productos.json',
        'embeddings.json'
    ]
    
    archivos_faltantes = []
    for archivo in archivos_requeridos:
        if not (backup_dir / archivo).exists():
            archivos_faltantes.append(archivo)
    
    if archivos_faltantes:
        print(f"[ERROR] Archivos faltantes: {', '.join(archivos_faltantes)}")
        print("\n[SOLUCION]: Exporta datos desde Supabase primero")
        return False, None
    
    return True, backup_dir

def limpiar_base_datos(skip_confirmation=False):
    """Limpia la base de datos local antes de importar"""
    if not skip_confirmation:
        print("\n[ADVERTENCIA] Se eliminarán todos los datos existentes")
        try:
            respuesta = input("¿Deseas continuar? (s/n): ").strip().lower()
            if respuesta != 's':
                print("[INFO] Importación cancelada")
                return False
        except (EOFError, KeyboardInterrupt):
            print("\n[INFO] Importación cancelada (sin confirmación)")
            return False
    
    print("\n[INFO] Limpiando base de datos...")
    
    try:
        with transaction.atomic():
            # Eliminar en orden (respetando foreign keys)
            try:
                EnvioEmbedding.objects.all().delete()
            except Exception as e:
                print(f"[ADVERTENCIA] Error al eliminar embeddings: {e}")
            
            try:
                Producto.objects.all().delete()
            except Exception as e:
                print(f"[ADVERTENCIA] Error al eliminar productos: {e}")
            
            try:
                Envio.objects.all().delete()
            except Exception as e:
                print(f"[ADVERTENCIA] Error al eliminar envíos: {e}")
            
            # No eliminar usuarios admin, solo compradores/digitadores
            try:
                Usuario.objects.filter(rol__in=[3, 4]).delete()
            except Exception as e:
                print(f"[ADVERTENCIA] Error al eliminar usuarios: {e}")
        
        print("[OK] Base de datos limpiada")
        return True
    except Exception as e:
        print(f"[ERROR] Error al limpiar base de datos: {e}")
        # Continuar de todas formas si es solo un error de tabla inexistente
        if 'does not exist' in str(e):
            print("[INFO] Continuando con la importación...")
            return True
        return False

def importar_usuarios(backup_dir):
    """Importa usuarios"""
    print("\n[INFO] Importando usuarios...")
    
    file_path = backup_dir / 'usuarios.json'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
    
    count = 0
    for obj in serializers.deserialize('json', data):
        try:
            # Verificar si ya existe
            if not Usuario.objects.filter(username=obj.object.username).exists():
                obj.save()
                count += 1
        except Exception as e:
            print(f"[ADVERTENCIA] Error al importar usuario {obj.object.username}: {e}")
    
    print(f"[OK] {count} usuarios importados")

def importar_envios(backup_dir):
    """Importa envíos"""
    print("\n[INFO] Importando envíos...")
    
    file_path = backup_dir / 'envios.json'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
    
    for obj in serializers.deserialize('json', data):
        obj.save()
    
    count = Envio.objects.count()
    print(f"[OK] {count} envíos importados")

def importar_productos(backup_dir):
    """Importa productos"""
    print("\n[INFO] Importando productos...")
    
    file_path = backup_dir / 'productos.json'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
    
    for obj in serializers.deserialize('json', data):
        obj.save()
    
    count = Producto.objects.count()
    print(f"[OK] {count} productos importados")

def importar_embeddings(backup_dir):
    """Importa embeddings"""
    print("\n[INFO] Importando embeddings...")
    
    # Intentar restaurar desde pg_dump primero
    dump_file = backup_dir / 'envio_embeddings.pgdump'
    
    if dump_file.exists():
        print("[INFO] Intentando restaurar vectores desde pg_dump...")
        
        try:
            import subprocess
            
            db_config = connection.settings_dict
            
            cmd = [
                'pg_restore',
                '-h', db_config['HOST'],
                '-p', str(db_config['PORT']),
                '-U', db_config['USER'],
                '-d', db_config['NAME'],
                '--clean',
                '--if-exists',
                '-t', 'busqueda_envioembedding',
                str(dump_file)
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['PASSWORD']
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("[OK] Vectores restaurados desde pg_dump")
                count = EnvioEmbedding.objects.count()
                print(f"[OK] {count} embeddings importados")
                return
            else:
                print(f"[ADVERTENCIA] Error al restaurar vectores: {result.stderr}")
        
        except FileNotFoundError:
            print("[INFO] pg_restore no encontrado")
        except Exception as e:
            print(f"[ADVERTENCIA] Error al restaurar vectores: {e}")
    
    # Si no funciona pg_dump, importar sin vectores
    print("[INFO] Importando embeddings sin vectores...")
    print("[INFO] Los vectores se regenerarán automáticamente cuando sea necesario")
    
    file_path = backup_dir / 'embeddings.json'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    count = 0
    for item in data:
        try:
            # Crear embedding sin vector (se regenerará después)
            EnvioEmbedding.objects.create(
                envio_id=item['envio_id'],
                texto_indexado=item.get('texto_indexado', ''),
                modelo_usado=item.get('modelo_usado', 'text-embedding-3-small'),
                cosine_similarity_avg=item.get('cosine_similarity_avg', 0.0),
            )
            count += 1
        except Exception as e:
            print(f"[ADVERTENCIA] Error al importar embedding {item.get('id', 'unknown')}: {e}")
    
    print(f"[OK] {count} embeddings importados (sin vectores)")
    print("[INFO] Para regenerar vectores, ejecuta:")
    print("   python manage.py regenerar_embeddings")

def main():
    """Función principal"""
    print("=" * 70)
    print("IMPORTAR DATOS A BASE DE DATOS LOCAL")
    print("=" * 70)
    
    # Verificar archivos
    archivos_ok, backup_dir = verificar_archivos_backup()
    if not archivos_ok:
        return
    
    # Verificar conexión
    print("\n[INFO] Verificando conexión a base de datos local...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"[OK] Conectado a: {version[0][:50]}...")
            
            # Verificar pgvector
            cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
            if cursor.fetchone():
                print("[OK] pgvector disponible")
            else:
                print("[ADVERTENCIA] pgvector no encontrado")
                print("[INFO] Los embeddings se importarán sin vectores")
    except Exception as e:
        print(f"\n[ERROR] No se puede conectar a la base de datos: {e}")
        print("\n[INFO] Asegúrate de:")
        print("   1. Tener PostgreSQL local corriendo (o Docker)")
        print("   2. Tener configurado DB_HOST=localhost en .env")
        print("   3. Ejecutar migraciones: python manage.py migrate")
        return
    
    # Limpiar base de datos
    if not limpiar_base_datos():
        return
    
    # Importar datos
    try:
        with transaction.atomic():
            importar_usuarios(backup_dir)
            importar_envios(backup_dir)
            importar_productos(backup_dir)
        
        # Embeddings fuera de transacción (pueden tardar)
        importar_embeddings(backup_dir)
        
        # Resumen
        print("\n" + "=" * 70)
        print("[OK] IMPORTACION COMPLETADA")
        print("=" * 70)
        
        print("\n[INFO] Resumen de datos importados:")
        print(f"   - Usuarios: {Usuario.objects.count()}")
        print(f"   - Envíos: {Envio.objects.count()}")
        print(f"   - Productos: {Producto.objects.count()}")
        print(f"   - Embeddings: {EnvioEmbedding.objects.count()}")
        
        print("\n[INFO] Próximos pasos:")
        print("   1. Inicia Django: python manage.py runserver")
        print("   2. Ya puedes trabajar con datos locales")
        print("   3. Cuando vuelvas a casa, sincroniza:")
        print("      python sincronizar_bases_datos.py")
        
    except Exception as e:
        print(f"\n[ERROR] Error durante la importación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[ADVERTENCIA] Importación interrumpida")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

