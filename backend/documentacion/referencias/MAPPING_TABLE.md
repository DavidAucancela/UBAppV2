# Tabla de Mapeo XML → RIS

## Mapeo de Tipos de Referencia

| Tipo XML | Tipo RIS | Descripción |
|----------|----------|-------------|
| DocumentFromInternetSite | ELEC | Documento electrónico |
| InternetSite | WEB | Sitio web |
| Report | RPRT | Reporte/Informe técnico |

## Mapeo de Campos

| Campo XML | Campo RIS | Descripción |
|-----------|-----------|-------------|
| Tag | ID | Identificador único de la referencia |
| Author/Person | AU | Autor(es) - uno por línea |
| Title | TI | Título principal |
| Year | PY | Año de publicación |
| Month | M1 | Mes (formateado en DA) |
| Day | M2 | Día (formateado en DA) |
| Year/Month/Day | DA | Fecha completa (YYYY/MM/DD) |
| Publisher | PB | Editorial/Editor |
| City | CY | Ciudad de publicación |
| URL | UR | URL del recurso |
| InternetSiteTitle | T2 | Título secundario/Sitio web |
| ProductionCompany | T3/PB | Compañía productora |

## Resumen de Conversión

- **Total de referencias convertidas**: 116
- **Tipos únicos de referencias**: 3

### Distribución por Tipo

| Tipo | Cantidad |
|------|----------|
| Report | 59 |
| InternetSite | 56 |
| DocumentFromInternetSite | 1 |