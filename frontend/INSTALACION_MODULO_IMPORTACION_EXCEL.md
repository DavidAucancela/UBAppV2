# 🚀 Guía de Instalación Rápida - Módulo de Importación de Excel

Esta guía le ayudará a poner en funcionamiento el módulo de importación de Excel en pocos minutos.

---

## ✅ Prerrequisitos

- Python 3.11+ y Django 5.2+
- Node.js 18+ y Angular 17+
- PostgreSQL o base de datos compatible
- Dependencias del proyecto instaladas

---

## 📦 Paso 1: Backend (Django)

### 1.1 Verificar Dependencias

Las siguientes librerías ya deberían estar en `backend/requirements.txt`:

```txt
openpyxl==3.1.2
pandas
numpy==1.26.4
```

Si no están instaladas:

```bash
cd backend
pip install openpyxl pandas numpy
```

### 1.2 Crear Migraciones

```bash
cd backend
python manage.py makemigrations archivos --name importacion_excel
```

Esto creará un archivo de migración que incluirá el modelo `ImportacionExcel`.

### 1.3 Aplicar Migraciones

```bash
python manage.py migrate
```

### 1.4 Verificar Instalación

Inicie el servidor de desarrollo:

```bash
python manage.py runserver
```

Verifique que el endpoint esté disponible:
```
http://localhost:8000/api/archivos/importaciones-excel/
```

---

## 🎨 Paso 2: Frontend (Angular)

### 2.1 Verificar Dependencias

La librería `xlsx` ya debería estar en `frontend/package.json`:

```json
"xlsx": "^0.18.5"
```

Si no está instalada:

```bash
cd frontend
npm install xlsx
```

### 2.2 Compilar el Proyecto

```bash
npm run build
```

O para desarrollo:

```bash
npm start
```

### 2.3 Verificar Instalación

Abra el navegador y navegue a:
```
http://localhost:4200/importacion-excel
```

---

## 🧪 Paso 3: Pruebas

### 3.1 Descargar Plantilla de Ejemplo

1. Acceda al módulo en `/importacion-excel`
2. Haga clic en "📥 Descargar Plantilla de Ejemplo"
3. Se descargará un archivo `plantilla_importacion_envios.xlsx`

### 3.2 Probar Importación

1. Edite la plantilla con datos de prueba
2. Suba el archivo en el módulo
3. Siga los pasos del asistente:
   - Cargar archivo
   - Mapear columnas
   - Validar datos
   - Procesar importación

### 3.3 Verificar en la Base de Datos

```bash
cd backend
python manage.py shell
```

```python
from apps.archivos.models import ImportacionExcel, Envio

# Ver importaciones
ImportacionExcel.objects.all()

# Ver envíos creados
Envio.objects.filter(fecha_creacion__gte='2025-10-20')
```

---

## 🔧 Configuración Adicional (Opcional)

### Ajustar Límite de Tamaño de Archivo

Edite `backend/settings.py`:

```python
# Tamaño máximo de archivo (50 MB por defecto)
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800  # 50 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800
```

### Configurar Almacenamiento de Archivos

Para producción, configure un storage backend como S3:

```python
# settings.py
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'tu-bucket'
AWS_ACCESS_KEY_ID = 'tu-access-key'
AWS_SECRET_ACCESS_KEY = 'tu-secret-key'
```

### Agregar Acceso Rápido en el Dashboard

Edite el componente del dashboard para agregar un botón:

```html
<!-- dashboard.component.html -->
<div class="quick-actions">
  <button routerLink="/importacion-excel" class="btn btn-primary">
    📊 Importar Envíos desde Excel
  </button>
</div>
```

---

## 🎯 Siguientes Pasos

1. **Personalizar campos**: Edite `CAMPOS_DISPONIBLES` en `importacion-excel.model.ts`
2. **Agregar validaciones**: Modifique `ValidadorDatos` en `utils_importacion.py`
3. **Crear reportes personalizados**: Extienda `generar_reporte_errores()`
4. **Integrar con notificaciones**: Agregue envío de emails al completar importación

---

## 📚 Recursos Adicionales

- [README Principal del Módulo](./MODULO_IMPORTACION_EXCEL_README.md)
- [Documentación de la API](http://localhost:8000/api/schema/swagger/)
- [Código fuente del módulo](./backend/apps/archivos/)

---

## ❓ Preguntas Frecuentes

### ¿Puedo importar archivos CSV?

Actualmente solo se soportan archivos Excel (.xlsx, .xls). Para CSV, puede convertirlos a Excel o extender el módulo para soportar CSV.

### ¿Cómo limito quién puede importar archivos?

El módulo está protegido por roles. Solo usuarios con roles ADMIN, GERENTE y DIGITADOR tienen acceso. Para cambiar esto, edite la configuración de rutas en `app.routes.ts`.

### ¿Los datos se validan antes de guardar?

Sí, hay dos niveles de validación:
1. Validación en el frontend (cliente)
2. Validación en el backend (servidor)

Los datos con errores no se importan a menos que se corrijan.

### ¿Puedo deshacer una importación?

No automáticamente. Se recomienda hacer un backup de la base de datos antes de importaciones grandes. En futuras versiones se puede agregar funcionalidad de rollback.

---

## 🐛 Solución de Problemas Comunes

### Error: "Module 'openpyxl' not found"

```bash
pip install openpyxl
```

### Error: "Cannot find module 'xlsx'"

```bash
cd frontend
npm install xlsx
```

### Error: "Permission denied" al subir archivos

Verifique los permisos de la carpeta `media/`:

```bash
chmod -R 755 backend/media/
```

### El mapeo automático no funciona

Asegúrese de que los nombres de las columnas en Excel coincidan con los nombres esperados (HAWB, Peso Total, etc.) o utilice el mapeo manual.

---

## ✅ Checklist de Instalación

- [ ] Dependencias de Python instaladas (openpyxl, pandas)
- [ ] Migraciones creadas y aplicadas
- [ ] Dependencias de Node.js instaladas (xlsx)
- [ ] Servidor backend funcionando
- [ ] Servidor frontend funcionando
- [ ] Ruta `/importacion-excel` accesible
- [ ] Plantilla de ejemplo descargable
- [ ] Importación de prueba exitosa
- [ ] Datos visibles en la base de datos

---

## 🎉 ¡Listo!

El módulo de importación de Excel está completamente instalado y funcionando.

Para más información, consulte la [documentación completa](./MODULO_IMPORTACION_EXCEL_README.md).

---

**Desarrollado como parte del Trabajo de Titulación - Universal Box**

📧 Soporte: [correo de soporte]
🌐 Web: [sitio web del proyecto]


