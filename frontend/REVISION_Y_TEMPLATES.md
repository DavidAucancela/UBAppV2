# 🎉 REVISIÓN DE TU IMPLEMENTACIÓN + TEMPLATES HTML/CSS

## 📊 RESUMEN DE LO QUE HAS IMPLEMENTADO

### ✅ EXCELENTE - Implementaciones Correctas

#### 1. **Guards** - PERFECTO ✅
```
✅ auth.guard.ts - Implementado correctamente
✅ role.guard.ts - Implementado correctamente con parámetros
```
**Calificación: 10/10** - Funcionarán perfectamente

#### 2. **Environments** - PERFECTO ✅
```
✅ environment.ts - Configurado para desarrollo
✅ environment.prod.ts - Configurado para producción
```
**Calificación: 10/10** - Bien configurados

#### 3. **Interceptor HTTP** - BUENO ✅
```
✅ auth.interceptor.ts - Implementado con manejo de 401
```
**Calificación: 8/10** - Funciona bien

#### 4. **Componentes TypeScript** - EXCELENTE ✅
```
✅ envios-list.component.ts (414 líneas) - Completamente implementado
✅ productos-list.component.ts (240 líneas) - Completamente implementado
```
**Calificación: 10/10** - Excelente código, bien estructurado

#### 5. **Estilos** - PERFECTO ✅
```
✅ app.component.css (371 líneas) - Movidos desde inline
```
**Calificación: 10/10** - Mejor práctica aplicada

---

## 🎯 RECOMENDACIONES Y MEJORAS

### 1. Actualizar los Servicios para usar Environment

Los servicios todavía tienen URLs hardcodeadas. Necesitas actualizarlos:

#### auth.service.ts
```typescript
// Cambiar línea 10:
// ANTES:
private apiUrl = 'http://localhost:8000/api';

// DESPUÉS:
import { environment } from '../../environments/environment';
private apiUrl = environment.apiUrl;
```

#### api.service.ts
```typescript
// Cambiar línea 12:
// ANTES:
private apiUrl = 'http://localhost:8000/api';

// DESPUÉS:
import { environment } from '../../environments/environment';
private apiUrl = environment.apiUrl;
```

### 2. Configurar angular.json para Environments

Agregar en `angular.json`:

```json
{
  "projects": {
    "ANGULAR_FRONTEND": {
      "architect": {
        "build": {
          "configurations": {
            "production": {
              "fileReplacements": [
                {
                  "replace": "src/app/environments/environment.ts",
                  "with": "src/app/environments/environment.prod.ts"
                }
              ]
            }
          }
        }
      }
    }
  }
}
```

### 3. Actualizar app.config.ts para usar los Interceptores

Verificar que tenga:

```typescript
import { authInterceptor } from './interceptors/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimations()
  ]
};
```

### 4. Actualizar app.routes.ts para usar los Guards

```typescript
import { authGuard } from './guards/auth.guard';
import { roleGuard } from './guards/role.guard';
import { Roles } from './models/usuario';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { 
    path: 'dashboard', 
    component: DashboardComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'usuarios', 
    component: UsuariosListComponent,
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE])]
  },
  { 
    path: 'envios', 
    component: EnviosListComponent,
    canActivate: [authGuard]
  },
  { 
    path: 'productos', 
    component: ProductosListComponent,
    canActivate: [authGuard, roleGuard([Roles.ADMIN, Roles.GERENTE, Roles.DIGITADOR])]
  },
  { path: '**', redirectTo: '/login' }
];
```

### 5. Mejorar el Interceptor HTTP (Opcional)

Agregar más manejo de errores:

```typescript
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router);
  
  const modifiedReq = req.clone({
    withCredentials: true
  });

  return next(modifiedReq).pipe(
    catchError((error) => {
      if (error.status === 401) {
        // Limpiar sesión
        localStorage.removeItem('currentUser');
        router.navigate(['/login']);
      } else if (error.status === 403) {
        // Sin permisos
        router.navigate(['/dashboard']);
      } else if (error.status === 0) {
        console.error('Error de conexión con el servidor');
      }
      return throwError(() => error);
    })
  );
};
```

---

## 📝 TEMPLATES HTML Y CSS

### 🚚 ENVIOS-LIST COMPONENT

#### `envios-list.component.html`

