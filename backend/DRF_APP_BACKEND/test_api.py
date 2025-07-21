#!/usr/bin/env python3
"""
Script de prueba para verificar la API del sistema de gestión de archivos
"""

import requests
import json
import os

# Configuración
BASE_URL = "http://localhost:8000"
ADMIN_URL = f"{BASE_URL}/admin/"
API_BASE = f"{BASE_URL}/api"

def test_admin_access():
    """Prueba acceso al admin"""
    print("🔍 Probando acceso al admin...")
    try:
        response = requests.get(ADMIN_URL)
        if response.status_code == 200:
            print("✅ Admin accesible")
            return True
        else:
            print(f"❌ Error al acceder al admin: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_api_endpoints():
    """Prueba endpoints de la API"""
    print("\n🔍 Probando endpoints de la API...")
    
    endpoints = [
        "/api/usuarios/",
        "/api/archivos/archivos/",
        "/api/archivos/categorias/",
        "/api/busqueda/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code in [200, 401, 403]:  # 401/403 es normal sin autenticación
                print(f"✅ {endpoint} - Status: {response.status_code}")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def test_media_directory():
    """Prueba que el directorio media existe"""
    print("\n🔍 Verificando directorio media...")
    media_dir = os.path.join(os.path.dirname(__file__), 'media')
    if os.path.exists(media_dir):
        print("✅ Directorio media existe")
    else:
        print("❌ Directorio media no existe")
        try:
            os.makedirs(media_dir)
            print("✅ Directorio media creado")
        except Exception as e:
            print(f"❌ Error creando directorio media: {e}")

def test_database():
    """Prueba conexión a la base de datos"""
    print("\n🔍 Verificando base de datos...")
    db_file = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    if os.path.exists(db_file):
        size = os.path.getsize(db_file)
        print(f"✅ Base de datos existe ({size} bytes)")
    else:
        print("❌ Base de datos no existe")

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del sistema de gestión de archivos...")
    print("=" * 60)
    
    # Verificar que el servidor esté corriendo
    if not test_admin_access():
        print("\n❌ El servidor no está corriendo. Ejecuta:")
        print("   python manage.py runserver")
        return
    
    # Probar endpoints
    test_api_endpoints()
    
    # Verificar directorios
    test_media_directory()
    test_database()
    
    print("\n" + "=" * 60)
    print("📋 Resumen de pruebas completado")
    print("\n🎯 Para usar el sistema:")
    print("1. Accede al admin: http://localhost:8000/admin/")
    print("2. Inicia sesión con tu superusuario")
    print("3. Explora la API en: http://localhost:8000/api/")
    print("\n📚 Documentación completa en README.md")

if __name__ == "__main__":
    main() 