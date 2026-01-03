"""
Text Processor - Procesamiento de texto para generación de embeddings
"""
import re
import unicodedata
from typing import List


class TextProcessor:
    """
    Procesador de texto para preparar contenido para embeddings.
    Centraliza la lógica de generación de texto descriptivo.
    """
    
    # TODO: Normaliza acentos y caracteres especiales a su equivalente sin acento.
    @staticmethod
    def normalizar_acentos(texto: str) -> str:
        """
        Normaliza acentos y caracteres especiales a su equivalente sin acento.
        Convierte vocales con tilde (á, é, í, ó, ú, ñ) a vocales sin tilde (a, e, i, o, u, n).
        
        Args:
            texto: Texto a normalizar
            
        Returns:
            str: Texto con acentos normalizados
        """
        if not texto:
            return ""
        
        # Normalizar a NFD (Normalized Form Decomposed) para separar caracteres base de diacríticos
        texto = unicodedata.normalize('NFD', texto)
        
        # Eliminar diacríticos (tildes, acentos, etc.)
        texto = ''.join(
            char for char in texto 
            if unicodedata.category(char) != 'Mn'  # Mn = Mark, Nonspacing (diacríticos)
        )
        
        return texto
    
    # TODO: Aplica todas las transformaciones de limpieza y normalización al texto.
    @staticmethod
    def limpiar_texto(texto: str) -> str:
        """
        Limpia el texto eliminando caracteres especiales no alfanuméricos,
        espacios múltiples y símbolos de dólar.
        Primero normaliza acentos antes de limpiar.
        
        Args:
            texto: Texto a limpiar
            
        Returns:
            str: Texto limpio
        """
        if not texto:
            return ""
        
        # Primero normalizar acentos (convertir tildes a vocales sin tilde)
        texto = TextProcessor.normalizar_acentos(texto)
        
        # Eliminar símbolos de dólar
        texto = texto.replace('$', '')
        
        # Eliminar caracteres especiales no alfanuméricos (excepto espacios)
        # Mantener letras, números, espacios y caracteres básicos de puntuación
        texto = re.sub(r'[^a-zA-Z0-9\s\-\.]', '', texto)
        
        # Normalizar espacios múltiples a un solo espacio
        texto = re.sub(r'\s+', ' ', texto)
        
        # Eliminar espacios al inicio y final
        texto = texto.strip()
        
        return texto
    
    # TODO: Normaliza formatos de números eliminando comas y puntos de miles.
    @staticmethod
    def normalizar_numeros(texto: str) -> str:
        """
        Normaliza formatos de números eliminando comas y puntos de miles.
        Mantiene el punto decimal si existe.
        
        Args:
            texto: Texto con números a normalizar
            
        Returns:
            str: Texto con números normalizados
        """
        if not texto:
            return ""
        
        def normalizar_numero(match):
            numero = match.group(0)
            
            # Si tiene punto y coma, asumir formato europeo (1.234,56 -> 1234.56)
            if '.' in numero and ',' in numero:
                # Formato europeo: eliminar puntos (separadores de miles) y convertir coma a punto decimal
                numero = numero.replace('.', '').replace(',', '.')
            # Si solo tiene comas
            elif ',' in numero and '.' not in numero:
                partes = numero.split(',')
                # Si hay 2 partes y la segunda tiene 1-2 dígitos, es decimal (formato europeo)
                if len(partes) == 2 and 1 <= len(partes[1]) <= 2:
                    numero = numero.replace(',', '.')
                else:
                    # Es separador de miles, eliminar todas las comas
                    numero = numero.replace(',', '')
            # Si solo tiene puntos
            elif '.' in numero and ',' not in numero:
                partes = numero.split('.')
                # Si hay múltiples partes, son separadores de miles
                if len(partes) > 2:
                    # Eliminar todos los puntos (separadores de miles)
                    numero = numero.replace('.', '')
                # Si hay 2 partes, verificar si es decimal o separador de miles
                elif len(partes) == 2:
                    # Si la segunda parte tiene más de 2 dígitos, es separador de miles
                    if len(partes[1]) > 2:
                        numero = numero.replace('.', '')
                    # Si tiene 1-2 dígitos, mantener el punto (es decimal)
                    # else: mantener el punto
            
            return numero
        
        # Patrón para detectar números con posibles separadores de miles o decimales
        # Captura números con dígitos, puntos y comas
        patron = r'\d+[.,]?\d*[.,]?\d*'
        texto = re.sub(patron, normalizar_numero, texto)
        
        return texto
    
    # TODO: Normaliza el texto convirtiendo todo a minúsculas.
    @staticmethod
    def normalizar_texto(texto: str) -> str:
        """
        Normaliza el texto convirtiendo todo a minúsculas.
        
        Args:
            texto: Texto a normalizar
            
        Returns:
            str: Texto en minúsculas
        """
        if not texto:
            return ""
        
        return texto.lower()
    
    # TODO: unión de limpieza
    @staticmethod
    def procesar_texto(texto: str, preservar_codigos: bool = True) -> str:
        """
        Aplica todas las transformaciones de limpieza y normalización al texto.
        
        Proceso aplicado:
        1. Normalización de números
        2. Limpieza de caracteres especiales
        3. Normalización a minúsculas
        
        Args:
            texto: Texto a procesar
            preservar_codigos: Si True, intenta preservar códigos y referencias (no implementado aún)
            
        Returns:
            str: Texto procesado y normalizado
        """
        if not texto:
            return ""
        
        # 1. Normalizar números primero (antes de eliminar caracteres)
        texto = TextProcessor.normalizar_numeros(texto)
        
        # 2. Limpiar texto (eliminar caracteres especiales, espacios múltiples, símbolos de dólar)
        texto = TextProcessor.limpiar_texto(texto)
        
        # 3. Normalizar a minúsculas
        texto = TextProcessor.normalizar_texto(texto)
        
        return texto
    

    
    # TODO: Generar texto descriptivo del envío para indexación semántica.
    @staticmethod
    def generar_texto_envio(envio) -> str:
        """
        Genera texto descriptivo del envío para indexación semántica.
        Versión mejorada con más contexto y repetición de información importante.
        
        Args:
            envio: Instancia del modelo Envio
            
        Returns:
            str: Texto descriptivo completo del envío
        """
        # Información principal (ordenada por importancia semántica)
        estado_display = envio.get_estado_display()
        partes = [
            # Estado y código identificador primero (más importante para búsqueda)
            f"Envió {envio.hawb} con estado {estado_display}",
            f"Estado del envío: {estado_display}",
            f"Código HAWB: {envio.hawb}",
            f"Comprador: {envio.comprador.nombre}",
        ]
        
        # Información de ubicación (importante para búsquedas geográficas)
        if envio.comprador.ciudad:
            partes.append(f"Ciudad destino: {envio.comprador.ciudad}")
            partes.append(f"Ubicación: {envio.comprador.ciudad}")  # Repetir para más peso
        if envio.comprador.provincia:
            partes.append(f"Provincia: {envio.comprador.provincia}")
        if envio.comprador.canton:
            partes.append(f"Cantón: {envio.comprador.canton}")
        
        # Información temporal
        fecha_str = envio.fecha_emision.strftime('%Y-%m-%d')
        partes.append(f"Fecha de emisión: {fecha_str}")
        partes.append(f"Fecha: {fecha_str}")  # Variación para mejor matching
        
        # Información de envío
        partes.extend([
            f"Peso total: {envio.peso_total} kg",
            f"Peso: {envio.peso_total} kg",
            f"Valor total: ${envio.valor_total}",
            f"Valor: ${envio.valor_total}",
            f"Costo del servicio: ${envio.costo_servicio}",
        ])
        
        # Información de productos (muy importante para búsquedas de productos)
        # MEJORADO: Incluye más información y sinónimos para mejor búsqueda semántica
        productos = envio.productos.all()
        if productos.exists():
            descripciones = []
            descripciones_completas = []  # Con detalles adicionales
            categorias = []
            categorias_sinonimos = []  # Sinónimos de categorías
            
            # Mapeo de sinónimos para categorías
            sinonimos_categorias = {
                'electronica': ['electrónica', 'electrónicos', 'tecnología', 'tecnologico', 'dispositivos', 'gadgets', 'equipos electrónicos'],
                'ropa': ['vestimenta', 'prendas', 'indumentaria', 'textiles', 'moda', 'ropa y accesorios'],
                'hogar': ['artículos para el hogar', 'decoración', 'muebles', 'utensilios', 'herramientas del hogar', 'artículos domésticos'],
                'deportes': ['artículos deportivos', 'equipamiento deportivo', 'deportivo', 'fitness', 'ejercicio'],
                'otros': ['misceláneos', 'varios', 'diversos', 'otros artículos']
            }
            
            # Procesar todos los productos (no limitar a 5)
            for producto in productos:
                descripcion = producto.descripcion
                descripciones.append(descripcion)
                
                # Crear descripción completa con detalles
                descripcion_completa = descripcion
                if producto.peso:
                    descripcion_completa += f" peso {producto.peso}kg"
                if producto.cantidad > 1:
                    descripcion_completa += f" cantidad {producto.cantidad}"
                if producto.valor:
                    descripcion_completa += f" valor ${producto.valor}"
                descripciones_completas.append(descripcion_completa)
                
                # Categorías y sinónimos
                cat_display = producto.get_categoria_display()
                if cat_display not in categorias:
                    categorias.append(cat_display)
                    # Agregar sinónimos de la categoría
                    cat_key = producto.categoria
                    if cat_key in sinonimos_categorias:
                        categorias_sinonimos.extend(sinonimos_categorias[cat_key])
            
            # Agregar información de productos de múltiples formas para mejor matching
            if descripciones:
                # Lista completa de productos
                partes.append(f"Productos incluidos: {', '.join(descripciones)}")
                # Versión corta con primeros productos
                partes.append(f"Contiene: {', '.join(descripciones[:5])}")
                # Descripciones con detalles
                partes.append(f"Productos con detalles: {' | '.join(descripciones_completas[:10])}")
                # Cada producto individualmente para mejor matching
                for desc in descripciones[:10]:
                    partes.append(f"Producto: {desc}")
            
            # Categorías
            if categorias:
                partes.append(f"Categorías de productos: {', '.join(categorias)}")
                # Agregar sinónimos de categorías
                if categorias_sinonimos:
                    partes.append(f"Tipos de productos: {', '.join(set(categorias_sinonimos))}")
            
            # Información numérica de productos
            partes.append(f"Cantidad total de productos: {envio.cantidad_total}")
            partes.append(f"Total de artículos: {envio.cantidad_total}")
            
            # Información agregada de productos
            peso_total_productos = sum(p.peso * p.cantidad for p in productos)
            valor_total_productos = sum(p.valor * p.cantidad for p in productos)
            if peso_total_productos > 0:
                partes.append(f"Peso total productos: {peso_total_productos} kg")
            if valor_total_productos > 0:
                partes.append(f"Valor total productos: ${valor_total_productos}")
        
        # Observaciones (pueden contener información relevante)
        if envio.observaciones:
            partes.append(f"Observaciones: {envio.observaciones}")
            partes.append(envio.observaciones)  # También como texto libre
        
        # Resumen descriptivo al final
        resumen = f"Envío {envio.hawb} {estado_display} para {envio.comprador.nombre}"
        if envio.comprador.ciudad:
            resumen += f" en {envio.comprador.ciudad}"
        partes.append(resumen)
        
        # Concatenar todas las partes
        texto_completo = " | ".join(partes)
        
        # Aplicar limpieza y normalización antes de retornar
        texto_procesado = TextProcessor.procesar_texto(texto_completo)
        
        return texto_procesado
    
    # TODO: Extraer fragmentos relevantes del texto basados en la consulta.
    @staticmethod
    def extraer_fragmentos(
        consulta: str,
        texto: str,
        max_fragmentos: int = 3
    ) -> List[str]:
        """
        Extrae fragmentos relevantes del texto basados en la consulta.
        
        Args:
            consulta: Texto de la consulta
            texto: Texto indexado
            max_fragmentos: Máximo de fragmentos a extraer
            
        Returns:
            Lista de fragmentos relevantes
        """
        fragmentos = []
        palabras_consulta = consulta.lower().split()
        texto_lower = texto.lower()
        
        for palabra in palabras_consulta:
            if len(palabra) < 3:  # Ignorar palabras muy cortas
                continue
            
            if palabra in texto_lower:
                # Encontrar posición y extraer contexto
                pos = texto_lower.find(palabra)
                inicio = max(0, pos - 30)
                fin = min(len(texto), pos + 50)
                fragmento = texto[inicio:fin].strip()
                
                if fragmento and fragmento not in fragmentos:
                    # Agregar puntos suspensivos si es necesario
                    if inicio > 0:
                        fragmento = "..." + fragmento
                    if fin < len(texto):
                        fragmento = fragmento + "..."
                    
                    fragmentos.append(fragmento)
                    
                    if len(fragmentos) >= max_fragmentos:
                        break
        
        return fragmentos if fragmentos else [texto[:100] + "..."]
    
    # TODO: Generar una explicación de por qué el resultado es relevante.
    @staticmethod
    def generar_razon_relevancia(
        consulta: str,
        envio,
        similitud: float
    ) -> str:
        """
        Genera una explicación de por qué el resultado es relevante.
        
        Args:
            consulta: Texto de la consulta
            envio: Instancia del envío
            similitud: Score de similitud
            
        Returns:
            Explicación de relevancia
        """
        razones = []
        consulta_lower = consulta.lower()
        
        # Verificar coincidencias específicas
        if envio.comprador.ciudad and envio.comprador.ciudad.lower() in consulta_lower:
            razones.append(f"ciudad {envio.comprador.ciudad}")
        
        if envio.get_estado_display().lower() in consulta_lower:
            razones.append(f"estado {envio.get_estado_display()}")
        
        if envio.comprador.nombre and envio.comprador.nombre.lower() in consulta_lower:
            razones.append(f"comprador {envio.comprador.nombre}")
        
        if envio.hawb.lower() in consulta_lower:
            razones.append(f"código {envio.hawb}")
        
        # Verificar productos (mejorado para detectar mejor consultas sobre productos)
        productos_coinciden = []
        consulta_palabras = set(consulta_lower.split())
        
        for producto in envio.productos.all():
            descripcion_lower = producto.descripcion.lower()
            categoria_display = producto.get_categoria_display().lower()
            categoria_key = producto.categoria.lower()
            
            # Verificar coincidencia exacta en descripción
            if descripcion_lower in consulta_lower or any(palabra in descripcion_lower for palabra in consulta_palabras if len(palabra) > 3):
                productos_coinciden.append(f"producto '{producto.descripcion}'")
            
            # Verificar coincidencia en categoría
            if categoria_display in consulta_lower or categoria_key in consulta_lower:
                productos_coinciden.append(f"categoría {categoria_display}")
            
            # Verificar sinónimos de categorías
            sinonimos = {
                'electronica': ['electrónica', 'electrónicos', 'tecnología', 'tecnologico', 'dispositivos'],
                'ropa': ['vestimenta', 'prendas', 'indumentaria', 'textiles', 'moda'],
                'hogar': ['artículos para el hogar', 'decoración', 'muebles', 'utensilios'],
                'deportes': ['artículos deportivos', 'equipamiento deportivo', 'deportivo', 'fitness'],
            }
            if categoria_key in sinonimos:
                for sinonimo in sinonimos[categoria_key]:
                    if sinonimo in consulta_lower:
                        productos_coinciden.append(f"tipo de producto {sinonimo}")
                        break
            
            # Verificar información numérica de productos
            if 'peso' in consulta_lower and producto.peso:
                productos_coinciden.append(f"producto con peso {producto.peso}kg")
            if 'valor' in consulta_lower or 'precio' in consulta_lower:
                if producto.valor:
                    productos_coinciden.append(f"producto con valor ${producto.valor}")
        
        if productos_coinciden:
            razones.extend(productos_coinciden[:3])  # Limitar a 3 razones de productos
        
        if razones:
            return f"Coincide con: {', '.join(razones)}"
        else:
            porcentaje = int(similitud * 100)
            return f"Similitud semántica: {porcentaje}%"
    
    # TODO: Calcular un score de coincidencias exactas entre consulta y texto indexado.
    @staticmethod
    def calcular_coincidencias_exactas(
        texto_consulta: str,
        texto_indexado: str
    ) -> float:
        """
        Calcula un score de coincidencias exactas entre consulta y texto indexado.
        MEJORADO: Incluye detección de consultas numéricas sobre productos.
        
        Args:
            texto_consulta: Texto de la consulta del usuario
            texto_indexado: Texto indexado del envío
            
        Returns:
            float: Score de coincidencias [0.0, 1.0]
        """
        consulta_lower = texto_consulta.lower()
        texto_lower = texto_indexado.lower()
        
        # Separar palabras significativas (más de 3 caracteres)
        palabras_consulta = [p for p in consulta_lower.split() if len(p) > 3]
        if not palabras_consulta:
            return 0.0
        
        coincidencias = 0
        total_palabras = len(palabras_consulta)
        boost_numerico = 0.0
        
        # Detectar consultas numéricas sobre productos
        import re
        
        # Patrones para detectar números y unidades
        patrones_numericos = [
            r'(\d+\.?\d*)\s*(kg|kilogramos?|gramos?|g)',  # Peso
            r'(\d+\.?\d*)\s*(\$|usd|dolares?|pesos?)',   # Valor/precio
            r'mayor\s+a\s*(\d+)',                        # Mayor que
            r'menor\s+a\s*(\d+)',                        # Menor que
            r'más\s+de\s*(\d+)',                         # Más de
            r'peso\s+(\d+)',                             # Peso específico
            r'valor\s+(\d+)',                            # Valor específico
        ]
        
        # Verificar si la consulta contiene información numérica
        tiene_info_numerica = False
        valores_consulta = []
        
        for patron in patrones_numericos:
            matches = re.findall(patron, consulta_lower)
            if matches:
                tiene_info_numerica = True
                # Extraer valores numéricos
                for match in matches:
                    if isinstance(match, tuple):
                        valores_consulta.extend([m for m in match if m.replace('.', '').isdigit()])
                    elif match.replace('.', '').isdigit():
                        valores_consulta.append(match)
        
        # Si hay información numérica, buscar coincidencias en el texto indexado
        if tiene_info_numerica:
            for valor in valores_consulta:
                # Buscar el valor en el texto indexado
                if valor in texto_lower:
                    boost_numerico += 0.2  # Boost adicional por coincidencia numérica
                    break
        
        # Coincidencias de palabras normales
        for palabra in palabras_consulta:
            # Verificar coincidencia exacta
            if palabra in texto_lower:
                coincidencias += 1
            # Verificar coincidencia parcial (palabra contenida)
            elif any(palabra in p or p in palabra for p in texto_lower.split() if len(p) > 3):
                coincidencias += 0.5
        
        # Calcular score base
        score_base = min(coincidencias / total_palabras, 1.0) if total_palabras > 0 else 0.0
        
        # Agregar boost numérico (limitado a 0.3 adicional)
        score_final = min(score_base + boost_numerico, 1.0)
        
        return score_final

