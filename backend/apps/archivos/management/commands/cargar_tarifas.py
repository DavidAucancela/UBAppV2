from django.core.management.base import BaseCommand
from apps.archivos.models import Tarifa


class Command(BaseCommand):
    help = 'Carga tarifas de ejemplo para el sistema de envíos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando carga de tarifas de ejemplo...'))
        
        # Eliminar tarifas existentes si se desea empezar desde cero
        # Tarifa.objects.all().delete()
        
        tarifas_ejemplo = [
            # ELECTRÓNICA - Productos frágiles, tarifa más alta
            {
                'categoria': 'electronica',
                'peso_minimo': 0.0,
                'peso_maximo': 1.0,
                'precio_por_kg': 8.50,
                'cargo_base': 5.00,
                'activa': True
            },
            {
                'categoria': 'electronica',
                'peso_minimo': 1.01,
                'peso_maximo': 5.0,
                'precio_por_kg': 7.00,
                'cargo_base': 8.00,
                'activa': True
            },
            {
                'categoria': 'electronica',
                'peso_minimo': 5.01,
                'peso_maximo': 20.0,
                'precio_por_kg': 6.00,
                'cargo_base': 12.00,
                'activa': True
            },
            {
                'categoria': 'electronica',
                'peso_minimo': 20.01,
                'peso_maximo': 100.0,
                'precio_por_kg': 5.00,
                'cargo_base': 20.00,
                'activa': True
            },
            
            # ROPA - Tarifa estándar
            {
                'categoria': 'ropa',
                'peso_minimo': 0.0,
                'peso_maximo': 1.0,
                'precio_por_kg': 5.00,
                'cargo_base': 3.00,
                'activa': True
            },
            {
                'categoria': 'ropa',
                'peso_minimo': 1.01,
                'peso_maximo': 5.0,
                'precio_por_kg': 4.00,
                'cargo_base': 5.00,
                'activa': True
            },
            {
                'categoria': 'ropa',
                'peso_minimo': 5.01,
                'peso_maximo': 20.0,
                'precio_por_kg': 3.50,
                'cargo_base': 8.00,
                'activa': True
            },
            {
                'categoria': 'ropa',
                'peso_minimo': 20.01,
                'peso_maximo': 100.0,
                'precio_por_kg': 3.00,
                'cargo_base': 12.00,
                'activa': True
            },
            
            # HOGAR - Productos voluminosos, tarifa media-alta
            {
                'categoria': 'hogar',
                'peso_minimo': 0.0,
                'peso_maximo': 2.0,
                'precio_por_kg': 6.00,
                'cargo_base': 4.00,
                'activa': True
            },
            {
                'categoria': 'hogar',
                'peso_minimo': 2.01,
                'peso_maximo': 10.0,
                'precio_por_kg': 5.00,
                'cargo_base': 7.00,
                'activa': True
            },
            {
                'categoria': 'hogar',
                'peso_minimo': 10.01,
                'peso_maximo': 30.0,
                'precio_por_kg': 4.00,
                'cargo_base': 15.00,
                'activa': True
            },
            {
                'categoria': 'hogar',
                'peso_minimo': 30.01,
                'peso_maximo': 100.0,
                'precio_por_kg': 3.50,
                'cargo_base': 25.00,
                'activa': True
            },
            
            # DEPORTES - Tarifa estándar
            {
                'categoria': 'deportes',
                'peso_minimo': 0.0,
                'peso_maximo': 1.0,
                'precio_por_kg': 5.50,
                'cargo_base': 3.50,
                'activa': True
            },
            {
                'categoria': 'deportes',
                'peso_minimo': 1.01,
                'peso_maximo': 5.0,
                'precio_por_kg': 4.50,
                'cargo_base': 6.00,
                'activa': True
            },
            {
                'categoria': 'deportes',
                'peso_minimo': 5.01,
                'peso_maximo': 20.0,
                'precio_por_kg': 3.80,
                'cargo_base': 10.00,
                'activa': True
            },
            {
                'categoria': 'deportes',
                'peso_minimo': 20.01,
                'peso_maximo': 100.0,
                'precio_por_kg': 3.20,
                'cargo_base': 15.00,
                'activa': True
            },
            
            # OTROS - Tarifa general
            {
                'categoria': 'otros',
                'peso_minimo': 0.0,
                'peso_maximo': 1.0,
                'precio_por_kg': 5.00,
                'cargo_base': 3.00,
                'activa': True
            },
            {
                'categoria': 'otros',
                'peso_minimo': 1.01,
                'peso_maximo': 5.0,
                'precio_por_kg': 4.00,
                'cargo_base': 5.00,
                'activa': True
            },
            {
                'categoria': 'otros',
                'peso_minimo': 5.01,
                'peso_maximo': 20.0,
                'precio_por_kg': 3.50,
                'cargo_base': 8.00,
                'activa': True
            },
            {
                'categoria': 'otros',
                'peso_minimo': 20.01,
                'peso_maximo': 100.0,
                'precio_por_kg': 3.00,
                'cargo_base': 12.00,
                'activa': True
            },
        ]
        
        count_creadas = 0
        count_existentes = 0
        
        for tarifa_data in tarifas_ejemplo:
            # Verificar si ya existe una tarifa con estos parámetros
            tarifa_existe = Tarifa.objects.filter(
                categoria=tarifa_data['categoria'],
                peso_minimo=tarifa_data['peso_minimo'],
                peso_maximo=tarifa_data['peso_maximo']
            ).exists()
            
            if not tarifa_existe:
                Tarifa.objects.create(**tarifa_data)
                count_creadas += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Creada: {tarifa_data['categoria']} "
                        f"({tarifa_data['peso_minimo']}-{tarifa_data['peso_maximo']}kg) "
                        f"- ${tarifa_data['precio_por_kg']}/kg + ${tarifa_data['cargo_base']} base"
                    )
                )
            else:
                count_existentes += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"- Ya existe: {tarifa_data['categoria']} "
                        f"({tarifa_data['peso_minimo']}-{tarifa_data['peso_maximo']}kg)"
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*60}\n'
                f'Resumen:\n'
                f'  - Tarifas creadas: {count_creadas}\n'
                f'  - Tarifas que ya existían: {count_existentes}\n'
                f'  - Total procesadas: {len(tarifas_ejemplo)}\n'
                f'{"="*60}'
            )
        )

