"""
Script para exportar datos desde Supabase (incluyendo embeddings)
Ejecuta este script cuando estés en casa conectado a Supabase
"""
import os
import sys
import json
import django
from pathlib import Path

# Configurar Django
# Agregar el directorio padre (backend) al path para encontrar settings.py
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.core import serializers
from django.db import connection
from apps.usuarios.models import Usuario
from apps.archivos.models import Envio, Producto
from apps.busqueda.models import EnvioEmbedding

def crear_directorio_backup():
    """Crea directorio para backups"""
    # El backup está en backend/backup/, no en funciones/backup/
    backend_dir = Path(__file__).parent.parent  # Subir de funciones/ a backend/
    backup_dir = backend_dir / 'backup'
    backup_dir.mkdir(exist_ok=True)
    return backup_dir

def exportar_usuarios(backup_dir):
    """Exporta usuarios (sin relaciones Many-to-Many)"""
    print("\n[INFO] Exportando usuarios...")
    
    usuarios = Usuario.objects.all()
    
    # Exportar usando values() para evitar relaciones Many-to-Many
    usuarios_data = []
    for usuario in usuarios:
        usuario_dict = {
            'model': 'usuarios.usuario',
            'pk': usuario.pk,
            'fields': {
                'username': usuario.username,
                'password': usuario.password,  # Hash de contraseña
                'last_login': usuario.last_login.isoformat() if usuario.last_login else None,
                'is_superuser': usuario.is_superuser,
                'is_staff': usuario.is_staff,
                'is_active': usuario.is_active,
                'date_joined': usuario.date_joined.isoformat() if usuario.date_joined else None,
                'nombre': usuario.nombre,
                'correo': usuario.correo,
                'cedula': usuario.cedula,
                'rol': usuario.rol,
                'telefono': usuario.telefono,
                'fecha_nacimiento': usuario.fecha_nacimiento.isoformat() if usuario.fecha_nacimiento else None,
                'direccion': usuario.direccion,
                'cupo_anual': str(usuario.cupo_anual),
                'provincia': usuario.provincia,
                'canton': usuario.canton,
                'ciudad': usuario.ciudad,
                'fecha_creacion': usuario.fecha_creacion.isoformat() if usuario.fecha_creacion else None,
                'fecha_actualizacion': usuario.fecha_actualizacion.isoformat() if usuario.fecha_actualizacion else None,
            }
        }
        usuarios_data.append(usuario_dict)
    
    data = json.dumps(usuarios_data, indent=2, ensure_ascii=False)
    
    file_path = backup_dir / 'usuarios.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(data)
    
    print(f"[OK] {len(usuarios_data)} usuarios exportados")
    return file_path

def exportar_envios(backup_dir):
    """Exporta envíos"""
    print("\n[INFO] Exportando envíos...")
    
    envios = Envio.objects.all()
    data = serializers.serialize('json', envios, indent=2)
    
    file_path = backup_dir / 'envios.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(data)
    
    print(f"[OK] {envios.count()} envíos exportados")
    return file_path

def exportar_productos(backup_dir):
    """Exporta productos"""
    print("\n[INFO] Exportando productos...")
    
    productos = Producto.objects.all()
    data = serializers.serialize('json', productos, indent=2)
    
    file_path = backup_dir / 'productos.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(data)
    
    print(f"[OK] {productos.count()} productos exportados")
    return file_path

