"""
URLs para la app de métricas.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PruebaControladaSemanticaViewSet,
    MetricaSemanticaViewSet,
    RegistroGeneracionEmbeddingViewSet,
    PruebaCargaViewSet,
    MetricaRendimientoViewSet,
    RegistroManualEnvioViewSet,
    ExportacionMetricasViewSet,
    PruebasSistemaViewSet
)

router = DefaultRouter()
router.register(r'pruebas-controladas', PruebaControladaSemanticaViewSet, basename='prueba-controlada')
router.register(r'metricas-semanticas', MetricaSemanticaViewSet, basename='metrica-semantica')
router.register(r'registros-embedding', RegistroGeneracionEmbeddingViewSet, basename='registro-embedding')
router.register(r'pruebas-carga', PruebaCargaViewSet, basename='prueba-carga')
router.register(r'metricas-rendimiento', MetricaRendimientoViewSet, basename='metrica-rendimiento')
router.register(r'registros-manuales', RegistroManualEnvioViewSet, basename='registro-manual')
router.register(r'exportacion', ExportacionMetricasViewSet, basename='exportacion')
router.register(r'pruebas-sistema', PruebasSistemaViewSet, basename='pruebas-sistema')

urlpatterns = [
    path('', include(router.urls)),
]

