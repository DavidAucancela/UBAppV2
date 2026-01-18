# 💰 Módulo de Gestión de Tarifas

## 📍 Ubicación
- **Frontend:** `frontend/src/app/components/tarifas/`
- **Backend:** `backend/apps/archivos/models.py` (Modelo Tarifa)
- **Ruta:** `/tarifas`

## 🎯 Funcionalidad
Configuración de tarifas de envío por categoría de producto. Las tarifas se usan para calcular automáticamente los costos de envío.

## 📁 Estructura de Archivos

### Frontend
```
tarifas/
├── tarifas-list.component.ts
├── tarifas-list.component.html
└── tarifas-list.component.css
```

### Backend
```
archivos/
├── models.py          # Modelo Tarifa
├── views.py           # TarifaViewSet
└── serializers.py     # TarifaSerializer
```

## 🔑 Componentes Clave

### 1. Modelo Tarifa
**Archivo:** `backend/apps/archivos/models.py`
- Categoría de producto (Electrónica, Ropa, Hogar, etc.)
- Precio por kilogramo
- Precio base (si aplica)
- Fecha de vigencia

### 2. Cálculo de Costos
**Uso en:** `backend/apps/archivos/views.py` (creación de envío)
- Busca tarifa por categoría
- Calcula: cantidad × peso × precio_kg
- Suma total de costos
- Desglose por categoría

### 3. Categorías de Productos
- ELECTRONICA
- ROPA
- HOGAR
- DEPORTES
- OTROS

## 📊 Flujo de Cálculo

1. Usuario crea envío con productos
2. Para cada producto:
   - Se identifica su categoría
   - Se busca la tarifa correspondiente
   - Se calcula: cantidad × peso × precio_kg
3. Se suman todos los costos
4. Se muestra desglose en frontend

## 🚀 Prompts Útiles

1. **"Cómo se buscan las tarifas por categoría de producto"**
2. **"Dónde se calculan los costos de envío usando tarifas"**
3. **"Cómo se muestra el desglose de costos en el frontend"**
4. **"Qué pasa si no hay tarifa para una categoría"**
5. **"Cómo se crean y editan las tarifas"**

## 🔗 Relaciones
- **Productos:** Las tarifas se aplican por categoría de producto
- **Envios:** Los costos se calculan usando las tarifas
- **Categorías:** Cada tarifa está asociada a una categoría

## ⚠️ Validaciones Importantes
- Categoría requerida
- Precio por kg debe ser positivo
- No puede haber tarifas duplicadas por categoría (o manejo de vigencia)

