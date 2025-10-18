# 🧠 Módulo de Búsqueda Semántica de Envíos - Universal Box

## 🎯 Descripción General

El **Módulo de Búsqueda Semántica** es un sistema avanzado de búsqueda inteligente que utiliza procesamiento de lenguaje natural y técnicas de IA para permitir a los usuarios encontrar envíos usando descripciones en lenguaje cotidiano, en lugar de filtros técnicos específicos.

---

## ✨ Características Principales

### 🤖 Búsqueda con Inteligencia Artificial
- **Lenguaje Natural**: Los usuarios pueden buscar como si hablaran: "envíos entregados en Quito la semana pasada"
- **Comprensión Semántica**: El sistema entiende sinónimos, variaciones y contexto
- **Resultados por Relevancia**: Ordenados por puntuación de similitud (0-100%)
- **Fragmentos Destacados**: Muestra las partes del texto que coinciden

### 💡 Sistema de Sugerencias Inteligentes
- **Sugerencias Predefinidas**: 6 ejemplos de búsquedas comunes
- **Autocompletado Dinámico**: Sugerencias mientras el usuario escribe (debounce 300ms)
- **Categorización**: Sugerencias organizadas por tipo (estado, ciudad, fecha, general)
- **Ejemplos Contextuales**: Cada sugerencia incluye variaciones

### 📚 Historial de Búsquedas
- **Persistencia**: Guarda las últimas 10 búsquedas
- **Reutilización**: Click para repetir búsqueda anterior
- **Métricas**: Muestra total de resultados de cada búsqueda
- **Gestión**: Opción de limpiar historial

### 🔍 Filtros Adicionales Opcionales
- Rango de fechas (desde/hasta)
- Estado del envío
- Ciudad de destino
- Combinables con búsqueda semántica

### 📊 Visualización Múltiple de Resultados
1. **Vista de Tarjetas** (Detallada)
   - Información completa del envío
   - Barra visual de similitud
   - Fragmentos relevantes destacados
   - Razón de relevancia
   
2. **Vista de Lista** (Intermedia)
   - Información resumida
   - Compacta y escaneable
   
3. **Vista Compacta** (Tabla)
   - Máxima densidad de información
   - Ideal para grandes volúmenes

### 👍 Sistema de Feedback
- Botones "relevante" / "no relevante" en cada resultado
- Mejora continua del algoritmo mediante aprendizaje
- Confirmación visual del feedback

---

## 📁 Estructura de Archivos

```
frontend/src/app/
├── models/
│   └── busqueda-semantica.ts              # Interfaces y tipos (150 líneas)
├── services/
│   └── api.service.ts                     # Métodos API (actualizado +7 métodos)
└── components/
    ├── busqueda-semantica/                # Componente principal
    │   ├── busqueda-semantica.component.ts       # Lógica (500+ líneas)
    │   ├── busqueda-semantica.component.html     # Template (500+ líneas)
    │   ├── busqueda-semantica.component.css      # Estilos (800+ líneas)
    │   └── busqueda-semantica.component.spec.ts  # Pruebas (400+ líneas)
    └── busqueda-unificada/                # Componente integrador
        ├── busqueda-unificada.component.ts       # Toggle entre modos
        ├── busqueda-unificada.component.html     # UI integrada
        └── busqueda-unificada.component.css      # Estilos toggle
```

**Total**: ~2,800 líneas de código

---

## 🚀 Instalación e Integración

### Paso 1: Verificar Archivos

Todos los archivos del módulo ya están creados en sus ubicaciones correspondientes.

### Paso 2: Rutas Configuradas

Las siguientes rutas ya están agregadas en `app.routes.ts`:

```typescript
// Búsqueda semántica standalone
{ 
  path: 'busqueda-semantica', 
  component: BusquedaSemanticaComponent,
  canActivate: [authGuard]
}

// Búsqueda unificada (recomendada)
{ 
  path: 'busqueda', 
  component: BusquedaUnificadaComponent,
  canActivate: [authGuard]
}
```

### Paso 3: Agregar al Menú

Agregue el enlace en el menú de navegación:

```html
<nav>
  <a routerLink="/busqueda" routerLinkActive="active" class="nav-link">
    <i class="fas fa-brain"></i>
    Búsqueda Inteligente
  </a>
</nav>
```

### Paso 4: Configurar Backend

El backend debe implementar los siguientes endpoints:

---

## 🔧 Endpoints del Backend

### 1. Búsqueda Semántica (POST)

```
POST /api/busqueda/semantica/
```

