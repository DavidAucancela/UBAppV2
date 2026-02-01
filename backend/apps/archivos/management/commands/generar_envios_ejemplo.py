from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from datetime import datetime, timedelta
import random

from apps.archivos.models import Envio, Producto
from apps.archivos.services import EnvioService
from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Genera 75 envíos de ejemplo con fechas desde noviembre hasta enero'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cantidad',
            type=int,
            default=75,
            help='Número de envíos a crear (default: 75)'
        )

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        self.stdout.write(self.style.SUCCESS(f'Iniciando generación de {cantidad} envíos...'))
        
        # Obtener usuarios compradores existentes
        compradores = Usuario.objects.filter(rol=4, is_active=True)
        if not compradores.exists():
            self.stdout.write(self.style.ERROR('No hay compradores activos en el sistema. Crea al menos un comprador primero.'))
            return
        
        compradores_list = list(compradores)
        self.stdout.write(self.style.SUCCESS(f'Encontrados {len(compradores_list)} compradores activos'))
        
        # Definir rangos de fechas: noviembre 2025, diciembre 2025, enero 2026
        fecha_inicio = datetime(2025, 11, 1, 0, 0, 0)
        fecha_fin = datetime(2026, 1, 31, 23, 59, 59)
        
        # Definir productos de ejemplo por categoría con pesos que se ajusten a las tarifas
        productos_ejemplo = {
            'electronica': [
                {'descripcion': 'Smartphone Samsung Galaxy', 'peso': 0.5, 'valor': 450.00},
                {'descripcion': 'Laptop Dell Inspiron', 'peso': 2.5, 'valor': 850.00},
                {'descripcion': 'Tablet iPad Pro', 'peso': 0.8, 'valor': 650.00},
                {'descripcion': 'Monitor LG 27 pulgadas', 'peso': 5.5, 'valor': 320.00},
                {'descripcion': 'Teclado mecánico RGB', 'peso': 1.2, 'valor': 120.00},
                {'descripcion': 'Mouse inalámbrico Logitech', 'peso': 0.3, 'valor': 45.00},
                {'descripcion': 'Auriculares Sony WH-1000XM4', 'peso': 0.4, 'valor': 280.00},
                {'descripcion': 'Cámara Canon EOS', 'peso': 8.5, 'valor': 1200.00},
                {'descripcion': 'Impresora HP LaserJet', 'peso': 12.5, 'valor': 380.00},
                {'descripcion': 'Router WiFi 6', 'peso': 0.6, 'valor': 95.00},
            ],
            'ropa': [
                {'descripcion': 'Camiseta básica algodón', 'peso': 0.2, 'valor': 15.00},
                {'descripcion': 'Jeans Levis 501', 'peso': 0.8, 'valor': 85.00},
                {'descripcion': 'Chaqueta de cuero', 'peso': 1.5, 'valor': 250.00},
                {'descripcion': 'Zapatos deportivos Nike', 'peso': 1.2, 'valor': 120.00},
                {'descripcion': 'Vestido elegante', 'peso': 0.5, 'valor': 95.00},
                {'descripcion': 'Abrigo de invierno', 'peso': 2.8, 'valor': 180.00},
                {'descripcion': 'Conjunto deportivo', 'peso': 0.6, 'valor': 45.00},
                {'descripcion': 'Bufanda de lana', 'peso': 0.3, 'valor': 25.00},
                {'descripcion': 'Gorra ajustable', 'peso': 0.1, 'valor': 18.00},
                {'descripcion': 'Cinturón de cuero', 'peso': 0.4, 'valor': 35.00},
            ],
            'hogar': [
                {'descripcion': 'Juego de sábanas algodón', 'peso': 1.2, 'valor': 65.00},
                {'descripcion': 'Cafetera Nespresso', 'peso': 3.5, 'valor': 180.00},
                {'descripcion': 'Aspiradora robot', 'peso': 4.2, 'valor': 320.00},
                {'descripcion': 'Lámpara de pie moderna', 'peso': 6.8, 'valor': 95.00},
                {'descripcion': 'Juego de ollas acero inoxidable', 'peso': 8.5, 'valor': 150.00},
                {'descripcion': 'Cortinas blackout', 'peso': 2.3, 'valor': 75.00},
                {'descripcion': 'Alfombra persa', 'peso': 15.5, 'valor': 450.00},
                {'descripcion': 'Mesa de centro vidrio', 'peso': 22.8, 'valor': 280.00},
                {'descripcion': 'Sofá cama desplegable', 'peso': 45.5, 'valor': 650.00},
                {'descripcion': 'Estantería modular', 'peso': 28.5, 'valor': 180.00},
            ],
            'deportes': [
                {'descripcion': 'Pelota de fútbol oficial', 'peso': 0.5, 'valor': 35.00},
                {'descripcion': 'Raqueta de tenis Wilson', 'peso': 0.4, 'valor': 120.00},
                {'descripcion': 'Bicicleta de montaña', 'peso': 15.5, 'valor': 850.00},
                {'descripcion': 'Pesas ajustables 20kg', 'peso': 22.5, 'valor': 180.00},
                {'descripcion': 'Colchoneta yoga', 'peso': 1.8, 'valor': 45.00},
                {'descripcion': 'Mancuernas 10kg par', 'peso': 12.5, 'valor': 95.00},
                {'descripcion': 'Cinta de correr plegable', 'peso': 35.5, 'valor': 450.00},
                {'descripcion': 'Tabla de surf', 'peso': 8.5, 'valor': 320.00},
                {'descripcion': 'Equipo de buceo completo', 'peso': 18.5, 'valor': 650.00},
                {'descripcion': 'Mochila senderismo 50L', 'peso': 2.2, 'valor': 95.00},
            ],
            'otros': [
                {'descripcion': 'Libro de cocina', 'peso': 0.8, 'valor': 25.00},
                {'descripcion': 'Juego de herramientas', 'peso': 5.5, 'valor': 85.00},
                {'descripcion': 'Maleta de viaje rígida', 'peso': 4.8, 'valor': 120.00},
                {'descripcion': 'Caja de juguetes educativos', 'peso': 3.2, 'valor': 65.00},
                {'descripcion': 'Set de maquillaje profesional', 'peso': 1.5, 'valor': 95.00},
                {'descripcion': 'Botiquín de primeros auxilios', 'peso': 2.1, 'valor': 45.00},
                {'descripcion': 'Organizador de escritorio', 'peso': 0.9, 'valor': 35.00},
                {'descripcion': 'Caja de almacenamiento plástico', 'peso': 1.8, 'valor': 28.00},
                {'descripcion': 'Set de vajilla 12 piezas', 'peso': 6.5, 'valor': 75.00},
                {'descripcion': 'Decoración navideña', 'peso': 2.5, 'valor': 55.00},
            ],
        }
        
        # Estados posibles
        estados = ['pendiente', 'en_transito', 'entregado', 'cancelado']
        # Distribución de estados (más entregados y en tránsito que pendientes)
        pesos_estados = [0.15, 0.35, 0.45, 0.05]  # pendiente, en_transito, entregado, cancelado
        
        # Generar envíos
        envios_creados = 0
        envios_con_error = 0
        
        # Calcular días totales y distribuir envíos uniformemente
        dias_totales = (fecha_fin - fecha_inicio).days + 1
        
        for i in range(cantidad):
            try:
                # Seleccionar comprador aleatorio
                comprador = random.choice(compradores_list)
                
                # Calcular fecha distribuida uniformemente
                # Asegurar que i/cantidad esté entre 0 y 1
                progreso = i / max(cantidad - 1, 1) if cantidad > 1 else 0
                dias_desde_inicio = int(progreso * dias_totales)
                # Asegurar que no exceda el rango
                dias_desde_inicio = min(dias_desde_inicio, dias_totales - 1)
                fecha_base = fecha_inicio + timedelta(days=dias_desde_inicio)
                # Agregar variación de horas aleatoria
                # Usar replace para mantener el timezone
                fecha_envio = fecha_base.replace(
                    hour=random.randint(8, 18),
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )
                
                # Generar HAWB único
                hawb = f"HAWB{datetime.now().strftime('%Y%m%d')}{str(i+1).zfill(6)}"
                # Verificar que no exista
                while Envio.objects.filter(hawb=hawb).exists():
                    hawb = f"HAWB{datetime.now().strftime('%Y%m%d')}{str(random.randint(100000, 999999))}"
                
                # Seleccionar estado según distribución
                estado = random.choices(estados, weights=pesos_estados)[0]
                
                # Seleccionar categoría aleatoria
                categoria = random.choice(list(productos_ejemplo.keys()))
                
                # Seleccionar 1-3 productos aleatorios de la categoría
                num_productos = random.randint(1, 3)
                productos_seleccionados = random.sample(productos_ejemplo[categoria], min(num_productos, len(productos_ejemplo[categoria])))
                
                # Preparar datos del envío
                productos_data = []
                for prod_ejemplo in productos_seleccionados:
                    cantidad = random.randint(1, 5)
                    productos_data.append({
                        'descripcion': prod_ejemplo['descripcion'],
                        'categoria': categoria,
                        'peso': Decimal(str(prod_ejemplo['peso'])),
                        'cantidad': cantidad,
                        'valor': Decimal(str(prod_ejemplo['valor'])),
                    })
                
                # Crear envío usando el servicio (esto calculará automáticamente los costos)
                # Necesitamos un usuario administrador para crear envíos
                admin_user = Usuario.objects.filter(rol=1, is_active=True).first()
                if not admin_user:
                    admin_user = Usuario.objects.filter(is_active=True).first()
                
                if not admin_user:
                    self.stdout.write(self.style.ERROR('No hay usuarios activos para crear envíos'))
                    return
                
                data_envio = {
                    'hawb': hawb,
                    'comprador': comprador,
                    'estado': estado,
                    'fecha_emision': fecha_envio,
                    'productos': productos_data,
                }
                
                # Crear envío usando el servicio
                envio = EnvioService.crear_envio(
                    data=data_envio,
                    usuario_creador=admin_user
                )
                
                envios_creados += 1
                
                if envios_creados % 10 == 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Progreso: {envios_creados}/{cantidad} envíos creados...'
                        )
                    )
                    
            except Exception as e:
                envios_con_error += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'Error creando envío {i+1}: {str(e)}'
                    )
                )
                import traceback
                self.stdout.write(self.style.ERROR(traceback.format_exc()))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*60}\n'
                f'Resumen:\n'
                f'  - Envíos creados exitosamente: {envios_creados}\n'
                f'  - Envíos con errores: {envios_con_error}\n'
                f'  - Total procesados: {cantidad}\n'
                f'{"="*60}'
            )
        )
