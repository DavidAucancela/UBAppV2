from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Sum
from django.utils import timezone
import json
import pandas as pd
from .models import Shipment, Product
from .serializers import (
    ShipmentSerializer, ShipmentListSerializer, ShipmentCreateSerializer,
    ShipmentUpdateSerializer, ShipmentArchiveSerializer, ShipmentBulkImportSerializer,
    ProductSerializer
)
from users.permissions import CanEditShipment


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all()
    permission_classes = [permissions.IsAuthenticated, CanEditShipment]
    filterset_fields = ['status', 'priority', 'is_archived']
    search_fields = ['shipment_id', 'tracking_number', 'sender_name', 'recipient_name']
    ordering_fields = ['created_at', 'status', 'priority']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ShipmentCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ShipmentUpdateSerializer
        elif self.action == 'list':
            return ShipmentListSerializer
        return ShipmentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range if provided
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        shipment = self.get_object()
        serializer = ShipmentArchiveSerializer(data=request.data)
        
        if serializer.is_valid():
            shipment.archive(reason=serializer.data.get('reason', ''))
            return Response({'message': 'Shipment archived successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def unarchive(self, request, pk=None):
        shipment = self.get_object()
        shipment.is_archived = False
        shipment.archived_date = None
        shipment.archive_reason = ''
        shipment.status = 'PENDING'
        shipment.save()
        return Response({'message': 'Shipment unarchived successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        serializer = ShipmentBulkImportSerializer(data=request.data)
        
        if serializer.is_valid():
            file = serializer.validated_data['file']
            
            try:
                # Read JSON file
                data = json.load(file)
                
                # Data cleansing
                cleaned_data = self._clean_import_data(data)
                
                # Create shipments
                created_count = 0
                errors = []
                
                for shipment_data in cleaned_data:
                    try:
                        products_data = shipment_data.pop('products', [])
                        shipment_data['created_by'] = request.user
                        
                        shipment = Shipment.objects.create(**shipment_data)
                        
                        for product_data in products_data:
                            Product.objects.create(shipment=shipment, **product_data)
                        
                        created_count += 1
                    except Exception as e:
                        errors.append(str(e))
                
                return Response({
                    'message': f'Successfully imported {created_count} shipments',
                    'errors': errors
                }, status=status.HTTP_201_CREATED)
                
            except json.JSONDecodeError:
                return Response({'error': 'Invalid JSON file'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        queryset = self.get_queryset()
        
        if query:
            queryset = queryset.filter(
                Q(shipment_id__icontains=query) |
                Q(tracking_number__icontains=query) |
                Q(sender_name__icontains=query) |
                Q(recipient_name__icontains=query) |
                Q(sender_email__icontains=query) |
                Q(recipient_email__icontains=query)
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ShipmentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ShipmentListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        queryset = self.get_queryset()
        
        stats = {
            'total_shipments': queryset.count(),
            'active_shipments': queryset.exclude(status__in=['DELIVERED', 'CANCELLED', 'ARCHIVED']).count(),
            'archived_shipments': queryset.filter(is_archived=True).count(),
            'shipments_by_status': {},
            'shipments_by_priority': {},
            'total_value': queryset.aggregate(total=Sum('value'))['total'] or 0,
            'average_shipping_cost': queryset.aggregate(avg=Sum('shipping_cost'))['avg'] or 0,
        }
        
        # Count by status
        for status, label in Shipment.STATUS_CHOICES:
            stats['shipments_by_status'][status] = queryset.filter(status=status).count()
        
        # Count by priority
        for priority, label in Shipment.PRIORITY_CHOICES:
            stats['shipments_by_priority'][priority] = queryset.filter(priority=priority).count()
        
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        shipment = self.get_object()
        products = shipment.products.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    def _clean_import_data(self, data):
        """Clean and validate imported data"""
        cleaned_data = []
        
        for item in data:
            # Remove any null or empty values
            cleaned_item = {k: v for k, v in item.items() if v is not None and v != ''}
            
            # Ensure required fields
            required_fields = [
                'sender_name', 'sender_address', 'sender_city', 'sender_state',
                'sender_zip', 'sender_phone', 'sender_email',
                'recipient_name', 'recipient_address', 'recipient_city', 'recipient_state',
                'recipient_zip', 'recipient_phone', 'recipient_email',
                'weight', 'value'
            ]
            
            # Skip if missing required fields
            if all(field in cleaned_item for field in required_fields):
                # Convert string numbers to proper types
                try:
                    cleaned_item['weight'] = float(cleaned_item['weight'])
                    cleaned_item['value'] = float(cleaned_item['value'])
                    if 'insurance_amount' in cleaned_item:
                        cleaned_item['insurance_amount'] = float(cleaned_item['insurance_amount'])
                    if 'shipping_cost' in cleaned_item:
                        cleaned_item['shipping_cost'] = float(cleaned_item['shipping_cost'])
                except (ValueError, TypeError):
                    continue
                
                cleaned_data.append(cleaned_item)
        
        return cleaned_data


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, CanEditShipment]
    filterset_fields = ['category', 'is_fragile', 'is_hazardous']
    search_fields = ['name', 'description', 'sku', 'barcode']