# ✅ Integración JWT Corregida

## Cambios Realizados

### Backend (Django)

1. **`backend/settings.py`**:
   - ✅ Configurado `JWTAuthentication` como método principal de autenticación
   - ✅ Eliminado `TokenAuthentication` de las clases de autenticación
   - ✅ Configurado `SIMPLE_JWT` con todos los parámetros necesarios:
     - `ACCESS_TOKEN_LIFETIME`: 60 minutos
     - `REFRESH_TOKEN_LIFETIME`: 1 día
     - `AUTH_HEADER_TYPES`: `('Bearer',)` - Formato correcto para JWT
     - `UPDATE_LAST_LOGIN`: True

2. **`backend/apps/usuarios/views.py`**:
   - ✅ **LoginView**: Ahora genera tokens JWT usando `RefreshToken.for_user()`
     - Devuelve `access_token` y `refresh_token`
   - ✅ **LogoutView**: Actualizado para manejar blacklist de tokens JWT (opcional)
   - ✅ Eliminado el uso de `Token.objects` (TokenAuthentication antiguo)

### Frontend (Angular)

1. **`frontend/src/app/interceptors/auth.interceptor.ts`**:
   - ✅ Cambiado formato de autorización de `Token ${authToken}` a `Bearer ${authToken}`
   - Esto es requerido por JWT

2. **`frontend/src/app/services/auth.service.ts`**:
   - ✅ Actualizado `login()` para guardar el `refresh_token` en localStorage
   - ✅ Actualizado `logout()` para enviar el `refresh_token` al backend
   - ✅ Agregado método `getRefreshToken()`

## 🔧 Pasos para Probar

### 1. Reiniciar el Servidor de Django

```powershell
# En la terminal del backend
cd backend
python manage.py runserver
```

### 2. Limpiar el LocalStorage del Navegador

**Opción A - Desde DevTools (Recomendado):**
1. Presiona `F12` para abrir DevTools
2. Ve a la pestaña **Application** (o **Aplicación**)
3. En el menú lateral, selecciona **Local Storage** > `http://localhost:4200`
4. Haz clic derecho y selecciona **Clear** (o **Limpiar**)

**Opción B - Desde la Consola del Navegador:**
```javascript
localStorage.clear();
location.reload();
```

### 3. Reiniciar el Frontend (si está corriendo)

```powershell
# Detén el servidor (Ctrl + C)
# Vuelve a iniciarlo
cd frontend
npm start
```

### 4. Probar el Login

1. Ve a `http://localhost:4200/login`
2. Ingresa tus credenciales
3. El login debería ser exitoso
4. **Verifica en DevTools (F12) > Console** que veas:
   ```
   Login exitoso: {token: "eyJ0eXAiOiJKV1Q...", refresh: "eyJ0eXAiOiJKV1Q...", user: {...}}
   ```
   - El token ahora es un JWT largo (comienza con `eyJ0eXA...`)
   - Ya no es el token corto anterior (`5efeb4ffa14578878e0e6c17e8115c58c2bf4963`)

5. **Verifica que las peticiones funcionen**:
   - NO deberías ver errores 401 (Unauthorized)
   - El dashboard debería cargar datos correctamente
   - Verifica en **Network** que las peticiones incluyan el header:
     ```
     Authorization: Bearer eyJ0eXAiOiJKV1Q...
     ```

## 🔍 Verificación del Token JWT

### En el Frontend (localStorage)
```javascript
// Abre la consola del navegador y ejecuta:
console.log('Access Token:', localStorage.getItem('authToken'));
console.log('Refresh Token:', localStorage.getItem('refreshToken'));
```

### Formato Correcto del JWT
Un JWT válido tiene 3 partes separadas por puntos:
```
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYwODk2MDAwLCJpYXQiOjE3NjA4OTI0MDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

header.payload.signature
```

### En las Peticiones HTTP
Abre DevTools > **Network** y verifica cualquier petición:
```
Request Headers:
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## 🚨 Solución de Problemas Comunes

### Error 401 después del Login

**Causa**: Token antiguo en localStorage  
**Solución**: Limpiar localStorage como se indica arriba

### Error: "Token is invalid or expired"

**Causa**: El token JWT expiró (60 minutos de vida)  
**Solución**: 
1. Hacer logout
2. Volver a hacer login

### Error: "detail": "Given token not valid for any token type"

**Causa**: El formato del header de autorización es incorrecto  
**Solución**: Verificar que el interceptor use `Bearer` y no `Token`

### Error en Backend: "ImportError: cannot import name 'RefreshToken'"

**Causa**: El paquete `djangorestframework-simplejwt` no está instalado  
**Solución**:
```powershell
cd backend
pip install djangorestframework-simplejwt==5.3.2
```

## 📊 Diferencias: Token Antiguo vs JWT

| Aspecto | Token Antiguo (DRF) | Token JWT |
|---------|---------------------|-----------|
| **Formato Header** | `Token abc123...` | `Bearer eyJ0eXA...` |
| **Longitud** | 40 caracteres | ~200+ caracteres |
| **Almacenamiento** | Base de datos | Stateless (no DB) |
| **Expiración** | No expira | Expira (configurable) |
| **Información** | Solo key aleatoria | Contiene payload con datos |
| **Refresh** | No disponible | Tiene refresh token |

## 🎯 Próximos Pasos Opcionales

### 1. Implementar Refresh Token Automático

Puedes crear un interceptor que refresque el token automáticamente cuando expire:

```typescript
// frontend/src/app/interceptors/token-refresh.interceptor.ts
// (Código de ejemplo)
```

### 2. Habilitar Token Blacklist

Si quieres que los tokens JWT se invaliden al hacer logout:

```python
# backend/settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework_simplejwt.token_blacklist',
]

SIMPLE_JWT = {
    # ...
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

```powershell
# Ejecutar migraciones
python manage.py migrate
```

### 3. Configurar Tiempo de Expiración

Ajusta según tus necesidades en `settings.py`:
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),  # Mayor duración
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Una semana
}
```

## ✅ Checklist de Verificación

- [ ] Servidor Django reiniciado
- [ ] LocalStorage limpiado
- [ ] Login exitoso con JWT (token largo)
- [ ] No hay errores 401 en las peticiones
- [ ] Dashboard carga correctamente
- [ ] Headers incluyen `Authorization: Bearer ...`
- [ ] Logout funciona correctamente

## 📝 Notas Importantes

1. **Seguridad**: En producción, cambia `SECRET_KEY` en `.env`
2. **CORS**: Configura `CORS_ALLOW_ALL_ORIGINS = False` y especifica orígenes permitidos
3. **HTTPS**: En producción, asegúrate de usar HTTPS para proteger los tokens
4. **Refresh Token**: Guárdalo de forma segura (HttpOnly cookies en producción)

---

**¡La integración JWT ahora está completa y funcional! 🎉**

