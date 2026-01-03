"""
Servicio para generación de PDFs de búsquedas (tradicionales y semánticas)
"""
from typing import Dict, Any, List
from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, 
    Spacer, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.conf import settings

from apps.core.base.base_service import BaseService


class PDFBusquedaService(BaseService):
    """
    Servicio para generar PDFs de búsquedas tradicionales y semánticas.
    """
    
    @staticmethod
    def generar_pdf_busqueda_tradicional(busqueda_data: Dict[str, Any]) -> BytesIO:
        """
        Genera un PDF para una búsqueda tradicional.
        
        Args:
            busqueda_data: Dict con datos de la búsqueda
            
        Returns:
            BytesIO con el contenido del PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para el título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para subtítulos
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Título
        elements.append(Paragraph("🔍 Reporte de Búsqueda Tradicional", title_style))
        elements.append(Spacer(1, 12))
        
        # Información de la búsqueda
        info_data = [
            ['Término de búsqueda:', busqueda_data.get('termino_busqueda', 'N/A')],
            ['Tipo de búsqueda:', busqueda_data.get('tipo_busqueda', 'N/A')],
            ['Fecha de búsqueda:', busqueda_data.get('fecha_busqueda', 'N/A')],
            ['Resultados encontrados:', str(busqueda_data.get('resultados_encontrados', 0))],
            ['Usuario:', busqueda_data.get('usuario_nombre', 'N/A')],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        # Resultados
        resultados_json = busqueda_data.get('resultados_json', {})
        
        if resultados_json:
            elements.append(Paragraph("📊 Resultados", subtitle_style))
            elements.append(Spacer(1, 12))
            
            # Procesar cada tipo de resultado
            for tipo, items in resultados_json.items():
                if items and len(items) > 0:
                    elements.append(Paragraph(f"{tipo.upper()} ({len(items)})", subtitle_style))
                    
                    # Crear tabla de resultados
                    if tipo == 'envios':
                        headers = ['HAWB', 'Comprador', 'Estado', 'Ciudad', 'Fecha']
                        data = [headers]
                        for item in items[:20]:  # Limitar a 20 resultados
                            data.append([
                                item.get('hawb', 'N/A'),
                                item.get('comprador_nombre', 'N/A')[:30],
                                item.get('estado_display', 'N/A'),
                                item.get('comprador_ciudad', 'N/A'),
                                item.get('fecha_emision', 'N/A')[:10]
                            ])
                    elif tipo == 'usuarios':
                        headers = ['Usuario', 'Email', 'Rol', 'Ciudad']
                        data = [headers]
                        for item in items[:20]:
                            data.append([
                                item.get('username', 'N/A'),
                                item.get('email', 'N/A')[:30],
                                item.get('rol_display', 'N/A'),
                                item.get('ciudad', 'N/A')
                            ])
                    elif tipo == 'productos':
                        headers = ['Descripción', 'Cantidad', 'Peso', 'Valor']
                        data = [headers]
                        for item in items[:20]:
                            data.append([
                                item.get('descripcion', 'N/A')[:40],
                                str(item.get('cantidad', 0)),
                                f"{item.get('peso_kg', 0)} kg",
                                f"${item.get('valor', 0)}"
                            ])
                    
                    if len(data) > 1:
                        results_table = Table(data, repeatRows=1)
                        results_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                            ('FONTSIZE', (0, 1), (-1, -1), 8),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
                        ]))
                        
                        elements.append(results_table)
                        elements.append(Spacer(1, 20))
        else:
            elements.append(Paragraph("No se encontraron resultados.", styles['Normal']))
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_text = f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elements.append(Paragraph(footer_text, ParagraphStyle('Footer', alignment=TA_CENTER, fontSize=8, textColor=colors.grey)))
        
        # Construir PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generar_pdf_busqueda_semantica(busqueda_data: Dict[str, Any]) -> BytesIO:
        """
        Genera un PDF para una búsqueda semántica con métricas de similitud.
        
        Args:
            busqueda_data: Dict con datos de la búsqueda semántica
            
        Returns:
            BytesIO con el contenido del PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para el título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#8e44ad'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#9b59b6'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Título
        elements.append(Paragraph("🧠 Reporte de Búsqueda Semántica", title_style))
        elements.append(Spacer(1, 12))
        
        # Información de la búsqueda
        info_data = [
            ['Consulta:', busqueda_data.get('consulta', 'N/A')[:100]],
            ['Modelo utilizado:', busqueda_data.get('modelo_utilizado', 'N/A')],
            ['Fecha de búsqueda:', busqueda_data.get('fecha_busqueda', 'N/A')],
            ['Resultados encontrados:', str(busqueda_data.get('resultados_encontrados', 0))],
            ['Tiempo de respuesta:', f"{busqueda_data.get('tiempo_respuesta', 0)} ms"],
            ['Tokens utilizados:', str(busqueda_data.get('tokens_utilizados', 0))],
            ['Costo de consulta:', f"${busqueda_data.get('costo_consulta', 0):.6f}"],
            ['Usuario:', busqueda_data.get('usuario_nombre', 'N/A')],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3e5f5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#4a148c')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ce93d8'))
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 20))
        
        # Resultados con métricas de similitud
        resultados_json = busqueda_data.get('resultados_json', [])
        
        if resultados_json and len(resultados_json) > 0:
            elements.append(Paragraph("📊 Resultados con Métricas de Similitud", subtitle_style))
            elements.append(Spacer(1, 12))
            
            # Crear tabla de resultados
            headers = ['HAWB', 'Comprador', 'Score', 'Cosine', 'Euclidean', 'Boost']
            data = [headers]
            
            for resultado in resultados_json[:15]:  # Limitar a 15 resultados
                envio = resultado.get('envio', {})
                data.append([
                    envio.get('hawb', 'N/A'),
                    envio.get('comprador_nombre', 'N/A')[:25],
                    f"{resultado.get('scoreCombinado', 0):.4f}",
                    f"{resultado.get('cosineSimilarity', 0):.4f}",
                    f"{resultado.get('euclideanDistance', 0):.2f}",
                    f"{resultado.get('boostExactas', 0):.4f}"
                ])
            
            results_table = Table(data, repeatRows=1)
            results_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9c27b0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3e5f5')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ce93d8')),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fce4ec')])
            ]))
            
            elements.append(results_table)
            elements.append(Spacer(1, 20))
            
            # Explicación de métricas
            elements.append(Paragraph("ℹ️ Explicación de Métricas", subtitle_style))
            elements.append(Spacer(1, 8))
            
            metricas_text = """
            <b>Score Combinado:</b> Métrica final que combina similitud coseno normalizada + boost de coincidencias exactas.<br/>
            <b>Cosine Similarity:</b> Mide el ángulo entre vectores. Rango: [-1, 1], mayor es mejor.<br/>
            <b>Euclidean Distance:</b> Distancia geométrica entre vectores. Menor es mejor.<br/>
            <b>Boost Exactas:</b> Bonificación por coincidencias exactas de palabras (hasta +0.15).
            """
            elements.append(Paragraph(metricas_text, styles['Normal']))
        else:
            elements.append(Paragraph("No se encontraron resultados.", styles['Normal']))
        
        # Footer
        elements.append(Spacer(1, 30))
        footer_text = f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elements.append(Paragraph(footer_text, ParagraphStyle('Footer', alignment=TA_CENTER, fontSize=8, textColor=colors.grey)))
        
        # Construir PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer

