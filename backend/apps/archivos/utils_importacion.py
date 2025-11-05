"""
Utilidades para procesamiento de archivos Excel
"""
import pandas as pd
import openpyxl
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple, Any
from django.db import transaction
from .models import ImportacionExcel, Envio, Producto


class ValidadorDatos:
    """Clase para validar datos de Excel"""
    
    @staticmethod
    def limpiar_texto(valor):
        """Limpia y normaliza texto"""
        if pd.isna(valor) or valor is None:
            return ""
        return str(valor).strip()
    
    @staticmethod
    def validar_numero(valor, nombre_campo="campo"):
        """Valida y convierte a número"""
        if pd.isna(valor) or valor == "" or valor is None:
            return None, f"{nombre_campo} está vacío"
        
        try:
            # Intentar convertir a float
            numero = float(str(valor).replace(',', '.'))
            if numero < 0:
                return None, f"{nombre_campo} no puede ser negativo"
            return numero, None
        except (ValueError, TypeError):
            return None, f"{nombre_campo} debe ser un número válido"
    
    @staticmethod
    def validar_entero(valor, nombre_campo="campo"):
        """Valida y convierte a entero"""
        if pd.isna(valor) or valor == "" or valor is None:
            return None, f"{nombre_campo} está vacío"
        
        try:
            entero = int(float(str(valor)))
            if entero < 0:
                return None, f"{nombre_campo} no puede ser negativo"
            return entero, None
        except (ValueError, TypeError):
            return None, f"{nombre_campo} debe ser un número entero válido"
    
    @staticmethod
    def validar_categoria(valor):
        """Valida que la categoría sea válida"""
        categorias_validas = {
            'electronica': 'electronica',
            'electrónica': 'electronica',
            'ropa': 'ropa',
            'hogar': 'hogar',
            'deportes': 'deportes',
            'otros': 'otros',
        }
        
        if pd.isna(valor) or valor == "" or valor is None:
            return 'otros', None
        
        categoria_limpia = str(valor).lower().strip()
        if categoria_limpia in categorias_validas:
            return categorias_validas[categoria_limpia], None
        
        return 'otros', None  # Por defecto asignar 'otros'