**Request Body:**
```json
{
  "texto": "envíos entregados en Quito la semana pasada",
  "limite": 20,
  "filtrosAdicionales": {
    "fechaDesde": "2025-01-01",
    "estado": "entregado"
  }
}
```

**Response:**
```json
{
  "consulta": "envíos entregados en Quito la semana pasada",
  "resultados": [
    {
      "envio": {
        "id": 1,
        "hawb": "HAWB001",
        "comprador_info": { ... },
        "estado": "entregado",
        ...
      },
      "puntuacionSimilitud": 0.92,
      "fragmentosRelevantes": [
        "Envío a Quito",
        "Entregado el 12 de enero"
      ],
      "razonRelevancia": "Coincide con ciudad y estado solicitados"
    }
  ],
  "totalEncontrados": 5,
  "tiempoRespuesta": 156,
  "modeloUtilizado": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
}
```

### 2. Sugerencias (GET)

```
GET /api/busqueda/semantica/sugerencias/?q=envios
```

**Response:**
```json
[
  {
    "texto": "envíos a Quito",
    "icono": "fa-map-marker-alt",
    "categoria": "ciudad"
  },
  {
    "texto": "envíos entregados",
    "icono": "fa-check-circle",
    "categoria": "estado"
  }
]
```

### 3. Historial (GET/POST/DELETE)

```
GET /api/busqueda/semantica/historial/       # Obtener
POST /api/busqueda/semantica/historial/      # Guardar
DELETE /api/busqueda/semantica/historial/    # Limpiar
```

### 4. Feedback (POST)

```
POST /api/busqueda/semantica/feedback/
```

**Request Body:**
```json
{
  "resultadoId": 123,
  "esRelevante": true
}
```

### 5. Métricas (GET)

```
GET /api/busqueda/semantica/metricas/
```

---

## 💻 Implementación del Backend (Python/Django)

### Ejemplo con Sentence Transformers

```python
# backend/apps/busqueda/views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from sentence_transformers import SentenceTransformer, util
import torch

# Cargar modelo (una vez al inicio)
modelo = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

@api_view(['POST'])
def busqueda_semantica(request):
    """
    Búsqueda semántica de envíos usando embeddings
    """
    consulta = request.data.get('texto', '')
    limite = request.data.get('limite', 20)
    
    # Obtener envíos de la base de datos
    envios = Envio.objects.all()[:200]  # Limitar para performance
    
    # Generar embedding de la consulta
    consulta_embedding = modelo.encode(consulta, convert_to_tensor=True)
    
    # Generar textos descriptivos de cada envío
    envios_textos = []
    for envio in envios:
        texto = f"{envio.hawb} {envio.comprador.nombre} {envio.comprador.ciudad} {envio.get_estado_display()} {envio.fecha_emision}"
        envios_textos.append(texto)
    
    # Generar embeddings de envíos
    envios_embeddings = modelo.encode(envios_textos, convert_to_tensor=True)
    
    # Calcular similitud coseno
    similitudes = util.cos_sim(consulta_embedding, envios_embeddings)[0]
    
    # Ordenar por similitud
    resultados = []
    for idx, envio in enumerate(envios):
        score = float(similitudes[idx])
        
        if score >= 0.3:  # Umbral mínimo
            resultados.append({
                'envio': EnvioSerializer(envio).data,
                'puntuacionSimilitud': score,
                'fragmentosRelevantes': extraer_fragmentos(consulta, envios_textos[idx]),
                'razonRelevancia': generar_razon(consulta, envio, score)
            })
    
    # Ordenar por puntuación
    resultados = sorted(resultados, key=lambda x: x['puntuacionSimilitud'], reverse=True)[:limite]
    
    return Response({
        'consulta': consulta,
        'resultados': resultados,
        'totalEncontrados': len(resultados),
        'tiempoRespuesta': 150,  # Calcular tiempo real
        'modeloUtilizado': 'paraphrase-multilingual-MiniLM-L12-v2'
    })

def extraer_fragmentos(consulta, texto):
    """
    Extrae fragmentos relevantes del texto
    """
    palabras_consulta = consulta.lower().split()
    fragmentos = []
    
    for palabra in palabras_consulta:
        if palabra in texto.lower():
            # Encontrar contexto alrededor de la palabra
            inicio = max(0, texto.lower().find(palabra) - 20)
            fin = min(len(texto), texto.lower().find(palabra) + 30)
            fragmentos.append(texto[inicio:fin])
    
    return fragmentos[:3]  # Máximo 3 fragmentos

def generar_razon(consulta, envio, score):
    """
    Genera una explicación de por qué el resultado es relevante
    """
    razones = []
    
    if envio.comprador.ciudad.lower() in consulta.lower():
        razones.append(f"ciudad {envio.comprador.ciudad}")
    
    if envio.get_estado_display().lower() in consulta.lower():
        razones.append(f"estado {envio.get_estado_display()}")
    
    if razones:
        return f"Coincide con: {', '.join(razones)}"
    else:
        return f"Similitud semántica: {int(score*100)}%"
```

