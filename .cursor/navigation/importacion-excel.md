# 📊 Módulo de Importación desde Excel

## 📍 Ubicación
- **Frontend:** `frontend/src/app/components/importacion-excel/`
- **Backend:** `backend/apps/archivos/views.py` (ImportacionExcelViewSet)
- **Ruta:** `/importacion-excel`

## 🎯 Funcionalidad
Carga masiva de envíos desde archivos Excel con validación previa, preview de datos y procesamiento controlado.

## 📁 Estructura de Archivos

### Frontend
```
importacion-excel/
├── importacion-excel.component.ts
├── importacion-excel.component.html
└── importacion-excel.component.css
```

### Backend
```
archivos/
├── views.py               # ImportacionExcelViewSet
├── serializers.py         # ImportacionExcelSerializer, PreviewExcelSerializer
└── models.py              # Modelo ImportacionExcel (si existe)
```

## 🔑 Componentes Clave

### 1. Carga de Archivo
- Selección de archivo Excel (.xlsx, .xls)
- Validación de formato
- Lectura de datos

### 2. Preview de Datos
- Muestra datos antes de importar
- Validación de estructura
- Indicación de errores

### 3. Procesamiento
- Validación de cada fila
- Creación de envíos
- Manejo de errores
- Reporte de resultados

## 📋 Formato Esperado del Excel

Columnas típicas:
- HAWB (opcional, se puede generar)
- Comprador (nombre o cédula)
- Productos (descripción, peso, cantidad, valor)
- Estado
- Observaciones

## 🚀 Prompts Útiles

1. **"Cómo se valida el formato del archivo Excel"**
2. **"Dónde se procesan los datos del Excel antes de crear envíos"**
3. **"Cómo se manejan los errores en la importación"**
4. **"Qué validaciones se aplican a los datos importados"**
5. **"Cómo se muestra el preview de datos en el frontend"**

## 🔗 Relaciones
- **Envios:** Crea múltiples envíos desde el Excel
- **Productos:** Puede crear productos nuevos durante la importación
- **Usuarios:** Asocia envíos a compradores existentes

## ⚠️ Validaciones Importantes
- Formato de archivo correcto
- Estructura de columnas válida
- Datos requeridos presentes
- Validación de tipos de datos
- Unicidad de HAWB (si se proporciona)

