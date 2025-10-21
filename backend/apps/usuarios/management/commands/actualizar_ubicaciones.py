"""
Comando para actualizar ubicaciones de compradores con datos de prueba
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
import random
from apps.usuarios.datos_ecuador import UBICACIONES_ECUADOR, obtener_coordenadas

Usuario = get_user_model()


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
        
        # Crear lista de ubicaciones disponibles (provincia, canton, ciudad)
        ubicaciones_disponibles = []
        for provincia, datos_provincia in UBICACIONES_ECUADOR.items():
            for canton, datos_canton in datos_provincia['cantones'].items():
                for ciudad, coordenadas in datos_canton['ciudades'].items():
                    ubicaciones_disponibles.append({
                        'provincia': provincia,
                        'canton': canton,
                        'ciudad': ciudad,
                        'latitud': coordenadas['latitud'],
                        'longitud': coordenadas['longitud']
                    })
        
        for comprador in compradores:
            # Si el comprador ya tiene ubicación completa, no lo actualizamos a menos que sea random
            if comprador.provincia and comprador.canton and comprador.ciudad and not options['random']:
                self.stdout.write(
                    f'  • {comprador.nombre} ya tiene ubicación: '
                    f'{comprador.ciudad}, {comprador.canton}, {comprador.provincia}'
                )
                continue
            
            # Asignar ubicación aleatoria si se especifica --random, o si no tiene ubicación completa
            if options['random'] or not (comprador.provincia and comprador.canton and comprador.ciudad):
                ubicacion = random.choice(ubicaciones_disponibles)
                
                # Agregar pequeña variación para evitar superposición exacta
                offset_lat = Decimal(str(random.uniform(-0.005, 0.005)))
                offset_lng = Decimal(str(random.uniform(-0.005, 0.005)))
                
                comprador.provincia = ubicacion['provincia']
                comprador.canton = ubicacion['canton']
                comprador.ciudad = ubicacion['ciudad']
                comprador.latitud = ubicacion['latitud'] + offset_lat
                comprador.longitud = ubicacion['longitud'] + offset_lng
                comprador.save()
                
                total_actualizados += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ {comprador.nombre} → {ubicacion["ciudad"]}, '
                        f'{ubicacion["canton"]}, {ubicacion["provincia"]} '
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
        
        # Estadísticas por provincia
        self.stdout.write('\n📊 Distribución por provincia:')
        for provincia in sorted(set(u['provincia'] for u in ubicaciones_disponibles)):
            count = Usuario.objects.filter(rol=4, provincia=provincia).count()
            if count > 0:
                self.stdout.write(f'  • {provincia}: {count} compradores')



