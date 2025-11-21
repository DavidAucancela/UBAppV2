# Script de instalación de Búsqueda Semántica - Universal Box
# PowerShell para Windows

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Instalación de Búsqueda Semántica v1.0" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "[1/6] Verificando Python..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python no encontrado. Instala Python 3.11+ primero." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python OK" -ForegroundColor Green
Write-Host ""

# 2. Instalar dependencias
Write-Host "[2/6] Instalando dependencias Python..." -ForegroundColor Yellow
pip install psycopg2-binary==2.9.9 pgvector==0.2.5
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error instalando dependencias." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
Write-Host ""

# 3. Verificar configuración
Write-Host "[3/6] Verificando configuración..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ Archivo .env encontrado" -ForegroundColor Green
    
    # Verificar OpenAI Key
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "OPENAI_API_KEY=sk-") {
        Write-Host "✅ OpenAI API Key configurada" -ForegroundColor Green
    } else {
        Write-Host "⚠️  ADVERTENCIA: OpenAI API Key no configurada correctamente" -ForegroundColor Yellow
        Write-Host "   Edita .env y agrega: OPENAI_API_KEY=sk-tu-key-aqui" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Archivo .env no encontrado" -ForegroundColor Yellow
    Write-Host "   Crea un archivo .env con:" -ForegroundColor Yellow
    Write-Host "   OPENAI_API_KEY=sk-tu-key-aqui" -ForegroundColor Yellow
    Write-Host "   DB_NAME=equityDB" -ForegroundColor Yellow
    Write-Host "   DB_USER=postgres" -ForegroundColor Yellow
    Write-Host "   DB_PASSWORD=admin" -ForegroundColor Yellow
    Write-Host "   DB_HOST=localhost" -ForegroundColor Yellow
    Write-Host "   DB_PORT=5434" -ForegroundColor Yellow
}
Write-Host ""

# 4. Ejecutar migraciones
Write-Host "[4/6] Ejecutando migraciones..." -ForegroundColor Yellow
python manage.py migrate busqueda
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error en migraciones. Verifica que PostgreSQL esté corriendo." -ForegroundColor Red
    Write-Host "   Debes habilitar pgvector en PostgreSQL primero:" -ForegroundColor Yellow
    Write-Host "   psql -U postgres -d equityDB -c 'CREATE EXTENSION vector;'" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Migraciones completadas" -ForegroundColor Green
Write-Host ""

# 5. Generar embeddings para 10 envíos de prueba
Write-Host "[5/6] Generando embeddings de prueba..." -ForegroundColor Yellow
Write-Host "   (Procesando hasta 10 envíos para prueba)" -ForegroundColor Gray
python manage.py generar_embeddings_masivo --limite 10
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Error generando embeddings (puede ser por API Key)" -ForegroundColor Yellow
} else {
    Write-Host "✅ Embeddings de prueba generados" -ForegroundColor Green
}
Write-Host ""

# 6. Resumen
Write-Host "[6/6] Instalación completada!" -ForegroundColor Green
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Próximos pasos:" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Iniciar servidor Django:" -ForegroundColor White
Write-Host "   python manage.py runserver" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Prueba la búsqueda semántica:" -ForegroundColor White
Write-Host "   POST http://localhost:8000/api/busqueda/semantica/" -ForegroundColor Gray
Write-Host "   Body: { ""texto"": ""envíos entregados en Quito"" }" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Generar embeddings para todos los envíos:" -ForegroundColor White
Write-Host "   python manage.py generar_embeddings_masivo" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Ver métricas:" -ForegroundColor White
Write-Host "   GET http://localhost:8000/api/busqueda/semantica/metricas/" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentación completa en:" -ForegroundColor Cyan
Write-Host "   GUIA_BUSQUEDA_SEMANTICA_COMPLETA.md" -ForegroundColor Gray
Write-Host ""

