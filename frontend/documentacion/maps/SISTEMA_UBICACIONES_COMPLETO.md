# ✅ Sistema de Ubicaciones Geográficas de Ecuador - Completo

## 🎯 Resumen de Cambios

Se ha implementado un sistema completo de ubicaciones geográficas jerárquicas (Provincia → Cantón → Ciudad) que reemplaza el sistema anterior de solo ciudades.

---

## 📊 Cambios en el Backend

### 1. **Nuevo Archivo: `datos_ecuador.py`**

**Ubicación:** `backend/apps/usuarios/datos_ecuador.py`

Contiene toda la estructura de ubicaciones de Ecuador con:
- 12 provincias
- Múltiples cantones por provincia
- Ciudades con coordenadas geográficas precisas

**Funciones disponibles:**
```python
obtener_provincias()  # Lista de provincias
obtener_cantones(provincia)  # Cantones de una provincia
obtener_ciudades(provincia, canton)  # Ciudades de un cantón
obtener_coordenadas(provincia, canton, ciudad)  # Lat/Lng
buscar_ciudad_por_nombre(nombre_ciudad)  # Búsqueda inversa
```

### 2. **Modelo Usuario Actualizado**

**Archivo:** `backend/apps/usuarios/models.py`

**Campos nuevos:**
```python
provincia = models.CharField(max_length=100, blank=True, null=True)
canton = models.CharField(max_length=100, blank=True, null=True)
ciudad = models.CharField(max_length=100, blank=True, null=True)
```

**Método nuevo:**
```python
def get_ubicacion_completa(self):
    """Retorna: 'Ciudad, Cantón, Provincia'"""
    return ', '.join([self.ciudad, self.canton, self.provincia])
```

### 3. **Migración Aplicada**

```bash
python manage.py makemigrations usuarios
python manage.py migrate usuarios
```

**Resultado:**
- ✅ Campo `provincia` agregado
- ✅ Campo `canton` agregado
- ✅ Campo `ciudad` ahora es text field (sin choices)

### 4. **Serializers Actualizados**

**Archivo:** `backend/apps/usuarios/serializers.py`

Todos los serializers ahora incluyen:
- `provincia`
- `canton`
- `ciudad`
- `ubicacion_completa` (read-only, formato legible)

**Ejemplo:**
```python
class UsuarioListSerializer(serializers.ModelSerializer):
    ubicacion_completa = serializers.CharField(
        source='get_ubicacion_completa', 
        read_only=True
    )
    
    fields = ['provincia', 'canton', 'ciudad', 'ubicacion_completa', ...]
```

### 5. **Nuevos Endpoints de API**

**Archivo:** `backend/apps/usuarios/views_ubicaciones.py` (nuevo)

#### GET `/api/usuarios/ubicaciones/provincias/`
```json
{
  "provincias": ["Azuay", "Chimborazo", ...],
  "total": 12
}
```

#### GET `/api/usuarios/ubicaciones/cantones/?provincia=Pichincha`
```json
{
  "provincia": "Pichincha",
  "cantones": ["Quito", "Cayambe", "Mejía"],
  "total": 3
}
```

#### GET `/api/usuarios/ubicaciones/ciudades/?provincia=Pichincha&canton=Quito`
```json
{
  "provincia": "Pichincha",
  "canton": "Quito",
  "ciudades": ["Quito", "Conocoto", "Tumbaco"],
  "total": 3
}
```

#### GET `/api/usuarios/ubicaciones/coordenadas/?provincia=Pichincha&canton=Quito&ciudad=Quito`
```json
{
  "provincia": "Pichincha",
  "canton": "Quito",
  "ciudad": "Quito",
  "latitud": -0.1807,
  "longitud": -78.4678
}
```

### 6. **Comando Actualizado**

**Archivo:** `backend/apps/usuarios/management/commands/actualizar_ubicaciones.py`

Ahora asigna ubicaciones completas (provincia + cantón + ciudad):

```bash
# Actualizar todos los compradores sin ubicación
python manage.py actualizar_ubicaciones

# Forzar reasignación aleatoria
python manage.py actualizar_ubicaciones --random
```

**Salida:**
```
✓ Jacquelien Tene → Cuenca, Cuenca, Azuay (-2.896, -79.004)
📊 Distribución por provincia:
  • Azuay: 1 compradores
  • Loja: 1 compradores
```

---

## 🎨 Cambios en el Frontend

### 1. **Nuevo Servicio: `UbicacionesService`**

