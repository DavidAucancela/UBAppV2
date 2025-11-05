"""
Vistas para manejo de ubicaciones de Ecuador
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .datos_ecuador import (
    obtener_provincias, 
    obtener_cantones, 
    obtener_ciudades,
    obtener_coordenadas
)


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_provincias_view(request):
    """
    Endpoint para obtener todas las provincias de Ecuador
    GET /api/usuarios/ubicaciones/provincias/
    """
    provincias = obtener_provincias()
    return Response({
        'provincias': provincias,
        'total': len(provincias)
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_cantones_view(request):
    """
    Endpoint para obtener cantones de una provincia
    GET /api/usuarios/ubicaciones/cantones/?provincia=Pichincha
    """
    provincia = request.query_params.get('provincia')
    
    if not provincia:
        return Response({
            'error': 'Parámetro "provincia" es requerido'
        }, status=400)
    
    cantones = obtener_cantones(provincia)
    
    if not cantones:
        return Response({
            'error': f'No se encontraron cantones para la provincia {provincia}'
        }, status=404)
    
    return Response({
        'provincia': provincia,
        'cantones': cantones,
        'total': len(cantones)
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_ciudades_view(request):
    """
    Endpoint para obtener ciudades de un cantón
    GET /api/usuarios/ubicaciones/ciudades/?provincia=Pichincha&canton=Quito
    """
    provincia = request.query_params.get('provincia')
    canton = request.query_params.get('canton')
    
    if not provincia or not canton:
        return Response({
            'error': 'Parámetros "provincia" y "canton" son requeridos'
        }, status=400)
    
    ciudades = obtener_ciudades(provincia, canton)
    
    if not ciudades:
        return Response({
            'error': f'No se encontraron ciudades para {canton}, {provincia}'
        }, status=404)
    
    return Response({
        'provincia': provincia,
        'canton': canton,
        'ciudades': ciudades,
        'total': len(ciudades)
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_coordenadas_view(request):
    """
    Endpoint para obtener coordenadas de una ubicación específica
    GET /api/usuarios/ubicaciones/coordenadas/?provincia=Pichincha&canton=Quito&ciudad=Quito
    """
    provincia = request.query_params.get('provincia')
    canton = request.query_params.get('canton')
    ciudad = request.query_params.get('ciudad')
    
    if not provincia or not canton or not ciudad:
        return Response({
            'error': 'Parámetros "provincia", "canton" y "ciudad" son requeridos'
        }, status=400)
    
    latitud, longitud = obtener_coordenadas(provincia, canton, ciudad)
    
    if latitud is None or longitud is None:
        return Response({
            'error': f'No se encontraron coordenadas para {ciudad}, {canton}, {provincia}'
        }, status=404)
    
    return Response({
        'provincia': provincia,
        'canton': canton,
        'ciudad': ciudad,
        'latitud': float(latitud),
        'longitud': float(longitud)
    })












