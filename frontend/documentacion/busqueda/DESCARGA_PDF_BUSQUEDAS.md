# 📄 Descarga de PDFs de Búsquedas - Frontend

## 🎯 Nueva Funcionalidad Implementada

Se ha agregado la capacidad de descargar informes en PDF de las búsquedas realizadas (tanto tradicionales como semánticas).

---

## 📦 Archivos Creados/Modificados

### Archivos Nuevos

1. **`frontend/src/app/services/busqueda.service.ts`** ✨
   - Servicio dedicado para gestión de búsquedas
   - Métodos para descargar PDFs
   - Utilidades para manejo de archivos

### Archivos Modificados

1. **`frontend/src/app/components/busqueda-semantica/busqueda-semantica.component.ts`**
   - Agregado import de `BusquedaService`
   - Método `descargarPdfBusquedaActual()`
   - Método `descargarPdfHistorial()`
   - Método `tienePdfDisponible()`

2. **`frontend/src/app/components/busqueda-semantica/busqueda-semantica.component.html`**
   - Botón "Descargar PDF" en controles de vista
   - Botones de descarga en cada ítem del historial

3. **`frontend/src/app/components/busqueda-semantica/busqueda-semantica.component.css`**
   - Estilos para botones de descarga PDF
   - Estilos para acciones del historial
   - Responsive design

---

## 🚀 Cómo Usar

### 1. Descargar PDF de Búsqueda Actual

Cuando realizas una búsqueda semántica con resultados, aparece un botón "Descargar PDF":

```html
<button class="btn-descargar-pdf" (click)="descargarPdfBusquedaActual()">
  <i class="fas fa-file-pdf"></i>
  Descargar PDF
</button>
```

**Flujo:**
1. Usuario realiza búsqueda semántica
2. Aparecen resultados
3. Botón "Descargar PDF" se habilita
4. Click descarga PDF con métricas completas

### 2. Descargar PDF del Historial

En el panel de historial, cada búsqueda anterior tiene un ícono de PDF:

```html
<button 
  class="btn-accion-historial btn-pdf"
  (click)="descargarPdfHistorial(busqueda, $event)"
>
  <i class="fas fa-file-pdf"></i>
</button>
```

**Flujo:**
1. Usuario abre historial (botón "Historial")
2. Ve lista de búsquedas anteriores
3. Hace clic en ícono PDF (🔴)
4. Se descarga el PDF de esa búsqueda

---

## 📋 Contenido del PDF

### PDF de Búsqueda Semántica

El PDF generado incluye:

#### 1. Información de la Búsqueda
- Consulta realizada
- Modelo de embedding utilizado (text-embedding-3-small, etc.)
- Fecha de búsqueda
- Resultados encontrados
- Tiempo de respuesta (ms)
- Tokens utilizados
- Costo de la consulta (USD)
- Usuario que realizó la búsqueda

#### 2. Resultados con Métricas
Tabla con columnas:
- **HAWB**: Código de guía
- **Comprador**: Nombre del destinatario
- **Score**: Métrica combinada final (0-1)
- **Cosine**: Similitud coseno (-1 a 1)
- **Euclidean**: Distancia euclidiana
- **Boost**: Bonificación por coincidencias exactas

#### 3. Explicación de Métricas
- **Score Combinado**: Métrica final que ordena resultados
- **Cosine Similarity**: Mide ángulo entre vectores
- **Euclidean Distance**: Distancia geométrica
- **Boost Exactas**: Bonificación hasta +0.15

### PDF de Búsqueda Tradicional

El PDF incluye:

#### 1. Información de la Búsqueda
- Término de búsqueda
- Tipo de búsqueda (general, envíos, usuarios, productos)
- Fecha de búsqueda
- Resultados encontrados
- Usuario que realizó la búsqueda

#### 2. Resultados por Tipo

**Envíos:**
- HAWB
- Comprador
- Estado
- Ciudad
- Fecha

**Usuarios:**
- Usuario
- Email
- Rol
- Ciudad

**Productos:**
- Descripción
- Cantidad
- Peso
- Valor

---

## 🛠️ Métodos del Servicio

### BusquedaService

```typescript
// Descargar PDF de búsqueda tradicional
descargarPdfBusquedaTradicional(busquedaId: number): Observable<Blob>

// Descargar PDF de búsqueda semántica
descargarPdfBusquedaSemantica(busquedaId: number): Observable<Blob>

// Helper para descargar blob como archivo
descargarArchivo(blob: Blob, filename: string): void
```

### Ejemplo de Uso

```typescript
// En tu componente
this.busquedaService.descargarPdfBusquedaSemantica(123).subscribe({
  next: (blob) => {
    const filename = `busqueda_semantica_123_2025-11-26.pdf`;
    this.busquedaService.descargarArchivo(blob, filename);
    this.mensajeExito = '✅ PDF descargado correctamente';
  },
  error: (error) => {
    console.error('Error:', error);
    this.errorMensaje = 'Error al generar el PDF';
  }
});
```

---

## 🎨 Estilos CSS