class ProcesadorExcel:
    """Clase para procesar archivos Excel"""
    
    def __init__(self, archivo_path):
        self.archivo_path = archivo_path
        self.df = None
        self.errores = []
        self.duplicados = []
        
    def leer_archivo(self) -> Tuple[bool, str]:
        """Lee el archivo Excel y carga los datos"""
        try:
            # Intentar leer el archivo Excel
            self.df = pd.read_excel(self.archivo_path, engine='openpyxl')
            
            # Limpiar nombres de columnas
            self.df.columns = [str(col).strip() for col in self.df.columns]
            
            return True, "Archivo leído correctamente"
        except Exception as e:
            return False, f"Error al leer el archivo: {str(e)}"
    
    def obtener_columnas(self) -> List[str]:
        """Obtiene las columnas del DataFrame"""
        if self.df is not None:
            return list(self.df.columns)
        return []
    
    def obtener_preview(self, limite=50) -> Dict[str, Any]:
        """Obtiene una vista previa de los datos"""
        if self.df is None:
            return {
                'columnas': [],
                'filas': [],
                'total_filas': 0
            }
        
        # Obtener filas limitadas
        df_preview = self.df.head(limite)
        
        # Convertir a lista de diccionarios
        filas = []
        for idx, row in df_preview.iterrows():
            fila_dict = {'_indice': int(idx)}
            for col in self.df.columns:
                valor = row[col]
                # Convertir valores especiales
                if pd.isna(valor):
                    fila_dict[col] = None
                elif isinstance(valor, (int, float)):
                    fila_dict[col] = float(valor) if not pd.isna(valor) else None
                else:
                    fila_dict[col] = str(valor)
            filas.append(fila_dict)
        
        return {
            'columnas': list(self.df.columns),
            'filas': filas,
            'total_filas': len(self.df)
        }
    
    def detectar_duplicados(self, columna_clave='HAWB') -> List[int]:
        """Detecta registros duplicados basándose en una columna clave"""
        if self.df is None or columna_clave not in self.df.columns:
            return []
        
        # Encontrar duplicados
        duplicados_mask = self.df[columna_clave].duplicated(keep=False)
        indices_duplicados = self.df[duplicados_mask].index.tolist()
        
        return [int(idx) for idx in indices_duplicados]
    
    def validar_datos(self, mapeo_columnas: Dict[str, str]) -> Dict[str, Any]:
        """
        Valida los datos según el mapeo de columnas
        
        Args:
            mapeo_columnas: Dict con formato {'columna_excel': 'campo_modelo'}
        
        Returns:
            Dict con errores detectados y estadísticas
        """
        if self.df is None:
            return {'errores': [], 'total_errores': 0, 'filas_con_errores': 0}
        
        errores_validacion = []
        filas_con_errores = set()
        
        for idx, row in self.df.iterrows():
            errores_fila = []
            
            # Validar cada campo según el mapeo
            for col_excel, campo_modelo in mapeo_columnas.items():
                if col_excel not in self.df.columns:
                    continue
                
                valor = row[col_excel]
                
                # Validaciones según el tipo de campo
                if campo_modelo == 'hawb':
                    if pd.isna(valor) or str(valor).strip() == "":
                        errores_fila.append({
                            'fila': int(idx) + 2,  # +2 porque Excel empieza en 1 y hay header
                            'columna': col_excel,
                            'error': 'HAWB es obligatorio'
                        })
                
                elif campo_modelo in ['peso', 'peso_total']:
                    _, error = ValidadorDatos.validar_numero(valor, 'Peso')
                    if error:
                        errores_fila.append({
                            'fila': int(idx) + 2,
                            'columna': col_excel,
                            'error': error
                        })
                
                elif campo_modelo in ['cantidad', 'cantidad_total']:
                    _, error = ValidadorDatos.validar_entero(valor, 'Cantidad')
                    if error:
                        errores_fila.append({
                            'fila': int(idx) + 2,
                            'columna': col_excel,
                            'error': error
                        })
                
                elif campo_modelo in ['valor', 'valor_total']:
                    _, error = ValidadorDatos.validar_numero(valor, 'Valor')
                    if error:
                        errores_fila.append({
                            'fila': int(idx) + 2,
                            'columna': col_excel,
                            'error': error
                        })
                
                elif campo_modelo == 'categoria':
                    _, error = ValidadorDatos.validar_categoria(valor)
                    # La categoría siempre tiene un valor por defecto, no genera error
            
            if errores_fila:
                errores_validacion.extend(errores_fila)
                filas_con_errores.add(int(idx))
        
        return {
            'errores': errores_validacion,
            'total_errores': len(errores_validacion),
            'filas_con_errores': len(filas_con_errores)
        }
    
    def procesar_e_importar(
        self, 
        importacion: ImportacionExcel,
        mapeo_columnas: Dict[str, str],
        indices_seleccionados: List[int] = None,
        comprador_id: int = None
    ) -> Tuple[bool, str]:
        """
        Procesa e importa los datos a la base de datos
        
        Args:
            importacion: Instancia de ImportacionExcel
            mapeo_columnas: Mapeo entre columnas del Excel y campos del modelo
            indices_seleccionados: Lista de índices a importar (None = todos)
            comprador_id: ID del comprador para asignar a los envíos
        
        Returns:
            Tuple (éxito, mensaje)
        """
        if self.df is None:
            return False, "No hay datos cargados"
        
        # Determinar qué filas procesar
        if indices_seleccionados:
            df_procesar = self.df.iloc[indices_seleccionados]
        else:
            df_procesar = self.df
        
        importacion.estado = 'procesando'
        importacion.total_registros = len(df_procesar)
        importacion.save()
        
        registros_exitosos = 0
        registros_con_error = 0
        
        try:
            with transaction.atomic():
                for idx, row in df_procesar.iterrows():
                    try:
                        # Extraer datos según el mapeo
                        datos_envio = self._extraer_datos_fila(row, mapeo_columnas, comprador_id)
                        
                        # Crear el envío
                        envio = self._crear_envio(datos_envio)
                        
                        registros_exitosos += 1
                        
                    except Exception as e:
                        registros_con_error += 1
                        importacion.agregar_error(
                            int(idx) + 2,
                            'general',
                            f"Error al procesar: {str(e)}"
                        )
            
            # Actualizar estadísticas
            importacion.registros_procesados = registros_exitosos
            importacion.registros_validos = registros_exitosos
            importacion.registros_errores = registros_con_error
            
            if registros_con_error == 0:
                importacion.marcar_como_completado()
                importacion.mensaje_resultado = f"✅ Importación completada con éxito. {registros_exitosos} registros procesados."
            else:
                importacion.estado = 'completado'
                importacion.mensaje_resultado = f"⚠️ Importación completada con errores. {registros_exitosos} éxitos, {registros_con_error} errores."
            
            importacion.save()
            
            return True, importacion.mensaje_resultado
            
        except Exception as e:
            importacion.estado = 'error'
            importacion.mensaje_resultado = f"❌ Error en la importación: {str(e)}"
            importacion.save()
            return False, importacion.mensaje_resultado
    
    def _extraer_datos_fila(
        self, 
        row, 
        mapeo_columnas: Dict[str, str],
        comprador_id: int
    ) -> Dict[str, Any]:
        """Extrae y valida los datos de una fila"""
        datos = {}
        
        # Mapeo inverso para facilitar búsqueda
        mapeo_inv = {v: k for k, v in mapeo_columnas.items()}
        
        # HAWB (obligatorio)
        if 'hawb' in mapeo_inv:
            datos['hawb'] = ValidadorDatos.limpiar_texto(row[mapeo_inv['hawb']])
            if not datos['hawb']:
                raise ValueError("HAWB es obligatorio")
        
        # Comprador
        datos['comprador_id'] = comprador_id
        
        # Campos numéricos del envío
        if 'peso_total' in mapeo_inv:
            peso, error = ValidadorDatos.validar_numero(row[mapeo_inv['peso_total']])
            datos['peso_total'] = Decimal(str(peso)) if peso is not None else Decimal('0')
        else:
            datos['peso_total'] = Decimal('0')
        
        if 'cantidad_total' in mapeo_inv:
            cantidad, error = ValidadorDatos.validar_entero(row[mapeo_inv['cantidad_total']])
            datos['cantidad_total'] = cantidad if cantidad is not None else 0
        else:
            datos['cantidad_total'] = 0
        
        if 'valor_total' in mapeo_inv:
            valor, error = ValidadorDatos.validar_numero(row[mapeo_inv['valor_total']])
            datos['valor_total'] = Decimal(str(valor)) if valor is not None else Decimal('0')
        else:
            datos['valor_total'] = Decimal('0')
        
        # Estado
        if 'estado' in mapeo_inv:
            estado = ValidadorDatos.limpiar_texto(row[mapeo_inv['estado']]).lower()
            if estado in ['pendiente', 'en_transito', 'entregado', 'cancelado']:
                datos['estado'] = estado
            else:
                datos['estado'] = 'pendiente'
        else:
            datos['estado'] = 'pendiente'
        
        # Observaciones
        if 'observaciones' in mapeo_inv:
            datos['observaciones'] = ValidadorDatos.limpiar_texto(row[mapeo_inv['observaciones']])
        
        # Datos del producto (si existen)
        producto = {}
        if 'descripcion' in mapeo_inv:
            producto['descripcion'] = ValidadorDatos.limpiar_texto(row[mapeo_inv['descripcion']])
        
        if 'peso' in mapeo_inv:
            peso, _ = ValidadorDatos.validar_numero(row[mapeo_inv['peso']])
            producto['peso'] = Decimal(str(peso)) if peso is not None else Decimal('0')
        
        if 'cantidad' in mapeo_inv:
            cantidad, _ = ValidadorDatos.validar_entero(row[mapeo_inv['cantidad']])
            producto['cantidad'] = cantidad if cantidad is not None else 0
        
        if 'valor' in mapeo_inv:
            valor, _ = ValidadorDatos.validar_numero(row[mapeo_inv['valor']])
            producto['valor'] = Decimal(str(valor)) if valor is not None else Decimal('0')
        
        if 'categoria' in mapeo_inv:
            categoria, _ = ValidadorDatos.validar_categoria(row[mapeo_inv['categoria']])
            producto['categoria'] = categoria
        else:
            producto['categoria'] = 'otros'
        
        if producto:
            datos['producto'] = producto
        
        return datos
    
    def _crear_envio(self, datos: Dict[str, Any]) -> Envio:
        """Crea un envío con los datos proporcionados"""
        # Extraer datos del producto si existe
        producto_datos = datos.pop('producto', None)
        
        # Crear el envío
        envio = Envio.objects.create(**datos)
        
        # Crear el producto asociado si existe
        if producto_datos and producto_datos.get('descripcion'):
            Producto.objects.create(envio=envio, **producto_datos)
            # Recalcular totales
            envio.calcular_totales()
        
        return envio


def generar_reporte_errores(importacion: ImportacionExcel) -> Dict[str, Any]:
    """
    Genera un reporte detallado de los errores de una importación
    
    Args:
        importacion: Instancia de ImportacionExcel
    
    Returns:
        Dict con el reporte de errores
    """
    reporte = {
        'importacion_id': importacion.id,
        'nombre_archivo': importacion.nombre_original,
        'fecha': importacion.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
        'estado': importacion.get_estado_display(),
        'estadisticas': {
            'total_registros': importacion.total_registros,
            'registros_validos': importacion.registros_validos,
            'registros_errores': importacion.registros_errores,
            'registros_duplicados': importacion.registros_duplicados,
            'porcentaje_exito': round((importacion.registros_validos / importacion.total_registros * 100), 2) if importacion.total_registros > 0 else 0
        },
        'errores': importacion.errores_validacion,
        'mensaje': importacion.mensaje_resultado
    }
    
    return reporte







