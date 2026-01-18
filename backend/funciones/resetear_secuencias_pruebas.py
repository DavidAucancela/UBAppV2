"""
Script para resetear secuencias de PostgreSQL antes de ejecutar pruebas de rendimiento.
Soluciona IntegrityErrors causados por secuencias desincronizadas.
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.db import connection

def resetear_secuencias():
    """Resetea todas las secuencias de las tablas principales"""
    print("="*80)
    print("RESETEO DE SECUENCIAS POSTGRESQL")
    print("="*80)
    
    with connection.cursor() as cursor:
        # 1. Listar todas las secuencias
        cursor.execute("""
            SELECT sequence_schema, sequence_name
            FROM information_schema.sequences
            WHERE sequence_schema = 'public'
            AND (
                sequence_name LIKE '%_id_seq'
                OR sequence_name LIKE 'archivos_%'
                OR sequence_name LIKE 'usuarios_%'
            );
        """)
        
        secuencias = cursor.fetchall()
        print(f"\nEncontradas {len(secuencias)} secuencias:\n")
        
        for schema, secuencia in secuencias:
            print(f"  - {secuencia}")
        
        print("\n" + "-"*80)
        print("Reseteando secuencias...")
        print("-"*80 + "\n")
        
        # 2. Resetear secuencias específicas conocidas
        tablas_config = [
            ('envio', 'archivos_envio_id_seq'),
            ('producto', 'archivos_producto_id_seq'),
            ('usuarios_usuario', 'usuarios_usuario_id_seq'),
            ('tarifa', 'tarifa_id_seq'),
            ('archivo', 'archivo_id_seq'),
        ]
        
        for tabla, secuencia in tablas_config:
            try:
                # Obtener máximo ID
                cursor.execute(f"SELECT MAX(id) FROM {tabla}")
                max_id = cursor.fetchone()[0]
                
                if max_id is None:
                    max_id = 1
                
                # Resetear secuencia
                cursor.execute(f"SELECT setval('{secuencia}', {max_id}, true)")
                
                # Verificar
                cursor.execute(f"SELECT last_value FROM {secuencia}")
                ultimo_valor = cursor.fetchone()[0]
                
                print(f"[OK] {tabla:25} -> {secuencia:35} = {ultimo_valor}")
                
            except Exception as e:
                print(f"[ERROR] {tabla:25} -> Error: {str(e)}")
        
        print("\n" + "="*80)
        print("RESETEO COMPLETADO")
        print("="*80)

if __name__ == '__main__':
    resetear_secuencias()