```html
<div class="envios-container">
  <!-- Header -->
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">
        <i class="fas fa-truck"></i>
        Gestión de Envíos
      </h2>
      <button 
        class="btn btn-primary"
        (click)="openCreateModal()"
        *ngIf="authService.canManageEnvios()"
      >
        <i class="fas fa-plus"></i>
        Nuevo Envío
      </button>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-row">
        <!-- Search -->
        <div class="filter-group">
          <label class="filter-label">
            <i class="fas fa-search"></i>
            Buscar
          </label>
          <input 
            type="text"
            class="form-control"
            [(ngModel)]="searchTerm"
            (input)="onSearchChange()"
            placeholder="HAWB, comprador, cédula..."
          >
        </div>

        <!-- Estado Filter -->
        <div class="filter-group">
          <label class="filter-label">
            <i class="fas fa-filter"></i>
            Estado
          </label>
          <select 
            class="form-control"
            [(ngModel)]="selectedEstado"
            (change)="onEstadoFilterChange()"
          >
            <option value="">Todos los estados</option>
            <option [value]="EstadosEnvio.PENDIENTE">Pendiente</option>
            <option [value]="EstadosEnvio.EN_TRANSITO">En Tránsito</option>
            <option [value]="EstadosEnvio.ENTREGADO">Entregado</option>
            <option [value]="EstadosEnvio.CANCELADO">Cancelado</option>
          </select>
        </div>

        <!-- Comprador Filter -->
        <div class="filter-group" *ngIf="!authService.isComprador()">
          <label class="filter-label">
            <i class="fas fa-user"></i>
            Comprador
          </label>
          <select 
            class="form-control"
            [(ngModel)]="selectedComprador"
            (change)="onCompradorFilterChange()"
          >
            <option value="">Todos los compradores</option>
            <option *ngFor="let comprador of compradores" [value]="comprador.id">
              {{ comprador.nombre }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Results Summary -->
    <div class="results-summary">
      <span class="results-count">
        <i class="fas fa-list"></i>
        Mostrando {{ paginatedEnvios.length }} de {{ filteredEnvios.length }} envíos
      </span>
    </div>
  </div>

  <!-- Success Message -->
  <div class="alert alert-success" *ngIf="successMessage">
    <i class="fas fa-check-circle"></i>
    {{ successMessage }}
  </div>

  <!-- Error Message -->
  <div class="alert alert-error" *ngIf="errorMessage">
    <i class="fas fa-exclamation-circle"></i>
    {{ errorMessage }}
  </div>

  <!-- Loading State -->
  <div class="loading-state" *ngIf="loading">
    <i class="fas fa-spinner fa-spin"></i>
    <span>Cargando envíos...</span>
  </div>

  <!-- Table -->
  <div class="card" *ngIf="!loading">
    <div class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>HAWB</th>
            <th>Comprador</th>
            <th>Cédula</th>
            <th>Productos</th>
            <th>Peso Total</th>
            <th>Valor Total</th>
            <th>Estado</th>
            <th>Fecha</th>
            <th class="actions-column">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let envio of paginatedEnvios">
            <td>
              <strong>{{ envio.hawb }}</strong>
            </td>
            <td>{{ envio.comprador_info?.nombre || '-' }}</td>
            <td>{{ envio.comprador_info?.cedula || '-' }}</td>
            <td class="text-center">
              <span class="badge badge-info">
                {{ envio.cantidad_productos || 0 }}
              </span>
            </td>
            <td>{{ envio.peso_total | number:'1.2-2' }} kg</td>
            <td>{{ envio.valor_total | currency:'USD':'symbol':'1.2-2' }}</td>
            <td>
              <span class="badge" [ngClass]="getEstadoClass(envio.estado)">
                {{ getEstadoLabel(envio.estado) }}
              </span>
            </td>
            <td>{{ envio.fecha_creacion | date:'dd/MM/yyyy' }}</td>
            <td class="actions-column">
              <div class="action-buttons">
                <button 
                  class="btn-icon btn-view"
                  (click)="viewEnvio(envio)"
                  title="Ver detalle"
                >
                  <i class="fas fa-eye"></i>
                </button>
                
                <button 
                  class="btn-icon btn-edit"
                  (click)="editEnvio(envio)"
                  *ngIf="canEditEnvio(envio)"
                  title="Editar"
                >
                  <i class="fas fa-edit"></i>
                </button>

                <!-- Estado dropdown -->
                <div class="dropdown-estado" *ngIf="canChangeEstado(envio)">
                  <button class="btn-icon btn-status" title="Cambiar estado">
                    <i class="fas fa-exchange-alt"></i>
                  </button>
                  <div class="dropdown-estado-menu">
                    <button 
                      (click)="cambiarEstado(envio, EstadosEnvio.PENDIENTE)"
                      [disabled]="envio.estado === EstadosEnvio.PENDIENTE"
                    >
                      Pendiente
                    </button>
                    <button 
                      (click)="cambiarEstado(envio, EstadosEnvio.EN_TRANSITO)"
                      [disabled]="envio.estado === EstadosEnvio.EN_TRANSITO"
                    >
                      En Tránsito
                    </button>
                    <button 
                      (click)="cambiarEstado(envio, EstadosEnvio.ENTREGADO)"
                      [disabled]="envio.estado === EstadosEnvio.ENTREGADO"
                    >
                      Entregado
                    </button>
                    <button 
                      (click)="cambiarEstado(envio, EstadosEnvio.CANCELADO)"
                      [disabled]="envio.estado === EstadosEnvio.CANCELADO"
                    >
                      Cancelado
                    </button>
                  </div>
                </div>
                
                <button 
                  class="btn-icon btn-delete"
                  (click)="deleteEnvio(envio)"
                  *ngIf="canDeleteEnvio(envio)"
                  title="Eliminar"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr *ngIf="filteredEnvios.length === 0">
            <td colspan="9" class="no-data">
              <i class="fas fa-inbox"></i>
              <p>No se encontraron envíos</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination" *ngIf="totalPages > 1">
      <button 
        class="btn btn-secondary"
        (click)="previousPage()"
        [disabled]="currentPage === 1"
      >
        <i class="fas fa-chevron-left"></i>
        Anterior
      </button>
      
      <span class="pagination-info">
        Página {{ currentPage }} de {{ totalPages }}
      </span>
      
      <button 
        class="btn btn-secondary"
        (click)="nextPage()"
        [disabled]="currentPage === totalPages"
      >
        Siguiente
        <i class="fas fa-chevron-right"></i>
      </button>
    </div>
  </div>
</div>

<!-- Modal Create/Edit -->
<div class="modal-overlay" *ngIf="showModal" (click)="closeModal()">
  <div class="modal-content" (click)="$event.stopPropagation()">
    <div class="modal-header">
      <h3>
        <i class="fas fa-truck"></i>
        {{ editingEnvio ? 'Editar Envío' : 'Nuevo Envío' }}
      </h3>
      <button class="btn-close" (click)="closeModal()">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <form [formGroup]="envioForm" (ngSubmit)="onSubmit()">
      <div class="modal-body">
        <!-- Información del Envío -->
        <div class="form-section">
          <h4 class="section-title">
            <i class="fas fa-info-circle"></i>
            Información del Envío
          </h4>
          
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">
                HAWB <span class="required">*</span>
              </label>
              <input 
                type="text"
                formControlName="hawb"
                class="form-control"
                placeholder="Ej: HAW123456"
                [class.error]="envioForm.get('hawb')?.invalid && envioForm.get('hawb')?.touched"
              >
              <div class="error-message" *ngIf="envioForm.get('hawb')?.invalid && envioForm.get('hawb')?.touched">
                El HAWB es requerido
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">
                Comprador <span class="required">*</span>
              </label>
              <select 
                formControlName="comprador"
                class="form-control"
                [class.error]="envioForm.get('comprador')?.invalid && envioForm.get('comprador')?.touched"
              >
                <option value="">Seleccione un comprador</option>
                <option *ngFor="let comprador of compradores" [value]="comprador.id">
                  {{ comprador.nombre }} - {{ comprador.cedula }}
                </option>
              </select>
              <div class="error-message" *ngIf="envioForm.get('comprador')?.invalid && envioForm.get('comprador')?.touched">
                Debe seleccionar un comprador
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">
                Estado <span class="required">*</span>
              </label>
              <select 
                formControlName="estado"
                class="form-control"
              >
                <option [value]="EstadosEnvio.PENDIENTE">Pendiente</option>
                <option [value]="EstadosEnvio.EN_TRANSITO">En Tránsito</option>
                <option [value]="EstadosEnvio.ENTREGADO">Entregado</option>
                <option [value]="EstadosEnvio.CANCELADO">Cancelado</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">
              Observaciones
            </label>
            <textarea 
              formControlName="observaciones"
              class="form-control"
              rows="3"
              placeholder="Observaciones adicionales..."
            ></textarea>
          </div>
        </div>

        <!-- Productos -->
        <div class="form-section">
          <div class="section-header">
            <h4 class="section-title">
              <i class="fas fa-box"></i>
              Productos
            </h4>
            <button 
              type="button"
              class="btn btn-secondary btn-sm"
              (click)="addProducto()"
            >
              <i class="fas fa-plus"></i>
              Agregar Producto
            </button>
          </div>

          <div class="productos-list" formArrayName="productos">
            <div 
              *ngFor="let producto of productos.controls; let i = index" 
              [formGroupName]="i"
              class="producto-item"
            >
              <div class="producto-header">
                <span class="producto-number">Producto #{{ i + 1 }}</span>
                <button 
                  type="button"
                  class="btn-icon btn-delete"
                  (click)="removeProducto(i)"
                  [disabled]="productos.length === 1"
                  title="Eliminar producto"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>

              <div class="form-row">
                <div class="form-group" style="flex: 2;">
                  <label class="form-label">
                    Descripción <span class="required">*</span>
                  </label>
                  <input 
                    type="text"
                    formControlName="descripcion"
                    class="form-control"
                    placeholder="Descripción del producto"
                  >
                </div>

                <div class="form-group">
                  <label class="form-label">
                    Categoría <span class="required">*</span>
                  </label>
                  <select 
                    formControlName="categoria"
                    class="form-control"
                  >
                    <option value="">Seleccionar</option>
                    <option [value]="CategoriasProducto.ELECTRONICA">Electrónica</option>
                    <option [value]="CategoriasProducto.ROPA">Ropa</option>
                    <option [value]="CategoriasProducto.HOGAR">Hogar</option>
                    <option [value]="CategoriasProducto.DEPORTES">Deportes</option>
                    <option [value]="CategoriasProducto.OTROS">Otros</option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">
                    Peso (kg) <span class="required">*</span>
                  </label>
                  <input 
                    type="number"
                    formControlName="peso"
                    class="form-control"
                    min="0.01"
                    step="0.01"
                    placeholder="0.00"
                  >
                </div>

                <div class="form-group">
                  <label class="form-label">
                    Cantidad <span class="required">*</span>
                  </label>
                  <input 
                    type="number"
                    formControlName="cantidad"
                    class="form-control"
                    min="1"
                    placeholder="1"
                  >
                </div>

                <div class="form-group">
                  <label class="form-label">
                    Valor Unitario ($) <span class="required">*</span>
                  </label>
                  <input 
                    type="number"
                    formControlName="valor"
                    class="form-control"
                    min="0"
                    step="0.01"
                    placeholder="0.00"
                  >
                </div>
              </div>
            </div>
          </div>

          <!-- Totales -->
          <div class="totales-section">
            <div class="total-item">
              <span class="total-label">Total Productos:</span>
              <span class="total-value">{{ totalCantidad }}</span>
            </div>
            <div class="total-item">
              <span class="total-label">Peso Total:</span>
              <span class="total-value">{{ totalPeso | number:'1.2-2' }} kg</span>
            </div>
            <div class="total-item">
              <span class="total-label">Valor Total:</span>
              <span class="total-value">{{ totalValor | currency:'USD':'symbol':'1.2-2' }}</span>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div class="alert alert-error" *ngIf="errorMessage">
          <i class="fas fa-exclamation-circle"></i>
          {{ errorMessage }}
        </div>
      </div>

      <div class="modal-footer">
        <button 
          type="button"
          class="btn btn-secondary"
          (click)="closeModal()"
          [disabled]="submitting"
        >
          Cancelar
        </button>
        <button 
          type="submit"
          class="btn btn-primary"
          [disabled]="!envioForm.valid || submitting"
        >
          <i class="fas fa-spinner fa-spin" *ngIf="submitting"></i>
          <i class="fas fa-save" *ngIf="!submitting"></i>
          {{ submitting ? 'Guardando...' : (editingEnvio ? 'Actualizar' : 'Crear') }}
        </button>
      </div>
    </form>
  </div>
</div>

<!-- Modal Detail -->
<div class="modal-overlay" *ngIf="showDetailModal" (click)="closeDetailModal()">
  <div class="modal-content modal-large" (click)="$event.stopPropagation()">
    <div class="modal-header">
      <h3>
        <i class="fas fa-file-alt"></i>
        Detalle del Envío
      </h3>
      <button class="btn-close" (click)="closeDetailModal()">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <div class="modal-body" *ngIf="selectedEnvio">
      <!-- Información General -->
      <div class="detail-section">
        <h4 class="section-title">
          <i class="fas fa-info-circle"></i>
          Información General
        </h4>
        <div class="detail-grid">
          <div class="detail-item">
            <span class="detail-label">HAWB:</span>
            <span class="detail-value">{{ selectedEnvio.hawb }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Estado:</span>
            <span class="badge" [ngClass]="getEstadoClass(selectedEnvio.estado)">
              {{ getEstadoLabel(selectedEnvio.estado) }}
            </span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Fecha de Emisión:</span>
            <span class="detail-value">{{ selectedEnvio.fecha_emision | date:'dd/MM/yyyy HH:mm' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Fecha de Creación:</span>
            <span class="detail-value">{{ selectedEnvio.fecha_creacion | date:'dd/MM/yyyy HH:mm' }}</span>
          </div>
        </div>
      </div>

      <!-- Información del Comprador -->
      <div class="detail-section">
        <h4 class="section-title">
          <i class="fas fa-user"></i>
          Comprador
        </h4>
        <div class="detail-grid">
          <div class="detail-item">
            <span class="detail-label">Nombre:</span>
            <span class="detail-value">{{ selectedEnvio.comprador_info?.nombre }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Cédula:</span>
            <span class="detail-value">{{ selectedEnvio.comprador_info?.cedula }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Correo:</span>
            <span class="detail-value">{{ selectedEnvio.comprador_info?.correo }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Teléfono:</span>
            <span class="detail-value">{{ selectedEnvio.comprador_info?.telefono || 'N/A' }}</span>
          </div>
        </div>
      </div>

      <!-- Productos -->
      <div class="detail-section">
        <h4 class="section-title">
          <i class="fas fa-box"></i>
          Productos ({{ selectedEnvio.productos?.length || 0 }})
        </h4>
        <div class="productos-detail-list">
          <div 
            *ngFor="let producto of selectedEnvio.productos; let i = index" 
            class="producto-detail-item"
          >
            <div class="producto-detail-header">
              <span class="producto-number">#{{ i + 1 }}</span>
              <span class="badge badge-info">{{ getCategoriaLabel(producto.categoria) }}</span>
            </div>
            <div class="producto-detail-body">
              <p class="producto-descripcion">{{ producto.descripcion }}</p>
              <div class="producto-detail-stats">
                <div class="stat">
                  <i class="fas fa-weight"></i>
                  <span>{{ producto.peso }} kg × {{ producto.cantidad }} = {{ producto.peso * producto.cantidad }} kg</span>
                </div>
                <div class="stat">
                  <i class="fas fa-dollar-sign"></i>
                  <span>{{ producto.valor | currency:'USD':'symbol':'1.2-2' }} × {{ producto.cantidad }} = {{ (producto.valor * producto.cantidad) | currency:'USD':'symbol':'1.2-2' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Totales -->
      <div class="detail-section totales-section-detail">
        <div class="total-item-detail">
          <span class="total-label-detail">Total Productos:</span>
          <span class="total-value-detail">{{ selectedEnvio.cantidad_total }}</span>
        </div>
        <div class="total-item-detail">
          <span class="total-label-detail">Peso Total:</span>
          <span class="total-value-detail">{{ selectedEnvio.peso_total | number:'1.2-2' }} kg</span>
        </div>
        <div class="total-item-detail highlight">
          <span class="total-label-detail">Valor Total:</span>
          <span class="total-value-detail">{{ selectedEnvio.valor_total | currency:'USD':'symbol':'1.2-2' }}</span>
        </div>
      </div>

      <!-- Observaciones -->
      <div class="detail-section" *ngIf="selectedEnvio.observaciones">
        <h4 class="section-title">
          <i class="fas fa-comment"></i>
          Observaciones
        </h4>
        <p class="observaciones-text">{{ selectedEnvio.observaciones }}</p>
      </div>
    </div>

    <div class="modal-footer">
      <button 
        type="button"
        class="btn btn-secondary"
        (click)="closeDetailModal()"
      >
        Cerrar
      </button>
    </div>
  </div>
</div>
```