### Botón Principal de Descarga

```css
.btn-descargar-pdf {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
  color: white;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(231, 76, 60, 0.3);
}

.btn-descargar-pdf:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
}
```

### Botones en Historial

```css
.btn-accion-historial.btn-pdf {
  border-color: #e74c3c;
  color: #e74c3c;
}

.btn-accion-historial.btn-pdf:hover {
  background: #e74c3c;
  color: white;
  box-shadow: 0 4px 10px rgba(231, 76, 60, 0.3);
}
```

---

## 📱 Responsive Design

Los botones de descarga se adaptan a diferentes tamaños de pantalla:

```css
@media (max-width: 768px) {
  .btn-descargar-pdf {
    padding: 0.5rem 0.8rem;
    font-size: 0.85rem;
  }
  
  .btn-accion-historial {
    width: 32px;
    height: 32px;
  }
}
```

---

## ✅ Características

### 1. **Diseño Profesional**
- PDFs con tablas formateadas
- Colores diferenciados por tipo
- Headers y footers informativos
- Fecha de generación automática

### 2. **Contenido Completo**
- Toda la información de la búsqueda
- Métricas detalladas (semántica)
- Resultados organizados en tablas
- Explicaciones técnicas

### 3. **Nombres Descriptivos**
- Formato: `busqueda_semantica_{id}_{fecha}.pdf`
- Ejemplo: `busqueda_semantica_123_2025-11-26.pdf`

### 4. **Manejo de Errores**
- Mensajes claros al usuario
- Logs en consola para debugging
- Validaciones previas

---

## 🔄 Flujo Completo

```
Usuario realiza búsqueda
    ↓
Backend guarda:
  - Embedding (si es semántica)
  - Resultados completos (resultados_json)
  - Métricas (tiempo, tokens, costo)
    ↓
Frontend muestra resultados
    ↓
Usuario clickea "Descargar PDF"
    ↓
Frontend llama al backend:
  GET /api/busqueda/semantica/{id}/descargar-pdf/
    ↓
Backend genera PDF con ReportLab:
  - Lee datos de embedding_busqueda
  - Formatea con estilos profesionales
  - Incluye todas las métricas
    ↓
Frontend recibe Blob
    ↓
Se descarga automáticamente
    ↓
Usuario recibe archivo PDF ✅
```

---

## 🐛 Solución de Problemas

### Error: "No se puede descargar el PDF"

**Causa**: La búsqueda no tiene ID o no hay resultados
**Solución**: Verificar que `respuestaActual.busquedaId` existe

```typescript
tienePdfDisponible(): boolean {
  return !!(
    this.respuestaActual && 
    this.respuestaActual.busquedaId && 
    this.resultadosSemanticos.length > 0
  );
}
```

### Error: "PDF vacío o corrupto"

**Causa**: Backend no generó correctamente el PDF
**Solución**: 
1. Verificar que `reportlab` está instalado
2. Revisar logs del backend
3. Verificar que `resultados_json` no es null

### Error: "No se encontró la búsqueda"

**Causa**: ID incorrecto o búsqueda eliminada
**Solución**: Verificar que el ID existe en `embedding_busqueda`

---

## 📖 Ejemplo Completo

```typescript
// busqueda-semantica.component.ts

import { BusquedaService } from '../../services/busqueda.service';

export class BusquedaSemanticaComponent {
  constructor(private busquedaService: BusquedaService) {}

  // Descargar PDF de búsqueda actual
  descargarPdfBusquedaActual(): void {
    if (!this.tienePdfDisponible()) {
      this.errorMensaje = 'No hay búsqueda activa para descargar';
      return;
    }

    this.mensajeExito = '⏳ Generando PDF...';
    
    this.busquedaService.descargarPdfBusquedaSemantica(
      this.respuestaActual.busquedaId
    ).subscribe({
      next: (blob) => {
        const fecha = new Date().toISOString().split('T')[0];
        const filename = `busqueda_semantica_${this.respuestaActual.busquedaId}_${fecha}.pdf`;
        
        this.busquedaService.descargarArchivo(blob, filename);
        this.mensajeExito = '✅ PDF descargado correctamente';
        setTimeout(() => this.mensajeExito = '', 3000);
      },
      error: (error) => {
        console.error('Error:', error);
        this.errorMensaje = 'Error al generar el PDF';
        setTimeout(() => this.errorMensaje = '', 5000);
      }
    });
  }

  // Verificar disponibilidad de PDF
  tienePdfDisponible(): boolean {
    return !!(
      this.respuestaActual && 
      this.respuestaActual.busquedaId && 
      this.resultadosSemanticos.length > 0
    );
  }
}
```

---

## 📞 Soporte

Si encuentras problemas:

1. Verificar que el backend está actualizado
2. Revisar logs en consola del navegador
3. Verificar permisos del usuario
4. Comprobar que `reportlab` está instalado en backend

---

**Fecha de implementación**: 26 de noviembre de 2025
**Autor**: Sistema de Implementación Frontend
**Versión**: 1.0.0

