from rest_framework import serializers
from .models import Shipment, Product
from users.serializers import UserListSerializer


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'sku', 'barcode',
            'quantity', 'unit_price', 'total_price', 'weight', 'dimensions',
            'is_fragile', 'is_hazardous', 'requires_refrigeration', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ['shipment', 'total_price']


class ShipmentSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    created_by = UserListSerializer(read_only=True)
    updated_by = UserListSerializer(read_only=True)
    total_products = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Shipment
        fields = '__all__'
        read_only_fields = [
            'shipment_id', 'tracking_number', 'created_at', 'updated_at',
            'created_by', 'updated_by', 'total_products', 'total_value'
        ]
    
    def get_total_products(self, obj):
        return obj.products.count()
    
    def get_total_value(self, obj):
        return sum(product.total_price for product in obj.products.all())


class ShipmentListSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()
    total_products = serializers.SerializerMethodField()
    
    class Meta:
        model = Shipment
        fields = [
            'id', 'shipment_id', 'tracking_number', 'status', 'priority',
            'sender_name', 'recipient_name', 'recipient_city', 'recipient_country',
            'created_at', 'created_by', 'total_products', 'is_archived'
        ]
    
    def get_total_products(self, obj):
        return obj.products.count()


class ShipmentCreateSerializer(serializers.ModelSerializer):
    products = ProductCreateSerializer(many=True)
    
    class Meta:
        model = Shipment
        exclude = [
            'shipment_id', 'tracking_number', 'created_by', 'updated_by',
            'is_archived', 'archived_date', 'archive_reason'
        ]
    
    def create(self, validated_data):
        products_data = validated_data.pop('products')
        shipment = Shipment.objects.create(**validated_data)
        
        for product_data in products_data:
            Product.objects.create(shipment=shipment, **product_data)
        
        return shipment


class ShipmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        exclude = [
            'shipment_id', 'tracking_number', 'created_by', 'updated_by',
            'created_at', 'updated_at'
        ]


class ShipmentArchiveSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)


class ShipmentBulkImportSerializer(serializers.Serializer):
    file = serializers.FileField()
    
    def validate_file(self, value):
        if not value.name.endswith('.json'):
            raise serializers.ValidationError("Only JSON files are supported")
        return value


class ShipmentSearchSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=Shipment.STATUS_CHOICES, required=False)
    priority = serializers.ChoiceField(choices=Shipment.PRIORITY_CHOICES, required=False)
    sender_name = serializers.CharField(required=False)
    recipient_name = serializers.CharField(required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    is_archived = serializers.BooleanField(required=False)