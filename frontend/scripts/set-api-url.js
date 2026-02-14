#!/usr/bin/env node
/**
 * Reemplaza apiUrl en environment.prod.ts con API_URL (env o build arg).
 * Usado para builds de producción (Render, etc.)
 */
const fs = require('fs');
const path = require('path');

const envPath = path.join(__dirname, '../src/app/environments/environment.prod.ts');
const apiUrl = process.env.API_URL || 'http://localhost:8000/api';

if (apiUrl.includes('REPLACE') || apiUrl.includes('tu-backend')) {
  console.warn('⚠️  API_URL no configurada. Configúrala en Render Dashboard antes del deploy.');
}

let content = fs.readFileSync(envPath, 'utf8');
content = content.replace(
  /apiUrl:\s*['"][^'"]*['"]/,
  `apiUrl: '${apiUrl.replace(/'/g, "\\'")}'`
);

fs.writeFileSync(envPath, content);
console.log(`✓ API URL: ${apiUrl}`);
