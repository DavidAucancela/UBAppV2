# 📦 Módulo de Gestión de Productos

## 📍 Ubicación
- **Frontend:** `frontend/src/app/components/productos/productos-list/`
- **Backend:** `backend/apps/archivos/models.py` (Modelo Producto)
- **Ruta:** `/productos`

## 🎯 Funcionalidad
Catálogo de productos con categorías, características y reutilización en múltiples envíos. Los productos se pueden crear independientemente y asociar a envíos.

## 📁 Estructura de Archivos

### Frontend
```
productos/
└── productos-list/
    ├── productos-list.component.ts
    ├── productos-list.component.html
    └── productos-list.component.css
```

### Backend
```
archivos/
├── models.py          # Modelo Producto
├── views.py           # ProductoViewSet
└── serializers.py     # ProductoSerializer, ProductoCreateSerializer
```

## 🔑 Componentes Clave

### 1. Modelo Producto
**Archivo:** `backend/apps/archivos/models.py`
- Descripción
- Categoría (Electrónica, Ropa, Hogar, Deportes, Otros)
- Peso (kg)
- Valor unitario
- Reutilizable en múltiples envíos

### 2. Categorías de Productos
- **ELECTRONICA** 📱
- **ROPA** 👕
- **HOGAR** 🏠
- **DEPORTES** ⚽
- **OTROS** 📦

### 3. Relación con Envíos
- Un producto puede estar en múltiples envíos
- Cada envío puede tener múltiples productos
- Se especifica cantidad por envío
- Cálculo de totales (peso × cantidad, valor × cantidad)

## 📊 Funcionalidades

### Gestión de Productos
- Crear productos nuevos
- Editar productos existentes
- Listar productos con filtros
- Buscar productos por descripción o categoría

### Uso en Envíos
- Seleccionar producto existente al crear envío
- Crear producto nuevo desde el formulario de envío
- Cálculo automático de totales

## 🚀 Prompts Útiles

1. **"Cómo se crean y gestionan los productos"**
2. **"Cómo se relacionan productos con envíos"**
3. **"Dónde se calculan los totales de peso y valor por producto"**
4. **"Cómo se reutilizan productos en múltiples envíos"**
5. **"Dónde se filtran productos por categoría"**
6. **"Cómo se selecciona un producto existente al crear un envío"**

## 🔗 Relaciones
- **Envios:** Productos se asocian a envíos con cantidad
- **Tarifas:** Las tarifas se aplican por categoría de producto
- **Cálculos:** Peso y valor total se calculan desde productos

## ⚠️ Validaciones Importantes
- Descripción requerida
- Categoría requerida
- Peso debe ser positivo
- Valor debe ser positivo o cero

