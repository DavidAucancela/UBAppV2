# Instrucciones para Aplicar Migraciones

## ⚠️ IMPORTANTE: Ejecutar Migraciones

Se ha creado un nuevo modelo `PruebaRendimientoCompleta` que necesita migración.

### Pasos:

```bash
# 1. Ir al directorio backend
cd backend

# 2. Crear migraciones
python manage.py makemigrations metricas

# 3. Aplicar migraciones
python manage.py migrate metricas
```

### Si hay errores:

Si aparece un error de importación, verifica que:
1. El modelo `PruebaRendimientoCompleta` esté en `backend/apps/metricas/models.py`
2. El serializer esté en `backend/apps/metricas/serializers.py`
3. El admin esté registrado en `backend/apps/metricas/admin.py`

### Verificar que funcionó:

```bash
# Verificar que la tabla existe
python manage.py dbshell
# En PostgreSQL:
\dt prueba_rendimiento_completa
# Debe mostrar la tabla
```

---

## ✅ Después de Migrar

1. **Ejecutar una prueba:**
   ```bash
   python manage.py pruebas_rendimiento --usuario admin
   ```

2. **Verificar en dashboard:**
   - Login como Admin
   - Dashboard → Reportes de Pruebas → Pruebas del Sistema
   - Scroll hasta "Historial de Pruebas de Rendimiento"
   - Debe mostrar la prueba ejecutada

3. **Verificar en admin:**
   - `/admin/metricas/pruebarendimientocompleta/`
   - Debe mostrar las pruebas guardadas

---

## 🎯 Listo para Usar

Una vez aplicadas las migraciones, el sistema está completamente funcional:
- ✅ Pruebas se guardan automáticamente
- ✅ Dashboard muestra historial
- ✅ CPU se mide correctamente
- ✅ JSON se exporta sin errores
- ✅ Pruebas optimizadas (1-3 min)