def exportar_embeddings(backup_dir):
    """Exporta embeddings (incluyendo vectores pgvector)"""
    print("\n[INFO] Exportando embeddings...")
    
    # Obtener el total primero (sin cargar todos los datos)
    total_count = EnvioEmbedding.objects.count()
    print(f"[INFO] Total de embeddings a exportar: {total_count}")
    
    if total_count == 0:
        print("[INFO] No hay embeddings para exportar")
        file_path = backup_dir / 'embeddings.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        return file_path
    
    # Aumentar timeout de statement para consultas largas
    from django.db import connection
    with connection.cursor() as cursor:
        # Aumentar statement_timeout a 10 minutos (600000 ms)
        cursor.execute("SET statement_timeout = 600000;")
    
    # Exportar datos sin los vectores (Django serializer no soporta vector)
    # Procesar en lotes para evitar timeout y problemas de memoria
    data_list = []
    batch_size = 1000  # Procesar 1000 a la vez
    processed = 0
    
    print(f"[INFO] Procesando en lotes de {batch_size}...")
    
    # Usar iterator() para procesar en lotes sin cargar todo en memoria
    embeddings = EnvioEmbedding.objects.all().iterator(chunk_size=batch_size)
    
    try:
        for emb in embeddings:
            try:
                data_list.append({
                    'id': emb.id,
                    'envio_id': emb.envio_id,
                    'texto_indexado': emb.texto_indexado,
                    'modelo_usado': emb.modelo_usado,
                    'cosine_similarity_avg': float(emb.cosine_similarity_avg),
                    'fecha_generacion': emb.fecha_generacion.isoformat() if emb.fecha_generacion else None,
                })
                processed += 1
                
                # Mostrar progreso cada 1000 registros
                if processed % 1000 == 0:
                    print(f"[INFO] Procesados: {processed}/{total_count} ({processed*100//total_count}%)")
                    
            except Exception as e:
                print(f"[ADVERTENCIA] Error al procesar embedding {emb.id}: {e}")
                continue
        
        print(f"[INFO] Procesados: {processed}/{total_count} (100%)")
        
    except Exception as e:
        print(f"[ADVERTENCIA] Error durante el procesamiento: {e}")
        print(f"[INFO] Continuando con {len(data_list)} embeddings procesados...")
    
    # Guardar en archivo
    file_path = backup_dir / 'embeddings.json'
    print(f"[INFO] Guardando {len(data_list)} embeddings en archivo...")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] {len(data_list)} embeddings exportados (sin vectores)")
    
    # Exportar vectores usando pg_dump (más eficiente)
    print("\n[INFO] Intentando exportar vectores con pg_dump...")
    
    try:
        import subprocess
        
        db_config = connection.settings_dict
        dump_file = backup_dir / 'envio_embeddings.pgdump'
        
        cmd = [
            'pg_dump',
            '-h', db_config['HOST'],
            '-p', str(db_config['PORT']),
            '-U', db_config['USER'],
            '-d', db_config['NAME'],
            '-t', 'busqueda_envioembedding',
            '--data-only',  # Solo datos, no estructura
            '-F', 'c',  # Formato custom (comprimido)
            '-f', str(dump_file)
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['PASSWORD']
        
        # Aumentar timeout a 15 minutos para bases de datos grandes
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=900)
        
        if result.returncode == 0:
            print(f"[OK] Vectores exportados a: {dump_file}")
            dump_size = dump_file.stat().st_size / (1024 * 1024)  # MB
            print(f"[INFO] Tamaño del archivo: {dump_size:.2f} MB")
        else:
            error_msg = result.stderr.strip()
            
            # Detectar error de versión
            if 'version mismatch' in error_msg or 'server version' in error_msg:
                print(f"[ADVERTENCIA] Incompatibilidad de versiones de pg_dump:")
                print(f"   {error_msg}")
                print("\n[INFO] Soluciones:")
                print("   1. Los vectores se regenerarán automáticamente al importar")
                print("   2. O instala pg_dump versión 17+ para exportar vectores")
                print("   3. O usa Docker con pg_dump: docker exec postgres_local pg_dump ...")
            else:
                print(f"[ADVERTENCIA] Error al exportar vectores con pg_dump:")
                print(f"   {error_msg}")
                print("[INFO] Los embeddings se regenerarán al importar")
    
    except FileNotFoundError:
        print("[ADVERTENCIA] pg_dump no encontrado en el sistema")
        print("[INFO] Los embeddings se regenerarán automáticamente al importar")
        print("\n[INFO] Nota: Los vectores no son críticos para la exportación.")
        print("      Se pueden regenerar cuando sea necesario usando:")
        print("      python manage.py regenerar_embeddings")
    except subprocess.TimeoutExpired:
        print("[ADVERTENCIA] pg_dump tardó demasiado (timeout de 15 minutos)")
        print("[INFO] Los embeddings se regenerarán al importar")
    except Exception as e:
        print(f"[ADVERTENCIA] Error al exportar vectores: {e}")
        print("[INFO] Los embeddings se regenerarán al importar")
    
    return file_path

