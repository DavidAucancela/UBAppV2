# 📝 Ejemplo de Formulario con Selector de Ubicaciones

## Implementación Completa para Crear/Editar Usuarios

### 1. Component TypeScript

```typescript
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { UbicacionesService } from '../services/ubicaciones.service';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-usuario-form',
  templateUrl: './usuario-form.component.html'
})
export class UsuarioFormComponent implements OnInit {
  usuarioForm: FormGroup;
  
  // Listas para los selectores
  provincias: string[] = [];
  cantones: string[] = [];
  ciudades: string[] = [];
  
  // Estado de carga
  loadingCantones = false;
  loadingCiudades = false;

  constructor(
    private fb: FormBuilder,
    private ubicacionesService: UbicacionesService,
    private apiService: ApiService
  ) {
    this.usuarioForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      nombre: ['', [Validators.required]],
      correo: ['', [Validators.required, Validators.email]],
      cedula: ['', [Validators.required, Validators.pattern(/^\d{10}$/)]],
      rol: [4, Validators.required],
      telefono: [''],
      provincia: ['', Validators.required],
      canton: ['', Validators.required],
      ciudad: ['', Validators.required],
      latitud: [null],
      longitud: [null],
      password: ['', [Validators.required, Validators.minLength(8)]],
      password_confirm: ['', Validators.required]
    });
  }

  ngOnInit() {
    // Cargar provincias al iniciar
    this.cargarProvincias();
  }

  cargarProvincias() {
    this.ubicacionesService.getProvincias().subscribe({
      next: (data) => {
        this.provincias = data.provincias || [];
      },
      error: (error) => {
        console.error('Error cargando provincias:', error);
      }
    });
  }

  onProvinciaChange(event: Event) {
    const provincia = (event.target as HTMLSelectElement).value;
    
    // Limpiar cantones y ciudades
    this.usuarioForm.patchValue({
      canton: '',
      ciudad: '',
      latitud: null,
      longitud: null
    });
    this.cantones = [];
    this.ciudades = [];
    
    if (!provincia) return;
    
    // Cargar cantones de la provincia seleccionada
    this.loadingCantones = true;
    this.ubicacionesService.getCantones(provincia).subscribe({
      next: (data) => {
        this.cantones = data.cantones || [];
        this.loadingCantones = false;
      },
      error: (error) => {
        console.error('Error cargando cantones:', error);
        this.loadingCantones = false;
      }
    });
  }

  onCantonChange(event: Event) {
    const canton = (event.target as HTMLSelectElement).value;
    const provincia = this.usuarioForm.get('provincia')?.value;
    
    // Limpiar ciudades
    this.usuarioForm.patchValue({
      ciudad: '',
      latitud: null,
      longitud: null
    });
    this.ciudades = [];
    
    if (!canton || !provincia) return;
    
    // Cargar ciudades del cantón seleccionado
    this.loadingCiudades = true;
    this.ubicacionesService.getCiudades(provincia, canton).subscribe({
      next: (data) => {
        this.ciudades = data.ciudades || [];
        this.loadingCiudades = false;
      },
      error: (error) => {
        console.error('Error cargando ciudades:', error);
        this.loadingCiudades = false;
      }
    });
  }

  onCiudadChange(event: Event) {
    const ciudad = (event.target as HTMLSelectElement).value;
    const provincia = this.usuarioForm.get('provincia')?.value;
    const canton = this.usuarioForm.get('canton')?.value;
    
    if (!ciudad || !provincia || !canton) return;
    
    // Obtener coordenadas de la ciudad seleccionada
    this.ubicacionesService.getCoordenadas(provincia, canton, ciudad).subscribe({
      next: (data) => {
        this.usuarioForm.patchValue({
          latitud: data.latitud,
          longitud: data.longitud
        });
        console.log('Coordenadas asignadas:', data);
      },
      error: (error) => {
        console.error('Error obteniendo coordenadas:', error);
      }
    });
  }

  onSubmit() {
    if (this.usuarioForm.invalid) {
      this.markFormGroupTouched(this.usuarioForm);
      return;
    }

    const usuario = this.usuarioForm.value;
    
    this.apiService.createUsuario(usuario).subscribe({
      next: (response) => {
        console.log('Usuario creado:', response);
        // Redirigir o mostrar mensaje de éxito
      },
      error: (error) => {
        console.error('Error creando usuario:', error);
        // Mostrar mensaje de error
      }
    });
  }

  private markFormGroupTouched(formGroup: FormGroup) {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();
      if (control instanceof FormGroup) {
        this.markFormGroupTouched(control);
      }
    });
  }
}
```

### 2. Template HTML

