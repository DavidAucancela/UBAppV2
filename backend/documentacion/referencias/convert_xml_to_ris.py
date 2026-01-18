#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para convertir referencias bibliográficas de XML (formato Word Bibliography)
a formato RIS (Research Information Systems).
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional

# Mapeo de tipos de fuente XML a tipos RIS
XML_TO_RIS_TYPE = {
    'Report': 'RPRT',
    'InternetSite': 'WEB',
    'DocumentFromInternetSite': 'ELEC',
    'JournalArticle': 'JOUR',
    'Book': 'BOOK',
    'BookSection': 'CHAP',
    'Conference': 'CONF',
    'Thesis': 'THES',
    'Patent': 'PAT',
    'Art': 'ART',
}

# Mapeo de campos XML a campos RIS
XML_TO_RIS_FIELDS = {
    'Title': 'TI',
    'Year': 'PY',
    'Month': 'M1',
    'Day': 'M2',
    'Publisher': 'PB',
    'City': 'CY',
    'URL': 'UR',
    'InternetSiteTitle': 'T2',
    'ProductionCompany': 'PB',
    'Tag': 'ID',
}

def get_month_number(month_str: str) -> Optional[str]:
    """Convierte nombre de mes a número"""
    month_map = {
        '01': '01', '1': '01',
        '02': '02', '2': '02',
        '03': '03', '3': '03',
        '04': '04', '4': '04',
        '05': '05', '5': '05',
        '06': '06', '6': '06',
        '07': '07', '7': '07',
        '08': '08', '8': '08',
        '09': '09', '9': '09',
        '10': '10',
        '11': '11',
        '12': '12',
        'enero': '01', 'Enero': '01', 'ENERO': '01',
        'febrero': '02', 'Febrero': '02', 'FEBRERO': '02',
        'marzo': '03', 'Marzo': '03', 'MARZO': '03',
        'abril': '04', 'Abril': '04', 'ABRIL': '04',
        'mayo': '05', 'Mayo': '05', 'MAYO': '05',
        'junio': '06', 'Junio': '06', 'JUNIO': '06',
        'julio': '07', 'Julio': '07', 'JULIO': '07',
        'agosto': '08', 'Agosto': '08', 'AGOSTO': '08',
        'septiembre': '09', 'Septiembre': '09', 'SEPTIEMBRE': '09',
        'octubre': '10', 'Octubre': '10', 'OCTUBRE': '10',
        'noviembre': '11', 'Noviembre': '11', 'NOVIEMBRE': '11',
        'diciembre': '12', 'Diciembre': '12', 'DICIEMBRE': '12',
        'january': '01', 'January': '01', 'JANUARY': '01',
        'february': '02', 'February': '02', 'FEBRUARY': '02',
        'march': '03', 'March': '03', 'MARCH': '03',
        'april': '04', 'April': '04', 'APRIL': '04',
        'may': '05', 'May': '05', 'MAY': '05',
        'june': '06', 'June': '06', 'JUNE': '06',
        'july': '07', 'July': '07', 'JULY': '07',
        'august': '08', 'August': '08', 'AUGUST': '08',
        'september': '09', 'September': '09', 'SEPTEMBER': '09',
        'october': '10', 'October': '10', 'OCTOBER': '10',
        'november': '11', 'November': '11', 'NOVEMBER': '11',
        'december': '12', 'December': '12', 'DECEMBER': '12',
    }
    month_str = month_str.strip() if month_str else ''
    return month_map.get(month_str, month_str[:2] if month_str and month_str[:2].isdigit() else None)


def format_author_name(person_element: ET.Element, namespace: Dict) -> str:
    """Formatea el nombre del autor en formato RIS: Last, First Middle"""
    last = person_element.find('b:Last', namespace)
    first = person_element.find('b:First', namespace)
    middle = person_element.find('b:Middle', namespace)
    
    last_name = last.text.strip() if last is not None and last.text else ''
    first_name = first.text.strip() if first is not None and first.text else ''
    middle_name = middle.text.strip() if middle is not None and middle.text else ''
    
    parts = [p for p in [last_name, first_name, middle_name] if p]
    if not parts:
        return ''
    
    # Formato RIS: Last, First Middle
    if len(parts) == 1:
        return parts[0]
    elif len(parts) >= 2:
        return f"{parts[0]}, {' '.join(parts[1:])}"


