from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardMetricViewSet, ReportViewSet, UserActivityViewSet,
    DashboardStatsView, MetricsSummaryView
)

router = DefaultRouter()
router.register(r'metrics', DashboardMetricViewSet)
router.register(r'reports', ReportViewSet)
router.register(r'activities', UserActivityViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('metrics-summary/', MetricsSummaryView.as_view(), name='metrics-summary'),
]