```html
<div class="form-container">
  <h2>Crear Usuario</h2>
  
  <form [formGroup]="usuarioForm" (ngSubmit)="onSubmit()">
    
    <!-- Información Básica -->
    <div class="form-section">
      <h3>Información Básica</h3>
      
      <div class="form-group">
        <label for="username">Usuario *</label>
        <input 
          type="text" 
          id="username" 
          formControlName="username"
          class="form-control"
          [class.invalid]="usuarioForm.get('username')?.invalid && usuarioForm.get('username')?.touched"
        >
        <small class="error" *ngIf="usuarioForm.get('username')?.invalid && usuarioForm.get('username')?.touched">
          Usuario requerido (mínimo 3 caracteres)
        </small>
      </div>

      <div class="form-group">
        <label for="nombre">Nombre Completo *</label>
        <input 
          type="text" 
          id="nombre" 
          formControlName="nombre"
          class="form-control"
          [class.invalid]="usuarioForm.get('nombre')?.invalid && usuarioForm.get('nombre')?.touched"
        >
        <small class="error" *ngIf="usuarioForm.get('nombre')?.invalid && usuarioForm.get('nombre')?.touched">
          Nombre es requerido
        </small>
      </div>

      <div class="form-group">
        <label for="correo">Correo Electrónico *</label>
        <input 
          type="email" 
          id="correo" 
          formControlName="correo"
          class="form-control"
          [class.invalid]="usuarioForm.get('correo')?.invalid && usuarioForm.get('correo')?.touched"
        >
        <small class="error" *ngIf="usuarioForm.get('correo')?.invalid && usuarioForm.get('correo')?.touched">
          Correo válido requerido
        </small>
      </div>

      <div class="form-group">
        <label for="cedula">Cédula *</label>
        <input 
          type="text" 
          id="cedula" 
          formControlName="cedula"
          class="form-control"
          placeholder="0123456789"
          maxlength="10"
          [class.invalid]="usuarioForm.get('cedula')?.invalid && usuarioForm.get('cedula')?.touched"
        >
        <small class="error" *ngIf="usuarioForm.get('cedula')?.invalid && usuarioForm.get('cedula')?.touched">
          Cédula ecuatoriana de 10 dígitos requerida
        </small>
      </div>

      <div class="form-group">
        <label for="telefono">Teléfono</label>
        <input 
          type="tel" 
          id="telefono" 
          formControlName="telefono"
          class="form-control"
          placeholder="0999999999"
        >
      </div>

      <div class="form-group">
        <label for="rol">Rol *</label>
        <select id="rol" formControlName="rol" class="form-control">
          <option [value]="1">Admin</option>
          <option [value]="2">Gerente</option>
          <option [value]="3">Digitador</option>
          <option [value]="4">Comprador</option>
        </select>
      </div>
    </div>

    <!-- Ubicación Geográfica -->
    <div class="form-section">
      <h3>📍 Ubicación Geográfica</h3>
      <p class="section-description">Seleccione la ubicación del usuario de forma jerárquica</p>
      
      <div class="form-group">
        <label for="provincia">Provincia *</label>
        <select 
          id="provincia" 
          formControlName="provincia"
          (change)="onProvinciaChange($event)"
          class="form-control"
          [class.invalid]="usuarioForm.get('provincia')?.invalid && usuarioForm.get('provincia')?.touched"
        >
          <option value="">Seleccione una provincia</option>
          <option *ngFor="let prov of provincias" [value]="prov">
            {{ prov }}
          </option>
        </select>
        <small class="error" *ngIf="usuarioForm.get('provincia')?.invalid && usuarioForm.get('provincia')?.touched">
          Provincia es requerida
        </small>
      </div>

      <div class="form-group">
        <label for="canton">
          Cantón *
          <span class="loading-indicator" *ngIf="loadingCantones">
            <i class="fas fa-spinner fa-spin"></i> Cargando...
          </span>
        </label>
        <select 
          id="canton" 
          formControlName="canton"
          (change)="onCantonChange($event)"
          class="form-control"
          [disabled]="cantones.length === 0"
          [class.invalid]="usuarioForm.get('canton')?.invalid && usuarioForm.get('canton')?.touched"
        >
          <option value="">
            {{ cantones.length === 0 ? 'Primero seleccione una provincia' : 'Seleccione un cantón' }}
          </option>
          <option *ngFor="let cant of cantones" [value]="cant">
            {{ cant }}
          </option>
        </select>
        <small class="error" *ngIf="usuarioForm.get('canton')?.invalid && usuarioForm.get('canton')?.touched">
          Cantón es requerido
        </small>
      </div>

      <div class="form-group">
        <label for="ciudad">
          Ciudad *
          <span class="loading-indicator" *ngIf="loadingCiudades">
            <i class="fas fa-spinner fa-spin"></i> Cargando...
          </span>
        </label>
        <select 
          id="ciudad" 
          formControlName="ciudad"
          (change)="onCiudadChange($event)"
          class="form-control"
          [disabled]="ciudades.length === 0"
          [class.invalid]="usuarioForm.get('ciudad')?.invalid && usuarioForm.get('ciudad')?.touched"
        >
          <option value="">
            {{ ciudades.length === 0 ? 'Primero seleccione un cantón' : 'Seleccione una ciudad' }}
          </option>
          <option *ngFor="let ciud of ciudades" [value]="ciud">
            {{ ciud }}
          </option>
        </select>
        <small class="error" *ngIf="usuarioForm.get('ciudad')?.invalid && usuarioForm.get('ciudad')?.touched">
          Ciudad es requerida
        </small>
      </div>

      <!-- Mostrar coordenadas (read-only) -->
      <div class="coordenadas-display" *ngIf="usuarioForm.get('latitud')?.value">
        <div class="coordenadas-badge">
          <i class="fas fa-map-marker-alt"></i>
          <span>
            Coordenadas: {{ usuarioForm.get('latitud')?.value | number:'1.4-4' }}, 
            {{ usuarioForm.get('longitud')?.value | number:'1.4-4' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Seguridad -->
    <div class="form-section">
      <h3>🔒 Seguridad</h3>
      
      <div class="form-group">
        <label for="password">Contraseña *</label>
        <input 
          type="password" 
          id="password" 
          formControlName="password"
          class="form-control"
          [class.invalid]="usuarioForm.get('password')?.invalid && usuarioForm.get('password')?.touched"
        >
        <small class="error" *ngIf="usuarioForm.get('password')?.invalid && usuarioForm.get('password')?.touched">
          Contraseña requerida (mínimo 8 caracteres)
        </small>
      </div>

      <div class="form-group">
        <label for="password_confirm">Confirmar Contraseña *</label>
        <input 
          type="password" 
          id="password_confirm" 
          formControlName="password_confirm"
          class="form-control"
          [class.invalid]="usuarioForm.get('password_confirm')?.invalid && usuarioForm.get('password_confirm')?.touched"
        >
      </div>
    </div>

    <!-- Botones -->
    <div class="form-actions">
      <button type="button" class="btn btn-secondary" routerLink="/usuarios">
        Cancelar
      </button>
      <button type="submit" class="btn btn-primary" [disabled]="usuarioForm.invalid">
        <i class="fas fa-save"></i>
        Guardar Usuario
      </button>
    </div>
  </form>
</div>
```