---

## 🎨 Personalización

### Cambiar Umbral de Similitud

```typescript
// En el componente
this.configuracion.umbralSimilitud = 0.5;  // 0.0 a 1.0
```

### Cambiar Número de Resultados

```typescript
this.configuracion.limiteResultados = 30;  // Por defecto: 20
```

### Personalizar Sugerencias Predefinidas

```typescript
// En busqueda-semantica.ts
export const SUGERENCIAS_PREDEFINIDAS: SugerenciaSemantica[] = [
  {
    texto: 'Tu sugerencia personalizada',
    icono: 'fa-custom-icon',
    categoria: 'general',
    ejemplos: ['ejemplo 1', 'ejemplo 2']
  },
  // ... más sugerencias
];
```

---

## 🧪 Pruebas

### Ejecutar Pruebas Unitarias

```bash
cd frontend
npm test -- --include='**/busqueda-semantica.component.spec.ts'
```

### Pruebas Incluidas (25+ tests)

✅ Inicialización del componente
✅ Búsqueda semántica exitosa
✅ Manejo de errores
✅ Validaciones
✅ Filtrado por umbral
✅ Sugerencias dinámicas
✅ Historial de búsquedas
✅ Acciones (ver detalles, feedback)
✅ Filtros adicionales
✅ Métodos auxiliares

---

## 📊 Ejemplos de Uso

### Ejemplo 1: Búsqueda Simple

**Usuario escribe:** "paquetes para Guayaquil"

**Sistema encuentra:**
- Envíos con destino Guayaquil
- Variaciones: "envíos a Guayaquil", "productos Guayaquil"
- Ordenados por relevancia

### Ejemplo 2: Búsqueda Temporal

**Usuario escribe:** "envíos de la semana pasada"

**Sistema encuentra:**
- Envíos con fechas de 7-14 días atrás
- Interpreta "semana pasada" correctamente
- Muestra fragmentos con fechas

### Ejemplo 3: Búsqueda por Estado y Destinatario

**Usuario escribe:** "envíos entregados de María Gómez"

**Sistema encuentra:**
- Envíos con estado "entregado"
- Comprador con nombre similar a "María Gómez"
- Alta puntuación de similitud

### Ejemplo 4: Búsqueda Compleja

**Usuario escribe:** "paquetes retrasados en tránsito a la costa este mes"

**Sistema encuentra:**
- Estado: "en tránsito"
- Fechas: mes actual
- Ciudades de la costa (Guayaquil, Manta, etc.)
- Posible retraso (fecha estimada vs actual)

---

## 🔐 Seguridad y Permisos

### Autenticación

Todos los usuarios autenticados pueden usar la búsqueda semántica.

### Autorización por Rol

| Funcionalidad | Admin | Gerente | Digitador | Comprador |
|--------------|-------|---------|-----------|-----------|
| Búsqueda semántica | ✅ | ✅ | ✅ | ✅ |
| Ver todos los envíos | ✅ | ✅ | ✅ | ❌ |
| Ver propios envíos | ✅ | ✅ | ✅ | ✅ |
| Historial | ✅ | ✅ | ✅ | ✅ |
| Feedback | ✅ | ✅ | ✅ | ✅ |

---

## ⚡ Performance y Optimización

### Recomendaciones

1. **Caché de Embeddings**
   - Precalcular y cachear embeddings de envíos
   - Actualizar caché solo cuando hay cambios

2. **Índices de Base de Datos**
   - Crear índices en campos frecuentemente buscados
   - Usar PostgreSQL con pg_trgm para similitud de texto

3. **Límite de Envíos**
   - Procesar máximo 500-1000 envíos por búsqueda
   - Usar filtros preliminares (fechas, estado)

4. **Modelo Ligero**
   - Usar modelos como MiniLM en lugar de BERT completo
   - Considerar cuantización para producción

### Benchmarks Esperados

- **Búsqueda simple**: < 500ms
- **Búsqueda con filtros**: < 800ms
- **Autocompletado**: < 200ms
- **Carga de historial**: < 100ms

---

## 🐛 Solución de Problemas

### Problema: Resultados no relevantes

**Solución:**
1. Ajustar umbral de similitud (aumentar a 0.5-0.6)
2. Mejorar textos descriptivos de envíos
3. Entrenar modelo personalizado con datos propios