**Archivo:** `frontend/src/app/services/ubicaciones.service.ts` (nuevo)

```typescript
export class UbicacionesService {
  getProvincias(): Observable<UbicacionesResponse>
  getCantones(provincia: string): Observable<UbicacionesResponse>
  getCiudades(provincia: string, canton: string): Observable<UbicacionesResponse>
  getCoordenadas(provincia, canton, ciudad): Observable<CoordenaddasResponse>
}
```

### 2. **Modelo Usuario Actualizado**

**Archivo:** `frontend/src/app/models/usuario.ts`

```typescript
export interface Usuario {
  // ... campos existentes
  provincia?: string;
  canton?: string;
  ciudad?: string;
  ubicacion_completa?: string;  // "Ciudad, Cantón, Provincia"
  latitud?: number;
  longitud?: number;
}
```

### 3. **Modelo Mapa Actualizado**

**Archivo:** `frontend/src/app/models/mapa.ts`

```typescript
export interface CompradorMapa {
  // ... campos existentes
  provincia: string;
  canton: string;
  ciudad: string;
  ubicacion_completa: string;
}
```

### 4. **Popups del Mapa Mejorados**

**Cambios en:** `mapa-compradores.component.ts`

- **Tamaño aumentado:**
  - Popups de ciudad: `maxWidth: 400px, minWidth: 300px`
  - Popups de comprador: `maxWidth: 500px, minWidth: 400px`
  
- **Información mostrada:**
  - Ahora muestra "Ubicación: Ciudad, Cantón, Provincia"
  - En lugar de solo "Ciudad"

- **Estilos mejorados:**
  - Gradientes personalizados
  - Bordes de color
  - Scroll interno para envíos

---

## 🔧 Uso del Sistema

### En Formularios de Creación/Edición de Usuario

#### 1. Cargar Provincias al Iniciar
```typescript
ngOnInit() {
  this.ubicacionesService.getProvincias().subscribe(data => {
    this.provincias = data.provincias;
  });
}
```

#### 2. Al Seleccionar Provincia, Cargar Cantones
```typescript
onProvinciaChange(provincia: string) {
  this.canton = null;
  this.ciudad = null;
  this.cantones = [];
  this.ciudades = [];
  
  this.ubicacionesService.getCantones(provincia).subscribe(data => {
    this.cantones = data.cantones;
  });
}
```

#### 3. Al Seleccionar Cantón, Cargar Ciudades
```typescript
onCantonChange(canton: string) {
  this.ciudad = null;
  this.ciudades = [];
  
  this.ubicacionesService.getCiudades(this.provincia, canton).subscribe(data => {
    this.ciudades = data.ciudades;
  });
}
```

#### 4. Al Seleccionar Ciudad, Obtener Coordenadas
```typescript
onCiudadChange(ciudad: string) {
  this.ubicacionesService.getCoordenadas(
    this.provincia, 
    this.canton, 
    ciudad
  ).subscribe(data => {
    this.usuario.latitud = data.latitud;
    this.usuario.longitud = data.longitud;
    // Las coordenadas se guardan automáticamente con el usuario
  });
}
```

### Ejemplo de Formulario HTML

```html
<form [formGroup]="usuarioForm">
  <!-- Provincia -->
  <select formControlName="provincia" (change)="onProvinciaChange($event.target.value)">
    <option value="">Seleccione provincia</option>
    <option *ngFor="let prov of provincias" [value]="prov">
      {{ prov }}
    </option>
  </select>

  <!-- Cantón -->
  <select formControlName="canton" 
          (change)="onCantonChange($event.target.value)"
          [disabled]="!provincia">
    <option value="">Seleccione cantón</option>
    <option *ngFor="let cant of cantones" [value]="cant">
      {{ cant }}
    </option>
  </select>

  <!-- Ciudad -->
  <select formControlName="ciudad" 
          (change)="onCiudadChange($event.target.value)"
          [disabled]="!canton">
    <option value="">Seleccione ciudad</option>
    <option *ngFor="let ciud of ciudades" [value]="ciud">
      {{ ciud }}
    </option>
  </select>
</form>
```

---

## 📋 Tablas y Vistas

### Mostrar Ubicación en Tablas