def extract_authors(source_element: ET.Element, namespace: Dict) -> List[str]:
    """Extrae todos los autores de un elemento Source"""
    authors = []
    
    # Buscar todas las personas dentro de cualquier estructura Author anidada
    # El XML tiene estructura: <b:Author><b:Author><b:NameList><b:Person>...
    persons = source_element.findall('.//b:Person', namespace)
    
    for person in persons:
        author_name = format_author_name(person, namespace)
        if author_name:
            authors.append(author_name)
    
    return authors


def format_date(year: Optional[str], month: Optional[str], day: Optional[str]) -> Optional[str]:
    """Formatea la fecha en formato RIS: YYYY/MM/DD"""
    if not year:
        return None
    
    month_num = get_month_number(month) if month else None
    day_num = day.zfill(2) if day and day.strip() else None
    
    date_parts = [year]
    if month_num:
        date_parts.append(month_num)
        if day_num:
            date_parts.append(day_num)
    
    return '/'.join(date_parts) if len(date_parts) > 1 else None


def convert_source_to_ris(source_element: ET.Element, namespace: Dict) -> List[str]:
    """Convierte un elemento Source XML a formato RIS"""
    ris_lines = []
    
    # Tipo de referencia
    source_type = source_element.find('b:SourceType', namespace)
    ris_type = XML_TO_RIS_TYPE.get(source_type.text if source_type is not None and source_type.text else 'Report', 'GEN')
    ris_lines.append(f"TY  - {ris_type}")
    
    # ID/Tag
    tag = source_element.find('b:Tag', namespace)
    if tag is not None and tag.text:
        ris_lines.append(f"ID  - {tag.text.strip()}")
    
    # Autores
    authors = extract_authors(source_element, namespace)
    for author in authors:
        ris_lines.append(f"AU  - {author}")
    
    # Título
    title = source_element.find('b:Title', namespace)
    if title is not None and title.text:
        ris_lines.append(f"TI  - {title.text.strip()}")
    
    # Año
    year = source_element.find('b:Year', namespace)
    year_text = year.text.strip() if year is not None and year.text else None
    if year_text:
        ris_lines.append(f"PY  - {year_text}")
    
    # Fecha completa
    month = source_element.find('b:Month', namespace)
    day = source_element.find('b:Day', namespace)
    month_text = month.text.strip() if month is not None and month.text else None
    day_text = day.text.strip() if day is not None and day.text else None
    date_formatted = format_date(year_text, month_text, day_text)
    if date_formatted:
        ris_lines.append(f"DA  - {date_formatted}")
    
    # Publisher
    publisher = source_element.find('b:Publisher', namespace)
    if publisher is not None and publisher.text:
        ris_lines.append(f"PB  - {publisher.text.strip()}")
    
    # City
    city = source_element.find('b:City', namespace)
    if city is not None and city.text:
        ris_lines.append(f"CY  - {city.text.strip()}")
    
    # URL
    url = source_element.find('b:URL', namespace)
    if url is not None and url.text:
        ris_lines.append(f"UR  - {url.text.strip()}")
    
    # InternetSiteTitle / Secondary Title
    internet_site = source_element.find('b:InternetSiteTitle', namespace)
    if internet_site is not None and internet_site.text:
        ris_lines.append(f"T2  - {internet_site.text.strip()}")
    
    # Production Company (puede ir como Publisher alternativo)
    prod_company = source_element.find('b:ProductionCompany', namespace)
    if prod_company is not None and prod_company.text:
        # Si ya hay publisher, usar como T2, sino como PB
        if publisher is None or not publisher.text:
            ris_lines.append(f"PB  - {prod_company.text.strip()}")
        else:
            ris_lines.append(f"T3  - {prod_company.text.strip()}")
    
    # End of reference
    ris_lines.append("ER  - ")
    ris_lines.append("")
    
    return ris_lines


def convert_xml_to_ris(xml_file_path: str, ris_file_path: str) -> Dict[str, Dict]:
    """Convierte archivo XML a RIS y retorna tabla de mapeo"""
    
    # Parsear XML
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    # Namespace
    namespace = {'b': 'http://schemas.openxmlformats.org/officeDocument/2006/bibliography'}
    
    # Encontrar todas las fuentes
    sources = root.findall('.//b:Source', namespace)
    
    # Generar archivo RIS
    ris_lines = []
    mapping_table = {}
    
    for source in sources:
        # Extraer información para tabla de mapeo
        tag_elem = source.find('b:Tag', namespace)
        type_elem = source.find('b:SourceType', namespace)
        title_elem = source.find('b:Title', namespace)
        
        tag = tag_elem.text if tag_elem is not None and tag_elem.text else 'N/A'
        xml_type = type_elem.text if type_elem is not None and type_elem.text else 'N/A'
        ris_type = XML_TO_RIS_TYPE.get(xml_type, 'GEN')
        title = title_elem.text[:50] + '...' if title_elem is not None and title_elem.text and len(title_elem.text) > 50 else (title_elem.text if title_elem is not None and title_elem.text else 'N/A')
        
        mapping_table[tag] = {
            'XML_Type': xml_type,
            'RIS_Type': ris_type,
            'Title': title
        }
        
        # Convertir a RIS
        ris_lines.extend(convert_source_to_ris(source, namespace))
    
    # Escribir archivo RIS
    with open(ris_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(ris_lines))
    
    return mapping_table


