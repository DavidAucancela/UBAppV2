from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShipmentViewSet, ProductViewSet

router = DefaultRouter()
router.register('shipments', ShipmentViewSet)
router.register('products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
]