from django.contrib import admin
from .models import Shipment, Product


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fields = ['name', 'category', 'quantity', 'unit_price', 'weight', 'is_fragile']


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = [
        'shipment_id', 'tracking_number', 'status', 'priority',
        'sender_name', 'recipient_name', 'created_at', 'is_archived'
    ]
    list_filter = ['status', 'priority', 'is_archived', 'created_at']
    search_fields = [
        'shipment_id', 'tracking_number', 'sender_name', 'recipient_name',
        'sender_email', 'recipient_email'
    ]
    readonly_fields = ['shipment_id', 'tracking_number', 'created_at', 'updated_at']
    inlines = [ProductInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('shipment_id', 'tracking_number', 'status', 'priority')
        }),
        ('Sender Information', {
            'fields': (
                'sender_name', 'sender_company', 'sender_address',
                'sender_city', 'sender_state', 'sender_zip',
                'sender_country', 'sender_phone', 'sender_email'
            )
        }),
        ('Recipient Information', {
            'fields': (
                'recipient_name', 'recipient_company', 'recipient_address',
                'recipient_city', 'recipient_state', 'recipient_zip',
                'recipient_country', 'recipient_phone', 'recipient_email'
            )
        }),
        ('Shipment Details', {
            'fields': (
                'weight', 'dimensions', 'value', 'insurance_amount', 'shipping_cost'
            )
        }),
        ('Dates', {
            'fields': (
                'created_at', 'updated_at', 'shipped_date',
                'estimated_delivery', 'actual_delivery'
            )
        }),
        ('Archive Information', {
            'fields': ('is_archived', 'archived_date', 'archive_reason'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'updated_by', 'notes'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'shipment', 'category', 'quantity', 'unit_price',
        'total_price', 'is_fragile', 'is_hazardous'
    ]
    list_filter = ['category', 'is_fragile', 'is_hazardous', 'requires_refrigeration']
    search_fields = ['name', 'description', 'sku', 'barcode', 'shipment__shipment_id']
    readonly_fields = ['total_price', 'created_at', 'updated_at']