#!/usr/bin/env python
"""
Script to populate the Universal Box system with sample data for testing purposes.
Run this script after setting up the database and creating a superuser.

Usage: python sample_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DRF_APP_BACKEND.settings')
django.setup()

from django.contrib.auth import get_user_model
from archivos.models import Envio, Producto
from dashboard.models import DashboardMetric, Report, UserActivity

Usuario = get_user_model()

def create_sample_users():
    """Create sample users with different roles"""
    print("Creating sample users...")
    
    # Admin user (if not exists)
    admin, created = Usuario.objects.get_or_create(
        username='admin',
        defaults={
            'nombre': 'Administrador del Sistema',
            'correo': 'admin@universalbox.com',
            'cedula': '1234567890',
            'rol': 1,
            'telefono': '+1234567890',
            'direccion': 'Oficina Principal',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"Created admin user: {admin.username}")
    
    # Gerente users
    gerentes_data = [
        {
            'username': 'gerente1',
            'nombre': 'María González',
            'correo': 'maria.gonzalez@universalbox.com',
            'cedula': '1234567891',
            'telefono': '+1234567891'
        },
        {
            'username': 'gerente2',
            'nombre': 'Carlos Rodríguez',
            'correo': 'carlos.rodriguez@universalbox.com',
            'cedula': '1234567892',
            'telefono': '+1234567892'
        }
    ]
    
    for data in gerentes_data:
        user, created = Usuario.objects.get_or_create(
            username=data['username'],
            defaults={
                **data,
                'rol': 2,
                'direccion': 'Oficina de Gerencia'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"Created gerente user: {user.username}")
    
    # Digitador users
    digitadores_data = [
        {
            'username': 'digitador1',
            'nombre': 'Ana Martínez',
            'correo': 'ana.martinez@universalbox.com',
            'cedula': '1234567893',
            'telefono': '+1234567893'
        },
        {
            'username': 'digitador2',
            'nombre': 'Luis Herrera',
            'correo': 'luis.herrera@universalbox.com',
            'cedula': '1234567894',
            'telefono': '+1234567894'
        },
        {
            'username': 'digitador3',
            'nombre': 'Sofia López',
            'correo': 'sofia.lopez@universalbox.com',
            'cedula': '1234567895',
            'telefono': '+1234567895'
        }
    ]
    
    for data in digitadores_data:
        user, created = Usuario.objects.get_or_create(
            username=data['username'],
            defaults={
                **data,
                'rol': 3,
                'direccion': 'Oficina de Digitación'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"Created digitador user: {user.username}")
    
    # Comprador users
    compradores_data = [
        {
            'username': 'comprador1',
            'nombre': 'Juan Pérez',
            'correo': 'juan.perez@email.com',
            'cedula': '0987654321',
            'telefono': '+0987654321'
        },
        {
            'username': 'comprador2',
            'nombre': 'Laura Silva',
            'correo': 'laura.silva@email.com',
            'cedula': '0987654322',
            'telefono': '+0987654322'
        },
        {
            'username': 'comprador3',
            'nombre': 'Roberto García',
            'correo': 'roberto.garcia@email.com',
            'cedula': '0987654323',
            'telefono': '+0987654323'
        },
        {
            'username': 'comprador4',
            'nombre': 'Carmen Ruiz',
            'correo': 'carmen.ruiz@email.com',
            'cedula': '0987654324',
            'telefono': '+0987654324'
        },
        {
            'username': 'comprador5',
            'nombre': 'Diego Morales',
            'correo': 'diego.morales@email.com',
            'cedula': '0987654325',
            'telefono': '+0987654325'
        }
    ]
    
    for data in compradores_data:
        user, created = Usuario.objects.get_or_create(
            username=data['username'],
            defaults={
                **data,
                'rol': 4,
                'direccion': 'Dirección del Cliente'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"Created comprador user: {user.username}")

def create_sample_shipments():
    """Create sample shipments with products"""
    print("Creating sample shipments...")
    
    compradores = Usuario.objects.filter(rol=4)
    if not compradores:
        print("No compradores found. Creating users first...")
        create_sample_users()
        compradores = Usuario.objects.filter(rol=4)
    
    # Sample product data
    productos_sample = [
        {'descripcion': 'Laptop Dell XPS 13', 'categoria': 'electronica', 'peso_base': 1.5, 'valor_base': 1200},
        {'descripcion': 'iPhone 15 Pro', 'categoria': 'electronica', 'peso_base': 0.3, 'valor_base': 1000},
        {'descripcion': 'Camiseta Nike', 'categoria': 'ropa', 'peso_base': 0.2, 'valor_base': 50},
        {'descripcion': 'Jeans Levis', 'categoria': 'ropa', 'peso_base': 0.5, 'valor_base': 80},
        {'descripcion': 'Cafetera Nespresso', 'categoria': 'hogar', 'peso_base': 3.0, 'valor_base': 200},
        {'descripcion': 'Aspiradora Dyson', 'categoria': 'hogar', 'peso_base': 5.0, 'valor_base': 400},
        {'descripcion': 'Balón de Fútbol', 'categoria': 'deportes', 'peso_base': 0.4, 'valor_base': 30},
        {'descripcion': 'Raqueta de Tenis', 'categoria': 'deportes', 'peso_base': 0.3, 'valor_base': 150},
        {'descripcion': 'Auriculares Sony', 'categoria': 'electronica', 'peso_base': 0.25, 'valor_base': 300},
        {'descripcion': 'Libro de Cocina', 'categoria': 'otros', 'peso_base': 0.8, 'valor_base': 25},
        {'descripcion': 'Perfume Chanel', 'categoria': 'otros', 'peso_base': 0.15, 'valor_base': 120},
        {'descripcion': 'Reloj Casio', 'categoria': 'otros', 'peso_base': 0.1, 'valor_base': 200}
    ]
    
    estados = ['pendiente', 'en_transito', 'entregado', 'cancelado']
    
    # Create shipments for the last 6 months
    start_date = datetime.now() - timedelta(days=180)
    
    for i in range(100):  # Create 100 sample shipments
        # Random date in the last 6 months
        random_days = random.randint(0, 180)
        fecha_emision = start_date + timedelta(days=random_days)
        
        # Random comprador
        comprador = random.choice(compradores)
        
        # Generate HAWB
        hawb = f"UB{fecha_emision.strftime('%Y%m')}{str(i+1).zfill(4)}"
        
        # Random estado (more likely to be delivered for older shipments)
        days_old = (datetime.now() - fecha_emision).days
        if days_old > 30:
            estado = random.choices(estados, weights=[10, 20, 60, 10])[0]
        elif days_old > 7:
            estado = random.choices(estados, weights=[20, 50, 25, 5])[0]
        else:
            estado = random.choices(estados, weights=[60, 30, 5, 5])[0]
        
        # Create shipment
        envio = Envio.objects.create(
            hawb=hawb,
            comprador=comprador,
            estado=estado,
            peso_total=0,  # Will be calculated
            cantidad_total=0,  # Will be calculated
            valor_total=0,  # Will be calculated
            observaciones=f"Envío de prueba #{i+1}",
            fecha_emision=fecha_emision
        )
        
        # Add random products to shipment
        num_productos = random.randint(1, 5)
        for j in range(num_productos):
            producto_data = random.choice(productos_sample)
            
            # Add some variation to weight and value
            peso_variation = random.uniform(0.8, 1.2)
            valor_variation = random.uniform(0.9, 1.1)
            
            Producto.objects.create(
                descripcion=producto_data['descripcion'],
                categoria=producto_data['categoria'],
                peso=Decimal(str(producto_data['peso_base'] * peso_variation)),
                cantidad=random.randint(1, 3),
                valor=Decimal(str(producto_data['valor_base'] * valor_variation)),
                envio=envio
            )
        
        # Recalculate totals
        envio.calcular_totales()
        
        if i % 10 == 0:
            print(f"Created {i+1} shipments...")
    
    print(f"Created {Envio.objects.count()} total shipments")

def create_sample_activities():
    """Create sample user activities"""
    print("Creating sample user activities...")
    
    usuarios = Usuario.objects.all()
    envios = Envio.objects.all()
    productos = Producto.objects.all()
    
    activities = [
        'login', 'create_envio', 'update_envio', 'create_producto',
        'search', 'export_data', 'generate_report'
    ]
    
    # Create activities for the last 30 days
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(200):  # Create 200 sample activities
        random_hours = random.randint(0, 720)  # 30 days * 24 hours
        fecha_actividad = start_date + timedelta(hours=random_hours)
        
        usuario = random.choice(usuarios)
        action = random.choice(activities)
        
        # Create appropriate description based on action
        if action == 'create_envio' and envios:
            envio = random.choice(envios)
            description = f"Creado envío {envio.hawb}"
            object_type = 'Envio'
            object_id = envio.id
        elif action == 'create_producto' and productos:
            producto = random.choice(productos)
            description = f"Creado producto {producto.descripcion}"
            object_type = 'Producto'
            object_id = producto.id
        elif action == 'search':
            description = f"Búsqueda realizada: {random.choice(['laptop', 'envío', 'producto', 'usuario'])}"
            object_type = None
            object_id = None
        else:
            description = f"Acción {action} realizada"
            object_type = None
            object_id = None
        
        UserActivity.objects.create(
            user=usuario,
            action=action,
            description=description,
            object_type=object_type,
            object_id=object_id,
            created_at=fecha_actividad
        )
        
        if i % 50 == 0:
            print(f"Created {i+1} activities...")
    
    print(f"Created {UserActivity.objects.count()} total activities")

def create_sample_reports():
    """Create sample reports"""
    print("Creating sample reports...")
    
    usuarios = Usuario.objects.filter(rol__in=[1, 2])  # Only admins and gerentes
    
    report_types = [
        'envios_summary',
        'productos_analysis',
        'usuarios_activity',
        'financial_summary'
    ]
    
    for i in range(10):
        usuario = random.choice(usuarios)
        report_type = random.choice(report_types)
        
        # Random date in the last 30 days
        created_date = datetime.now() - timedelta(days=random.randint(0, 30))
        
        status = random.choices(
            ['completed', 'pending', 'processing', 'failed'],
            weights=[70, 15, 10, 5]
        )[0]
        
        Report.objects.create(
            name=f"Reporte {report_type.replace('_', ' ').title()} #{i+1}",
            report_type=report_type,
            description=f"Reporte generado automáticamente para {report_type}",
            requested_by=usuario,
            status=status,
            date_from=(created_date - timedelta(days=30)).date(),
            date_to=created_date.date(),
            created_at=created_date,
            parameters={'auto_generated': True, 'sample_data': True}
        )
    
    print(f"Created {Report.objects.count()} total reports")

def create_sample_metrics():
    """Create sample dashboard metrics"""
    print("Creating sample dashboard metrics...")
    
    metric_types = [
        'envios_count',
        'envios_value',
        'envios_weight',
        'productos_count',
        'usuarios_activos',
        'compradores_activos'
    ]
    
    period_types = ['daily', 'weekly', 'monthly']
    
    # Create metrics for the last 3 months
    start_date = datetime.now() - timedelta(days=90)
    
    for metric_type in metric_types:
        for period_type in period_types:
            if period_type == 'daily':
                days_range = range(90)
                date_increment = timedelta(days=1)
            elif period_type == 'weekly':
                days_range = range(0, 90, 7)
                date_increment = timedelta(days=7)
            else:  # monthly
                days_range = range(0, 90, 30)
                date_increment = timedelta(days=30)
            
            for day in days_range:
                metric_date = start_date + timedelta(days=day)
                
                # Generate realistic values based on metric type
                if 'count' in metric_type:
                    base_value = random.randint(10, 100)
                    count = base_value
                elif 'value' in metric_type:
                    base_value = random.randint(1000, 50000)
                    count = random.randint(5, 50)
                elif 'weight' in metric_type:
                    base_value = random.randint(100, 1000)
                    count = random.randint(5, 50)
                else:
                    base_value = random.randint(5, 25)
                    count = base_value
                
                DashboardMetric.objects.create(
                    metric_type=metric_type,
                    period_type=period_type,
                    date=metric_date.date(),
                    value=Decimal(str(base_value)),
                    count=count,
                    metadata={'generated': True, 'sample': True}
                )
    
    print(f"Created {DashboardMetric.objects.count()} total metrics")

def main():
    """Main function to create all sample data"""
    print("Starting sample data creation...")
    print("=" * 50)
    
    try:
        # Create sample data in order
        create_sample_users()
        print("-" * 30)
        
        create_sample_shipments()
        print("-" * 30)
        
        create_sample_activities()
        print("-" * 30)
        
        create_sample_reports()
        print("-" * 30)
        
        create_sample_metrics()
        print("-" * 30)
        
        print("Sample data creation completed successfully!")
        print("=" * 50)
        
        # Print summary
        print(f"Total Users: {Usuario.objects.count()}")
        print(f"Total Shipments: {Envio.objects.count()}")
        print(f"Total Products: {Producto.objects.count()}")
        print(f"Total Activities: {UserActivity.objects.count()}")
        print(f"Total Reports: {Report.objects.count()}")
        print(f"Total Metrics: {DashboardMetric.objects.count()}")
        
        print("\nLogin credentials:")
        print("Admin: admin / admin123")
        print("Gerente: gerente1 / password123")
        print("Digitador: digitador1 / password123")
        print("Comprador: comprador1 / password123")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()