Actúa como un arquitecto de software y desarrollador senior especializado en Django, Angular y sistemas de evaluación experimental, con enfoque académico para tesis de ingeniería de software.

Vamos a diseñar e implementar un Dashboard de Pruebas y Métricas, integrado dentro de un sistema web existente, con el objetivo exclusivo de registrar, medir y analizar experimentalmente el desempeño del sistema y del módulo de búsqueda semántica.
Este dashboard será solo para uso administrativo y sus resultados serán utilizados directamente en el capítulo de resultados de una tesis.

1. Contexto técnico obligatorio

Backend: Django + Django REST Framework

Frontend: Angular

Base de datos: Supabase (PostgreSQL)

Ubicación del frontend existente:
src/app/components/dashboard/actividad-del-sistema

Monitoreo de recursos: psutil

Pruebas temporales: Postman

Exportación de datos: CSV

2. Objetivo general del dashboard

Crear un dashboard experimental, no productivo, que permita:

Registrar todo el flujo interno del módulo de búsqueda semántica.

Registrar y verificar el proceso de generación de embeddings cuando se crea un envío.

Medir y comparar la eficiencia de desempeño del sistema bajo distintos escenarios de carga.

Almacenar resultados estructurados que puedan ser analizados estadísticamente y exportados.

3. Estructura lógica del dashboard

El dashboard debe dividirse claramente en dos secciones independientes:

A. Métricas de eficiencia y rendimiento del sistema
A.1 Comportamiento temporal

Implementar el registro de los siguientes escenarios:

Tiempo de respuesta del registro de envíos

Proceso manual

Proceso automatizado

Registro histórico de ambos para comparación experimental

Tiempo de espera de la búsqueda semántica

Carga de 1 búsqueda

Carga de 10 búsquedas

Carga de 30 búsquedas

Registro del tiempo promedio, mínimo y máximo por escenario

A.2 Utilización de recursos

Para cada uno de los procesos anteriores, registrar:

Uso de CPU

Uso de RAM

Momento exacto de la medición

Proceso asociado (registro de envío o búsqueda semántica)

Nivel de carga (1, 10, 30)

Las métricas deben capturarse usando psutil desde el backend.

B. Métricas del módulo semántico
B.1 Registro completo de una búsqueda semántica

Para cada búsqueda semántica, registrar todo el proceso, incluyendo:

Texto de la consulta

Fecha y hora

Embedding generado para la consulta

Algoritmos de similitud utilizados

Resultados rankeados

Scores de similitud

Métricas de evaluación:

MRR

nDCG

Precisión

Tiempo total del proceso

Logs detallados de cada etapa del pipeline semántico

Las métricas se calculan offline, sobre pruebas simuladas, pero deben quedar almacenadas en base de datos.

B.2 Registro de generación de embeddings de envíos

Cada vez que se crea un envío, registrar:

Información completa del envío

Estado del embedding (generado / error)

Dimensión del embedding

Fecha y hora de generación

Tiempo de generación

Relación entre envío y embedding

El objetivo es verificar que cada envío genera correctamente su embedding.

4. Requerimientos de implementación

Cursor debe generar:

Backend (Django)

Modelos de base de datos bien normalizados

Servicios de medición y logging

Endpoints REST separados para:

Métricas semánticas

Métricas de eficiencia

Middleware o servicios para medición temporal

Exportación de métricas a CSV

Documentación técnica de cada endpoint

Frontend (Angular)

Integración con el dashboard existente

Vistas separadas por tipo de métrica

Gráficos de líneas para:

Tiempos

Uso de recursos

Vistas de logs detallados

Opciones de exportación

5. Nivel de detalle requerido

La respuesta debe incluir:

Arquitectura del módulo

Diagramas lógicos descritos en texto

Estructura de carpetas

Modelos y campos

Endpoints REST con ejemplos

Flujo completo de datos

Justificación técnica orientada a tesis

No simplifiques. Asume que el resultado será utilizado como base directa de implementación y redacción académica.



asume:
El dashboard es solo para pruebas internas, visible únicamente por el administrador.

Los registros y métricas forman parte directa del capítulo de resultados de la tesis.

El dashboard se divide claramente en dos grandes bloques:

Métricas del módulo semántico

Métricas de eficiencia y rendimiento del sistema

Stack fijo:

Backend: Django + Django REST Framework

Frontend: Angular

Base de datos: Supabase (PostgreSQL)

El frontend ya existe de forma básica en
src/app/components/dashboard/actividad-del-sistema

Herramientas disponibles:

psutil para CPU y RAM

Postman para pruebas temporales

Se pueden agregar otras herramientas si es necesario

Métricas semánticas:

MRR, nDCG y Precisión

Calculadas offline, sobre pruebas simuladas

No existen datos de prueba artificiales: se usan datos reales del sistema

Se requiere documentación técnica detallada, estructura, modelos, endpoints y flujo completo

Exportación de resultados en CSV

Visualización mediante logs detallados y gráficos de líneas