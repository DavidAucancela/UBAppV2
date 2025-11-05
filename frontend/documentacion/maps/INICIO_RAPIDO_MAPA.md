# 🚀 Inicio Rápido - Mapa de Compradores

## Pasos para Probar el Mapa

### 1. Asegúrate de que las migraciones estén aplicadas

```bash
cd backend
python manage.py migrate
```

### 2. Asigna ubicaciones a los compradores existentes

```bash
python manage.py actualizar_ubicaciones --random
```

**Salida esperada:**
```
✓ dav → Guayaquil (-2.18..., -79.88...)
✓ Jacquelien Tene → Manta (-0.96..., -80.70...)
✓ pedro → Ibarra (0.34..., -78.12...)

✓ Proceso completado: 3 compradores actualizados
```

### 3. Inicia el servidor backend

```bash
# Desde backend/
python manage.py runserver
```

El servidor estará disponible en: `http://localhost:8000`

### 4. Inicia el servidor frontend

```bash
# Desde frontend/
ng serve
```

El frontend estará disponible en: `http://localhost:4200`

### 5. Accede al sistema

1. Abre tu navegador en: `http://localhost:4200`
2. Inicia sesión con:
   - **Admin**, **Gerente** o **Digitador**
   - Ejemplo: usuario `admin` (consulta tus credenciales)

### 6. Navega al Mapa

**Opción 1: Desde el Dashboard**
- En la pantalla de inicio, verás una tarjeta verde: **"Mapa de Compradores"**
- Haz clic en ella

**Opción 2: URL Directa**
- Navega a: `http://localhost:4200/mapa-compradores`

## 🎯 Qué Verás

### Vista Inicial
- Mapa de Ecuador centrado
- Marcadores azules (📍) en ciudades con compradores
- Panel de estadísticas arriba
- Leyenda en la esquina superior derecha

### Interacción
1. **Haz clic en una ciudad** (marcador azul 📍)
   - Se abrirá un popup con información
   - El mapa hará zoom automático

2. **Observa los compradores** (marcadores verdes 👤)
   - Cada comprador tiene su propio marcador
   - Están distribuidos para evitar superposición

3. **Haz clic en un comprador** (marcador verde 👤)
   - Verás su información personal
   - Verás sus últimos 5 envíos
   - Cada envío muestra HAWB, estado, peso, valor

4. **Usa los controles**
   - **🏠 Vista General**: Vuelve a la vista completa
   - **🔄 Recargar**: Actualiza los datos

## 🔧 Solución de Problemas

### El mapa no aparece
```bash
# Verifica que Leaflet esté instalado
cd frontend
npm list leaflet
# Si no está, instálalo
npm install leaflet @types/leaflet
```

### No veo compradores en el mapa
```bash
# Asigna ubicaciones
cd backend
python manage.py actualizar_ubicaciones --random
```

### Error 403 (Forbidden)
- Asegúrate de estar logueado como **Admin**, **Gerente** o **Digitador**
- Los **Compradores** no tienen acceso al mapa

### El mapa se ve sin estilos
- Verifica que `angular.json` incluya los estilos de Leaflet
- Reinicia el servidor de desarrollo: `ng serve`

## 📊 Agregar Más Datos de Prueba

Si quieres más compradores en el mapa:

```bash
# 1. Crea nuevos compradores desde el sistema o Django admin
# 2. Asigna ubicaciones
cd backend
python manage.py actualizar_ubicaciones --random
```

## 🎨 Características para Probar

### Zoom
- Usa la rueda del mouse para hacer zoom in/out
- Observa cómo cambian los marcadores según el nivel de zoom

### Popups
- Los popups de ciudad muestran información agregada
- Los popups de comprador muestran información detallada con envíos

### Estadísticas
- El panel superior muestra estadísticas en tiempo real
- Se actualiza cuando recargas los datos

### Lista de Resumen
- Desplázate hacia abajo para ver la lista de ciudades
- Muestra un resumen de compradores por ciudad

## 📱 Prueba en Diferentes Dispositivos

El mapa es responsive:
- **Desktop**: Experiencia completa
- **Tablet**: Diseño adaptado
- **Mobile**: Interfaz optimizada

## 🎯 Puntos Clave

✅ El mapa es **totalmente funcional** e **interactivo**  
✅ Los datos vienen de la **base de datos real**  
✅ Los envíos se muestran **dentro del popup**  
✅ Funciona con **cualquier número de compradores**  
✅ Las **ubicaciones son reales** de Ecuador

## 🌟 Funcionalidades Avanzadas

### Filtrar por Ciudad (API)
```bash
# Obtener solo compradores de Quito
curl http://localhost:8000/api/usuarios/mapa_compradores/?ciudad=Quito
```

### Ver Envíos de un Comprador (API)
```bash
# Obtener envíos del comprador con ID 5
curl http://localhost:8000/api/usuarios/5/envios_comprador/
```

## 📖 Documentación Adicional

- **Guía Completa**: Ver `MAPA_COMPRADORES_README.md`
- **Detalles de Implementación**: Ver `IMPLEMENTACION_MAPA_COMPRADORES.md`

## 🆘 Soporte

Si encuentras algún problema:

1. Revisa la consola del navegador (F12)
2. Revisa los logs del servidor Django
3. Verifica que todos los servicios estén corriendo
4. Consulta los archivos de documentación

---

**¡Listo para explorar el mapa! 🗺️🎉**