### Problema: Búsqueda lenta

**Solución:**
1. Implementar caché de embeddings
2. Reducir número de envíos procesados
3. Usar índices de base de datos
4. Considerar ElasticSearch para búsqueda

### Problema: Sugerencias no aparecen

**Solución:**
1. Verificar que el backend está respondiendo
2. Revisar console del navegador para errores
3. Verificar configuración de CORS
4. Verificar que se escriben al menos 3 caracteres

---

## 🔄 Integración con Búsqueda Tradicional

El **Componente Unificado** (`busqueda-unificada.component`) combina ambas búsquedas:

### Uso del Componente Unificado

```html
<!-- Ruta recomendada -->
<a routerLink="/busqueda">Búsqueda de Envíos</a>
```

El usuario puede alternar entre:
- **Búsqueda Exacta**: Filtros tradicionales específicos
- **Búsqueda Semántica**: Lenguaje natural con IA

### Ventajas

- ✅ Un solo punto de entrada
- ✅ Transición fluida entre modos
- ✅ Mantiene preferencia del usuario
- ✅ Experiencia de usuario unificada

---

## 📚 Tecnologías Utilizadas

### Frontend
- **Angular 17+**: Framework principal
- **TypeScript 5+**: Lenguaje
- **RxJS 7+**: Programación reactiva
- **CSS3**: Estilos modernos

### Backend (Recomendado)
- **Django REST Framework**: API
- **Sentence Transformers**: Embeddings semánticos
- **PyTorch**: Framework de ML
- **PostgreSQL**: Base de datos con pg_trgm

### Modelos de IA Sugeridos
1. **paraphrase-multilingual-MiniLM-L12-v2** (Recomendado)
   - Multiidioma (incluye español)
   - Ligero y rápido
   - 118M parámetros

2. **distiluse-base-multilingual-cased-v2**
   - Más preciso
   - Más pesado

3. **all-MiniLM-L6-v2**
   - Muy rápido
   - Solo inglés (traducir consultas)

---

## 🎓 Capacitación de Usuarios

### Para Usuarios Finales (15 minutos)

1. **Introducción** (3 min)
   - Qué es búsqueda semántica
   - Ventajas sobre búsqueda tradicional

2. **Demostración** (7 min)
   - Ejemplos de búsquedas
   - Interpretación de resultados
   - Puntuación de similitud

3. **Práctica** (5 min)
   - Usuarios prueban búsquedas
   - Q&A

### Tips para Usuarios

**Búsquedas Efectivas:**
- ✅ "envíos entregados en Quito esta semana"
- ✅ "paquetes pendientes para María González"
- ✅ "envíos retrasados a la costa"

**Evitar:**
- ❌ Consultas muy vagas: "envíos"
- ❌ Código exactos (usar búsqueda tradicional)
- ❌ Consultas muy largas (>100 palabras)

---

## 📈 Próximas Mejoras

### Fase 1 (Corto plazo)
- ✅ Exportación de resultados
- ✅ Búsqueda por imágenes (foto del paquete)
- ✅ Reconocimiento de voz

### Fase 2 (Mediano plazo)
- ✅ Aprendizaje continuo del modelo
- ✅ Búsqueda multiidioma avanzada
- ✅ Sinónimos personalizados por empresa

### Fase 3 (Largo plazo)
- ✅ IA conversacional (chatbot)
- ✅ Predicción de consultas
- ✅ Análisis de sentimiento en búsquedas

---

## 📞 Soporte

### Documentación Adicional
- README principal del módulo de búsqueda tradicional
- Documentación de API del backend
- Guía de implementación de IA

### Contacto
- **Email**: soporte@universalbox.com
- **Documentación**: `/docs/busqueda-semantica`

---

## ✅ Checklist de Implementación

- [x] Interfaces y modelos creados
- [x] Servicios API actualizados
- [x] Componente principal implementado
- [x] Template HTML completo
- [x] Estilos CSS modernos
- [x] Componente unificado creado
- [x] Rutas configuradas
- [x] Pruebas unitarias (25+ tests)
- [ ] Backend implementado
- [ ] Modelo de IA integrado
- [ ] Pruebas de integración
- [ ] Documentación de usuario final
- [ ] Capacitación realizada

---

## 🎉 ¡Módulo Completado!

El Módulo de Búsqueda Semántica está **listo para ser integrado** con el backend. 

**Próximo paso crítico**: Implementar los endpoints del backend con el modelo de IA.

---

*Desarrollado para Universal Box - Sistema de Gestión de Envíos*
*Versión 1.0.0 - Octubre 2025*

