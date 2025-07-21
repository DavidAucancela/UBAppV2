from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('RETURNED', 'Returned'),
        ('ARCHIVED', 'Archived'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]
    
    # Basic Information
    shipment_id = models.CharField(max_length=50, unique=True, editable=False)
    tracking_number = models.CharField(max_length=100, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='NORMAL')
    
    # Sender Information
    sender_name = models.CharField(max_length=200)
    sender_company = models.CharField(max_length=200, blank=True)
    sender_address = models.TextField()
    sender_city = models.CharField(max_length=100)
    sender_state = models.CharField(max_length=100)
    sender_zip = models.CharField(max_length=20)
    sender_country = models.CharField(max_length=100, default='USA')
    sender_phone = models.CharField(max_length=20)
    sender_email = models.EmailField()
    
    # Recipient Information
    recipient_name = models.CharField(max_length=200)
    recipient_company = models.CharField(max_length=200, blank=True)
    recipient_address = models.TextField()
    recipient_city = models.CharField(max_length=100)
    recipient_state = models.CharField(max_length=100)
    recipient_zip = models.CharField(max_length=20)
    recipient_country = models.CharField(max_length=100, default='USA')
    recipient_phone = models.CharField(max_length=20)
    recipient_email = models.EmailField()
    
    # Shipment Details
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight in kg")
    dimensions = models.CharField(max_length=100, help_text="L x W x H in cm", blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Declared value")
    insurance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Dates
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_date = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)
    
    # Archive
    is_archived = models.BooleanField(default=False)
    archived_date = models.DateTimeField(null=True, blank=True)
    archive_reason = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_shipments')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_shipments')
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'shipments'
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['shipment_id']),
            models.Index(fields=['tracking_number']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.shipment_id:
            self.shipment_id = self.generate_shipment_id()
        if not self.tracking_number:
            self.tracking_number = self.generate_tracking_number()
        super().save(*args, **kwargs)
    
    def generate_shipment_id(self):
        return f"SHP-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    def generate_tracking_number(self):
        return f"UB{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:10].upper()}"
    
    def archive(self, reason=""):
        self.is_archived = True
        self.archived_date = timezone.now()
        self.archive_reason = reason
        self.status = 'ARCHIVED'
        self.save()
    
    def __str__(self):
        return f"{self.shipment_id} - {self.recipient_name}"


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('ELECTRONICS', 'Electronics'),
        ('CLOTHING', 'Clothing'),
        ('FOOD', 'Food & Beverages'),
        ('BOOKS', 'Books'),
        ('FURNITURE', 'Furniture'),
        ('TOYS', 'Toys'),
        ('COSMETICS', 'Cosmetics'),
        ('SPORTS', 'Sports Equipment'),
        ('TOOLS', 'Tools'),
        ('OTHER', 'Other'),
    ]
    
    # Relations
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='products')
    
    # Product Information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    sku = models.CharField(max_length=100, blank=True)
    barcode = models.CharField(max_length=100, blank=True)
    
    # Quantity and Pricing
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    
    # Physical Properties
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight per unit in kg")
    dimensions = models.CharField(max_length=100, blank=True, help_text="L x W x H in cm")
    
    # Additional Information
    is_fragile = models.BooleanField(default=False)
    is_hazardous = models.BooleanField(default=False)
    requires_refrigeration = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['id']
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} (x{self.quantity}) - {self.shipment.shipment_id}"