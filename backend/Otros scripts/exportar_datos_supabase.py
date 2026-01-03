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
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.core import serializers
from django.db import connection
from apps.usuarios.models import Usuario
from apps.archivos.models import Envio, Producto
from apps.busqueda.models import EnvioEmbedding

def crear_directorio_backup():
    """Crea directorio para backups"""
    backup_dir = Path(__file__).parent / 'backup'
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
    
    embeddings = EnvioEmbedding.objects.all()
    
    # Exportar datos sin los vectores (Django serializer no soporta vector)
    data_list = []
    for emb in embeddings:
        data_list.append({
            'id': emb.id,
            'envio_id': emb.envio_id,
            'texto_indexado': emb.texto_indexado,
            'modelo_usado': emb.modelo_usado,
            'cosine_similarity_avg': float(emb.cosine_similarity_avg),
            'fecha_generacion': emb.fecha_generacion.isoformat() if emb.fecha_generacion else None,
        })
    
    file_path = backup_dir / 'embeddings.json'
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] {len(data_list)} embeddings exportados (sin vectores)")
    
    # Exportar vectores usando pg_dump (más eficiente)
    print("\n[INFO] Exportando vectores con pg_dump...")
    
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
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"[OK] Vectores exportados a: {dump_file}")
        else:
            print(f"[ADVERTENCIA] Error al exportar vectores con pg_dump: {result.stderr}")
            print("[INFO] Los embeddings se regenerarán al importar")
    
    except FileNotFoundError:
        print("[ADVERTENCIA] pg_dump no encontrado")
        print("[INFO] Los embeddings se regenerarán al importar")
    except Exception as e:
        print(f"[ADVERTENCIA] Error al exportar vectores: {e}")
        print("[INFO] Los embeddings se regenerarán al importar")
    
    return file_path

def main():
    """Función principal"""
    print("=" * 70)
    print("EXPORTAR DATOS DESDE SUPABASE")
    print("=" * 70)
    
    # Verificar conexión
    print("\n[INFO] Verificando conexión a Supabase...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"[OK] Conectado a PostgreSQL: {version[0][:50]}...")
    except Exception as e:
        print(f"\n[ERROR] No se puede conectar a la base de datos: {e}")
        print("\n[INFO] Asegúrate de:")
        print("   1. Estar conectado a una red que soporte IPv6 (tu casa)")
        print("   2. Tener configurado DB_HOST para Supabase en .env")
        print("   3. Que las credenciales sean correctas")
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
        print("   2. Cuando estés en otra red, ejecuta:")
        print("      python importar_datos_local.py")
        print("   3. Los datos se importarán a tu base de datos local")
        
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

