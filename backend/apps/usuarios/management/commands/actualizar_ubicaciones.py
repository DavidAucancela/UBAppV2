"""
Comando para actualizar ubicaciones de compradores con datos de prueba
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
import random

Usuario = get_user_model()

# Coordenadas de ciudades principales de Ecuador
CIUDADES_ECUADOR = {
    'Quito': {'latitud': Decimal('-0.1807'), 'longitud': Decimal('-78.4678')},
    'Guayaquil': {'latitud': Decimal('-2.1894'), 'longitud': Decimal('-79.8849')},
    'Cuenca': {'latitud': Decimal('-2.9001'), 'longitud': Decimal('-79.0059')},
    'Ambato': {'latitud': Decimal('-1.2490'), 'longitud': Decimal('-78.6167')},
    'Manta': {'latitud': Decimal('-0.9677'), 'longitud': Decimal('-80.7089')},
    'Loja': {'latitud': Decimal('-3.9930'), 'longitud': Decimal('-79.2042')},
    'Esmeraldas': {'latitud': Decimal('0.9681'), 'longitud': Decimal('-79.6517')},
    'Riobamba': {'latitud': Decimal('-1.6711'), 'longitud': Decimal('-78.6475')},
    'Machala': {'latitud': Decimal('-3.2581'), 'longitud': Decimal('-79.9553')},
    'Santo Domingo': {'latitud': Decimal('-0.2521'), 'longitud': Decimal('-79.1749')},
    'Ibarra': {'latitud': Decimal('0.3499'), 'longitud': Decimal('-78.1263')},
    'Portoviejo': {'latitud': Decimal('-1.0544'), 'longitud': Decimal('-80.4535')},
    'Durán': {'latitud': Decimal('-2.1703'), 'longitud': Decimal('-79.8382')},
    'Quevedo': {'latitud': Decimal('-1.0285'), 'longitud': Decimal('-79.4602')},
    'Milagro': {'latitud': Decimal('-2.1344'), 'longitud': Decimal('-79.5922')},
}


class Command(BaseCommand):
    help = 'Actualiza las ubicaciones de los compradores con datos de ciudades ecuatorianas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--random',
            action='store_true',
            help='Asigna ciudades aleatorias a los compradores',
        )

    def handle(self, *args, **options):
        self.stdout.write('Actualizando ubicaciones de compradores...\n')
        
        # Obtener todos los compradores (rol = 4)
        compradores = Usuario.objects.filter(rol=4)
        
        if not compradores.exists():
            self.stdout.write(self.style.WARNING('No se encontraron compradores en el sistema.'))
            return
        
        total_actualizados = 0
        ciudades_list = list(CIUDADES_ECUADOR.keys())
        
        for comprador in compradores:
            # Si el comprador ya tiene ubicación, no lo actualizamos a menos que sea random
            if comprador.ciudad and not options['random']:
                self.stdout.write(f'  • {comprador.nombre} ya tiene ubicación: {comprador.ciudad}')
                continue
            
            # Asignar ciudad aleatoria si se especifica --random, o si no tiene ciudad
            if options['random'] or not comprador.ciudad:
                ciudad_nombre = random.choice(ciudades_list)
                coordenadas = CIUDADES_ECUADOR[ciudad_nombre]
                
                # Agregar pequeña variación para evitar superposición exacta
                offset_lat = Decimal(str(random.uniform(-0.005, 0.005)))
                offset_lng = Decimal(str(random.uniform(-0.005, 0.005)))
                
                comprador.ciudad = ciudad_nombre
                comprador.latitud = coordenadas['latitud'] + offset_lat
                comprador.longitud = coordenadas['longitud'] + offset_lng
                comprador.save()
                
                total_actualizados += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ {comprador.nombre} → {ciudad_nombre} '
                        f'({comprador.latitud}, {comprador.longitud})'
                    )
                )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Proceso completado: {total_actualizados} compradores actualizados'
            )
        )
        self.stdout.write(f'  Total de compradores: {compradores.count()}')
        
        # Estadísticas por ciudad
        self.stdout.write('\n📊 Distribución por ciudad:')
        for ciudad in ciudades_list:
            count = Usuario.objects.filter(rol=4, ciudad=ciudad).count()
            if count > 0:
                self.stdout.write(f'  • {ciudad}: {count} compradores')

