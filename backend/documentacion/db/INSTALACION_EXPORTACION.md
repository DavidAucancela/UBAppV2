# Guía de Instalación - Funcionalidad de Exportación

## Pasos de Instalación

### 1. Instalar Dependencias

Desde el directorio `backend`, ejecute:

```bash
cd backend
pip install -r requirements.txt
```

O instale manualmente las librerías necesarias:

```bash
pip install openpyxl==3.1.2 reportlab==4.0.9 Pillow==10.2.0
```

### 2. Verificar Instalación

```bash
python -c "import openpyxl; import reportlab; from reportlab.lib.pagesizes import letter; print('✅ Todas las dependencias instaladas correctamente')"
```

### 3. Aplicar Migraciones (si es necesario)

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Reiniciar el Servidor

```bash
python manage.py runserver
```

## Verificación de Funcionamiento

### Probar Endpoints

#### 1. Obtener Token JWT
```bash
curl -X POST http://localhost:8000/api/usuarios/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

#### 2. Exportar a Excel (ejemplo)
```bash
curl -X GET "http://localhost:8000/api/envios/envios/exportar/?formato=excel" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -o test_envios.xlsx
```

#### 3. Verificar que el archivo se descargó
```bash
ls -lh test_envios.xlsx
```

Si el archivo existe y tiene contenido, ¡la instalación fue exitosa! ✅

## Solución de Problemas

### Error: "No module named 'openpyxl'"
```bash
pip install --upgrade openpyxl
```

### Error: "No module named 'reportlab'"
```bash
pip install --upgrade reportlab Pillow
```

### Error con permisos en Windows
Ejecutar PowerShell como Administrador y usar:
```powershell
python -m pip install openpyxl reportlab Pillow
```

### Entorno Virtual
Si está usando un entorno virtual, asegúrese de activarlo primero:

**Linux/Mac:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

## Confirmación Final

Una vez instalado todo, debería ver estos endpoints disponibles:

- ✅ `GET /api/envios/envios/exportar/` - Exportación masiva
- ✅ `GET /api/envios/envios/{id}/comprobante/` - Comprobante individual

¡Listo para usar! 🚀