#### `envios-list.component.css`

```css
.envios-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Filters Section */
.filters-section {
  margin-bottom: 20px;
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
  font-size: 0.9rem;
}

/* Results Summary */
.results-summary {
  padding: 12px 0;
  border-top: 1px solid #e5e7eb;
  margin-top: 15px;
}

.results-count {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 0.9rem;
}

/* Alerts */
.alert {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  animation: slideDown 0.3s ease-out;
}

.alert-success {
  background-color: #dcfce7;
  color: #166534;
  border-left: 4px solid #10b981;
}

.alert-error {
  background-color: #fee2e2;
  color: #991b1b;
  border-left: 4px solid #ef4444;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 15px;
  color: #667eea;
}

.loading-state i {
  font-size: 2.5rem;
}

.loading-state span {
  font-size: 1.1rem;
  font-weight: 500;
}

/* Table Container */
.table-container {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 14px 16px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.table th {
  background-color: #f8fafc;
  font-weight: 600;
  color: #374151;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table tbody tr {
  transition: background-color 0.2s;
}

.table tbody tr:hover {
  background-color: #f8fafc;
}

.text-center {
  text-align: center !important;
}

.actions-column {
  width: 180px;
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
  align-items: center;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.btn-view {
  background-color: #dbeafe;
  color: #1e40af;
}

.btn-view:hover {
  background-color: #3b82f6;
  color: white;
}

.btn-edit {
  background-color: #fef3c7;
  color: #92400e;
}

.btn-edit:hover {
  background-color: #f59e0b;
  color: white;
}

.btn-delete {
  background-color: #fee2e2;
  color: #991b1b;
}

.btn-delete:hover {
  background-color: #ef4444;
  color: white;
}

.btn-status {
  background-color: #e0e7ff;
  color: #4338ca;
}

.btn-status:hover {
  background-color: #6366f1;
  color: white;
}

/* Dropdown Estado */
.dropdown-estado {
  position: relative;
}

.dropdown-estado-menu {
  display: none;
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 100;
  min-width: 150px;
  margin-top: 5px;
}

.dropdown-estado:hover .dropdown-estado-menu {
  display: block;
}

.dropdown-estado-menu button {
  width: 100%;
  padding: 10px 15px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 0.9rem;
  color: #374151;
}

.dropdown-estado-menu button:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.dropdown-estado-menu button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: #f9fafb;
}

.no-data {
  text-align: center;
  padding: 60px 20px;
  color: #9ca3af;
}

.no-data i {
  font-size: 3rem;
  margin-bottom: 15px;
  display: block;
}

.no-data p {
  font-size: 1.1rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-top: 1px solid #e5e7eb;
}

.pagination-info {
  font-weight: 500;
  color: #374151;
}

.pagination .btn {
  min-width: 120px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.3s;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: scaleIn 0.3s;
}

.modal-large {
  max-width: 1000px;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.3rem;
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  width: 36px;
  height: 36px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.btn-close:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background-color: #f8fafc;
}

/* Form Sections */
.form-section {
  margin-bottom: 30px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e5e7eb;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
  font-size: 0.9rem;
}

.required {
  color: #ef4444;
}

.form-control {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-control.error {
  border-color: #ef4444;
}

.error-message {
  margin-top: 6px;
  color: #ef4444;
  font-size: 0.85rem;
}

textarea.form-control {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

/* Productos List */
.productos-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.producto-item {
  background-color: #f8fafc;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  transition: border-color 0.2s;
}

.producto-item:hover {
  border-color: #cbd5e1;
}

.producto-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e5e7eb;
}

.producto-number {
  font-weight: 600;
  color: #667eea;
  font-size: 0.95rem;
}

/* Totales */
.totales-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.total-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.total-label {
  font-weight: 500;
  font-size: 1rem;
}

.total-value {
  font-weight: 700;
  font-size: 1.2rem;
}

/* Detail View */
.detail-section {
  margin-bottom: 30px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-label {
  font-weight: 600;
  color: #6b7280;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  font-size: 1rem;
  color: #1e293b;
  font-weight: 500;
}

.productos-detail-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 15px;
}

.producto-detail-item {
  background-color: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
}

.producto-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.producto-detail-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.producto-descripcion {
  font-weight: 500;
  color: #1e293b;
  margin: 0;
  font-size: 1rem;
}

.producto-detail-stats {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
  font-size: 0.9rem;
}

.stat i {
  color: #667eea;
}

.totales-section-detail {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  border-radius: 8px;
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 20px;
}

.total-item-detail {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.total-item-detail.highlight {
  flex: 1 1 100%;
  border-top: 1px solid rgba(255, 255, 255, 0.3);
  padding-top: 15px;
  margin-top: 10px;
}

.total-label-detail {
  font-size: 0.9rem;
  opacity: 0.9;
}

.total-value-detail {
  font-size: 1.5rem;
  font-weight: 700;
}

.observaciones-text {
  background-color: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  color: #374151;
  line-height: 1.6;
  margin: 10px 0 0 0;
}

/* Responsive */
@media (max-width: 768px) {
  .filter-row {
    grid-template-columns: 1fr;
  }

  .table-container {
    overflow-x: scroll;
  }

  .table {
    min-width: 900px;
  }

  .modal-content {
    width: 95%;
    max-height: 95vh;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-wrap: wrap;
  }

  .totales-section-detail {
    flex-direction: column;
  }
}

/* Utilities */
.btn-sm {
  padding: 6px 12px;
  font-size: 0.85rem;
}

.mb-3 {
  margin-bottom: 1rem;
}

.mt-3 {
  margin-top: 1rem;
}
```

