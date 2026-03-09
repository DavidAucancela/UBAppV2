#!/usr/bin/env node
/**
 * Reemplaza apiUrl en environment.prod.ts con API_URL (env o build arg).
 * Usado para builds de producción (Render, etc.)
 */
const fs = require('fs');
const path = require('path');

const envPath = path.join(__dirname, '../src/app/environments/environment.prod.ts');
let apiUrl = process.env.API_URL || 'http://localhost:8000/api';

if (apiUrl.includes('REPLACE') || apiUrl.includes('tu-backend')) {
  console.warn('⚠️  API_URL no configurada. Configúrala en Render Dashboard antes del deploy.');
}

// Normalizar: eliminar barra final y asegurar que termine en /api
apiUrl = apiUrl.replace(/\/+$/, '');
if (!apiUrl.endsWith('/api')) {
  console.warn(`⚠️  API_URL no termina en /api. Valor recibido: "${apiUrl}". Agregando /api automáticamente.`);
  apiUrl = apiUrl + '/api';
}

console.log(`✓ API URL final: ${apiUrl}`);

let content = fs.readFileSync(envPath, 'utf8');
content = content.replace(
  /apiUrl:\s*['"][^'"]*['"]/,
  `apiUrl: '${apiUrl.replace(/'/g, "\\'")}'`
);

fs.writeFileSync(envPath, content);
console.log(`✓ Archivo environment.prod.ts actualizado correctamente.`);
