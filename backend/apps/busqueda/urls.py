from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusquedaViewSet

router = DefaultRouter()
router.register(r'', BusquedaViewSet, basename='busqueda')

# Las URLs generadas automáticamente por el router incluyen:
# GET /api/busqueda/ - Listado de búsquedas
# POST /api/busqueda/ - Crear búsqueda
# GET /api/busqueda/buscar/ - Búsqueda tradicional
# GET /api/busqueda/historial/ - Historial de búsquedas
# DELETE /api/busqueda/limpiar_historial/ - Limpiar historial
# GET /api/busqueda/estadisticas/ - Estadísticas
# POST /api/busqueda/semantica/ - Búsqueda semántica (principal)
# GET /api/busqueda/semantica/sugerencias/ - Sugerencias semánticas
# GET /api/busqueda/semantica/historial/ - Historial semántico
# POST /api/busqueda/semantica/historial/ - Guardar en historial semántico
# DELETE /api/busqueda/semantica/historial/ - Limpiar historial semántico
# POST /api/busqueda/semantica/feedback/ - Enviar feedback
# GET /api/busqueda/semantica/metricas/ - Métricas semánticas

urlpatterns = [
    path('', include(router.urls)),
] 