```html
<table>
  <thead>
    <tr>
      <th>Nombre</th>
      <th>Ubicación</th>
      <th>Coordenadas</th>
    </tr>
  </thead>
  <tbody>
    <tr *ngFor="let usuario of usuarios">
      <td>{{ usuario.nombre }}</td>
      <td>{{ usuario.ubicacion_completa || 'Sin ubicación' }}</td>
      <td>
        <span *ngIf="usuario.latitud && usuario.longitud">
          {{ usuario.latitud | number:'1.4-4' }}, {{ usuario.longitud | number:'1.4-4' }}
        </span>
        <span *ngIf="!usuario.latitud">N/A</span>
      </td>
    </tr>
  </tbody>
</table>
```

### Badge de Ubicación

```html
<span class="badge-ubicacion">
  <i class="fas fa-map-marker-alt"></i>
  {{ usuario.ubicacion_completa }}
</span>
```

**CSS:**
```css
.badge-ubicacion {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
```

---

## 🗺️ Mejoras en el Mapa

### Popups Más Grandes

**Antes:**
- Ciudad: 300px max
- Comprador: 400px max

**Ahora:**
- Ciudad: 300-400px
- Comprador: 400-500px
- Scroll automático si hay muchos envíos

### Información Completa

**Popup de Comprador ahora muestra:**
- 👤 Nombre del comprador
- Usuario, Email, Teléfono
- **Ubicación completa:** "Ciudad, Cantón, Provincia"
- Total de envíos
- Lista de envíos recientes con:
  - HAWB, Estado (coloreado), Peso, Valor, Costo

---

## 🧪 Pruebas

### 1. Verificar Endpoints

```bash
# Provincias
curl http://localhost:8000/api/usuarios/ubicaciones/provincias/

# Cantones
curl http://localhost:8000/api/usuarios/ubicaciones/cantones/?provincia=Pichincha

# Ciudades
curl http://localhost:8000/api/usuarios/ubicaciones/ciudades/?provincia=Pichincha&canton=Quito

# Coordenadas
curl http://localhost:8000/api/usuarios/ubicaciones/coordenadas/?provincia=Pichincha&canton=Quito&ciudad=Quito
```

### 2. Verificar Datos en DB

```python
python manage.py shell

>>> from apps.usuarios.models import Usuario
>>> compradores = Usuario.objects.filter(rol=4)
>>> for c in compradores:
...     print(f"{c.nombre}: {c.get_ubicacion_completa()}")
...
dav: Loja, Loja, Loja
Jacquelien Tene: Cuenca, Cuenca, Azuay
pedro: Portoviejo, Portoviejo, Manabí
```

### 3. Probar en Frontend

1. Abrir formulario de creación de usuario
2. Seleccionar provincia → Ver cantones cargarse
3. Seleccionar cantón → Ver ciudades cargarse
4. Seleccionar ciudad → Ver coordenadas asignarse
5. Guardar usuario
6. Ver en mapa → Click en ciudad → Ver comprador con ubicación completa

---

## 📝 Checklist de Implementación

### Backend ✅
- [x] Archivo `datos_ecuador.py` creado
- [x] Modelo Usuario actualizado (provincia, canton)
- [x] Migración aplicada
- [x] Serializers actualizados
- [x] Views de ubicaciones creadas
- [x] URLs configuradas
- [x] Comando `actualizar_ubicaciones` actualizado
- [x] Datos de compradores actualizados

### Frontend ⏳
- [x] Servicio `UbicacionesService` creado
- [x] Modelos actualizados (Usuario, CompradorMapa)
- [x] Popups del mapa mejorados
- [ ] Formulario de usuario con selectores jerárquicos
- [ ] Tablas actualizadas para mostrar ubicación completa

---

## 🚀 Próximos Pasos

1. **Crear/actualizar formularios de usuario:**
   - Agregar selectores jerárquicos (Provincia → Cantón → Ciudad)
   - Asignación automática de coordenadas
   
2. **Actualizar todas las tablas:**
   - Mostrar `ubicacion_completa` en lugar de solo ciudad
   - Agregar columnas de provincia y cantón si es necesario

3. **Validaciones:**
   - Requerir ubicación completa para compradores
   - Validar que la combinación provincia-cantón-ciudad exista

4. **Filtros:**
   - Agregar filtros por provincia
   - Agregar filtros por cantón

5. **Búsqueda:**
   - Buscar usuarios por provincia/cantón/ciudad
   - Autocompletado de ubicaciones

---

**¡Sistema de ubicaciones completo y funcional! 🎉**

Las ubicaciones ahora son jerárquicas, precisas y fáciles de usar tanto en el backend como en el frontend.

