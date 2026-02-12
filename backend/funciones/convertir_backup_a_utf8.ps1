# Convierte backup_pre_docker.sql (UTF-16) a UTF-8 sin BOM para restaurar en Postgres
$ErrorActionPreference = "Stop"
$src = Join-Path $PSScriptRoot "..\backup\backup_pre_docker.sql"
$dst = Join-Path $PSScriptRoot "..\backup\backup_utf8.sql"

if (-not (Test-Path $src)) {
    Write-Error "No se encuentra: $src"
    exit 1
}

$content = [System.IO.File]::ReadAllText($src, [System.Text.Encoding]::Unicode)
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($dst, $content, $utf8NoBom)
Write-Host "Convertido: $dst (UTF-8 sin BOM)"
