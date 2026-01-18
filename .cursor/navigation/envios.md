# 📦 Módulo de Gestión de Envíos

## 📍 Ubicación
- **Frontend:** `frontend/src/app/components/envios/envios-list/`
- **Backend:** `backend/apps/archivos/`
- **Ruta:** `/envios`

## 🎯 Funcionalidad
Módulo core del sistema para crear, editar, listar, filtrar y gestionar envíos con productos, cálculo de costos y generación de comprobantes.

## 📁 Estructura de Archivos

### Frontend
```
envios/
├── envios-list/
│   ├── envios-list.component.ts
│   ├── envios-list.component.html
│   └── envios-list.component.css
└── mis-envios/
    ├── mis-envios.component.ts
    ├── mis-envios.component.html
    └── mis-envios.component.css
```

### Backend
```
archivos/
├── models.py              # Modelo Envio, Producto
├── views.py               # EnvioViewSet
├── serializers.py         # EnvioSerializer, EnvioCreateSerializer
├── utils_exportacion.py   # Generación de PDFs
└── services.py            # Lógica de negocio (si existe)
```

## 🔑 Componentes Clave

### 1. Modelo Envio
**Archivo:** `backend/apps/archivos/models.py`
- HAWB (House Air Waybill) - único
- Comprador (FK a Usuario)
- Productos (relación muchos a muchos)
- Estados: Pendiente, En Tránsito, Entregado, Cancelado
- Campos calculados: peso_total, cantidad_total, valor_total, costo_servicio

### 2. Generación de HAWB
**Lógica:** Secuencial automática
- Formato: HAW + número secuencial
- Se genera antes de guardar
- Validación de unicidad

### 3. Cálculo de Costos
**Archivo:** `backend/apps/archivos/views.py` (método create)
- Usa tarifas por categoría de producto
- Calcula costo por producto
- Suma total de costos
- Desglose por categoría

### 4. Generación de PDF
**Archivo:** `backend/apps/archivos/utils_exportacion.py`
- Función: `generar_comprobante_envio()`
- Usa ReportLab
- Incluye información del destinatario, productos, totales
- Manejo de texto largo con Paragraph

## 📊 Estados del Envío
1. **PENDIENTE** - Recién creado
2. **EN_TRANSITO** - En camino
3. **ENTREGADO** - Completado
4. **CANCELADO** - Cancelado

## 🚀 Prompts Útiles

1. **"Muéstrame el flujo completo de creación de un envío"**
2. **"Cómo se genera el HAWB automáticamente"**
3. **"Dónde se calculan los costos de envío usando tarifas"**
4. **"Cómo se genera el PDF del comprobante"**
5. **"Cómo se relacionan productos con envíos"**
6. **"Dónde se validan los datos del envío antes de guardar"**
7. **"Cómo funcionan los filtros en la lista de envíos"**

## 🔗 Relaciones
- **Usuarios:** Cada envío tiene un comprador
- **Productos:** Múltiples productos por envío
- **Tarifas:** Se usan para calcular costos
- **Búsqueda Semántica:** Los envíos tienen embeddings

## ⚠️ Validaciones Importantes
- HAWB es requerido y único
- Debe tener al menos un producto
- Comprador es requerido
- Peso y valor deben ser positivos

