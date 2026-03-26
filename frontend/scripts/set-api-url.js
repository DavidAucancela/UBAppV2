#!/usr/bin/env node
/**
 * Reemplaza apiUrl en environment.prod.ts con API_URL (env o build arg).
 * Solo aplica si API_URL está definida Y empieza con https://.
 */
const fs = require('fs');
const path = require('path');

const envPath = path.join(__dirname, '../src/app/environments/environment.prod.ts');
const apiUrl = process.env.API_URL;

if (!apiUrl) {
  console.log('API_URL no definida — se usa la URL hardcodeada en environment.prod.ts');
  process.exit(0);
}

if (!apiUrl.startsWith('https://')) {
  console.warn(`⚠️  API_URL="${apiUrl}" no usa https — se ignora para evitar Mixed Content.`);
  process.exit(0);
}

let content = fs.readFileSync(envPath, 'utf8');
content = content.replace(
  /apiUrl:\s*['"][^'"]*['"]/,
  `apiUrl: '${apiUrl.replace(/'/g, "\\'")}'`
);

fs.writeFileSync(envPath, content);
console.log(`✓ API URL: ${apiUrl}`);
