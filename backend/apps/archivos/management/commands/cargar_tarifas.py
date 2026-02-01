from django.core.management.base import BaseCommand
from apps.archivos.models import Tarifa


class Command(BaseCommand):
    help = 'Carga 35 tarifas (7 por categoría) cubriendo rangos de 0 a 1000 kg'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando carga de 35 tarifas (7 por categoría)...'))
        
        # Definir rangos de peso secuenciales (0-1000 kg)
        # Nota: Los rangos son inclusivos en ambos extremos
        # Para evitar solapamiento, el peso máximo de un rango es exclusivo del siguiente
        # Ejemplo: 0-2.99, 3-6.99, 7-9.99, etc.
        rangos_peso = [
            {'min': 0.0, 'max': 2.99},      # 0-2.99 kg
            {'min': 3.0, 'max': 6.99},       # 3-6.99 kg (3-7 según ejemplo del usuario)
            {'min': 7.0, 'max': 9.99},      # 7-9.99 kg (7-10 según ejemplo del usuario)
            {'min': 10.0, 'max': 24.99},    # 10-24.99 kg
            {'min': 25.0, 'max': 49.99},    # 25-49.99 kg
            {'min': 50.0, 'max': 99.99},     # 50-99.99 kg
            {'min': 100.0, 'max': 1000.0},  # 100-1000 kg (inclusive hasta 1000)
        ]
        
        # Definir precios por categoría (precio_por_kg, cargo_base) para cada rango
        # Electrónica: más cara (productos frágiles)
        precios_electronica = [
            {'precio_kg': 9.00, 'cargo_base': 6.00},  # 0-3 kg
            {'precio_kg': 8.50, 'cargo_base': 7.00},  # 3-7 kg
            {'precio_kg': 8.00, 'cargo_base': 8.00},  # 7-10 kg
            {'precio_kg': 7.50, 'cargo_base': 10.00}, # 10-25 kg
            {'precio_kg': 7.00, 'cargo_base': 12.00}, # 25-50 kg
            {'precio_kg': 6.50, 'cargo_base': 15.00}, # 50-100 kg
            {'precio_kg': 6.00, 'cargo_base': 20.00}, # 100-1000 kg
        ]
        
        # Ropa: tarifa estándar
        precios_ropa = [
            {'precio_kg': 6.00, 'cargo_base': 4.00},  # 0-3 kg
            {'precio_kg': 5.50, 'cargo_base': 5.00},  # 3-7 kg
            {'precio_kg': 5.00, 'cargo_base': 6.00},  # 7-10 kg
            {'precio_kg': 4.50, 'cargo_base': 8.00}, # 10-25 kg
            {'precio_kg': 4.00, 'cargo_base': 10.00}, # 25-50 kg
            {'precio_kg': 3.50, 'cargo_base': 12.00}, # 50-100 kg
            {'precio_kg': 3.00, 'cargo_base': 15.00}, # 100-1000 kg
        ]
        
        # Hogar: tarifa media-alta (productos voluminosos)
        precios_hogar = [
            {'precio_kg': 7.00, 'cargo_base': 5.00},  # 0-3 kg
            {'precio_kg': 6.50, 'cargo_base': 6.00},  # 3-7 kg
            {'precio_kg': 6.00, 'cargo_base': 7.00},  # 7-10 kg
            {'precio_kg': 5.50, 'cargo_base': 9.00},  # 10-25 kg
            {'precio_kg': 5.00, 'cargo_base': 11.00}, # 25-50 kg
            {'precio_kg': 4.50, 'cargo_base': 14.00}, # 50-100 kg
            {'precio_kg': 4.00, 'cargo_base': 18.00}, # 100-1000 kg
        ]
        
        # Deportes: tarifa estándar
        precios_deportes = [
            {'precio_kg': 6.50, 'cargo_base': 4.50},  # 0-3 kg
            {'precio_kg': 6.00, 'cargo_base': 5.50},  # 3-7 kg
            {'precio_kg': 5.50, 'cargo_base': 6.50},  # 7-10 kg
            {'precio_kg': 5.00, 'cargo_base': 8.50},  # 10-25 kg
            {'precio_kg': 4.50, 'cargo_base': 10.50}, # 25-50 kg
            {'precio_kg': 4.00, 'cargo_base': 13.00}, # 50-100 kg
            {'precio_kg': 3.50, 'cargo_base': 16.00}, # 100-1000 kg
        ]
        
        # Otros: tarifa general (más económica)
        precios_otros = [
            {'precio_kg': 5.50, 'cargo_base': 3.50},  # 0-3 kg
            {'precio_kg': 5.00, 'cargo_base': 4.50},  # 3-7 kg
            {'precio_kg': 4.50, 'cargo_base': 5.50},  # 7-10 kg
            {'precio_kg': 4.00, 'cargo_base': 7.50},  # 10-25 kg
            {'precio_kg': 3.50, 'cargo_base': 9.50},  # 25-50 kg
            {'precio_kg': 3.00, 'cargo_base': 11.50}, # 50-100 kg
            {'precio_kg': 2.50, 'cargo_base': 14.00}, # 100-1000 kg
        ]
        
        # Mapeo de categorías a precios
        precios_por_categoria = {
            'electronica': precios_electronica,
            'ropa': precios_ropa,
            'hogar': precios_hogar,
            'deportes': precios_deportes,
            'otros': precios_otros,
        }
        
        # Generar todas las tarifas
        tarifas_ejemplo = []
        categorias = ['electronica', 'ropa', 'hogar', 'deportes', 'otros']
        
        for categoria in categorias:
            precios = precios_por_categoria[categoria]
            for i, rango in enumerate(rangos_peso):
                tarifas_ejemplo.append({
                    'categoria': categoria,
                    'peso_minimo': rango['min'],
                    'peso_maximo': rango['max'],
                    'precio_por_kg': precios[i]['precio_kg'],
                    'cargo_base': precios[i]['cargo_base'],
                    'activa': True
                })
        
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
                        f"[OK] Creada: {tarifa_data['categoria']} "
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

