"""
Script para verificar y mostrar información sobre el archivo .env
"""
import os

def check_env_file():
    env_path = '.env'
    
    print("=" * 60)
    print("VERIFICACIÓN DEL ARCHIVO .env")
    print("=" * 60)
    
    if not os.path.exists(env_path):
        print("❌ El archivo .env no existe")
        return
    
    print(f"✅ Archivo encontrado: {os.path.abspath(env_path)}")
    print(f"   Tamaño: {os.path.getsize(env_path)} bytes")
    
    # Intentar leer con diferentes codificaciones
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    
    print("\n🔍 Intentando leer con diferentes codificaciones:")
    for encoding in encodings:
        try:
            with open(env_path, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"   ✅ {encoding}: OK")
            
            if encoding == 'utf-8':
                print("\n✅ El archivo se puede leer en UTF-8")
        except Exception as e:
            print(f"   ❌ {encoding}: {type(e).__name__}")
    
    # Mostrar el contenido (sin mostrar contraseñas completas)
    print("\n📄 Contenido del archivo (contraseñas ocultas):")
    print("-" * 60)
    
    try:
        # Intentar primero con UTF-8
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            used_encoding = 'utf-8'
        except UnicodeDecodeError:
            # Si falla, usar latin-1
            with open(env_path, 'r', encoding='latin-1') as f:
                lines = f.readlines()
            used_encoding = 'latin-1'
            print(f"⚠️ Se leyó con {used_encoding} (NO UTF-8)")
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if 'PASSWORD' in line.upper():
                    key = line.split('=')[0]
                    print(f"{key}=***OCULTA***")
                else:
                    print(line)
            elif line:
                print(line)
                
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
    
    print("-" * 60)
    
    # Sugerencias
    print("\n💡 SOLUCIONES:")
    print("1. Si tu contraseña tiene caracteres especiales (ñ, á, é, etc.):")
    print("   - Abre el archivo .env con Notepad++, VS Code o Cursor")
    print("   - Guárdalo con codificación UTF-8 (sin BOM)")
    print()
    print("2. Alternativa: Cambia la contraseña de PostgreSQL:")
    print("   - Usa solo letras, números y símbolos básicos (sin acentos)")
    print("   - Ejemplo: Admin123!, Pass#2024, etc.")
    print()
    print("3. Verifica que la contraseña NO tenga espacios al inicio o final")
    print()
    print("=" * 60)

if __name__ == "__main__":
    check_env_file()

