# 🚀 Inicio Rápido: Trabajar desde Cualquier Red

## 📌 Tu Situación Actual

- **Supabase** funciona en casa (IPv6) ✅
- **Supabase** NO funciona en otras redes (no soportan IPv6) ❌
- **Necesitas** trabajar desde cualquier lugar

## ⚡ Solución Más Rápida (2 opciones)

### OPCIÓN A: Hotspot Móvil (Sin configuración)

```
1. Activa hotspot en tu móvil
2. Conéctate desde tu PC
3. ¡Listo! Usa Supabase normalmente
```

**Ventaja:** Sin configuración  
**Desventaja:** Consume datos móviles

### OPCIÓN B: Base de Datos Local con Docker (Configuración única)

```powershell
# 1. Instalar Docker Desktop (solo una vez)
#    https://www.docker.com/products/docker-desktop/

# 2. Configurar base de datos local (solo una vez)
cd backend
python setup_docker_postgres.py

# 3. Ejecutar migraciones (solo una vez)
python manage.py migrate

# ¡Listo! Ya puedes trabajar offline
```

**Ventaja:** Trabajo completamente offline  
**Desventaja:** Requiere configuración inicial

## 📋 Flujo de Trabajo Diario

### Si elegiste OPCIÓN A (Hotspot):

```
Cada vez que no estés en casa:
1. Activa hotspot móvil
2. Conéctate
3. Trabaja normalmente
```

### Si elegiste OPCIÓN B (Docker):

**Cuando estás en CASA (antes de salir):**
```powershell
cd backend
python exportar_datos_supabase.py
```

**Cuando NO estás en casa:**
```powershell
# Cambiar a local
python configuracion_dual_red.py
# Selecciona: 1 (Local)

# Importar datos (primera vez o actualizar)
python importar_datos_local.py

# Trabajar normalmente
python manage.py runserver
```

**Cuando vuelves a CASA:**
```powershell
# Cambiar a Supabase
python configuracion_dual_red.py
# Selecciona: 2 (Supabase)

# Exportar datos actualizados
python exportar_datos_supabase.py
```

## 🎯 ¿Qué Opción Elegir?

| Escenario | Opción Recomendada |
|-----------|-------------------|
| Sales poco de casa | Hotspot Móvil |
| Sales frecuentemente | Docker + Local |
| Quieres trabajo offline | Docker + Local |
| Quieres simplicidad | Hotspot Móvil |
| Datos móviles ilimitados | Hotspot Móvil |
| Datos móviles limitados | Docker + Local |

## 📚 Documentación Completa

- **Guía completa**: `documentacion/GUIA_DUAL_BASE_DATOS.md`
- **Resumen opciones**: `RESUMEN_OPCIONES_BASE_DATOS.md`
- **Problema IPv6**: `documentacion/PROBLEMA_IPV6_REDES.md`

## 🛠️ Scripts Disponibles

```powershell
# Configurar Docker + PostgreSQL
python setup_docker_postgres.py

# Cambiar entre Supabase/Local automáticamente
python configuracion_dual_red.py

# Exportar datos desde Supabase
python exportar_datos_supabase.py

# Importar datos a local
python importar_datos_local.py

# Verificar conexión actual
python verificar_dns_antes_iniciar.py
```

## ❓ Preguntas Frecuentes

**¿Puedo usar DBeaver para gestionar datos?**  
Sí, descárgalo de https://dbeaver.io/download/ y conéctate a Supabase o local.

**¿Los embeddings se importan correctamente?**  
Sí, pgvector está incluido en Docker. Los vectores se importan completos.

**¿Puedo cambiar entre opciones después?**  
Sí, todas las opciones son compatibles. Puedes cambiar cuando quieras.

**¿Qué pasa con los datos que modifico en local?**  
Se quedan en local. Cuando vuelvas a casa, exporta desde Supabase nuevamente.

**¿Necesito sincronizar cambios entre local y Supabase?**  
Si trabajas solo localmente como respaldo, no es necesario. Si haces cambios importantes, exporta desde Supabase cuando vuelvas a casa.

## 🎉 Recomendación Final

**Para empezar hoy mismo:**
1. Prueba el **hotspot móvil** primero (más simple)
2. Si funciona bien, ¡perfecto!
3. Si consumes muchos datos, configura **Docker** para la próxima

**Para máxima flexibilidad:**
1. Configura **Docker** una sola vez
2. Exporta datos antes de salir de casa
3. Trabaja offline cuando quieras
4. Sincroniza cuando vuelvas a casa

¡Ya estás listo para trabajar desde cualquier lugar! 🚀