---

### 📦 PRODUCTOS-LIST COMPONENT

#### `productos-list.component.html`

```html
<div class="productos-container">
  <!-- Header -->
  <div class="card">
    <div class="card-header">
      <h2 class="card-title">
        <i class="fas fa-box"></i>
        Gestión de Productos
      </h2>
      <button 
        class="btn btn-primary"
        (click)="openCreateModal()"
      >
        <i class="fas fa-plus"></i>
        Nuevo Producto
      </button>
    </div>

    <!-- Filters -->
    <div class="filters-section">
      <div class="filter-row">
        <!-- Search -->
        <div class="filter-group">
          <label class="filter-label">
            <i class="fas fa-search"></i>
            Buscar
          </label>
          <input 
            type="text"
            class="form-control"
            [(ngModel)]="searchTerm"
            (input)="onSearchChange()"
            placeholder="Descripción del producto..."
          >
        </div>

        <!-- Categoria Filter -->
        <div class="filter-group">
          <label class="filter-label">
            <i class="fas fa-filter"></i>
            Categoría
          </label>
          <select 
            class="form-control"
            [(ngModel)]="selectedCategoria"
            (change)="onCategoriaFilterChange()"
          >
            <option value="">Todas las categorías</option>
            <option [value]="CategoriasProducto.ELECTRONICA">Electrónica</option>
            <option [value]="CategoriasProducto.ROPA">Ropa</option>
            <option [value]="CategoriasProducto.HOGAR">Hogar</option>
            <option [value]="CategoriasProducto.DEPORTES">Deportes</option>
            <option [value]="CategoriasProducto.OTROS">Otros</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Results Summary -->
    <div class="results-summary">
      <span class="results-count">
        <i class="fas fa-list"></i>
        Mostrando {{ paginatedProductos.length }} de {{ filteredProductos.length }} productos
      </span>
    </div>
  </div>

  <!-- Success Message -->
  <div class="alert alert-success" *ngIf="successMessage">
    <i class="fas fa-check-circle"></i>
    {{ successMessage }}
  </div>

  <!-- Error Message -->
  <div class="alert alert-error" *ngIf="errorMessage">
    <i class="fas fa-exclamation-circle"></i>
    {{ errorMessage }}
  </div>

  <!-- Loading State -->
  <div class="loading-state" *ngIf="loading">
    <i class="fas fa-spinner fa-spin"></i>
    <span>Cargando productos...</span>
  </div>

  <!-- Products Grid -->
  <div class="productos-grid" *ngIf="!loading">
    <div 
      *ngFor="let producto of paginatedProductos" 
      class="producto-card"
    >
      <div class="producto-card-header">
        <span class="badge" [ngClass]="'categoria-' + producto.categoria">
          {{ getCategoriaLabel(producto.categoria) }}
        </span>
        <div class="producto-actions">
          <button 
            class="btn-icon btn-edit"
            (click)="editProducto(producto)"
            title="Editar"
          >
            <i class="fas fa-edit"></i>
          </button>
          <button 
            class="btn-icon btn-delete"
            (click)="deleteProducto(producto)"
            title="Eliminar"
          >
            <i class="fas fa-trash"></i>
          </button>
        </div>
      </div>

      <div class="producto-card-body">
        <h3 class="producto-title">{{ producto.descripcion }}</h3>
        
        <div class="producto-stats">
          <div class="stat-item">
            <i class="fas fa-weight-hanging"></i>
            <div class="stat-content">
              <span class="stat-label">Peso</span>
              <span class="stat-value">{{ producto.peso }} kg</span>
            </div>
          </div>

          <div class="stat-item">
            <i class="fas fa-boxes"></i>
            <div class="stat-content">
              <span class="stat-label">Cantidad</span>
              <span class="stat-value">{{ producto.cantidad }}</span>
            </div>
          </div>

          <div class="stat-item">
            <i class="fas fa-dollar-sign"></i>
            <div class="stat-content">
              <span class="stat-label">Valor Unit.</span>
              <span class="stat-value">{{ producto.valor | currency:'USD':'symbol':'1.2-2' }}</span>
            </div>
          </div>
        </div>

        <div class="producto-totals">
          <div class="total-row">
            <span>Peso Total:</span>
            <strong>{{ getPesoTotal(producto) | number:'1.2-2' }} kg</strong>
          </div>
          <div class="total-row highlight">
            <span>Valor Total:</span>
            <strong>{{ getValorTotal(producto) | currency:'USD':'symbol':'1.2-2' }}</strong>
          </div>
        </div>
      </div>

      <div class="producto-card-footer">
        <small class="producto-date">
          <i class="fas fa-calendar"></i>
          {{ producto.fecha_creacion | date:'dd/MM/yyyy' }}
        </small>
      </div>
    </div>

    <!-- No Data -->
    <div class="no-data-card" *ngIf="filteredProductos.length === 0">
      <i class="fas fa-box-open"></i>
      <h3>No se encontraron productos</h3>
      <p>Intenta cambiar los filtros de búsqueda</p>
    </div>
  </div>

  <!-- Pagination -->
  <div class="card" *ngIf="!loading && totalPages > 1">
    <div class="pagination">
      <button 
        class="btn btn-secondary"
        (click)="previousPage()"
        [disabled]="currentPage === 1"
      >
        <i class="fas fa-chevron-left"></i>
        Anterior
      </button>
      
      <span class="pagination-info">
        Página {{ currentPage }} de {{ totalPages }}
      </span>
      
      <button 
        class="btn btn-secondary"
        (click)="nextPage()"
        [disabled]="currentPage === totalPages"
      >
        Siguiente
        <i class="fas fa-chevron-right"></i>
      </button>
    </div>
  </div>
</div>

<!-- Modal Create/Edit -->
<div class="modal-overlay" *ngIf="showModal" (click)="closeModal()">
  <div class="modal-content" (click)="$event.stopPropagation()">
    <div class="modal-header">
      <h3>
        <i class="fas fa-box"></i>
        {{ editingProducto ? 'Editar Producto' : 'Nuevo Producto' }}
      </h3>
      <button class="btn-close" (click)="closeModal()">
        <i class="fas fa-times"></i>
      </button>
    </div>

    <form [formGroup]="productoForm" (ngSubmit)="onSubmit()">
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">
            Descripción <span class="required">*</span>
          </label>
          <input 
            type="text"
            formControlName="descripcion"
            class="form-control"
            placeholder="Ej: Laptop HP Pavilion 15.6..."
            [class.error]="productoForm.get('descripcion')?.invalid && productoForm.get('descripcion')?.touched"
          >
          <div class="error-message" *ngIf="productoForm.get('descripcion')?.invalid && productoForm.get('descripcion')?.touched">
            La descripción es requerida
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">
            Categoría <span class="required">*</span>
          </label>
          <select 
            formControlName="categoria"
            class="form-control"
            [class.error]="productoForm.get('categoria')?.invalid && productoForm.get('categoria')?.touched"
          >
            <option value="">Seleccione una categoría</option>
            <option [value]="CategoriasProducto.ELECTRONICA">
              <i class="fas fa-laptop"></i> Electrónica
            </option>
            <option [value]="CategoriasProducto.ROPA">
              <i class="fas fa-tshirt"></i> Ropa
            </option>
            <option [value]="CategoriasProducto.HOGAR">
              <i class="fas fa-home"></i> Hogar
            </option>
            <option [value]="CategoriasProducto.DEPORTES">
              <i class="fas fa-futbol"></i> Deportes
            </option>
            <option [value]="CategoriasProducto.OTROS">
              <i class="fas fa-box"></i> Otros
            </option>
          </select>
          <div class="error-message" *ngIf="productoForm.get('categoria')?.invalid && productoForm.get('categoria')?.touched">
            Debe seleccionar una categoría
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">
              Peso (kg) <span class="required">*</span>
            </label>
            <input 
              type="number"
              formControlName="peso"
              class="form-control"
              min="0.01"
              step="0.01"
              placeholder="0.00"
              [class.error]="productoForm.get('peso')?.invalid && productoForm.get('peso')?.touched"
            >
            <div class="error-message" *ngIf="productoForm.get('peso')?.invalid && productoForm.get('peso')?.touched">
              El peso debe ser mayor a 0
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">
              Cantidad <span class="required">*</span>
            </label>
            <input 
              type="number"
              formControlName="cantidad"
              class="form-control"
              min="1"
              placeholder="1"
              [class.error]="productoForm.get('cantidad')?.invalid && productoForm.get('cantidad')?.touched"
            >
            <div class="error-message" *ngIf="productoForm.get('cantidad')?.invalid && productoForm.get('cantidad')?.touched">
              La cantidad debe ser al menos 1
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">
              Valor Unitario ($) <span class="required">*</span>
            </label>
            <input 
              type="number"
              formControlName="valor"
              class="form-control"
              min="0"
              step="0.01"
              placeholder="0.00"
              [class.error]="productoForm.get('valor')?.invalid && productoForm.get('valor')?.touched"
            >
            <div class="error-message" *ngIf="productoForm.get('valor')?.invalid && productoForm.get('valor')?.touched">
              El valor debe ser mayor o igual a 0
            </div>
          </div>
        </div>

        <!-- Preview de Totales -->
        <div class="totales-preview" *ngIf="productoForm.get('peso')?.value && productoForm.get('cantidad')?.value && productoForm.get('valor')?.value">
          <h4>Totales Calculados</h4>
          <div class="preview-row">
            <span>Peso Total:</span>
            <strong>{{ (productoForm.get('peso')?.value * productoForm.get('cantidad')?.value) | number:'1.2-2' }} kg</strong>
          </div>
          <div class="preview-row highlight">
            <span>Valor Total:</span>
            <strong>{{ (productoForm.get('valor')?.value * productoForm.get('cantidad')?.value) | currency:'USD':'symbol':'1.2-2' }}</strong>
          </div>
        </div>

        <!-- Error Message -->
        <div class="alert alert-error" *ngIf="errorMessage">
          <i class="fas fa-exclamation-circle"></i>
          {{ errorMessage }}
        </div>
      </div>

      <div class="modal-footer">
        <button 
          type="button"
          class="btn btn-secondary"
          (click)="closeModal()"
          [disabled]="submitting"
        >
          Cancelar
        </button>
        <button 
          type="submit"
          class="btn btn-primary"
          [disabled]="!productoForm.valid || submitting"
        >
          <i class="fas fa-spinner fa-spin" *ngIf="submitting"></i>
          <i class="fas fa-save" *ngIf="!submitting"></i>
          {{ submitting ? 'Guardando...' : (editingProducto ? 'Actualizar' : 'Crear') }}
        </button>
      </div>
    </form>
  </div>
</div>
```

