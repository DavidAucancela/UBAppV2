"""
Datos de ubicaciones de Ecuador: Provincias, Cantones y Ciudades
Con coordenadas geográficas para cada ubicación
"""

from decimal import Decimal

# Estructura: Provincia -> Cantones -> Ciudades con coordenadas
UBICACIONES_ECUADOR = {
    'Pichincha': {
        'cantones': {
            'Quito': {
                'ciudades': {
                    'Quito': {'latitud': Decimal('-0.1807'), 'longitud': Decimal('-78.4678')},
                    'Conocoto': {'latitud': Decimal('-0.2667'), 'longitud': Decimal('-78.4833')},
                    'Tumbaco': {'latitud': Decimal('-0.2167'), 'longitud': Decimal('-78.4000')},
                }
            },
            'Cayambe': {
                'ciudades': {
                    'Cayambe': {'latitud': Decimal('0.0408'), 'longitud': Decimal('-78.1431')},
                }
            },
            'Mejía': {
                'ciudades': {
                    'Machachi': {'latitud': Decimal('-0.5103'), 'longitud': Decimal('-78.5672')},
                }
            },
        }
    },
    'Guayas': {
        'cantones': {
            'Guayaquil': {
                'ciudades': {
                    'Guayaquil': {'latitud': Decimal('-2.1894'), 'longitud': Decimal('-79.8849')},
                    'Samborondón': {'latitud': Decimal('-1.9667'), 'longitud': Decimal('-79.7333')},
                }
            },
            'Durán': {
                'ciudades': {
                    'Durán': {'latitud': Decimal('-2.1703'), 'longitud': Decimal('-79.8382')},
                }
            },
            'Milagro': {
                'ciudades': {
                    'Milagro': {'latitud': Decimal('-2.1344'), 'longitud': Decimal('-79.5922')},
                }
            },
            'Daule': {
                'ciudades': {
                    'Daule': {'latitud': Decimal('-1.8619'), 'longitud': Decimal('-79.9781')},
                }
            },
        }
    },
    'Azuay': {
        'cantones': {
            'Cuenca': {
                'ciudades': {
                    'Cuenca': {'latitud': Decimal('-2.9001'), 'longitud': Decimal('-79.0059')},
                }
            },
            'Gualaceo': {
                'ciudades': {
                    'Gualaceo': {'latitud': Decimal('-2.8926'), 'longitud': Decimal('-78.7803')},
                }
            },
        }
    },
    'Manabí': {
        'cantones': {
            'Manta': {
                'ciudades': {
                    'Manta': {'latitud': Decimal('-0.9677'), 'longitud': Decimal('-80.7089')},
                }
            },
            'Portoviejo': {
                'ciudades': {
                    'Portoviejo': {'latitud': Decimal('-1.0544'), 'longitud': Decimal('-80.4535')},
                }
            },
        }
    },
    'Tungurahua': {
        'cantones': {
            'Ambato': {
                'ciudades': {
                    'Ambato': {'latitud': Decimal('-1.2490'), 'longitud': Decimal('-78.6167')},
                }
            },
        }
    },
    'Loja': {
        'cantones': {
            'Loja': {
                'ciudades': {
                    'Loja': {'latitud': Decimal('-3.9930'), 'longitud': Decimal('-79.2042')},
                }
            },
        }
    },
    'Esmeraldas': {
        'cantones': {
            'Esmeraldas': {
                'ciudades': {
                    'Esmeraldas': {'latitud': Decimal('0.9681'), 'longitud': Decimal('-79.6517')},
                }
            },
        }
    },
    'Chimborazo': {
        'cantones': {
            'Riobamba': {
                'ciudades': {
                    'Riobamba': {'latitud': Decimal('-1.6711'), 'longitud': Decimal('-78.6475')},
                }
            },
        }
    },
    'El Oro': {
        'cantones': {
            'Machala': {
                'ciudades': {
                    'Machala': {'latitud': Decimal('-3.2581'), 'longitud': Decimal('-79.9553')},
                }
            },
        }
    },
    'Santo Domingo de los Tsáchilas': {
        'cantones': {
            'Santo Domingo': {
                'ciudades': {
                    'Santo Domingo': {'latitud': Decimal('-0.2521'), 'longitud': Decimal('-79.1749')},
                }
            },
        }
    },
    'Imbabura': {
        'cantones': {
            'Ibarra': {
                'ciudades': {
                    'Ibarra': {'latitud': Decimal('0.3499'), 'longitud': Decimal('-78.1263')},
                }
            },
            'Otavalo': {
                'ciudades': {
                    'Otavalo': {'latitud': Decimal('0.2347'), 'longitud': Decimal('-78.2628')},
                }
            },
        }
    },
    'Los Ríos': {
        'cantones': {
            'Quevedo': {
                'ciudades': {
                    'Quevedo': {'latitud': Decimal('-1.0285'), 'longitud': Decimal('-79.4602')},
                }
            },
            'Babahoyo': {
                'ciudades': {
                    'Babahoyo': {'latitud': Decimal('-1.8018'), 'longitud': Decimal('-79.5342')},
                }
            },
        }
    },
}


def obtener_provincias():
    """Retorna lista de provincias ordenadas alfabéticamente"""
    return sorted(UBICACIONES_ECUADOR.keys())


def obtener_cantones(provincia):
    """Retorna lista de cantones para una provincia específica"""
    if provincia in UBICACIONES_ECUADOR:
        return sorted(UBICACIONES_ECUADOR[provincia]['cantones'].keys())
    return []


def obtener_ciudades(provincia, canton):
    """Retorna lista de ciudades para un cantón específico"""
    if (provincia in UBICACIONES_ECUADOR and 
        canton in UBICACIONES_ECUADOR[provincia]['cantones']):
        return sorted(UBICACIONES_ECUADOR[provincia]['cantones'][canton]['ciudades'].keys())
    return []


def obtener_coordenadas(provincia, canton, ciudad):
    """Retorna coordenadas (latitud, longitud) para una ubicación específica"""
    try:
        ubicacion = UBICACIONES_ECUADOR[provincia]['cantones'][canton]['ciudades'][ciudad]
        return ubicacion['latitud'], ubicacion['longitud']
    except KeyError:
        return None, None


def buscar_ciudad_por_nombre(nombre_ciudad):
    """Busca una ciudad por nombre y retorna provincia, cantón y coordenadas"""
    for provincia, datos_provincia in UBICACIONES_ECUADOR.items():
        for canton, datos_canton in datos_provincia['cantones'].items():
            for ciudad, coordenadas in datos_canton['ciudades'].items():
                if ciudad.lower() == nombre_ciudad.lower():
                    return {
                        'provincia': provincia,
                        'canton': canton,
                        'ciudad': ciudad,
                        'latitud': coordenadas['latitud'],
                        'longitud': coordenadas['longitud']
                    }
    return None







