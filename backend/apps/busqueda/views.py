from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.db import models
import time
import numpy as np
from openai import OpenAI
from .utils_embeddings import (
    generar_embedding,
    generar_texto_envio,
    calcular_similitudes,
    ordenar_por_metrica,
    aplicar_umbral_similitud
)

from .models import (
    HistorialBusqueda, 
    BusquedaSemantica, 
    FeedbackSemantico,
    SugerenciaSemantica,
    EnvioEmbedding
)
from .serializers import (
    HistorialBusquedaSerializer, 
    HistorialBusquedaListSerializer,
    BusquedaSemanticaSerializer,
    FeedbackSemanticoSerializer,
    SugerenciaSemanticaSerializer,
    EnvioEmbeddingSerializer
)
from apps.archivos.models import Envio, Producto
from apps.archivos.serializers import EnvioSerializer

Usuario = get_user_model()

# Función para obtener el cliente de OpenAI (lazy initialization)
def get_openai_client():
    """Obtiene el cliente de OpenAI, inicializándolo solo cuando se necesita"""
    try:
        api_key = settings.OPENAI_API_KEY
        if not api_key or api_key == 'sk-proj-temp-key-replace-with-your-key':
            return None
        return OpenAI(api_key=api_key)
    except Exception:
        return None


class BusquedaViewSet(viewsets.ModelViewSet):
    """ViewSet para búsquedas y historial"""
    queryset = HistorialBusqueda.objects.all()
    serializer_class = HistorialBusquedaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['termino_busqueda']
    ordering_fields = ['fecha_busqueda', 'terminos_busqueda']
    ordering = ['-fecha_busqueda']

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return HistorialBusquedaListSerializer
        return HistorialBusquedaSerializer

    def get_queryset(self):
        """Filtra el queryset según el usuario"""
        return HistorialBusqueda.objects.filter(usuario=self.request.user)

    @action(detail=False, methods=['get'])
    def buscar(self, request):
        """Realiza una búsqueda tradicional en usuarios, envíos y productos"""
        query = request.query_params.get('q', '')
        tipo = request.query_params.get('tipo', 'general')
        
        if not query:
            return Response({'error': 'Término de búsqueda requerido'}, status=status.HTTP_400_BAD_REQUEST)

        # Realizar búsqueda según el tipo
        resultados = {}
        
        if tipo in ['general', 'usuarios']:
            usuarios = Usuario.objects.filter(
                Q(nombre__icontains=query) | 
                Q(correo__icontains=query) |
                Q(cedula__icontains=query) |
                Q(username__icontains=query)
            )
            
            # Filtrar por permisos del usuario
            user = request.user
            if user.es_comprador:
                usuarios = usuarios.filter(id=user.id)
            elif user.es_digitador:
                usuarios = usuarios.filter(rol__in=[3, 4])
            elif user.es_gerente:
                usuarios = usuarios.exclude(rol=1)
            
            from apps.usuarios.serializers import UsuarioListSerializer
            usuarios_serializer = UsuarioListSerializer(usuarios, many=True)
            resultados['usuarios'] = usuarios_serializer.data

        if tipo in ['general', 'envios']:
            envios = Envio.objects.filter(
                Q(hawb__icontains=query) | 
                Q(comprador__nombre__icontains=query) |
                Q(estado__icontains=query)
            )
            
            # Filtrar por permisos del usuario
            user = request.user
            if user.es_comprador:
                envios = envios.filter(comprador=user)
            
            from apps.archivos.serializers import EnvioListSerializer
            envios_serializer = EnvioListSerializer(envios, many=True)
            resultados['envios'] = envios_serializer.data

        if tipo in ['general', 'productos']:
            productos = Producto.objects.filter(
                Q(descripcion__icontains=query) | 
                Q(categoria__icontains=query) |
                Q(envio__hawb__icontains=query)
            )
            
            # Filtrar por permisos del usuario
            user = request.user
            if user.es_comprador:
                productos = productos.filter(envio__comprador=user)
            
            from apps.archivos.serializers import ProductoListSerializer
            productos_serializer = ProductoListSerializer(productos, many=True)
            resultados['productos'] = productos_serializer.data

        # Guardar en historial
        total_resultados = sum(len(resultados.get(key, [])) for key in resultados)
        HistorialBusqueda.objects.create(
            usuario=request.user,
            termino_busqueda=query,
            tipo_busqueda=tipo,
            resultados_encontrados=total_resultados
        )

        return Response({
            'query': query,
            'tipo': tipo,
            'total_resultados': total_resultados,
            'resultados': resultados
        })

    @action(detail=False, methods=['get'])
    def historial(self, request):
        """Obtiene el historial de búsquedas del usuario"""
        historial = self.get_queryset()
        page = self.paginate_queryset(historial)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(historial, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def limpiar_historial(self, request):
        """Limpia el historial de búsquedas del usuario"""
        self.get_queryset().delete()
        return Response({'message': 'Historial limpiado correctamente'})

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de búsquedas del usuario"""
        user = request.user
        total_busquedas = HistorialBusqueda.objects.filter(usuario=user).count()
        busquedas_hoy = HistorialBusqueda.objects.filter(
            usuario=user,
            fecha_busqueda__date=timezone.now().date()
        ).count()
        
        # Búsquedas más populares
        busquedas_populares = HistorialBusqueda.objects.filter(
            usuario=user
        ).values('termino_busqueda').annotate(
            count=models.Count('termino_busqueda')
        ).order_by('-count')[:5]

        return Response({
            'total_busquedas': total_busquedas,
            'busquedas_hoy': busquedas_hoy,
            'busquedas_populares': busquedas_populares
        })

    # ==================== BÚSQUEDA SEMÁNTICA ====================
    @action(detail=False, methods=['post'], url_path='semantica')
    def busqueda_semantica(self, request):
        """
        Búsqueda semántica de envíos usando OpenAI embeddings
        
        Request body:
        {
            "texto": "envíos entregados en Quito la semana pasada",
            "limite": 20,
            "filtrosAdicionales": {
                "fechaDesde": "2025-01-01",
                "estado": "entregado"
            }
        }
        """
        tiempo_inicio = time.time()
        
        consulta_texto = request.data.get('texto', '').strip()
        limite = request.data.get('limite', 20)
        filtros_adicionales = request.data.get('filtrosAdicionales', {})
        modelo_embedding = request.data.get('modeloEmbedding', settings.OPENAI_EMBEDDING_MODEL)
        
        # Validar modelo de embedding
        modelos_validos = ['text-embedding-3-small', 'text-embedding-3-large', 'text-embedding-ada-002']
        if modelo_embedding not in modelos_validos:
            modelo_embedding = settings.OPENAI_EMBEDDING_MODEL
        
        if not consulta_texto:
            return Response(
                {'error': 'El campo "texto" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 1. Obtener envíos base (aplicar filtros de permisos)
            envios_queryset = self._obtener_envios_filtrados(request.user, filtros_adicionales)
            
            if envios_queryset.count() == 0:
                tiempo_respuesta = int((time.time() - tiempo_inicio) * 1000)
                # Generar embedding para calcular costo incluso sin resultados
                embedding_resultado = self._generar_embedding(consulta_texto, modelo_embedding)
                
                # Guardar búsqueda sin resultados
                busqueda = BusquedaSemantica.objects.create(
                    usuario=request.user,
                    consulta=consulta_texto,
                    resultados_encontrados=0,
                    tiempo_respuesta=tiempo_respuesta,
                    filtros_aplicados=filtros_adicionales if filtros_adicionales else None,
                    modelo_utilizado=modelo_embedding,
                    costo_consulta=embedding_resultado['costo'],
                    tokens_utilizados=embedding_resultado['tokens']
                )
                
                return Response({
                    'consulta': consulta_texto,
                    'resultados': [],
                    'totalEncontrados': 0,
                    'tiempoRespuesta': tiempo_respuesta,
                    'modeloUtilizado': modelo_embedding,
                    'costoConsulta': float(embedding_resultado['costo']),
                    'tokensUtilizados': embedding_resultado['tokens'],
                    'busquedaId': busqueda.id
                })
            
            # 2. Generar embedding de la consulta y calcular costo
            embedding_resultado = self._generar_embedding(consulta_texto, modelo_embedding)
            embedding_consulta = embedding_resultado['embedding']
            tokens_consulta = embedding_resultado['tokens']
            costo_consulta = embedding_resultado['costo']
            
            # 3. Buscar envíos similares
            resultados = self._buscar_envios_similares(
                envios_queryset,
                embedding_consulta,
                consulta_texto,
                limite,
                modelo_embedding
            )
            
            # 4. Calcular tiempo de respuesta
            tiempo_respuesta = int((time.time() - tiempo_inicio) * 1000)
            
            # 5. Guardar en historial con toda la información
            busqueda = BusquedaSemantica.objects.create(
                usuario=request.user,
                consulta=consulta_texto,
                resultados_encontrados=len(resultados),
                tiempo_respuesta=tiempo_respuesta,
                filtros_aplicados=filtros_adicionales if filtros_adicionales else None,
                modelo_utilizado=modelo_embedding,
                costo_consulta=costo_consulta,
                tokens_utilizados=tokens_consulta
            )
            
            # 6. Retornar respuesta
            return Response({
                'consulta': consulta_texto,
                'resultados': resultados,
                'totalEncontrados': len(resultados),
                'tiempoRespuesta': tiempo_respuesta,
                'modeloUtilizado': modelo_embedding,
                'costoConsulta': float(costo_consulta),
                'tokensUtilizados': tokens_consulta,
                'busquedaId': busqueda.id
            })
            
        except Exception as e:
            print(f"Error en búsqueda semántica: {str(e)}")
            return Response(
                {'error': f'Error procesando búsqueda semántica: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='semantica/sugerencias')
    def sugerencias_semanticas(self, request):
        """
        Obtiene sugerencias para búsqueda semántica
        """
        query = request.query_params.get('q', '').lower()
        
        # Obtener sugerencias predefinidas activas
        sugerencias = SugerenciaSemantica.objects.filter(activa=True)
        
        # Filtrar si hay query
        if query and len(query) >= 2:
            sugerencias = sugerencias.filter(
                Q(texto__icontains=query) | Q(categoria__icontains=query)
            )
        
        sugerencias = sugerencias[:10]
        serializer = SugerenciaSemanticaSerializer(sugerencias, many=True)
        
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='semantica/historial')
    def historial_semantico(self, request):
        """Obtiene el historial de búsquedas semánticas del usuario"""
        historial = BusquedaSemantica.objects.filter(usuario=request.user).order_by('-fecha_busqueda')[:10]
        serializer = BusquedaSemanticaSerializer(historial, many=True)
        
        # Formatear datos para el frontend
        datos_formateados = []
        for item in serializer.data:
            datos_formateados.append({
                'id': item['id'],
                'consulta': item['consulta'],
                'fecha': item['fecha_busqueda'],
                'totalResultados': item['resultados_encontrados'],
                'tiempoRespuesta': item['tiempo_respuesta'],
                'modeloUtilizado': item.get('modelo_utilizado', 'text-embedding-3-small'),
                'costoConsulta': float(item.get('costo_consulta', 0)),
                'tokensUtilizados': item.get('tokens_utilizados', 0),
                'filtrosAplicados': item.get('filtros_aplicados')
            })
        
        return Response(datos_formateados)

    @action(detail=False, methods=['post'], url_path='semantica/historial')
    def guardar_historial_semantico(self, request):
        """Guarda una búsqueda en el historial semántico"""
        consulta = request.data.get('consulta', '')
        total_resultados = request.data.get('totalResultados', 0)
        
        if not consulta:
            return Response(
                {'error': 'Consulta requerida'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        busqueda = BusquedaSemantica.objects.create(
            usuario=request.user,
            consulta=consulta,
            resultados_encontrados=total_resultados
        )
        
        serializer = BusquedaSemanticaSerializer(busqueda)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'], url_path='semantica/historial')
    def limpiar_historial_semantico(self, request):
        """Limpia el historial semántico del usuario"""
        BusquedaSemantica.objects.filter(usuario=request.user).delete()
        return Response({'message': 'Historial semántico limpiado correctamente'})

    @action(detail=False, methods=['post'], url_path='semantica/feedback')
    def feedback_semantico(self, request):
        """
        Registra feedback sobre un resultado semántico
        
        Request body:
        {
            "resultadoId": 123,
            "esRelevante": true,
            "busquedaId": 456,
            "puntuacionSimilitud": 0.85
        }
        """
        resultado_id = request.data.get('resultadoId')
        es_relevante = request.data.get('esRelevante')
        busqueda_id = request.data.get('busquedaId')
        puntuacion = request.data.get('puntuacionSimilitud', 0)
        
        if resultado_id is None or es_relevante is None:
            return Response(
                {'error': 'resultadoId y esRelevante son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            envio = Envio.objects.get(id=resultado_id)
            busqueda = None
            
            if busqueda_id:
                busqueda = BusquedaSemantica.objects.get(id=busqueda_id, usuario=request.user)
            
            # Crear o actualizar feedback
            feedback, created = FeedbackSemantico.objects.update_or_create(
                usuario=request.user,
                envio=envio,
                busqueda=busqueda,
                defaults={
                    'es_relevante': es_relevante,
                    'puntuacion_similitud': puntuacion
                }
            )
            
            serializer = FeedbackSemanticoSerializer(feedback)
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            
        except Envio.DoesNotExist:
            return Response(
                {'error': 'Envío no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except BusquedaSemantica.DoesNotExist:
            return Response(
                {'error': 'Búsqueda no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], url_path='semantica/metricas')
    def metricas_semanticas(self, request):
        """Obtiene métricas de búsquedas semánticas"""
        user = request.user
        
        total_busquedas = BusquedaSemantica.objects.filter(usuario=user).count()
        
        # Tiempo promedio de respuesta
        busquedas = BusquedaSemantica.objects.filter(usuario=user)
        tiempo_promedio = busquedas.aggregate(
            promedio=models.Avg('tiempo_respuesta')
        )['promedio'] or 0
        
        # Total de feedback
        total_feedback = FeedbackSemantico.objects.filter(usuario=user).count()
        feedback_positivo = FeedbackSemantico.objects.filter(
            usuario=user,
            es_relevante=True
        ).count()
        
        # Embeddings generados
        total_embeddings = EnvioEmbedding.objects.count()
        
        return Response({
            'totalBusquedas': total_busquedas,
            'tiempoPromedioRespuesta': round(tiempo_promedio, 2),
            'totalFeedback': total_feedback,
            'feedbackPositivo': feedback_positivo,
            'feedbackNegativo': total_feedback - feedback_positivo,
            'totalEmbeddings': total_embeddings
        })

    # ==================== MÉTODOS AUXILIARES ====================
    def _obtener_envios_filtrados(self, user, filtros):
        """Obtiene envíos filtrados según permisos y filtros adicionales"""
        envios = Envio.objects.all().select_related('comprador').prefetch_related('productos')
        
        # Filtrar por permisos del usuario
        if user.es_comprador:
            envios = envios.filter(comprador=user)
        
        # Aplicar filtros adicionales
        if filtros:
            if 'fechaDesde' in filtros:
                envios = envios.filter(fecha_emision__gte=filtros['fechaDesde'])
            if 'fechaHasta' in filtros:
                envios = envios.filter(fecha_emision__lte=filtros['fechaHasta'])
            if 'estado' in filtros:
                envios = envios.filter(estado=filtros['estado'])
            if 'ciudadDestino' in filtros:
                envios = envios.filter(comprador__ciudad__icontains=filtros['ciudadDestino'])
        
        return envios

    def _generar_embedding(self, texto, modelo=None):
        """
        Genera un embedding usando OpenAI y calcula el costo
        
        Returns:
            dict: {
                'embedding': lista de floats,
                'tokens': int,
                'costo': float
            }
        """
        client = get_openai_client()
        if not client:
            raise ValueError("OpenAI API key no configurada. Por favor, configura OPENAI_API_KEY en el archivo .env")
        
        if modelo is None:
            modelo = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        
        # Precios por 1K tokens según modelo (USD)
        precios_modelos = {
            'text-embedding-3-small': 0.00002,
            'text-embedding-3-large': 0.00013,
            'text-embedding-ada-002': 0.0001
        }
        
        precio_por_1k = precios_modelos.get(modelo, 0.00002)
        
        try:
            response = client.embeddings.create(
                model=modelo,
                input=texto,
                encoding_format="float"
            )
            
            embedding = response.data[0].embedding
            tokens_utilizados = response.usage.total_tokens
            
            # Calcular costo: (tokens / 1000) * precio_por_1k
            costo = (tokens_utilizados / 1000.0) * precio_por_1k
            
            return {
                'embedding': embedding,
                'tokens': tokens_utilizados,
                'costo': costo
            }
        except Exception as e:
            print(f"Error generando embedding: {str(e)}")
            raise

    def _generar_texto_envio(self, envio):
        """Genera texto descriptivo del envío para indexación"""
        partes = [
            f"HAWB: {envio.hawb}",
            f"Comprador: {envio.comprador.nombre}",
            f"Ciudad: {envio.comprador.ciudad or 'No especificada'}",
            f"Estado: {envio.get_estado_display()}",
            f"Fecha: {envio.fecha_emision.strftime('%Y-%m-%d')}",
            f"Peso: {envio.peso_total} kg",
            f"Valor: ${envio.valor_total}",
        ]
        
        # Agregar información de productos
        productos = envio.productos.all()
        if productos:
            descripciones = [p.descripcion for p in productos[:5]]
            partes.append(f"Productos: {', '.join(descripciones)}")
        
        # Agregar observaciones si existen
        if envio.observaciones:
            partes.append(f"Observaciones: {envio.observaciones}")
        
        return " | ".join(partes)

    def _buscar_envios_similares(self, envios_queryset, embedding_consulta, texto_consulta, limite, modelo_embedding=None):
        """
        Busca envíos similares usando múltiples métricas de similitud
        (cosine similarity, dot product, euclidean distance)
        """
        if modelo_embedding is None:
            modelo_embedding = getattr(settings, 'OPENAI_EMBEDDING_MODEL', 'text-embedding-3-small')
        
        # Preparar datos para cálculo de similitudes
        embeddings_envios = []
        textos_indexados = {}
        
        for envio in envios_queryset[:500]:  # Limitar a 500 envíos para performance
            # Obtener o generar embedding del envío
            try:
                envio_embedding = EnvioEmbedding.objects.get(envio=envio, modelo_usado=modelo_embedding)
                vector_envio = envio_embedding.get_vector()
                texto_indexado = envio_embedding.texto_indexado
            except EnvioEmbedding.DoesNotExist:
                # Generar embedding si no existe o si el modelo cambió
                texto_indexado = generar_texto_envio(envio)
                embedding_resultado = generar_embedding(texto_indexado, modelo_embedding)
                vector_envio = embedding_resultado['embedding']
                
                # Guardar para futuras búsquedas
                envio_embedding = EnvioEmbedding.objects.create(
                    envio=envio,
                    texto_indexado=texto_indexado,
                    modelo_usado=modelo_embedding
                )
                envio_embedding.set_vector(vector_envio)
                envio_embedding.save()
            
            if vector_envio:
                embeddings_envios.append((envio.id, vector_envio, envio))
                textos_indexados[envio.id] = texto_indexado
        
        # Calcular todas las métricas de similitud
        resultados_similitud = calcular_similitudes(embedding_consulta, embeddings_envios)
        
        # Aplicar umbral de similitud (cosine >= 0.3)
        resultados_filtrados = aplicar_umbral_similitud(resultados_similitud, umbral_cosine=0.3)
        
        # Ordenar por similitud coseno (por defecto)
        resultados_ordenados = ordenar_por_metrica(resultados_filtrados, metrica='cosine_similarity', limite=limite)
        
        # Formatear resultados para el frontend
        resultados_finales = []
        for resultado in resultados_ordenados:
            envio = resultado['envio']
            texto_indexado = textos_indexados.get(envio.id, "")
            
            # Extraer fragmentos relevantes
            fragmentos = self._extraer_fragmentos(texto_consulta, texto_indexado)
            
            # Generar razón de relevancia
            razon = self._generar_razon_relevancia(texto_consulta, envio, resultado['cosine_similarity'])
            
            # Serializar envío
            envio_data = EnvioSerializer(envio).data
            
            resultados_finales.append({
                'envio': envio_data,
                # Métricas principales
                'puntuacionSimilitud': round(resultado['cosine_similarity'], 4),
                'cosineSimilarity': round(resultado['cosine_similarity'], 4),
                'dotProduct': round(resultado['dot_product'], 4),
                'euclideanDistance': round(resultado['euclidean_distance'], 4),
                'manhattanDistance': round(resultado['manhattan_distance'], 4),
                'scoreCombinado': round(resultado['score_combinado'], 4),
                # Información contextual
                'fragmentosRelevantes': fragmentos,
                'razonRelevancia': razon,
                'textoIndexado': texto_indexado[:200] + "..." if len(texto_indexado) > 200 else texto_indexado
            })
        
        return resultados_finales

    def _similitud_coseno(self, vec1, vec2):
        """Calcula la similitud coseno entre dos vectores"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))

    def _extraer_fragmentos(self, consulta, texto, max_fragmentos=3):
        """Extrae fragmentos relevantes del texto basados en la consulta"""
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

    def _generar_razon_relevancia(self, consulta, envio, similitud):
        """Genera una explicación de por qué el resultado es relevante"""
        razones = []
        consulta_lower = consulta.lower()
        
        # Verificar coincidencias específicas
        if envio.comprador.ciudad and envio.comprador.ciudad.lower() in consulta_lower:
            razones.append(f"ciudad {envio.comprador.ciudad}")
        
        if envio.get_estado_display().lower() in consulta_lower:
            razones.append(f"estado {envio.get_estado_display()}")
        
        if envio.comprador.nombre.lower() in consulta_lower:
            razones.append(f"comprador {envio.comprador.nombre}")
        
        if envio.hawb.lower() in consulta_lower:
            razones.append(f"código {envio.hawb}")
        
        # Verificar productos
        for producto in envio.productos.all()[:3]:
            if producto.descripcion.lower() in consulta_lower:
                razones.append(f"producto {producto.descripcion}")
                break
        
        if razones:
            return f"Coincide con: {', '.join(razones)}"
        else:
            porcentaje = int(similitud * 100)
            return f"Similitud semántica: {porcentaje}%"
