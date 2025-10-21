# Endpoints de Exportación - API Backend

## Fecha de Implementación
Octubre 20, 2025

## Resumen

Se han implementado endpoints completos para la exportación de datos de envíos en múltiples formatos, así como la generación de comprobantes individuales.

---

## 📋 Tabla de Contenidos

1. [Endpoints Disponibles](#endpoints-disponibles)
2. [Exportación Masiva de Envíos](#exportación-masiva-de-envíos)
3. [Comprobante Individual](#comprobante-individual)
4. [Ejemplos de Uso](#ejemplos-de-uso)
5. [Instalación de Dependencias](#instalación-de-dependencias)

---

## Endpoints Disponibles

### 1. Exportación Masiva de Envíos
**Endpoint:** `GET /api/envios/envios/exportar/`

**Descripción:** Exporta los envíos filtrados a Excel, CSV o PDF

**Métodos soportados:** `GET`

**Autenticación:** Requerida (Token JWT)

### 2. Comprobante Individual
**Endpoint:** `GET /api/envios/envios/{id}/comprobante/`

**Descripción:** Genera un comprobante detallado de un envío específico

**Métodos soportados:** `GET`

**Autenticación:** Requerida (Token JWT)

---

## Exportación Masiva de Envíos

### Endpoint
```
GET /api/envios/envios/exportar/
```

### Parámetros de Query

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `formato` | string | ✅ Sí | Formato de exportación: `excel`, `csv` o `pdf` |
| `search` | string | ❌ No | Búsqueda general en HAWB y nombre del comprador |
| `hawb` | string | ❌ No | Filtrar por número de guía específico |
| `estado` | string | ❌ No | Filtrar por estado: `pendiente`, `en_transito`, `entregado`, `cancelado` |
| `comprador` | integer | ❌ No | ID del comprador |
| `comprador__nombre__icontains` | string | ❌ No | Filtrar por nombre del destinatario (búsqueda parcial) |
| `comprador__ciudad__icontains` | string | ❌ No | Filtrar por ciudad (búsqueda parcial) |
| `fecha_emision__gte` | date | ❌ No | Fecha desde (formato: YYYY-MM-DD) |
| `fecha_emision__lte` | date | ❌ No | Fecha hasta (formato: YYYY-MM-DD) |
| `ordering` | string | ❌ No | Ordenamiento: `fecha_emision`, `-fecha_emision`, `valor_total`, etc. |

### Formatos de Exportación

#### 1. Excel (.xlsx)
- **Formato:** `formato=excel`
- **Características:**
  - Hoja de cálculo con formato profesional
  - Encabezados con colores y estilos
  - Columnas auto-ajustadas
  - Filtros automáticos habilitados
  - Fila de encabezado congelada
  - Formato de moneda en columnas de valores
  - Compatible con Microsoft Excel, LibreOffice, Google Sheets

- **Columnas incluidas:**
  - N° Guía (HAWB)
  - Destinatario
  - Cédula
  - Correo
  - Teléfono
  - Ciudad
  - Estado
  - Fecha Emisión
  - Peso Total (kg)
  - Cantidad Total
  - Valor Total ($)
  - Costo Servicio ($)
  - Observaciones

#### 2. CSV (.csv)
- **Formato:** `formato=csv`
- **Características:**
  - Archivo de texto separado por comas
  - Codificación UTF-8 con BOM (compatible con Excel)
  - Valores entrecomillados para evitar problemas con caracteres especiales
  - Fácil de importar en cualquier sistema
  - Tamaño de archivo más pequeño

- **Columnas:** Iguales a Excel

#### 3. PDF (.pdf)
- **Formato:** `formato=pdf`
- **Características:**
  - Documento profesional con formato de tabla
  - Diseño optimizado para tamaño A4
  - Encabezado con título y fecha de generación
  - Tabla con filas alternas para mejor legibilidad
  - Resumen de totales al final
  - No editable, ideal para reportes oficiales

- **Columnas optimizadas para impresión:**
  - HAWB
  - Destinatario
  - Ciudad
  - Estado
  - Fecha
  - Peso (kg)
  - Valor ($)
  - Costo ($)

- **Resumen incluido:**
  - Peso Total
  - Valor Total
  - Costo Total del Servicio

### Respuestas

#### Éxito (200 OK)
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet  (Excel)
Content-Type: text/csv; charset=utf-8  (CSV)
Content-Type: application/pdf  (PDF)
Content-Disposition: attachment; filename="envios_20251020_143025.xlsx"
```

**El archivo se descarga automáticamente**

#### Error - Formato Inválido (400 Bad Request)
```json
{
  "error": "Formato inválido. Use: excel, csv o pdf"
}
```

#### Error - Sin Resultados (404 Not Found)
```json
{
  "error": "No hay envíos para exportar con los filtros aplicados"
}
```

#### Error - Error de Generación (500 Internal Server Error)
```json
{
  "error": "Error al generar el archivo: [detalle del error]"
}
```

---

## Comprobante Individual

### Endpoint
```
GET /api/envios/envios/{id}/comprobante/
```

### Parámetros de URL

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `id` | integer | ID del envío |

### Características del Comprobante

- **Formato:** PDF profesional
- **Contenido incluido:**
  - Número de guía destacado
  - Información completa del destinatario
  - Detalles del envío (estado, fechas, peso, valores, costos)
  - Lista detallada de productos (si existen)
  - Observaciones (si existen)
  - Fecha y hora de generación del documento

### Respuestas

#### Éxito (200 OK)
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="comprobante_HAWB123456.pdf"
```

**El comprobante se descarga automáticamente**

#### Error - Envío No Encontrado (404 Not Found)
```json
{
  "error": "Envío no encontrado"
}
```

#### Error - Error de Generación (500 Internal Server Error)
```json
{
  "error": "Error al generar el comprobante: [detalle del error]"
}
```

---

## Ejemplos de Uso

### cURL

#### Exportar todos los envíos a Excel
```bash
curl -X GET "http://localhost:8000/api/envios/envios/exportar/?formato=excel" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o envios.xlsx
```

#### Exportar envíos pendientes a CSV
```bash
curl -X GET "http://localhost:8000/api/envios/envios/exportar/?formato=csv&estado=pendiente" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o envios_pendientes.csv
```

#### Exportar envíos de una ciudad a PDF
```bash
curl -X GET "http://localhost:8000/api/envios/envios/exportar/?formato=pdf&comprador__ciudad__icontains=Quito" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o envios_quito.pdf
```

#### Exportar envíos por rango de fechas
```bash
curl -X GET "http://localhost:8000/api/envios/envios/exportar/?formato=excel&fecha_emision__gte=2025-01-01&fecha_emision__lte=2025-01-31" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o envios_enero.xlsx
```

#### Descargar comprobante de un envío
```bash
curl -X GET "http://localhost:8000/api/envios/envios/123/comprobante/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o comprobante_envio_123.pdf
```

### JavaScript (Frontend)

```javascript
// Función de exportación desde el frontend
async function exportarEnvios(formato, filtros) {
  const params = new URLSearchParams({
    formato: formato,
    ...filtros
  });
  
  const response = await fetch(
    `${API_URL}/envios/envios/exportar/?${params.toString()}`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `envios_${Date.now()}.${formato === 'excel' ? 'xlsx' : formato}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  } else {
    const error = await response.json();
    console.error('Error:', error);
  }
}

// Uso
exportarEnvios('excel', { estado: 'pendiente' });
exportarEnvios('csv', { comprador__ciudad__icontains: 'Quito' });
exportarEnvios('pdf', { fecha_emision__gte: '2025-01-01' });
```

### Python (Requests)

```python
import requests

# Configuración
API_URL = 'http://localhost:8000/api/envios/envios'
TOKEN = 'your_jwt_token_here'
headers = {'Authorization': f'Bearer {TOKEN}'}

# Exportar a Excel
response = requests.get(
    f'{API_URL}/exportar/',
    params={'formato': 'excel', 'estado': 'pendiente'},
    headers=headers
)

if response.status_code == 200:
    with open('envios.xlsx', 'wb') as f:
        f.write(response.content)
    print('Archivo descargado exitosamente')
else:
    print(f'Error: {response.json()}')

# Descargar comprobante
envio_id = 123
response = requests.get(
    f'{API_URL}/{envio_id}/comprobante/',
    headers=headers
)

if response.status_code == 200:
    with open(f'comprobante_{envio_id}.pdf', 'wb') as f:
        f.write(response.content)
```

---

## Instalación de Dependencias

### 1. Instalar las librerías requeridas

```bash
cd backend
pip install -r requirements.txt
```

### 2. Dependencias agregadas

El archivo `requirements.txt` ahora incluye:

```
# Exportación de archivos
openpyxl==3.1.2      # Para generar archivos Excel (.xlsx)
reportlab==4.0.9     # Para generar archivos PDF
Pillow==10.2.0       # Soporte de imágenes para reportlab
```

### 3. Verificar instalación

```bash
python -c "import openpyxl; import reportlab; print('Dependencias instaladas correctamente')"
```

---

## Estructura de Archivos

```
backend/apps/archivos/
├── __init__.py
├── models.py
├── serializers.py
├── views.py                      # Endpoints de exportación agregados aquí
├── utils_exportacion.py          # NUEVO: Funciones de exportación
└── urls.py
```

---

## Funciones de Utilidad

El archivo `utils_exportacion.py` contiene las siguientes funciones:

### 1. `exportar_envios_excel(envios_queryset, filename)`
Genera un archivo Excel profesional con:
- Formato y colores en encabezados
- Auto-ajuste de columnas
- Filtros automáticos
- Fila de encabezado congelada
- Formato de moneda

### 2. `exportar_envios_csv(envios_queryset, filename)`
Genera un archivo CSV compatible con:
- UTF-8 con BOM para Excel
- Valores entrecomillados
- Formato universal

### 3. `exportar_envios_pdf(envios_queryset, filename)`
Genera un PDF profesional con:
- Tabla formateada
- Resumen de totales
- Fecha de generación
- Diseño optimizado para impresión

### 4. `generar_comprobante_envio(envio, filename)`
Genera un comprobante detallado con:
- Información completa del envío
- Datos del destinatario
- Lista de productos
- Observaciones
- Diseño profesional

---

## Permisos y Seguridad

### Autenticación
- Todos los endpoints requieren autenticación mediante JWT
- Token debe enviarse en el header: `Authorization: Bearer <token>`

### Autorización
- **Compradores:** Solo pueden exportar sus propios envíos
- **Digitadores:** Pueden exportar todos los envíos
- **Gerentes:** Pueden exportar todos los envíos
- **Administradores:** Pueden exportar todos los envíos

### Filtrado Automático
El sistema automáticamente filtra los envíos según el rol del usuario que realiza la petición.

---

## Testing

### Test Manual con Postman

1. **Obtener Token JWT:**
```
POST /api/usuarios/login/
Body: { "username": "usuario", "password": "contraseña" }
```

2. **Exportar a Excel:**
```
GET /api/envios/envios/exportar/?formato=excel
Headers: Authorization: Bearer <token>
```

3. **Exportar con Filtros:**
```
GET /api/envios/envios/exportar/?formato=pdf&estado=pendiente&comprador__ciudad__icontains=Quito
Headers: Authorization: Bearer <token>
```

4. **Descargar Comprobante:**
```
GET /api/envios/envios/123/comprobante/
Headers: Authorization: Bearer <token>
```

---

## Troubleshooting

### Error: "Module not found: openpyxl"
**Solución:** Instalar dependencias
```bash
pip install openpyxl reportlab Pillow
```

### Error: "No hay envíos para exportar"
**Causa:** Los filtros aplicados no retornan resultados
**Solución:** Verificar que existan envíos con los criterios especificados

### Error: "Permission denied"
**Causa:** Usuario no tiene permisos para acceder a los envíos solicitados
**Solución:** Verificar rol del usuario y permisos asignados

### Archivo Excel no abre correctamente
**Causa:** Posible corrupción en la generación
**Solución:** Verificar que openpyxl esté actualizado: `pip install --upgrade openpyxl`

### PDF con caracteres extraños
**Causa:** Problemas de codificación
**Solución:** Ya implementado UTF-8 correcto en las funciones de exportación

---

## Optimizaciones y Mejoras Futuras

### Posibles Mejoras
1. **Cache de exportaciones frecuentes**
2. **Exportación asíncrona para grandes volúmenes** (Celery)
3. **Compresión de archivos grandes** (ZIP)
4. **Plantillas personalizables** por usuario/empresa
5. **Envío por email** del archivo generado
6. **Límite de registros** para exportaciones masivas
7. **Logs de exportaciones** para auditoría

### Performance
- Las exportaciones son síncronas
- Para más de 10,000 registros, considere implementar tarea asíncrona
- Los archivos se generan en memoria para mejor performance

---

## Soporte

Para reportar problemas o solicitar nuevas funcionalidades, contacte al equipo de desarrollo.

**Versión:** 1.0.0  
**Última actualización:** Octubre 20, 2025  
**Autor:** Sistema de Gestión de Envíos