def detectar_tipo_base_datos():
    """Detecta si estamos conectados a Supabase o Docker/local"""
    db_config = connection.settings_dict
    host = db_config.get('HOST', '')
    
    # Detectar Supabase
    if 'supabase.co' in str(host) or host.startswith('db.'):
        return 'supabase'
    
    # Detectar Docker/local
    if host in ('localhost', '127.0.0.1', '::1'):
        return 'local'
    
    return 'desconocido'

def main():
    """Función principal"""
    print("=" * 70)
    print("EXPORTAR DATOS DESDE SUPABASE")
    print("=" * 70)
    
    # Verificar conexión y tipo de base de datos
    print("\n[INFO] Verificando conexión...")
    try:
        db_config = connection.settings_dict
        tipo_db = detectar_tipo_base_datos()
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"[OK] Conectado a PostgreSQL: {version[0][:50]}...")
        
        # Verificar que estemos conectados a Supabase
        if tipo_db != 'supabase':
            print(f"\n[ADVERTENCIA] Estás conectado a: {tipo_db.upper()}")
            print("[INFO] Este script está diseñado para exportar desde Supabase")
            print("\n[INFO] Configuración actual:")
            print(f"   Host: {db_config.get('HOST', 'N/A')}")
            print(f"   Port: {db_config.get('PORT', 'N/A')}")
            print(f"   Database: {db_config.get('NAME', 'N/A')}")
            
            if tipo_db == 'local':
                print("\n[SOLUCION]:")
                print("   1. Cambia a Supabase en tu archivo .env:")
                print("      DB_HOST=db.xxxxx.supabase.co")
                print("      DB_PORT=5432")
                print("      DB_NAME=postgres")
                print("   2. O usa el script de importación si quieres trabajar localmente")
                return
            else:
                respuesta = input("\n¿Deseas continuar de todas formas? (s/n): ").strip().lower()
                if respuesta != 's':
                    print("[INFO] Exportación cancelada")
                    return
        else:
            print("[OK] Conectado a Supabase")
            
    except Exception as e:
        print(f"\n[ERROR] No se puede conectar a la base de datos: {e}")
        print("\n[INFO] Asegúrate de:")
        print("   1. Estar conectado a una red que soporte IPv6 (tu casa)")
        print("   2. Tener configurado DB_HOST para Supabase en .env")
        print("   3. Que las credenciales sean correctas")
        print("   4. Que Docker esté corriendo si usas Docker")
        return
    
    # Crear directorio backup
    backup_dir = crear_directorio_backup()
    print(f"\n[INFO] Directorio de backup: {backup_dir}")
    
    # Exportar datos
    archivos_exportados = []
    
    try:
        archivos_exportados.append(exportar_usuarios(backup_dir))
        archivos_exportados.append(exportar_envios(backup_dir))
        archivos_exportados.append(exportar_productos(backup_dir))
        archivos_exportados.append(exportar_embeddings(backup_dir))
        
        # Resumen
        print("\n" + "=" * 70)
        print("[OK] EXPORTACION COMPLETADA")
        print("=" * 70)
        
        print("\n[INFO] Archivos exportados:")
        for archivo in archivos_exportados:
            if archivo and archivo.exists():
                size_kb = archivo.stat().st_size / 1024
                print(f"   - {archivo.name} ({size_kb:.1f} KB)")
        
        print("\n[INFO] Próximos pasos:")
        print("   1. Estos archivos están en: backend/backup/")
        print("   2. Cuando estés en otra red, cambia a Docker/local:")
        print("      - Ejecuta: python funciones/setup_docker_postgres_auto.py")
        print("      - O cambia .env: DB_HOST=localhost, DB_PORT=5435")
        print("   3. Luego ejecuta: python funciones/importar_datos_local.py")
        print("   4. Los datos se importarán a tu base de datos Docker/local")
        
    except Exception as e:
        print(f"\n[ERROR] Error durante la exportación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[ADVERTENCIA] Exportación interrumpida")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

