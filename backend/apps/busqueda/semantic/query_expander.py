"""
Query Expander - Sistema de expansión de consultas para mejorar precisión
Expande consultas con sinónimos, contexto y términos relacionados
"""
from typing import Dict, List, Set, Tuple
import re
from datetime import datetime, timedelta
from django.utils import timezone


class QueryExpander:
    """
    Expande consultas de búsqueda con sinónimos, contexto y términos relacionados.
    Mejora significativamente la precisión de búsquedas semánticas.
    """
    
    # Diccionario de sinónimos para estados de envío
    SINONIMOS_ESTADOS = {
        'pendiente': ['pendiente', 'en espera', 'sin procesar', 'por procesar', 'no procesado', 'aguardando'],
        'en_transito': ['en tránsito', 'en camino', 'enviado', 'en ruta', 'transportándose', 'en movimiento'],
        'entregado': ['entregado', 'recibido', 'completado', 'finalizado', 'llegó', 'recepcionado'],
        'cancelado': ['cancelado', 'anulado', 'rechazado', 'descartado', 'eliminado']
    }
    
    # Sinónimos para ubicaciones en Ecuador
    SINONIMOS_CIUDADES = {
        'quito': ['quito', 'capital', 'pichincha', 'dme', 'distrito metropolitano'],
        'guayaquil': ['guayaquil', 'gye', 'guayas', 'puerto principal', 'perla del pacífico'],
        'cuenca': ['cuenca', 'azuay', 'morlaquía', 'atenas del ecuador'],
        'ambato': ['ambato', 'tungurahua', 'tierra de flores', 'jardín del ecuador'],
        'machala': ['machala', 'el oro', 'capital bananera'],
        'manta': ['manta', 'manabí', 'puerto', 'manta puerto'],
        'santo domingo': ['santo domingo', 'tsachilas', 'santo domingo de los tsachilas'],
        'portoviejo': ['portoviejo', 'manabí', 'capital manabita'],
        'loja': ['loja', 'castellana', 'ciudad musical'],
        'esmeraldas': ['esmeraldas', 'verde', 'provincia verde']
    }
    
    # Sinónimos para medidas de peso
    SINONIMOS_PESO = {
        'kg': ['kg', 'kilogramo', 'kilogramos', 'kilo', 'kilos', 'k'],
        'g': ['g', 'gramo', 'gramos', 'gr'],
        'lb': ['lb', 'libra', 'libras'],
        'ligero': ['ligero', 'liviano', 'poco peso', 'ligero peso', 'pequeño peso'],
        'pesado': ['pesado', 'mucho peso', 'gran peso', 'alto peso', 'peso considerable']
    }
    
    # Sinónimos para consultas de valor/precio
    SINONIMOS_VALOR = {
        'alto': ['alto', 'costoso', 'caro', 'elevado', 'considerable', 'grande', 'significativo'],
        'bajo': ['bajo', 'económico', 'barato', 'módico', 'reducido', 'pequeño'],
        'valor': ['valor', 'precio', 'costo', 'monto', 'importe', 'suma'],
    }
    
    # Sinónimos para productos y categorías
    SINONIMOS_PRODUCTOS = {
        'electronica': ['electrónica', 'electrónicos', 'tecnología', 'tecnológico', 'dispositivos', 
                        'gadgets', 'equipos electrónicos', 'aparatos electrónicos'],
        'laptop': ['laptop', 'portátil', 'computadora portátil', 'notebook', 'computador portátil'],
        'smartphone': ['smartphone', 'celular', 'teléfono', 'móvil', 'teléfono móvil', 'teléfono inteligente'],
        'tablet': ['tablet', 'tableta', 'ipad', 'tableta electrónica'],
        'ropa': ['ropa', 'vestimenta', 'prendas', 'indumentaria', 'textiles', 'moda', 
                 'vestuario', 'atuendo', 'vestido'],
        'hogar': ['hogar', 'casa', 'doméstico', 'artículos del hogar', 'para el hogar',
                  'decoración', 'muebles', 'utensilios'],
        'deportes': ['deportes', 'deportivo', 'deporte', 'fitness', 'ejercicio',
                     'equipamiento deportivo', 'artículos deportivos'],
    }
    
    # Sinónimos para referencias temporales
    SINONIMOS_TIEMPO = {
        'hoy': ['hoy', 'el día de hoy', 'este día', 'en el día'],
        'ayer': ['ayer', 'el día de ayer', 'día anterior'],
        'esta semana': ['esta semana', 'semana actual', 'esta semana en curso', 'semana presente'],
        'este mes': ['este mes', 'mes actual', 'mes en curso', 'mes presente'],
        'última semana': ['última semana', 'semana pasada', 'semana anterior', '7 días'],
        'último mes': ['último mes', 'mes pasado', 'mes anterior', '30 días'],
        'reciente': ['reciente', 'recientemente', 'últimamente', 'hace poco', 'nuevo'],
    }
    
    # Sinónimos para cantidad
    SINONIMOS_CANTIDAD = {
        'varios': ['varios', 'múltiples', 'diversos', 'variados', 'más de uno', 'distintos'],
        'muchos': ['muchos', 'numerosos', 'abundantes', 'gran cantidad'],
        'pocos': ['pocos', 'escasos', 'limitados', 'reducidos'],
    }
    
    @staticmethod
    def expandir_consulta(consulta: str, incluir_filtros_temporales: bool = True) -> Dict[str, any]:
        """
        Expande una consulta con sinónimos, contexto y términos relacionados.
        
        Args:
            consulta: Consulta original del usuario
            incluir_filtros_temporales: Si True, detecta y extrae filtros temporales
            
        Returns:
            Dict con:
                - consulta_expandida: Consulta con términos adicionales
                - terminos_originales: Términos de la consulta original
                - sinonimos_agregados: Sinónimos añadidos
                - filtros_sugeridos: Filtros que podrían aplicarse
                - contexto_adicional: Contexto extra para mejorar búsqueda
        """
        consulta_lower = consulta.lower().strip()
        
        # Extraer términos originales
        terminos_originales = set(consulta_lower.split())
        
        # Detectar y expandir componentes
        sinonimos = set()
        contexto = []
        filtros_sugeridos = {}
        
        # 1. Expandir estados
        estado_detectado = QueryExpander._detectar_estado(consulta_lower)
        if estado_detectado:
            sinonimos.update(QueryExpander.SINONIMOS_ESTADOS.get(estado_detectado, []))
            filtros_sugeridos['estado'] = estado_detectado
            contexto.append(f"Estado: {estado_detectado}")
        
        # 2. Expandir ciudades
        ciudad_detectada = QueryExpander._detectar_ciudad(consulta_lower)
        if ciudad_detectada:
            sinonimos.update(QueryExpander.SINONIMOS_CIUDADES.get(ciudad_detectada, []))
            filtros_sugeridos['ciudadDestino'] = ciudad_detectada.title()
            contexto.append(f"Ciudad: {ciudad_detectada}")
        
        # 3. Expandir términos de peso
        info_peso = QueryExpander._detectar_peso(consulta_lower)
        if info_peso:
            sinonimos.update(info_peso['sinonimos'])
            if info_peso.get('filtro_peso'):
                contexto.append(info_peso['filtro_peso'])
            # Agregar filtros numéricos al dict de filtros sugeridos
            if info_peso.get('peso_minimo'):
                filtros_sugeridos['peso_minimo'] = info_peso['peso_minimo']
            if info_peso.get('peso_maximo'):
                filtros_sugeridos['peso_maximo'] = info_peso['peso_maximo']
        
        # 4. Expandir términos de valor
        info_valor = QueryExpander._detectar_valor(consulta_lower)
        if info_valor:
            sinonimos.update(info_valor['sinonimos'])
            contexto.append(info_valor['contexto'])
            # Agregar filtros numéricos de valor
            if info_valor.get('valor_minimo'):
                filtros_sugeridos['valor_minimo'] = info_valor['valor_minimo']
            if info_valor.get('valor_maximo'):
                filtros_sugeridos['valor_maximo'] = info_valor['valor_maximo']
        
        # 5. Expandir productos
        productos_detectados = QueryExpander._detectar_productos(consulta_lower)
        if productos_detectados:
            for producto in productos_detectados:
                sinonimos.update(QueryExpander.SINONIMOS_PRODUCTOS.get(producto, []))
            contexto.append(f"Productos: {', '.join(productos_detectados)}")
        
        # 6. Expandir referencias temporales
        if incluir_filtros_temporales:
            info_temporal = QueryExpander._detectar_tiempo(consulta_lower)
            if info_temporal:
                sinonimos.update(info_temporal['sinonimos'])
                if info_temporal.get('fecha_desde'):
                    filtros_sugeridos['fechaDesde'] = info_temporal['fecha_desde']
                if info_temporal.get('fecha_hasta'):
                    filtros_sugeridos['fechaHasta'] = info_temporal['fecha_hasta']
                contexto.append(info_temporal['contexto'])
        
        # 7. Detectar consultas sobre cantidad de productos
        info_cantidad = QueryExpander._detectar_cantidad(consulta_lower)
        if info_cantidad:
            sinonimos.update(info_cantidad['sinonimos'])
            contexto.append(info_cantidad['contexto'])
            # Agregar filtro de cantidad mínima de productos
            if info_cantidad.get('cantidad_minima'):
                filtros_sugeridos['cantidad_productos_minima'] = info_cantidad['cantidad_minima']
        
        # 8. Detectar nombres propios (compradores)
        nombres = QueryExpander._detectar_nombres_propios(consulta)
        if nombres:
            contexto.append(f"Comprador mencionado: {' '.join(nombres)}")
        
        # 9. Detectar números de cédula o códigos
        codigos = QueryExpander._detectar_codigos(consulta_lower)
        if codigos:
            contexto.append(f"Código/Cédula: {codigos}")
        
        # Construir consulta expandida
        consulta_expandida = consulta_lower
        
        # Agregar sinónimos relevantes (no todos, solo los más importantes)
        sinonimos_relevantes = list(sinonimos)[:10]  # Limitar a 10 sinónimos
        if sinonimos_relevantes:
            consulta_expandida += " " + " ".join(sinonimos_relevantes)
        
        # Agregar contexto adicional
        if contexto:
            consulta_expandida += " | " + " | ".join(contexto)
        
        return {
            'consulta_expandida': consulta_expandida,
            'consulta_original': consulta,
            'terminos_originales': list(terminos_originales),
            'sinonimos_agregados': list(sinonimos),
            'filtros_sugeridos': filtros_sugeridos,
            'contexto_adicional': contexto,
            'peso_query': len(sinonimos) / 10.0  # Score de expansión (0-1)
        }
    
    @staticmethod
    def _detectar_estado(texto: str) -> str:
        """Detecta el estado del envío mencionado en la consulta"""
        for estado, sinonimos in QueryExpander.SINONIMOS_ESTADOS.items():
            for sinonimo in sinonimos:
                if sinonimo in texto:
                    return estado
        return None
    
    @staticmethod
    def _detectar_ciudad(texto: str) -> str:
        """Detecta la ciudad mencionada en la consulta"""
        for ciudad, sinonimos in QueryExpander.SINONIMOS_CIUDADES.items():
            for sinonimo in sinonimos:
                if sinonimo in texto:
                    return ciudad
        return None
    
    @staticmethod
    def _detectar_peso(texto: str) -> Dict:
        """Detecta información de peso en la consulta y extrae valores numéricos"""
        sinonimos = set()
        filtro_peso = None
        peso_minimo = None
        peso_maximo = None
        
        # Buscar patrones de peso específico
        # "peso mayor a 5 kg", "más de 5 kilogramos", etc.
        patrones = [
            r'peso\s+(?:mayor|superior|mas|más)\s+(?:a|de|que)\s+(\d+(?:\.\d+)?)\s*(kg|kilogramo|kilo)?',
            r'(?:mayor|superior|mas|más)\s+(?:a|de|que)\s+(\d+(?:\.\d+)?)\s*(kg|kilogramo|kilo)',
            r'peso\s+(?:menor|inferior)\s+(?:a|de|que)\s+(\d+(?:\.\d+)?)\s*(kg|kilogramo|kilo)?',
            r'(\d+(?:\.\d+)?)\s*(kg|kilogramo|kilo)',
        ]
        
        for patron in patrones:
            match = re.search(patron, texto)
            if match:
                valor = float(match.group(1))
                if 'mayor' in texto or 'mas' in texto or 'más' in texto:
                    filtro_peso = f"peso mayor a {valor} kg"
                    peso_minimo = valor
                    sinonimos.update(['pesado', 'gran peso', 'peso considerable'])
                elif 'menor' in texto:
                    filtro_peso = f"peso menor a {valor} kg"
                    peso_maximo = valor
                    sinonimos.update(['ligero', 'poco peso', 'liviano'])
                else:
                    filtro_peso = f"peso {valor} kg"
                    # Rango de ±20% para peso específico
                    peso_minimo = valor * 0.8
                    peso_maximo = valor * 1.2
                break
        
        # Buscar términos generales de peso
        if 'liviano' in texto or 'ligero' in texto or 'poco peso' in texto:
            sinonimos.update(QueryExpander.SINONIMOS_PESO['ligero'])
            filtro_peso = "peso ligero"
            peso_maximo = 2.0  # Menos de 2 kg
        elif 'pesado' in texto or 'mucho peso' in texto or 'gran peso' in texto:
            sinonimos.update(QueryExpander.SINONIMOS_PESO['pesado'])
            filtro_peso = "peso pesado"
            peso_minimo = 10.0  # Más de 10 kg
        
        if sinonimos or filtro_peso:
            resultado = {'sinonimos': sinonimos, 'filtro_peso': filtro_peso}
            if peso_minimo is not None:
                resultado['peso_minimo'] = peso_minimo
            if peso_maximo is not None:
                resultado['peso_maximo'] = peso_maximo
            return resultado
        return None
    
    @staticmethod
    def _detectar_valor(texto: str) -> Dict:
        """Detecta información de valor/precio en la consulta y extrae valores numéricos"""
        sinonimos = set()
        contexto = ""
        valor_minimo = None
        valor_maximo = None
        
        # Buscar patrones de valor numérico
        # "valor mayor a $100", "más de 200 dólares", etc.
        patrones_valor = [
            r'valor\s+(?:mayor|superior|mas|más)\s+(?:a|de|que)\s+\$?(\d+(?:\.\d+)?)',
            r'(?:mayor|superior|mas|más)\s+(?:a|de|que)\s+\$?(\d+(?:\.\d+)?)',
            r'\$(\d+(?:\.\d+)?)',
        ]
        
        for patron in patrones_valor:
            match = re.search(patron, texto)
            if match:
                valor = float(match.group(1))
                if 'mayor' in texto or 'mas' in texto or 'más' in texto or 'superior' in texto:
                    valor_minimo = valor
                    sinonimos.update(QueryExpander.SINONIMOS_VALOR['alto'])
                    contexto = f"valor mayor a ${valor}"
                elif 'menor' in texto or 'inferior' in texto:
                    valor_maximo = valor
                    sinonimos.update(QueryExpander.SINONIMOS_VALOR['bajo'])
                    contexto = f"valor menor a ${valor}"
                break
        
        # Buscar términos generales de valor alto/bajo
        if any(term in texto for term in ['valor alto', 'caro', 'costoso', 'elevado', 'considerable', 'requiere revisión', 'requieran revisión']):
            sinonimos.update(QueryExpander.SINONIMOS_VALOR['alto'])
            contexto = "valor alto"
            if valor_minimo is None:
                valor_minimo = 500.0  # Definir valor alto como > $500
        elif any(term in texto for term in ['valor bajo', 'barato', 'económico', 'módico']):
            sinonimos.update(QueryExpander.SINONIMOS_VALOR['bajo'])
            contexto = "valor bajo"
            if valor_maximo is None:
                valor_maximo = 50.0  # Definir valor bajo como < $50
        elif 'valor' in texto or 'precio' in texto or 'costo' in texto:
            sinonimos.update(QueryExpander.SINONIMOS_VALOR['valor'])
            contexto = "información de valor"
        
        if sinonimos or contexto:
            resultado = {'sinonimos': sinonimos, 'contexto': contexto}
            if valor_minimo is not None:
                resultado['valor_minimo'] = valor_minimo
            if valor_maximo is not None:
                resultado['valor_maximo'] = valor_maximo
            return resultado
        return None
    
    @staticmethod
    def _detectar_productos(texto: str) -> List[str]:
        """Detecta productos mencionados en la consulta"""
        productos_encontrados = []
        
        for producto, sinonimos in QueryExpander.SINONIMOS_PRODUCTOS.items():
            for sinonimo in sinonimos:
                if sinonimo in texto:
                    if producto not in productos_encontrados:
                        productos_encontrados.append(producto)
                    break
        
        return productos_encontrados
    
    @staticmethod
    def _detectar_tiempo(texto: str) -> Dict:
        """Detecta referencias temporales y calcula fechas"""
        sinonimos = set()
        contexto = ""
        fecha_desde = None
        fecha_hasta = None
        
        hoy = timezone.now().date()
        
        # Detectar "este mes"
        if any(term in texto for term in ['este mes', 'mes actual', 'mes en curso']):
            fecha_desde = hoy.replace(day=1).isoformat()
            fecha_hasta = hoy.isoformat()
            sinonimos.update(QueryExpander.SINONIMOS_TIEMPO['este mes'])
            contexto = "este mes"
        
        # Detectar "esta semana"
        elif any(term in texto for term in ['esta semana', 'semana actual']):
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            fecha_desde = inicio_semana.isoformat()
            fecha_hasta = hoy.isoformat()
            sinonimos.update(QueryExpander.SINONIMOS_TIEMPO['esta semana'])
            contexto = "esta semana"
        
        # Detectar "última semana" / "semana pasada"
        elif any(term in texto for term in ['última semana', 'semana pasada', '7 días']):
            fecha_desde = (hoy - timedelta(days=7)).isoformat()
            fecha_hasta = hoy.isoformat()
            sinonimos.update(QueryExpander.SINONIMOS_TIEMPO['última semana'])
            contexto = "última semana"
        
        # Detectar "último mes"
        elif any(term in texto for term in ['último mes', 'mes pasado', '30 días']):
            fecha_desde = (hoy - timedelta(days=30)).isoformat()
            fecha_hasta = hoy.isoformat()
            sinonimos.update(QueryExpander.SINONIMOS_TIEMPO['último mes'])
            contexto = "último mes"
        
        # Detectar "reciente"
        elif any(term in texto for term in ['reciente', 'recientemente', 'hace poco']):
            fecha_desde = (hoy - timedelta(days=14)).isoformat()
            fecha_hasta = hoy.isoformat()
            sinonimos.update(QueryExpander.SINONIMOS_TIEMPO['reciente'])
            contexto = "reciente (últimos 14 días)"
        
        # Detectar "hoy"
        elif 'hoy' in texto:
            fecha_desde = hoy.isoformat()
            fecha_hasta = hoy.isoformat()
            sinonimos.update(QueryExpander.SINONIMOS_TIEMPO['hoy'])
            contexto = "hoy"
        
        if sinonimos or contexto:
            return {
                'sinonimos': sinonimos,
                'contexto': contexto,
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta
            }
        return None
    
    @staticmethod
    def _detectar_cantidad(texto: str) -> Dict:
        """Detecta referencias a cantidad de productos y extrae valores numéricos"""
        sinonimos = set()
        contexto = ""
        cantidad_minima = None
        
        # Detectar "más de un producto", "varios productos", etc.
        if any(term in texto for term in ['más de un', 'varios', 'múltiples', 'más de 1', 'mismo paquete']):
            sinonimos.update(QueryExpander.SINONIMOS_CANTIDAD['varios'])
            contexto = "múltiples productos en el paquete"
            cantidad_minima = 2  # Al menos 2 productos
        elif any(term in texto for term in ['muchos', 'numerosos', 'abundantes']):
            sinonimos.update(QueryExpander.SINONIMOS_CANTIDAD['muchos'])
            contexto = "muchos productos"
            cantidad_minima = 5  # Al menos 5 productos
        elif any(term in texto for term in ['pocos', 'escasos']):
            sinonimos.update(QueryExpander.SINONIMOS_CANTIDAD['pocos'])
            contexto = "pocos productos"
            # No aplicar filtro para "pocos" ya que es ambiguo
        
        # Buscar patrones numéricos específicos: "más de 3 productos"
        patron_cantidad = r'más\s+de\s+(\d+)\s+producto'
        match = re.search(patron_cantidad, texto)
        if match:
            cantidad = int(match.group(1))
            cantidad_minima = cantidad + 1
            contexto = f"más de {cantidad} productos"
        
        if sinonimos or contexto:
            resultado = {'sinonimos': sinonimos, 'contexto': contexto}
            if cantidad_minima is not None:
                resultado['cantidad_minima'] = cantidad_minima
            return resultado
        return None
    
    @staticmethod
    def _detectar_nombres_propios(texto: str) -> List[str]:
        """Detecta nombres propios (potenciales nombres de compradores)"""
        # Buscar palabras con mayúscula inicial que no estén al inicio de la oración
        palabras = texto.split()
        nombres = []
        
        for i, palabra in enumerate(palabras):
            # Ignorar primera palabra y palabras comunes
            if i == 0:
                continue
            
            # Verificar si empieza con mayúscula y no es una palabra común
            if palabra[0].isupper() and len(palabra) > 2:
                # Filtrar palabras comunes que suelen ir con mayúscula
                palabras_comunes = ['Quito', 'Guayaquil', 'Cuenca', 'Ecuador', 'Enero', 'Febrero']
                if palabra not in palabras_comunes:
                    nombres.append(palabra)
        
        return nombres
    
    @staticmethod
    def _detectar_codigos(texto: str) -> str:
        """Detecta códigos HAWB o números de cédula"""
        # Buscar cédula (10 dígitos)
        cedula_match = re.search(r'\b\d{10}\b', texto)
        if cedula_match:
            return cedula_match.group(0)
        
        # Buscar código HAWB (patrón típico)
        hawb_match = re.search(r'\b[A-Z]{2,}\d{4,}\b', texto.upper())
        if hawb_match:
            return hawb_match.group(0)
        
        return None


# Instancia singleton
query_expander = QueryExpander()
