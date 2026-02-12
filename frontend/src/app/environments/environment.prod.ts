export const environment = {
    production: true,
    // Para Docker local: backend en localhost:8000. En producción real cambiar a tu dominio.
    apiUrl: 'http://localhost:8000/api',
    appName: 'UBApp',
    version: '1.0.0',
    enableDebug: false,
    sessionTimeout: 30 * 60 * 1000, // 30 minutos
  };