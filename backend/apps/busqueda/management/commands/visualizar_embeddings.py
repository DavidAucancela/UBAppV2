"""
Comando de Django para visualizar embeddings usando reducción de dimensionalidad
Uso: python manage.py visualizar_embeddings [--metodo tsne|umap|pca] [--limite N] [--clusters K]
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os
import numpy as np
from typing import List, Tuple, Optional
import json

# Importaciones opcionales con manejo de errores
try:
    import matplotlib
    matplotlib.use('Agg')  # Backend no interactivo
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from sklearn.manifold import TSNE
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import umap
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False

from apps.busqueda.models import EnvioEmbedding, EmbeddingBusqueda


class Command(BaseCommand):
    help = 'Visualiza embeddings usando reducción de dimensionalidad (t-SNE, UMAP, PCA)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--metodo',
            type=str,
            choices=['tsne', 'umap', 'pca'],
            default='tsne',
            help='Método de reducción de dimensionalidad (tsne, umap, pca)',
        )
        parser.add_argument(
            '--limite',
            type=int,
            default=1000,
            help='Límite de embeddings a visualizar (default: 1000)',
        )
        parser.add_argument(
            '--clusters',
            type=int,
            default=None,
            help='Número de clusters para agrupación (K-means). Si no se especifica, se calcula automáticamente',
        )
        parser.add_argument(
            '--tipo',
            type=str,
            choices=['envios', 'busquedas', 'ambos'],
            default='envios',
            help='Tipo de embeddings a visualizar (envios, busquedas, ambos)',
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='visualizaciones',
            help='Directorio donde guardar las visualizaciones (default: visualizaciones)',
        )
        parser.add_argument(
            '--perplexity',
            type=float,
            default=30.0,
            help='Perplexity para t-SNE (default: 30.0)',
        )
        parser.add_argument(
            '--n-neighbors',
            type=int,
            default=15,
            help='Número de vecinos para UMAP (default: 15)',
        )
        parser.add_argument(
            '--min-dist',
            type=float,
            default=0.1,
            help='Distancia mínima para UMAP (default: 0.1)',
        )

    def handle(self, *args, **options):
        # Verificar dependencias
        if not SKLEARN_AVAILABLE:
            raise CommandError(
                '❌ scikit-learn no está instalado. '
                'Instala con: pip install scikit-learn'
            )
        
        if not PLOTLY_AVAILABLE:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Plotly no está instalado. Se usará matplotlib. '
                    'Para gráficos interactivos, instala con: pip install plotly'
                )
            )
        
        metodo = options['metodo']
        limite = options['limite']
        n_clusters = options['clusters']
        tipo = options['tipo']
        output_dir = options['output_dir']
        
        # Crear directorio de salida
        os.makedirs(output_dir, exist_ok=True)
        
        self.stdout.write(self.style.SUCCESS('📊 Iniciando visualización de embeddings...'))
        
        # Extraer embeddings
        embeddings_data = self._extraer_embeddings(tipo, limite)
        
        if len(embeddings_data) == 0:
            raise CommandError('❌ No se encontraron embeddings para visualizar')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Extraídos {len(embeddings_data)} embeddings')
        )
        
        # Preparar datos
        vectors = np.array([item['vector'] for item in embeddings_data])
        labels = [item['label'] for item in embeddings_data]
        metadata = [item['metadata'] for item in embeddings_data]
        
        self.stdout.write(f'📐 Dimensiones originales: {vectors.shape}')
        
        # Reducir dimensionalidad
        self.stdout.write(f'🔄 Reduciendo dimensionalidad usando {metodo.upper()}...')
        coords_2d = self._reducir_dimensionalidad(
            vectors, 
            metodo, 
            options
        )
        
        # Calcular clusters si se solicita
        clusters = None
        if n_clusters or n_clusters is None:
            n_clusters_auto = n_clusters or self._calcular_clusters_optimo(vectors)
            self.stdout.write(f'🎯 Calculando {n_clusters_auto} clusters...')
            clusters = self._calcular_clusters(vectors, n_clusters_auto)
        
        # Generar visualizaciones
        self.stdout.write('🎨 Generando visualizaciones...')
        
        # Visualización principal
        if PLOTLY_AVAILABLE:
            self._generar_visualizacion_plotly(
                coords_2d, labels, metadata, clusters, metodo, output_dir, tipo
            )
        else:
            self._generar_visualizacion_matplotlib(
                coords_2d, labels, metadata, clusters, metodo, output_dir, tipo
            )
        
        # Generar estadísticas
        self._generar_estadisticas(
            vectors, coords_2d, clusters, output_dir, tipo
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Visualizaciones guardadas en: {os.path.abspath(output_dir)}'
            )
        )

    def _extraer_embeddings(self, tipo: str, limite: int) -> List[dict]:
        """Extrae embeddings de la base de datos"""
        embeddings_data = []
        
        if tipo in ['envios', 'ambos']:
            queryset = EnvioEmbedding.objects.filter(
                embedding_vector__isnull=False
            ).select_related('envio')[:limite]
            
            for emb in queryset:
                vector = emb.get_vector()
                if vector and len(vector) > 0:
                    embeddings_data.append({
                        'vector': vector,
                        'label': f"Envío {emb.envio.hawb}",
                        'metadata': {
                            'tipo': 'envio',
                            'id': emb.id,
                            'hawb': emb.envio.hawb,
                            'texto': emb.texto_indexado[:100] + '...' if len(emb.texto_indexado) > 100 else emb.texto_indexado,
                            'modelo': emb.modelo_usado,
                            'fecha': emb.fecha_generacion.isoformat(),
                        }
                    })
        
        if tipo in ['busquedas', 'ambos']:
            queryset = EmbeddingBusqueda.objects.filter(
                embedding_vector__isnull=False
            ).select_related('usuario')[:limite]
            
            for emb in queryset:
                vector = emb.get_vector()
                if vector and len(vector) > 0:
                    embeddings_data.append({
                        'vector': vector,
                        'label': f"Búsqueda: {emb.consulta[:30]}...",
                        'metadata': {
                            'tipo': 'busqueda',
                            'id': emb.id,
                            'consulta': emb.consulta,
                            'usuario': emb.usuario.username,
                            'fecha': emb.fecha_busqueda.isoformat(),
                        }
                    })
        
        return embeddings_data

    def _reducir_dimensionalidad(
        self, 
        vectors: np.ndarray, 
        metodo: str, 
        options: dict
    ) -> np.ndarray:
        """Reduce la dimensionalidad de los vectores"""
        # Normalizar vectores
        scaler = StandardScaler()
        vectors_scaled = scaler.fit_transform(vectors)
        
        if metodo == 'tsne':
            perplexity = options['perplexity']
            # Ajustar perplexity si es necesario
            # Perplexity debe ser estrictamente menor que n_samples
            n_samples = len(vectors)
            
            # Para muestras muy pequeñas, usar PCA en su lugar
            if n_samples < 4:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Muy pocas muestras ({n_samples}). t-SNE requiere al menos 4 muestras. '
                        'Usando PCA en su lugar.'
                    )
                )
                reducer = PCA(n_components=2, random_state=42)
                coords = reducer.fit_transform(vectors_scaled)
                explained_var = reducer.explained_variance_ratio_
                self.stdout.write(
                    self.style.SUCCESS(
                        f'📊 Varianza explicada: PC1={explained_var[0]:.2%}, '
                        f'PC2={explained_var[1]:.2%}, '
                        f'Total={sum(explained_var):.2%}'
                    )
                )
            else:
                # Ajustar perplexity: debe ser < n_samples, típicamente entre 5 y 50
                max_perplexity = min(50, n_samples - 1)
                if perplexity >= n_samples:
                    perplexity = max(5, max_perplexity)
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  Perplexity ajustado a {perplexity} (máximo {max_perplexity} para {n_samples} muestras)'
                        )
                    )
                elif perplexity > max_perplexity:
                    perplexity = max_perplexity
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  Perplexity ajustado a {perplexity} (máximo recomendado para {n_samples} muestras)'
                        )
                    )
                
                # Intentar crear TSNE con diferentes parámetros según la versión
                # Versiones recientes usan max_iter, versiones antiguas no tienen este parámetro
                try:
                    # Intentar con max_iter (versiones recientes de scikit-learn >= 1.2)
                    reducer = TSNE(
                        n_components=2,
                        perplexity=perplexity,
                        random_state=42,
                        max_iter=1000,
                        verbose=1
                    )
                except TypeError:
                    try:
                        # Intentar sin max_iter (versiones intermedias)
                        reducer = TSNE(
                            n_components=2,
                            perplexity=perplexity,
                            random_state=42,
                            verbose=1
                        )
                    except TypeError:
                        # Versiones muy antiguas pueden no tener verbose
                        reducer = TSNE(
                            n_components=2,
                            perplexity=perplexity,
                            random_state=42
                        )
                
                coords = reducer.fit_transform(vectors_scaled)
            
        elif metodo == 'umap':
            if not UMAP_AVAILABLE:
                raise CommandError(
                    '❌ UMAP no está instalado. '
                    'Instala con: pip install umap-learn'
                )
            
            reducer = umap.UMAP(
                n_components=2,
                n_neighbors=options['n_neighbors'],
                min_dist=options['min_dist'],
                random_state=42,
                verbose=True
            )
            coords = reducer.fit_transform(vectors_scaled)
            
        elif metodo == 'pca':
            reducer = PCA(n_components=2, random_state=42)
            coords = reducer.fit_transform(vectors_scaled)
            explained_var = reducer.explained_variance_ratio_
            self.stdout.write(
                self.style.SUCCESS(
                    f'📊 Varianza explicada: PC1={explained_var[0]:.2%}, '
                    f'PC2={explained_var[1]:.2%}, '
                    f'Total={sum(explained_var):.2%}'
                )
            )
        
        return coords

    def _calcular_clusters_optimo(self, vectors: np.ndarray) -> int:
        """Calcula el número óptimo de clusters usando el método del codo"""
        n_samples = len(vectors)
        max_clusters = min(10, n_samples // 10) if n_samples > 20 else min(5, n_samples // 2)
        
        if max_clusters < 2:
            return 2
        
        # Método del codo simplificado
        inertias = []
        k_range = range(2, max_clusters + 1)
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(vectors)
            inertias.append(kmeans.inertia_)
        
        # Calcular diferencias para encontrar el "codo"
        if len(inertias) > 1:
            diffs = [inertias[i] - inertias[i+1] for i in range(len(inertias)-1)]
            if diffs:
                # Encontrar donde la diferencia disminuye significativamente
                avg_diff = np.mean(diffs)
                for i, diff in enumerate(diffs):
                    if diff < avg_diff * 0.5:
                        return k_range[i]
        
        return max_clusters

    def _calcular_clusters(self, vectors: np.ndarray, n_clusters: int) -> np.ndarray:
        """Calcula clusters usando K-means"""
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        return kmeans.fit_predict(vectors)

    def _generar_visualizacion_plotly(
        self,
        coords_2d: np.ndarray,
        labels: List[str],
        metadata: List[dict],
        clusters: Optional[np.ndarray],
        metodo: str,
        output_dir: str,
        tipo: str
    ):
        """Genera visualización interactiva con Plotly"""
        # Preparar datos para hover
        hover_texts = []
        for i, meta in enumerate(metadata):
            if meta['tipo'] == 'envio':
                hover_text = f"<b>{labels[i]}</b><br>"
                hover_text += f"HAWB: {meta['hawb']}<br>"
                hover_text += f"Texto: {meta['texto']}<br>"
                hover_text += f"Modelo: {meta['modelo']}"
            else:
                hover_text = f"<b>{labels[i]}</b><br>"
                hover_text += f"Consulta: {meta['consulta']}<br>"
                hover_text += f"Usuario: {meta['usuario']}"
            hover_texts.append(hover_text)
        
        # Crear figura
        fig = go.Figure()
        
        if clusters is not None:
            # Visualización con clusters
            unique_clusters = np.unique(clusters)
            colors = px.colors.qualitative.Set3
            
            for cluster_id in unique_clusters:
                mask = clusters == cluster_id
                cluster_coords = coords_2d[mask]
                cluster_labels = [labels[i] for i in range(len(labels)) if mask[i]]
                cluster_hover = [hover_texts[i] for i in range(len(hover_texts)) if mask[i]]
                
                fig.add_trace(go.Scatter(
                    x=cluster_coords[:, 0],
                    y=cluster_coords[:, 1],
                    mode='markers',
                    name=f'Cluster {cluster_id}',
                    text=cluster_labels,
                    hovertext=cluster_hover,
                    hoverinfo='text',
                    marker=dict(
                        size=8,
                        color=colors[cluster_id % len(colors)],
                        line=dict(width=1, color='white')
                    )
                ))
        else:
            # Visualización sin clusters, colorear por tipo
            tipos = [m['tipo'] for m in metadata]
            unique_tipos = list(set(tipos))
            colors_map = {'envio': 'blue', 'busqueda': 'red'}
            
            for tipo_item in unique_tipos:
                mask = [t == tipo_item for t in tipos]
                tipo_coords = coords_2d[mask]
                tipo_labels = [labels[i] for i in range(len(labels)) if mask[i]]
                tipo_hover = [hover_texts[i] for i in range(len(hover_texts)) if mask[i]]
                
                fig.add_trace(go.Scatter(
                    x=tipo_coords[:, 0],
                    y=tipo_coords[:, 1],
                    mode='markers',
                    name=tipo_item.capitalize(),
                    text=tipo_labels,
                    hovertext=tipo_hover,
                    hoverinfo='text',
                    marker=dict(
                        size=8,
                        color=colors_map.get(tipo_item, 'gray'),
                        line=dict(width=1, color='white')
                    )
                ))
        
        # Configurar layout
        metodo_nombre = {'tsne': 't-SNE', 'umap': 'UMAP', 'pca': 'PCA'}[metodo]
        fig.update_layout(
            title=f'Visualización de Embeddings - {metodo_nombre}',
            xaxis_title=f'{metodo_nombre} Dimensión 1',
            yaxis_title=f'{metodo_nombre} Dimensión 2',
            hovermode='closest',
            width=1200,
            height=800,
            template='plotly_white'
        )
        
        # Guardar
        output_file = os.path.join(output_dir, f'embeddings_{metodo}_{tipo}.html')
        fig.write_html(output_file)
        self.stdout.write(
            self.style.SUCCESS(f'✅ Visualización guardada: {output_file}')
        )

    def _generar_visualizacion_matplotlib(
        self,
        coords_2d: np.ndarray,
        labels: List[str],
        metadata: List[dict],
        clusters: Optional[np.ndarray],
        metodo: str,
        output_dir: str,
        tipo: str
    ):
        """Genera visualización estática con Matplotlib"""
        if not MATPLOTLIB_AVAILABLE:
            raise CommandError('❌ Matplotlib no está instalado')
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        if clusters is not None:
            unique_clusters = np.unique(clusters)
            colors = plt.cm.Set3(np.linspace(0, 1, len(unique_clusters)))
            
            for i, cluster_id in enumerate(unique_clusters):
                mask = clusters == cluster_id
                cluster_coords = coords_2d[mask]
                ax.scatter(
                    cluster_coords[:, 0],
                    cluster_coords[:, 1],
                    c=[colors[i]],
                    label=f'Cluster {cluster_id}',
                    alpha=0.6,
                    s=50
                )
            ax.legend()
        else:
            tipos = [m['tipo'] for m in metadata]
            unique_tipos = list(set(tipos))
            colors_map = {'envio': 'blue', 'busqueda': 'red'}
            
            for tipo_item in unique_tipos:
                mask = [t == tipo_item for t in tipos]
                tipo_coords = coords_2d[mask]
                ax.scatter(
                    tipo_coords[:, 0],
                    tipo_coords[:, 1],
                    c=colors_map.get(tipo_item, 'gray'),
                    label=tipo_item.capitalize(),
                    alpha=0.6,
                    s=50
                )
            ax.legend()
        
        metodo_nombre = {'tsne': 't-SNE', 'umap': 'UMAP', 'pca': 'PCA'}[metodo]
        ax.set_title(f'Visualización de Embeddings - {metodo_nombre}', fontsize=16)
        ax.set_xlabel(f'{metodo_nombre} Dimensión 1')
        ax.set_ylabel(f'{metodo_nombre} Dimensión 2')
        ax.grid(True, alpha=0.3)
        
        output_file = os.path.join(output_dir, f'embeddings_{metodo}_{tipo}.png')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Visualización guardada: {output_file}')
        )

    def _generar_estadisticas(
        self,
        vectors: np.ndarray,
        coords_2d: np.ndarray,
        clusters: Optional[np.ndarray],
        output_dir: str,
        tipo: str
    ):
        """Genera estadísticas sobre los embeddings"""
        stats = {
            'total_embeddings': len(vectors),
            'dimensiones_originales': vectors.shape[1],
            'dimensiones_reducidas': coords_2d.shape[1],
            'estadisticas_vectores': {
                'media': float(np.mean(vectors)),
                'std': float(np.std(vectors)),
                'min': float(np.min(vectors)),
                'max': float(np.max(vectors)),
            },
            'estadisticas_coordenadas_2d': {
                'x_mean': float(np.mean(coords_2d[:, 0])),
                'x_std': float(np.std(coords_2d[:, 0])),
                'y_mean': float(np.mean(coords_2d[:, 1])),
                'y_std': float(np.std(coords_2d[:, 1])),
            }
        }
        
        if clusters is not None:
            unique_clusters, counts = np.unique(clusters, return_counts=True)
            stats['clusters'] = {
                'numero_clusters': int(len(unique_clusters)),
                'distribucion': {
                    int(cluster_id): int(count) 
                    for cluster_id, count in zip(unique_clusters, counts)
                }
            }
        
        # Calcular distancias promedio entre puntos
        try:
            from scipy.spatial.distance import pdist
            distances = pdist(coords_2d, metric='euclidean')
            stats['distancias'] = {
                'media': float(np.mean(distances)),
                'std': float(np.std(distances)),
                'min': float(np.min(distances)),
                'max': float(np.max(distances)),
            }
        except ImportError:
            # Calcular distancias manualmente si scipy no está disponible
            n = len(coords_2d)
            distances = []
            for i in range(n):
                for j in range(i + 1, n):
                    dist = np.linalg.norm(coords_2d[i] - coords_2d[j])
                    distances.append(dist)
            if distances:
                stats['distancias'] = {
                    'media': float(np.mean(distances)),
                    'std': float(np.std(distances)),
                    'min': float(np.min(distances)),
                    'max': float(np.max(distances)),
                }
            else:
                stats['distancias'] = 'No se pudieron calcular distancias'
        
        # Guardar estadísticas
        stats_file = os.path.join(output_dir, f'estadisticas_{tipo}.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Estadísticas guardadas: {stats_file}')
        )
        
        # Mostrar resumen
        self.stdout.write('\n' + '='*60)
        self.stdout.write('📊 RESUMEN DE ESTADÍSTICAS')
        self.stdout.write('='*60)
        self.stdout.write(f"Total de embeddings: {stats['total_embeddings']}")
        self.stdout.write(f"Dimensiones originales: {stats['dimensiones_originales']}")
        if clusters is not None:
            self.stdout.write(f"Número de clusters: {stats['clusters']['numero_clusters']}")
            self.stdout.write("Distribución de clusters:")
            for cluster_id, count in stats['clusters']['distribucion'].items():
                self.stdout.write(f"  Cluster {cluster_id}: {count} embeddings")
        self.stdout.write('='*60)

