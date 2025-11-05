# 🚀 Inicio Rápido - Módulo de Importación de Excel

Ponga el módulo en funcionamiento en **5 minutos**.

---

## ⚡ Pasos Rápidos

### 1️⃣ Backend - Django (2 minutos)

```bash
# Ir al directorio del backend
cd backend

# Crear migraciones
python manage.py makemigrations archivos --name importacion_excel

# Aplicar migraciones
python manage.py migrate

# Generar plantilla de ejemplo
python manage.py generar_plantilla_importacion --with-data

# Iniciar servidor (nueva terminal)
python manage.py runserver
```

✅ **Verificar**: Abra http://localhost:8000/api/archivos/importaciones-excel/

---

### 2️⃣ Frontend - Angular (2 minutos)

```bash
# Ir al directorio del frontend (nueva terminal)
cd frontend

# Verificar que xlsx está instalado
npm list xlsx

# Si no está instalado:
# npm install xlsx

# Compilar y servir
npm start
```

✅ **Verificar**: Abra http://localhost:4200/importacion-excel

---

### 3️⃣ Probar el Módulo (1 minuto)

1. **Iniciar sesión** en el sistema con usuario Digitador, Gerente o Admin

2. **Navegar** a `/importacion-excel`

3. **Descargar** la plantilla de ejemplo (botón "📥 Descargar Plantilla")

4. **Subir** el archivo descargado

5. **Seguir** los pasos del asistente

6. **¡Listo!** Datos importados exitosamente

---

## 📋 Checklist de Verificación

- [ ] ✅ Servidor Django corriendo en http://localhost:8000
- [ ] ✅ Servidor Angular corriendo en http://localhost:4200
- [ ] ✅ Migraciones aplicadas correctamente
- [ ] ✅ Endpoint `/api/archivos/importaciones-excel/` accesible
- [ ] ✅ Ruta `/importacion-excel` funciona en el frontend
- [ ] ✅ Plantilla de ejemplo descargada
- [ ] ✅ Primera importación exitosa

---

## 🎯 Comandos Útiles

### Generar Plantilla

```bash
# Plantilla vacía
python manage.py generar_plantilla_importacion

# Plantilla con datos de ejemplo
python manage.py generar_plantilla_importacion --with-data

# Especificar nombre de salida
python manage.py generar_plantilla_importacion --output plantilla.xlsx --with-data
```

### Ver Importaciones (Django Shell)

```bash
python manage.py shell
```

```python
from apps.archivos.models import ImportacionExcel, Envio

# Ver todas las importaciones
ImportacionExcel.objects.all()

# Ver última importación
ultima = ImportacionExcel.objects.last()
print(f"Estado: {ultima.estado}")
print(f"Registros: {ultima.total_registros}")
print(f"Válidos: {ultima.registros_validos}")
print(f"Errores: {ultima.registros_errores}")

# Ver envíos importados
Envio.objects.filter(fecha_creacion__gte='2025-10-20')
```

---

## 🔧 Solución Rápida de Problemas

### "Module 'openpyxl' not found"

```bash
pip install openpyxl pandas
```

### "Cannot find module 'xlsx'"

```bash
cd frontend
npm install xlsx
```

### "No route matches /importacion-excel"

Verifique que `app.routes.ts` tenga la ruta agregada y reinicie el servidor Angular.

### "Permission denied"

```bash
chmod -R 755 backend/media/
```

---

## 📚 Recursos Adicionales

- 📖 [Documentación Completa](./MODULO_IMPORTACION_EXCEL_README.md)
- 🔧 [Guía de Instalación Detallada](./INSTALACION_MODULO_IMPORTACION_EXCEL.md)
- 📊 [Resumen Ejecutivo](./RESUMEN_EJECUTIVO_MODULO_IMPORTACION_EXCEL.md)

---

## 💡 Ejemplo de Datos

Si desea crear su propio archivo Excel de prueba:

| HAWB | Peso Total | Cantidad Total | Valor Total | Categoría |
|------|------------|----------------|-------------|-----------|
| TEST001 | 5.5 | 2 | 150.00 | electronica |
| TEST002 | 1.2 | 3 | 45.50 | ropa |
| TEST003 | 3.0 | 1 | 80.00 | hogar |

**Nota**: El campo HAWB es obligatorio y debe ser único.

---

## 🎉 ¡Listo!

El módulo está completamente funcional. Para más información consulte la documentación completa.

---

## 📞 Soporte

Si encuentra problemas:

1. Consulte la [sección de solución de problemas](./INSTALACION_MODULO_IMPORTACION_EXCEL.md#-solución-de-problemas-comunes)
2. Revise los logs del servidor:
   ```bash
   # Backend
   tail -f backend/logs/django.log
   
   # Frontend (consola del navegador)
   F12 → Console
   ```
3. Verifique la [documentación completa](./MODULO_IMPORTACION_EXCEL_README.md)

---

**Desarrollado para Universal Box - Trabajo de Titulación 2025**

✅ Módulo completo y funcional
📊 +4,000 líneas de código
📚 Documentación completa
🚀 Listo para producción