def generate_mapping_table_markdown(mapping_table: Dict[str, Dict]) -> str:
    """Genera una tabla de mapeo en formato Markdown"""
    lines = [
        "# Tabla de Mapeo XML → RIS",
        "",
        "## Mapeo de Tipos de Referencia",
        "",
        "| Tipo XML | Tipo RIS | Descripción |",
        "|----------|----------|-------------|",
    ]
    
    # Tipos únicos
    type_mapping = {}
    for entry in mapping_table.values():
        xml_type = entry['XML_Type']
        ris_type = entry['RIS_Type']
        if xml_type not in type_mapping:
            type_descriptions = {
                'Report': 'Reporte/Informe técnico',
                'InternetSite': 'Sitio web',
                'DocumentFromInternetSite': 'Documento electrónico',
                'JournalArticle': 'Artículo de revista',
                'Book': 'Libro',
                'BookSection': 'Capítulo de libro',
                'Conference': 'Conferencia',
                'Thesis': 'Tesis',
                'Patent': 'Patente',
                'Art': 'Arte',
            }
            type_mapping[xml_type] = {
                'RIS': ris_type,
                'Desc': type_descriptions.get(xml_type, 'Genérico')
            }
    
    for xml_type, info in sorted(type_mapping.items()):
        lines.append(f"| {xml_type} | {info['RIS']} | {info['Desc']} |")
    
    lines.extend([
        "",
        "## Mapeo de Campos",
        "",
        "| Campo XML | Campo RIS | Descripción |",
        "|-----------|-----------|-------------|",
        "| Tag | ID | Identificador único de la referencia |",
        "| Author/Person | AU | Autor(es) - uno por línea |",
        "| Title | TI | Título principal |",
        "| Year | PY | Año de publicación |",
        "| Month | M1 | Mes (formateado en DA) |",
        "| Day | M2 | Día (formateado en DA) |",
        "| Year/Month/Day | DA | Fecha completa (YYYY/MM/DD) |",
        "| Publisher | PB | Editorial/Editor |",
        "| City | CY | Ciudad de publicación |",
        "| URL | UR | URL del recurso |",
        "| InternetSiteTitle | T2 | Título secundario/Sitio web |",
        "| ProductionCompany | T3/PB | Compañía productora |",
        "",
        f"## Resumen de Conversión",
        "",
        f"- **Total de referencias convertidas**: {len(mapping_table)}",
        f"- **Tipos únicos de referencias**: {len(type_mapping)}",
        "",
        "### Distribución por Tipo",
        "",
        "| Tipo | Cantidad |",
        "|------|----------|",
    ])
    
    # Contar por tipo
    type_counts = {}
    for entry in mapping_table.values():
        xml_type = entry['XML_Type']
        type_counts[xml_type] = type_counts.get(xml_type, 0) + 1
    
    for xml_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"| {xml_type} | {count} |")
    
    return '\n'.join(lines)


if __name__ == '__main__':
    import os
    # Obtener directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Rutas de archivos relativas al directorio del script
    xml_file = os.path.join(script_dir, 'Sources.xml')
    ris_file = os.path.join(script_dir, 'Sources.ris')
    mapping_file = os.path.join(script_dir, 'MAPPING_TABLE.md')
    
    print("Convirtiendo XML a RIS...")
    mapping_table = convert_xml_to_ris(xml_file, ris_file)
    
    print(f"[OK] Archivo RIS generado: {ris_file}")
    print(f"[OK] Total de referencias convertidas: {len(mapping_table)}")
    
    # Generar tabla de mapeo
    mapping_md = generate_mapping_table_markdown(mapping_table)
    with open(mapping_file, 'w', encoding='utf-8') as f:
        f.write(mapping_md)
    
    print(f"[OK] Tabla de mapeo generada: {mapping_file}")
