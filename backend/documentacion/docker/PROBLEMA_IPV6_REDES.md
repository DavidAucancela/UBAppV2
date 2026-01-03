# 🌐 Problema: IPv6 en Diferentes Redes

## 🎯 Problema Real

**Supabase solo tiene IPv6 gratis** (IPv4 es de pago), y algunas redes no soportan IPv6 correctamente.

### Situación:
- ✅ **En casa**: Tu red soporta IPv6 → Supabase funciona
- ❌ **Otras redes**: No soportan IPv6 → Supabase NO funciona
- 💰 **IPv4 en Supabase**: Requiere plan de pago

## 🔍 Por Qué Pasa

1. **Supabase gratis usa solo IPv6**
   - Para reducir costos
   - IPv4 está en plan de pago

2. **No todas las redes soportan IPv6**
   - Redes antiguas
   - Algunas redes corporativas/institucionales
   - Algunos ISPs no configuran IPv6

3. **Tu red de casa SÍ soporta IPv6**
   - Por eso funciona en casa
   - Pero al cambiar de red, deja de funcionar

## ✅ Soluciones Prácticas

### Solución 1: Script Automático (MÁS FÁCIL)

Ejecuta este script y elige la opción automáticamente:

```powershell
cd backend
python configuracion_dual_red.py
```

El script:
- Detecta si Supabase está accesible
- Si NO está accesible, te ofrece usar base de datos local
- Cambia la configuración automáticamente
- Guarda un backup para restaurar después

### Solución 2: Usar Hotspot Móvil

Muchos móviles soportan IPv6:

1. **Activa hotspot en tu móvil**
2. **Conéctate desde tu PC**
3. **Verifica que funcione:**
   ```powershell
   python configuracion_dual_red.py
   ```

### Solución 3: Base de Datos Local

Para trabajar sin Supabase cuando no estás en casa:

#### Requisitos:
- PostgreSQL instalado localmente
- Base de datos: `equityDB`
- Usuario: `postgres`
- Contraseña: `admin`

#### Configurar manualmente:

Edita `backend/.env`:

```env
# Cuando NO estás en casa (base de datos local)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=equityDB
DB_USER=postgres
DB_PASSWORD=admin
```

#### Cuando vuelvas a casa:

Edita `backend/.env`:

```env
# Cuando estás en casa (Supabase)
DB_HOST=db.gybrifikqkibwqpzjuxm.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=tu_password_supabase
```

### Solución 4: Túnel IPv6 (Avanzado)

Si necesitas acceder a Supabase desde cualquier red:

1. **Usar un servicio de túnel IPv6:**
   - Hurricane Electric (tunnelbroker.net)
   - Teredo (Windows incluido)

2. **O usar una VPN que soporte IPv6:**
   - Algunas VPNs comerciales soportan IPv6

## 📋 Flujo de Trabajo Recomendado

### Cuando NO estás en casa:

1. **Ejecuta el script:**
   ```powershell
   python configuracion_dual_red.py
   ```

2. **Selecciona "Usar base de datos local"**

3. **Trabaja normalmente con datos locales**

### Cuando vuelves a casa:

1. **Ejecuta el script:**
   ```powershell
   python configuracion_dual_red.py
   ```

2. **Selecciona "Cambiar a Supabase"**

3. **Trabaja con datos de Supabase**

## 🔄 Script de Configuración Dual

El script `configuracion_dual_red.py` hace todo automáticamente:

```powershell
cd backend
python configuracion_dual_red.py
```

**Funciones:**
- ✅ Detecta si Supabase está disponible
- ✅ Verifica soporte IPv6 de la red
- ✅ Cambia entre local y Supabase automáticamente
- ✅ Guarda backups de configuración
- ✅ Restaura configuración cuando vuelves a casa

## 📝 Comandos Útiles

```powershell
# Cambiar configuración según red
python configuracion_dual_red.py

# Verificar conectividad actual
python verificar_dns_antes_iniciar.py

# Iniciar Django
python manage.py runserver
```

## 💡 Recomendaciones

### Para Trabajo Diario:

1. **En casa:**
   - Usa Supabase (datos en la nube)
   - Todos los cambios se sincronizan

2. **Fuera de casa:**
   - Usa base de datos local
   - Trabaja con datos locales
   - Sincroniza cuando vuelvas a casa (si es necesario)

### Para Desarrollo:

1. **Mantén base de datos local:**
   - Instalada siempre
   - Para desarrollo y pruebas
   - No requiere internet

2. **Usa Supabase:**
   - Para producción
   - Cuando estés en casa
   - Para sincronizar datos

## 🎯 Solución Permanente (Si Quieres Pagar)

Si necesitas acceso desde cualquier red:

1. **Upgrade a plan de pago de Supabase**
   - Incluye IPv4
   - Funciona en todas las redes
   - Más confiable

2. **O usar un servidor con IPv4:**
   - Railway
   - Heroku
   - DigitalOcean
   - AWS RDS

## 🚨 Importante

- ❌ **NO es problema de DNS** - Es de soporte IPv6
- ✅ **Es normal** - Supabase gratis solo tiene IPv6
- ✅ **Tiene solución** - Usa el script automático
- ✅ **No afecta producción** - Solo desarrollo local

## 📚 Archivos Creados

1. **`configuracion_dual_red.py`** - Script automático para cambiar configuración
2. **`PROBLEMA_IPV6_REDES.md`** - Este documento (explicación completa)

## 🎉 Conclusión

No necesitas configurar DNS. El problema es que:
- Supabase gratis solo tiene IPv6
- Tu red actual no soporta IPv6
- Tu red de casa SÍ soporta IPv6

**Solución:** Usa el script `configuracion_dual_red.py` para cambiar entre local y Supabase según dónde estés.