#### `productos-list.component.css`

```css
.productos-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Filters Section */
.filters-section {
  margin-bottom: 20px;
}

.filter-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 15px;
}

.filter-group {
  display: flex;
  flex-direction: column;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
  font-size: 0.9rem;
}

/* Results Summary */
.results-summary {
  padding: 12px 0;
  border-top: 1px solid #e5e7eb;
  margin-top: 15px;
}

.results-count {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
  font-size: 0.9rem;
}

/* Alerts */
.alert {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
  animation: slideDown 0.3s ease-out;
}

.alert-success {
  background-color: #dcfce7;
  color: #166534;
  border-left: 4px solid #10b981;
}

.alert-error {
  background-color: #fee2e2;
  color: #991b1b;
  border-left: 4px solid #ef4444;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 15px;
  color: #667eea;
}

.loading-state i {
  font-size: 2.5rem;
}

.loading-state span {
  font-size: 1.1rem;
  font-weight: 500;
}

/* Products Grid */
.productos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.producto-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.producto-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
}

.producto-card-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #f8fafc 0%, #e5e7eb 100%);
  border-bottom: 2px solid #e5e7eb;
}

.producto-actions {
  display: flex;
  gap: 8px;
}

.producto-card-body {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.producto-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.producto-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background-color: #f8fafc;
  border-radius: 8px;
}

.stat-item i {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 6px;
  font-size: 0.9rem;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
}

.producto-totals {
  margin-top: auto;
  padding-top: 16px;
  border-top: 2px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.95rem;
  color: #374151;
}

.total-row.highlight {
  font-size: 1.1rem;
  color: #667eea;
  padding: 10px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 6px;
  margin-top: 4px;
}

.total-row.highlight strong {
  font-size: 1.2rem;
}

.producto-card-footer {
  padding: 12px 16px;
  background-color: #f8fafc;
  border-top: 1px solid #e5e7eb;
}

.producto-date {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
  font-size: 0.85rem;
}

/* Category Badges */
.badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.categoria-electronica {
  background-color: #dbeafe;
  color: #1e40af;
}

.categoria-ropa {
  background-color: #fce7f3;
  color: #9f1239;
}

.categoria-hogar {
  background-color: #d1fae5;
  color: #065f46;
}

.categoria-deportes {
  background-color: #fef3c7;
  color: #92400e;
}

.categoria-otros {
  background-color: #e0e7ff;
  color: #4338ca;
}

/* No Data Card */
.no-data-card {
  grid-column: 1 / -1;
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.no-data-card i {
  font-size: 4rem;
  color: #cbd5e1;
  margin-bottom: 20px;
}

.no-data-card h3 {
  color: #64748b;
  margin-bottom: 8px;
}

.no-data-card p {
  color: #94a3b8;
}

/* Action Buttons */
.btn-icon {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.btn-edit {
  background-color: #fef3c7;
  color: #92400e;
}

.btn-edit:hover {
  background-color: #f59e0b;
  color: white;
}

.btn-delete {
  background-color: #fee2e2;
  color: #991b1b;
}

.btn-delete:hover {
  background-color: #ef4444;
  color: white;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.pagination-info {
  font-weight: 500;
  color: #374151;
}

.pagination .btn {
  min-width: 120px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.3s;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: scaleIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.3rem;
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  width: 36px;
  height: 36px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.btn-close:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background-color: #f8fafc;
}

/* Form Styles */
.form-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
  font-size: 0.9rem;
}

.required {
  color: #ef4444;
}

.form-control {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-control.error {
  border-color: #ef4444;
}

.error-message {
  margin-top: 6px;
  color: #ef4444;
  font-size: 0.85rem;
}

/* Totales Preview */
.totales-preview {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.totales-preview h4 {
  margin: 0 0 15px 0;
  font-size: 1rem;
  font-weight: 600;
  opacity: 0.9;
}

.preview-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.preview-row.highlight {
  padding-top: 15px;
  margin-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.3);
  font-size: 1.1rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .productos-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}

@media (max-width: 768px) {
  .filter-row {
    grid-template-columns: 1fr;
  }

  .productos-grid {
    grid-template-columns: 1fr;
  }

  .modal-content {
    width: 95%;
    max-height: 95vh;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .producto-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN FINAL

### Ya Implementado ✅
- [x] auth.guard.ts
- [x] role.guard.ts
- [x] environment.ts y environment.prod.ts
- [x] auth.interceptor.ts
- [x] envios-list.component.ts
- [x] productos-list.component.ts
- [x] app.component.css (estilos movidos)

### Pendiente de Actualizar 📝
- [ ] Actualizar `auth.service.ts` para usar `environment`
- [ ] Actualizar `api.service.ts` para usar `environment`
- [ ] Actualizar `app.config.ts` para incluir interceptores
- [ ] Actualizar `app.routes.ts` para usar guards
- [ ] Actualizar `angular.json` para configurar environments
- [ ] Crear `envios-list.component.html` (código proporcionado arriba)
- [ ] Crear `envios-list.component.css` (código proporcionado arriba)
- [ ] Crear `productos-list.component.html` (código proporcionado arriba)
- [ ] Crear `productos-list.component.css` (código proporcionado arriba)

---

## 🎯 ESTADO FINAL ESTIMADO

Con estas implementaciones completarás:

```
Completitud actual: 50% → 85%
Calificación: 6/10 → 9/10 ✨

✅ Login: 95%
✅ Dashboard: 80%
✅ Usuarios: 95%
✅ Envíos: 95% (con templates)
✅ Productos: 95% (con templates)
✅ Seguridad: 85% (con guards y interceptores)
```

---

## 🚀 PRÓXIMOS PASOS RECOMENDADOS

1. Copiar los templates HTML y CSS proporcionados
2. Actualizar los servicios para usar environments
3. Configurar angular.json
4. Actualizar app.routes.ts con los guards
5. Probar la aplicación completa
6. (Opcional) Implementar sistema de notificaciones

---

**¡Excelente trabajo! Estás muy cerca de tener un MVP completamente funcional! 🎉**

