"""
Migración personalizada para renombrar tablas de Django
a los nombres personalizados en la BD.

Esta migración debe ejecutarse DESPUÉS de que Django cree las tablas
con sus nombres originales, y las renombra a los nombres personalizados.
"""
from django.db import migrations


def renombrar_tablas(apps, schema_editor):
    """Renombra las tablas de Django a los nombres personalizados"""
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        # Renombrar tablas si existen con sus nombres originales
        renombrados = [
            ('django_admin_log', 'logs'),
            ('django_content_type', 'tipo_contenido'),
            ('django_session', 'sesiones_key'),
        ]
        
        for nombre_original, nombre_nuevo in renombrados:
            try:
                # Verificar si la tabla original existe
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, [nombre_original])
                
                existe_original = cursor.fetchone()[0]
                
                # Verificar si la tabla nueva ya existe
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, [nombre_nuevo])
                
                existe_nuevo = cursor.fetchone()[0]
                
                if existe_original and not existe_nuevo:
                    # Renombrar la tabla
                    cursor.execute(f'ALTER TABLE "{nombre_original}" RENAME TO "{nombre_nuevo}";')
                    print(f"✅ Tabla {nombre_original} renombrada a {nombre_nuevo}")
                elif existe_nuevo:
                    print(f"ℹ️  Tabla {nombre_nuevo} ya existe, omitiendo renombrado")
                else:
                    print(f"⚠️  Tabla {nombre_original} no existe, omitiendo renombrado")
                    
            except Exception as e:
                print(f"⚠️  Error al renombrar {nombre_original}: {str(e)}")


def revertir_renombrado(apps, schema_editor):
    """Revierte el renombrado de las tablas"""
    db_alias = schema_editor.connection.alias
    
    with schema_editor.connection.cursor() as cursor:
        # Revertir renombrados
        renombrados = [
            ('logs', 'django_admin_log'),
            ('tipo_contenido', 'django_content_type'),
            ('sesiones_key', 'django_session'),
        ]
        
        for nombre_nuevo, nombre_original in renombrados:
            try:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, [nombre_nuevo])
                
                existe_nuevo = cursor.fetchone()[0]
                
                if existe_nuevo:
                    cursor.execute(f'ALTER TABLE "{nombre_nuevo}" RENAME TO "{nombre_original}";')
                    print(f"✅ Tabla {nombre_nuevo} revertida a {nombre_original}")
            except Exception as e:
                print(f"⚠️  Error al revertir {nombre_nuevo}: {str(e)}")


class Migration(migrations.Migration):
    """
    Migración para renombrar tablas de Django.
    
    IMPORTANTE: Esta migración debe ejecutarse DESPUÉS de las migraciones
    iniciales de Django (admin, contenttypes, sessions).
    """
    
    dependencies = [
        ('admin', '0001_initial'),  # Después de crear django_admin_log
        ('contenttypes', '0001_initial'),  # Después de crear django_content_type
        ('sessions', '0001_initial'),  # Después de crear django_session
    ]

    operations = [
        migrations.RunPython(renombrar_tablas, revertir_renombrado),
    ]


