### 3. Estilos CSS

```css
.form-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 30px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-container h2 {
  margin: 0 0 30px 0;
  color: #1f2937;
  font-size: 28px;
  border-bottom: 3px solid #3b82f6;
  padding-bottom: 15px;
}

.form-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
}

.form-section h3 {
  margin: 0 0 15px 0;
  color: #374151;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-description {
  margin: 0 0 20px 0;
  color: #6b7280;
  font-size: 14px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #374151;
  font-weight: 600;
  font-size: 14px;
}

.form-control {
  width: 100%;
  padding: 10px 15px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-control:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
  color: #9ca3af;
}

.form-control.invalid {
  border-color: #ef4444;
}

.form-control.invalid:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.error {
  display: block;
  margin-top: 5px;
  color: #ef4444;
  font-size: 12px;
}

.loading-indicator {
  margin-left: 8px;
  color: #3b82f6;
  font-size: 12px;
  font-weight: normal;
}

.coordenadas-display {
  margin-top: 15px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  border: 2px solid #10b981;
}

.coordenadas-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #059669;
  font-weight: 600;
}

.coordenadas-badge i {
  font-size: 18px;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px solid #e5e7eb;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 2px solid #e5e7eb;
}

.btn-secondary:hover {
  background: #e5e7eb;
  border-color: #d1d5db;
}
```

### 4. Uso en el Módulo

```typescript
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule
  ],
  // ...
})
```

---

## ✅ Características

✅ **Selectores Jerárquicos:** Provincia → Cantón → Ciudad  
✅ **Carga Dinámica:** Los cantones y ciudades se cargan según la selección previa  
✅ **Coordenadas Automáticas:** Se asignan automáticamente al seleccionar la ciudad  
✅ **Validaciones:** Todos los campos requeridos validados  
✅ **Feedback Visual:** Estados de carga, errores, y éxito  
✅ **Responsive:** Se adapta a diferentes tamaños de pantalla  
✅ **Accesibilidad:** Labels, placeholders y mensajes de error claros  

---

## 🔄 Para Editar Usuario Existente

Simplemente carga los valores en `ngOnInit`:

```typescript
ngOnInit() {
  this.cargarProvincias();
  
  if (this.usuarioId) {
    this.apiService.getUsuario(this.usuarioId).subscribe(usuario => {
      // Cargar datos del usuario
      this.usuarioForm.patchValue(usuario);
      
      // Cargar cantones de la provincia
      if (usuario.provincia) {
        this.ubicacionesService.getCantones(usuario.provincia).subscribe(data => {
          this.cantones = data.cantones || [];
        });
      }
      
      // Cargar ciudades del cantón
      if (usuario.provincia && usuario.canton) {
        this.ubicacionesService.getCiudades(usuario.provincia, usuario.canton).subscribe(data => {
          this.ciudades = data.ciudades || [];
        });
      }
    });
  }
}
```

---

**¡Formulario completo y listo para usar! 📝✨**





