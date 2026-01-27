"""
Utilidades para procesamiento de archivos Excel
"""
import pandas as pd
import openpyxl
import unicodedata
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Dict, List, Tuple, Any
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import ImportacionExcel, Envio, Producto
from apps.notificaciones.utils import crear_notificacion_envio_asignado
from apps.busqueda.utils_embeddings import generar_embedding_envio
from apps.usuarios.validators import validar_cedula_ecuatoriana

Usuario = get_user_model()


def validar_cedula_o_ruc(identificacion: str, estricto: bool = False) -> None:
    """
    Valida cédula ecuatoriana (10 dígitos), RUC (13 dígitos) o RUC extendido (14 dígitos).
    En modo flexible, también acepta 9 dígitos (puede ser cédula de otro país o formato especial).
    
    Args:
        identificacion: Número de identificación a validar
        estricto: Si es True, valida algoritmo de verificación. Si es False, solo valida formato.
    
    Lanza ValidationError si no es válida.
    """
    if not identificacion:
        raise ValidationError("La identificación es requerida")
    
    # Limpiar y extraer solo dígitos
    texto = ''.join(ch for ch in str(identificacion) if ch.isdigit())
    
    if not texto:
        raise ValidationError("La identificación debe contener al menos un dígito")
    
    # Verificar tamaño de identificación
    if len(texto) == 9:
        # En modo flexible, permitir 9 dígitos (puede ser cédula de otro país o formato especial)
        if estricto:
            raise ValidationError(f"La identificación debe tener 10 dígitos (cédula), 13 dígitos (RUC) o 14 dígitos (RUC extendido), se encontraron {len(texto)}")
        # En modo flexible, permitir 9 dígitos
        if not texto.isdigit():
            raise ValidationError("La identificación debe contener solo números")
        # Permitir 9 dígitos en modo flexible sin validación adicional
        return
    
    elif len(texto) == 10:
        # Es una cédula
        if estricto:
            # Validar con algoritmo estricto
            try:
                validar_cedula_ecuatoriana(texto)
            except ValidationError as e:
                raise ValidationError(f"Cédula inválida: {str(e)}")
        else:
            # Solo validar formato básico: 10 dígitos numéricos
            if not texto.isdigit():
                raise ValidationError("La cédula debe contener solo números")
            # Validación opcional de provincia (advertencia, no error)
            try:
                provincia = int(texto[0:2])
                if provincia < 1 or provincia > 24:
                    # Solo advertir, no rechazar en modo flexible
                    pass
            except (ValueError, IndexError):
                pass
    
    elif len(texto) == 13:
        # Es un RUC
        if not texto.isdigit():
            raise ValidationError("El RUC debe contener solo números")
        
        if estricto:
            # Validar provincia en modo estricto
            provincia = int(texto[0:2])
            if provincia < 1 or provincia > 24:
                raise ValidationError("Los dos primeros dígitos del RUC deben estar entre 01 y 24 (código de provincia)")
            
            # Para personas naturales, el RUC termina en 001
            if texto.endswith('001'):
                # Validar la cédula base (primeros 10 dígitos)
                try:
                    validar_cedula_ecuatoriana(texto[:10])
                except ValidationError as e:
                    raise ValidationError(f"RUC inválido (cédula base): {str(e)}")
        # En modo flexible, solo validamos que tenga 13 dígitos
    
    elif len(texto) == 14:
        # Es un RUC extendido (14 dígitos)
        if not texto.isdigit():
            raise ValidationError("El RUC debe contener solo números")
        # En modo flexible, solo validamos que tenga 14 dígitos
    
    else:
        # Mejorar mensaje de error según el modo
        if estricto:
            raise ValidationError(f"La identificación debe tener 10 dígitos (cédula), 13 dígitos (RUC) o 14 dígitos (RUC extendido), se encontraron {len(texto)}")
        else:
            raise ValidationError(f"La identificación debe tener 9 dígitos (formato especial), 10 dígitos (cédula), 13 dígitos (RUC) o 14 dígitos (RUC extendido), se encontraron {len(texto)}. Por favor, verifique que la identificación esté completa.")


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

    @staticmethod
    def validar_fecha(valor, nombre_campo="fecha"):
        """Valida y convierte valores de fecha"""
        if pd.isna(valor) or valor == "" or valor is None:
            return None, f"{nombre_campo} está vacía"
        
        if isinstance(valor, str):
            texto = valor.strip()
            if texto.lower() in {'', '-', '--', 'n/a', 'na', 's/n'}:
                return None, f"{nombre_campo} está vacía"
        
        if isinstance(valor, datetime):
            return valor, None
        
        try:
            fecha = pd.to_datetime(valor, errors='raise')
            if pd.isna(fecha):
                raise ValueError()
            return fecha.to_pydatetime(), None
        except Exception:
            return None, f"{nombre_campo} debe tener un formato de fecha válido"


class ProcesadorExcel:
    """Clase para procesar archivos Excel"""
    COLUMNAS_NO_UTILIZADAS = {
        'factura_comercial',
        'factura comercial',
        '_empty',
        '_empty_1',
        'unnamed: 0',
        'unnamed: 1'
    }
    PALABRAS_CLAVE_PROPAGACION = [
        'nombre', 'consignatario', 'comprador', 'cliente',
        'ruc', 'cedula', 'cédula', 'identificacion', 'identificación',
        'direccion', 'dirección', 'telefono', 'teléfono', 'correo', 'email'
    ]
    VALORES_VACIOS = {'', '-', '--', '—', 'n/a', 'na', 'n.d', 's/n', 'sin dato'}
    
    def __init__(self, archivo_path):
        self.archivo_path = archivo_path
        self.df = None
        self.errores = []
        self.duplicados = []
        self.nuevos_compradores = []
        
    def leer_archivo(self) -> Tuple[bool, str]:
        """Lee el archivo Excel y carga los datos"""
        try:
            # Intentar leer el archivo Excel
            self.df = pd.read_excel(self.archivo_path, engine='openpyxl')
            
            # Limpiar nombres de columnas
            self.df.columns = [str(col).strip() for col in self.df.columns]
            self._limpiar_columnas_no_utiles()
            
            # Propagar valores vacíos desde celdas superiores
            self._propagar_valores_vacios()
            
            return True, "Archivo leído correctamente"
        except Exception as e:
            return False, f"Error al leer el archivo: {str(e)}"
    
    def _propagar_valores_vacios(self):
        """
        Propaga valores desde celdas superiores cuando las celdas inferiores están vacías.
        Esto es útil cuando en Excel se ponen datos como nombre, RUC, etc. una sola vez
        y las celdas inferiores quedan en blanco.
        """
        if self.df is None or len(self.df) == 0:
            return
        
        # Columnas que típicamente tienen valores que se propagan
        # Buscar columnas que contengan estas palabras clave (case insensitive)
        columnas_propagables = []
        for col in self.df.columns:
            col_lower = self._normalizar_nombre_columna(col)
            # Verificar si la columna contiene alguna palabra clave
            if any(palabra in col_lower for palabra in self.PALABRAS_CLAVE_PROPAGACION):
                columnas_propagables.append(col)
        
        # Para cada columna propagable, usar ffill de pandas para propagar valores
        for col in columnas_propagables:
            # Convertir strings vacíos a NaN para que ffill funcione correctamente
            self.df[col] = self.df[col].apply(
                lambda x: pd.NA if self._es_valor_vacio(x) else x
            )
            # Usar ffill (forward fill) para propagar valores hacia abajo
            self.df[col] = self.df[col].ffill()

    def _limpiar_columnas_no_utiles(self):
        """Elimina columnas que no aportan al proceso"""
        if self.df is None:
            return
        
        columnas_utiles = []
        for col in self.df.columns:
            nombre_normalizado = self._normalizar_nombre_columna(col)
            if nombre_normalizado in self.COLUMNAS_NO_UTILIZADAS:
                continue
            columnas_utiles.append(col)
        
        self.df = self.df[columnas_utiles]

    def _normalizar_nombre_columna(self, nombre: Any) -> str:
        """Normaliza nombres de columnas para comparaciones"""
        if nombre is None:
            return ''
        texto = str(nombre).strip().lower()
        texto = unicodedata.normalize('NFKD', texto)
        texto = ''.join(c for c in texto if not unicodedata.combining(c))
        texto = texto.replace(' ', '_')
        texto = re.sub(r'[^a-z0-9_]', '', texto)
        return texto

    def _es_valor_vacio(self, valor: Any) -> bool:
        """Determina si un valor debe considerarse vacío"""
        if pd.isna(valor) or valor is None:
            return True
        if isinstance(valor, str):
            texto = valor.strip().lower()
            return texto in self.VALORES_VACIOS
        return False

    def _normalizar_identificacion(self, valor: Any) -> str:
        """Normaliza RUC/Cédula a un formato de 10 dígitos cuando sea posible"""
        if valor is None or (isinstance(valor, str) and self._es_valor_vacio(valor)):
            return ''
        texto = ''.join(ch for ch in str(valor) if ch.isdigit())
        if len(texto) == 13 and texto.endswith('001'):
            return texto[:10]
        if len(texto) >= 10:
            return texto[:10]
        return texto if len(texto) == 10 else ''

    def _aplicar_actualizaciones(self, df_procesar: pd.DataFrame, actualizaciones: List[Dict[str, Any]]):
        """Aplica modificaciones manuales realizadas en el frontend"""
        if not actualizaciones:
            return df_procesar
        
        df_editable = df_procesar.copy()
        for actualizacion in actualizaciones:
            indice = actualizacion.get('indice')
            valores = actualizacion.get('valores', {})
            if indice not in df_editable.index:
                continue
            for columna, valor in valores.items():
                if columna in df_editable.columns:
                    df_editable.at[indice, columna] = valor
        return df_editable
    
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
                
                elif campo_modelo == 'consignatario_nombre':
                    # Solo validar si está mapeado (si no está mapeado, se usará comprador_id)
                    if self._es_valor_vacio(valor):
                        errores_fila.append({
                            'fila': int(idx) + 2,
                            'columna': col_excel,
                            'error': 'El consignatario es obligatorio'
                        })
                
                elif campo_modelo == 'consignatario_identificacion':
                    # Solo validar si está mapeado (si no está mapeado, se usará comprador_id)
                    # No normalizar aquí, validar el valor original
                    texto_identificacion = ''.join(ch for ch in str(valor) if ch.isdigit()) if valor else ''
                    if not texto_identificacion:
                        errores_fila.append({
                            'fila': int(idx) + 2,
                            'columna': col_excel,
                            'error': 'El RUC/Cédula del consignatario es obligatorio'
                        })
                    else:
                        try:
                            # Validar tanto cédula como RUC (modo flexible para importación)
                            validar_cedula_o_ruc(texto_identificacion, estricto=False)
                        except ValidationError as exc:
                            # Formatear el mensaje de error correctamente
                            mensaje_error = str(exc)
                            if isinstance(exc.messages, list) and len(exc.messages) > 0:
                                mensaje_error = exc.messages[0] if isinstance(exc.messages[0], str) else str(exc.messages[0])
                            errores_fila.append({
                                'fila': int(idx) + 2,
                                'columna': col_excel,
                                'error': mensaje_error
                            })
                
                elif campo_modelo == 'fecha_emision':
                    _, error = ValidadorDatos.validar_fecha(valor, 'Fecha de emisión')
                    if error:
                        errores_fila.append({
                            'fila': int(idx) + 2,
                            'columna': col_excel,
                            'error': error
                        })
            
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
        comprador_id: int = None,
        actualizaciones: List[Dict[str, Any]] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Procesa e importa los datos a la base de datos
        
        Args:
            importacion: Instancia de ImportacionExcel
            mapeo_columnas: Mapeo entre columnas del Excel y campos del modelo
            indices_seleccionados: Lista de índices a importar (None = todos)
            comprador_id: ID del comprador para asignar a los envíos
            actualizaciones: Cambios manuales aplicados desde el frontend
        
        Returns:
            Tuple (éxito, mensaje, extras)
        """
        if self.df is None:
            return False, "No hay datos cargados", {}
        
        self.nuevos_compradores = []
        
        # Determinar qué filas procesar
        if indices_seleccionados:
            df_procesar = self.df.iloc[indices_seleccionados]
        else:
            df_procesar = self.df
        
        df_procesar = self._aplicar_actualizaciones(df_procesar, actualizaciones)
        
        importacion.estado = 'procesando'
        importacion.total_registros = len(df_procesar)
        importacion.save()
        
        registros_exitosos = 0
        registros_con_error = 0
        
        envios_creados = []  # Lista para almacenar envíos creados para generar embeddings después
        
        try:
            with transaction.atomic():
                # Agrupar filas por HAWB del archivo (aunque luego se ignore y se genere uno nuevo)
                # Esto permite que múltiples productos pertenezcan al mismo envío
                grupos_por_hawb = self._agrupar_filas_por_hawb(df_procesar, mapeo_columnas)
                
                # Procesar cada grupo (cada grupo representa un envío con uno o más productos)
                for hawb_archivo, filas_grupo in grupos_por_hawb.items():
                    try:
                        # Crear un solo envío para todo el grupo
                        envio = self._crear_envio_desde_grupo(
                            filas_grupo, 
                            mapeo_columnas, 
                            comprador_id,
                            generar_embedding=False
                        )
                        envios_creados.append(envio)
                        
                        # Contar todas las filas del grupo como exitosas
                        registros_exitosos += len(filas_grupo)
                        
                    except Exception as e:
                        # Si falla el grupo, marcar todas sus filas como error
                        registros_con_error += len(filas_grupo)
                        for fila_info in filas_grupo:
                            importacion.agregar_error(
                                int(fila_info['indice']) + 2,
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
            
            # Generar embeddings de forma asíncrona para todos los envíos creados
            # Esto se hace fuera de la transacción para no bloquear
            if envios_creados:
                print(f"✅ Se crearon {len(envios_creados)} envíos exitosamente.")
                print(f"🔄 Generando embeddings de forma asíncrona...")
                # Generar embeddings en un thread separado para no bloquear
                import threading
                from apps.busqueda.services import BusquedaSemanticaService
                
                def generar_embeddings_async():
                    import logging
                    import traceback
                    logger = logging.getLogger(__name__)
                    
                    exitosos = 0
                    errores = 0
                    total = len(envios_creados)
                    
                    logger.info(f"Iniciando generación de embeddings para {total} envíos...")
                    print(f"🔄 Generando embeddings para {total} envíos...")
                    
                    for i, envio in enumerate(envios_creados, 1):
                        try:
                            logger.debug(f"Generando embedding {i}/{total} para envío {envio.hawb} (ID: {envio.id})")
                            embedding = BusquedaSemanticaService.generar_embedding_envio(envio)
                            
                            if embedding:
                                exitosos += 1
                                logger.debug(f"✅ Embedding generado para envío {envio.hawb}")
                            else:
                                # Puede que ya exista, no es un error
                                exitosos += 1
                                logger.debug(f"⚠️ Embedding ya existía para envío {envio.hawb}")
                            
                            # Mostrar progreso cada 10 envíos
                            if i % 10 == 0 or i == total:
                                mensaje = f"   Progreso embeddings: {i}/{total} ({exitosos} exitosos, {errores} errores)"
                                print(mensaje)
                                logger.info(mensaje)
                        except Exception as e:
                            errores += 1
                            error_trace = traceback.format_exc()
                            mensaje_error = f"⚠️ Error generando embedding para envío {envio.hawb} (ID: {envio.id}): {str(e)}"
                            print(mensaje_error)
                            logger.error(
                                f"{mensaje_error}\n{error_trace}",
                                exc_info=True
                            )
                    
                    mensaje_final = f"✅ Embeddings generados: {exitosos} exitosos, {errores} errores"
                    print(mensaje_final)
                    logger.info(mensaje_final)
                
                threading.Thread(target=generar_embeddings_async, daemon=True).start()
            
            extras = {
                'compradores_pendientes': self.nuevos_compradores
            }
            return True, importacion.mensaje_resultado, extras
            
        except Exception as e:
            importacion.estado = 'error'
            importacion.mensaje_resultado = f"❌ Error en la importación: {str(e)}"
            importacion.save()
            extras = {
                'compradores_pendientes': self.nuevos_compradores
            }
            return False, importacion.mensaje_resultado, extras
    
    def _extraer_datos_fila(
        self, 
        row, 
        mapeo_columnas: Dict[str, str],
        comprador_id: int = None
    ) -> Dict[str, Any]:
        """Extrae y valida los datos de una fila"""
        datos = {}
        
        # Mapeo inverso para facilitar búsqueda
        mapeo_inv = {v: k for k, v in mapeo_columnas.items()}
        
        # HAWB: Se ignora el HAWB del archivo Excel
        # El HAWB se generará automáticamente en _crear_envio() usando _generar_hawb_secuencial()
        # No se requiere HAWB del archivo, siempre se genera desde el sistema
        
        # Comprador (desde selección manual o desde consignatario)
        if comprador_id:
            datos['comprador_id'] = comprador_id
        else:
            datos['comprador'] = self._resolver_comprador_desde_excel(row, mapeo_inv)
        
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
        
        if 'fecha_emision' in mapeo_inv:
            fecha_valor = row[mapeo_inv['fecha_emision']]
            fecha, error = ValidadorDatos.validar_fecha(fecha_valor, 'Fecha de emisión')
            if error:
                raise ValueError(error)
            datos['fecha_emision'] = self._formatear_fecha(fecha)
        
        # Datos del producto (si existen)
        producto = {}
        if 'descripcion' in mapeo_inv:
            producto['descripcion'] = ValidadorDatos.limpiar_texto(row[mapeo_inv['descripcion']])
        
        # Obtener cantidad del producto
        cantidad_producto = 0
        if 'cantidad' in mapeo_inv:
            cantidad, _ = ValidadorDatos.validar_entero(row[mapeo_inv['cantidad']])
            cantidad_producto = cantidad if cantidad is not None else 0
            producto['cantidad'] = cantidad_producto
        
        # Obtener peso del producto
        if 'peso' in mapeo_inv:
            peso, _ = ValidadorDatos.validar_numero(row[mapeo_inv['peso']])
            producto['peso'] = Decimal(str(peso)) if peso is not None else Decimal('0')
        elif 'peso_total' in mapeo_inv and cantidad_producto > 0:
            # Si no hay peso del producto pero sí peso_total y cantidad, calcular peso unitario
            peso_total = datos.get('peso_total', Decimal('0'))
            if peso_total > 0:
                producto['peso'] = peso_total / Decimal(str(cantidad_producto))
            else:
                producto['peso'] = Decimal('0')
        
        # Obtener valor del producto
        if 'valor' in mapeo_inv:
            valor, _ = ValidadorDatos.validar_numero(row[mapeo_inv['valor']])
            producto['valor'] = Decimal(str(valor)) if valor is not None else Decimal('0')
        elif 'valor_total' in mapeo_inv and cantidad_producto > 0:
            # Si no hay valor del producto pero sí valor_total y cantidad, calcular valor unitario
            valor_total = datos.get('valor_total', Decimal('0'))
            if valor_total > 0:
                producto['valor'] = valor_total / Decimal(str(cantidad_producto))
            else:
                producto['valor'] = Decimal('0')
        
        if 'categoria' in mapeo_inv:
            categoria, _ = ValidadorDatos.validar_categoria(row[mapeo_inv['categoria']])
            producto['categoria'] = categoria
        else:
            producto['categoria'] = 'otros'
        
        if producto:
            datos['producto'] = producto
        
        return datos
    
    def _resolver_comprador_desde_excel(self, row, mapeo_inv: Dict[str, str]) -> Usuario:
        """Obtiene o crea el comprador usando los datos del consignatario"""
        nombre_col = mapeo_inv.get('consignatario_nombre')
        identificacion_col = mapeo_inv.get('consignatario_identificacion')
        
        if not nombre_col or not identificacion_col:
            raise ValueError("Debe mapear las columnas de consignatario y RUC/Cédula para continuar")
        
        nombre = ValidadorDatos.limpiar_texto(row[nombre_col])
        # Extraer solo dígitos de la identificación
        texto_identificacion = ''.join(ch for ch in str(row[identificacion_col]) if ch.isdigit()) if row[identificacion_col] else ''
        
        if not texto_identificacion:
            raise ValueError("El RUC/Cédula del consignatario es obligatorio")
        
        try:
            # Validar tanto cédula como RUC (modo flexible para importación)
            validar_cedula_o_ruc(texto_identificacion, estricto=False)
        except ValidationError as exc:
            # Formatear el mensaje de error correctamente
            mensaje_error = str(exc)
            if hasattr(exc, 'messages') and isinstance(exc.messages, list) and len(exc.messages) > 0:
                mensaje_error = exc.messages[0] if isinstance(exc.messages[0], str) else str(exc.messages[0])
            raise ValueError(f"Identificación inválida del consignatario: {mensaje_error}")
        
        # Normalizar para almacenar: si es RUC de 13 dígitos terminado en 001, usar solo los primeros 10
        identificacion_normalizada = texto_identificacion[:10] if len(texto_identificacion) == 13 and texto_identificacion.endswith('001') else texto_identificacion
        
        return self._obtener_o_crear_comprador(nombre, identificacion_normalizada)
    
    def _obtener_o_crear_comprador(self, nombre: str, identificacion: str) -> Usuario:
        """Busca o crea un comprador usando los datos normalizados"""
        defaults = {
            'username': self._generar_username(identificacion),
            'nombre': nombre or f"Consignatario {identificacion}",
            'correo': None,
            'rol': 4,
            'es_activo': True
        }
        comprador, creado = Usuario.objects.get_or_create(
            cedula=identificacion,
            defaults=defaults
        )
        
        if creado:
            # Generar contraseña aleatoria usando get_user_model() o secrets
            import secrets
            password = secrets.token_urlsafe(12)  # Genera contraseña segura de 12 caracteres
            comprador.set_password(password)
            comprador.save()
            self._registrar_comprador_creado(comprador)
        else:
            if nombre and not comprador.nombre:
                comprador.nombre = nombre
                comprador.save(update_fields=['nombre'])
        
        return comprador
    
    def _generar_username(self, identificacion: str) -> str:
        """Genera un username único basado en la identificación"""
        base = f"consignatario_{identificacion}"
        username = base
        contador = 1
        while Usuario.objects.filter(username=username).exists():
            username = f"{base}_{contador}"
            contador += 1
        return username
    
    def _registrar_comprador_creado(self, comprador: Usuario):
        """Guarda información de compradores creados para completar datos luego"""
        self.nuevos_compradores.append({
            'id': comprador.id,
            'username': comprador.username,
            'nombre': comprador.nombre,
            'cedula': comprador.cedula,
            'correo': comprador.correo,
            'telefono': comprador.telefono,
            'direccion': comprador.direccion
        })
    
    def _formatear_fecha(self, fecha: datetime):
        """Se asegura de retornar fechas conscientes de zona horaria"""
        if fecha is None:
            return None
        if timezone.is_naive(fecha):
            return timezone.make_aware(fecha, timezone.get_current_timezone())
        return fecha
    
    def _agrupar_filas_por_hawb(
        self, 
        df: pd.DataFrame, 
        mapeo_columnas: Dict[str, str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Agrupa las filas del DataFrame por HAWB del archivo.
        Las filas con el mismo HAWB pertenecen al mismo envío.
        
        Args:
            df: DataFrame con las filas a procesar
            mapeo_columnas: Mapeo entre columnas del Excel y campos del modelo
        
        Returns:
            Dict con formato {hawb_archivo: [lista de filas]}
        """
        grupos = {}
        mapeo_inv = {v: k for k, v in mapeo_columnas.items()}
        
        # Obtener la columna de HAWB del archivo (si existe)
        columna_hawb = mapeo_inv.get('hawb')
        
        for idx, row in df.iterrows():
            # Obtener el HAWB del archivo para agrupar
            # Si no hay HAWB mapeado o está vacío, cada fila será un grupo único
            hawb_archivo = ''
            if columna_hawb and columna_hawb in df.columns:
                valor_hawb = row[columna_hawb]
                if not pd.isna(valor_hawb) and str(valor_hawb).strip():
                    hawb_archivo = str(valor_hawb).strip()
            
            # Si no hay HAWB, usar el índice como clave única para que cada fila sea un grupo
            if not hawb_archivo:
                hawb_archivo = f"_sin_hawb_{idx}"
            
            # Agregar la fila al grupo correspondiente
            if hawb_archivo not in grupos:
                grupos[hawb_archivo] = []
            
            grupos[hawb_archivo].append({
                'indice': idx,
                'fila': row
            })
        
        return grupos
    
    def _crear_envio_desde_grupo(
        self,
        filas_grupo: List[Dict[str, Any]],
        mapeo_columnas: Dict[str, str],
        comprador_id: int = None,
        generar_embedding: bool = True
    ) -> Envio:
        """
        Crea un envío desde un grupo de filas (todas con el mismo HAWB del archivo).
        Todos los productos de las filas se agregan al mismo envío.
        
        Args:
            filas_grupo: Lista de diccionarios con formato {'indice': idx, 'fila': row}
            mapeo_columnas: Mapeo entre columnas del Excel y campos del modelo
            comprador_id: ID del comprador para asignar al envío
            generar_embedding: Si True, genera el embedding inmediatamente
        
        Returns:
            Envio creado
        """
        if not filas_grupo:
            raise ValueError("El grupo de filas está vacío")
        
        # Usar la primera fila para obtener los datos base del envío
        primera_fila = filas_grupo[0]['fila']
        datos_envio = self._extraer_datos_fila(primera_fila, mapeo_columnas, comprador_id)
        
        # Extraer todos los productos de todas las filas del grupo
        productos_datos = []
        
        # Si la primera fila ya tiene un producto, agregarlo
        if 'producto' in datos_envio and datos_envio['producto']:
            productos_datos.append(datos_envio.pop('producto'))
        
        # Procesar las demás filas del grupo para obtener sus productos
        for fila_info in filas_grupo[1:]:
            fila = fila_info['fila']
            datos_fila = self._extraer_datos_fila(fila, mapeo_columnas, comprador_id)
            
            # Agregar el producto de esta fila
            if 'producto' in datos_fila and datos_fila['producto']:
                productos_datos.append(datos_fila['producto'])
        
        # Calcular totales del envío sumando todos los productos
        if len(productos_datos) > 0:
            # Calcular totales sumando todos los productos
            peso_total_calculado = sum(Decimal(str(p.get('peso', 0))) * Decimal(str(p.get('cantidad', 0))) for p in productos_datos)
            cantidad_total_calculada = sum(p.get('cantidad', 0) for p in productos_datos)
            valor_total_calculado = sum(Decimal(str(p.get('valor', 0))) * Decimal(str(p.get('cantidad', 0))) for p in productos_datos)
            
            # Usar los valores calculados desde los productos
            datos_envio['peso_total'] = peso_total_calculado
            datos_envio['cantidad_total'] = cantidad_total_calculada
            datos_envio['valor_total'] = valor_total_calculado
        else:
            # Si no hay productos, usar los valores de la primera fila
            datos_envio.setdefault('peso_total', Decimal('0'))
            datos_envio.setdefault('cantidad_total', 0)
            datos_envio.setdefault('valor_total', Decimal('0'))
        
        # Crear el envío base (sin productos aún)
        envio = self._crear_envio_base(datos_envio, generar_embedding=False)
        
        # Agregar todos los productos al envío
        for producto_datos in productos_datos:
            if producto_datos.get('descripcion'):
                Producto.objects.create(envio=envio, **producto_datos)
        
        # Recalcular totales del envío con todos los productos
        envio.calcular_totales()
        envio.save()
        
        # Generar embedding solo si se solicita
        if generar_embedding:
            try:
                generar_embedding_envio(envio)
            except Exception as e_embed:
                print(f"Advertencia: No se pudo generar embedding para envío {envio.hawb}: {str(e_embed)}")
        
        return envio
    
    def _crear_envio_base(self, datos: Dict[str, Any], generar_embedding: bool = True) -> Envio:
        """
        Crea un envío base sin productos (los productos se agregan después).
        Similar a _crear_envio pero sin manejar productos.
        """
        # Ajustar el nombre del campo comprador_id a comprador
        if 'comprador_id' in datos and 'comprador' not in datos:
            comprador_id = datos.pop('comprador_id')
            if comprador_id:
                try:
                    comprador = Usuario.objects.get(id=comprador_id)
                    # Validar que el usuario tenga rol de comprador (rol=4)
                    if comprador.rol != 4:
                        raise ValueError(f"El usuario con ID {comprador_id} no tiene rol de Comprador (rol=4). Rol actual: {comprador.rol}")
                    datos['comprador'] = comprador
                except Usuario.DoesNotExist:
                    raise ValueError(f"Comprador con ID {comprador_id} no existe")
        else:
            datos.pop('comprador_id', None)
        
        if 'comprador' not in datos or not datos['comprador']:
            raise ValueError("No se pudo determinar el comprador para el envío")
        
        # Validar que el comprador tenga rol correcto
        if hasattr(datos.get('comprador'), 'rol') and datos['comprador'].rol != 4:
            raise ValueError(f"El comprador debe tener rol de Comprador (rol=4). Rol actual: {datos['comprador'].rol}")
        
        # IMPORTANTE: Generar HAWB secuencial basado en la base de datos
        # Ignorar el HAWB del archivo y usar el próximo número en secuencia
        datos['hawb'] = self._generar_hawb_secuencial()
        
        # Asegurar que los campos opcionales tengan valores por defecto
        datos.setdefault('peso_total', 0)
        datos.setdefault('cantidad_total', 0)
        datos.setdefault('valor_total', 0)
        datos.setdefault('costo_servicio', 0)
        datos.setdefault('estado', 'pendiente')
        
        # Remover costo_extra si existe (no es parte del modelo)
        datos.pop('costo_extra', None)
        # Remover producto si existe (se agregará después)
        datos.pop('producto', None)
        
        # Crear el envío
        envio = Envio.objects.create(**datos)
        
        # Crear notificación cuando se asigna un envío a un comprador
        if envio.comprador and envio.comprador.es_comprador:
            crear_notificacion_envio_asignado(envio)
        
        return envio
    
    def _crear_envio(self, datos: Dict[str, Any], generar_embedding: bool = True) -> Envio:
        """
        Crea un envío con los datos proporcionados
        
        Args:
            datos: Diccionario con los datos del envío
            generar_embedding: Si True, genera el embedding inmediatamente (lento para importaciones masivas)
        """
        # Extraer datos del producto si existe
        producto_datos = datos.pop('producto', None)
        
        # Ajustar el nombre del campo comprador_id a comprador
        if 'comprador_id' in datos and 'comprador' not in datos:
            comprador_id = datos.pop('comprador_id')
            if comprador_id:
                try:
                    comprador = Usuario.objects.get(id=comprador_id)
                    # Validar que el usuario tenga rol de comprador (rol=4)
                    if comprador.rol != 4:
                        raise ValueError(f"El usuario con ID {comprador_id} no tiene rol de Comprador (rol=4). Rol actual: {comprador.rol}")
                    datos['comprador'] = comprador
                except Usuario.DoesNotExist:
                    raise ValueError(f"Comprador con ID {comprador_id} no existe")
        else:
            datos.pop('comprador_id', None)
        
        if 'comprador' not in datos or not datos['comprador']:
            raise ValueError("No se pudo determinar el comprador para el envío")
        
        # Validar que el comprador tenga rol correcto
        if hasattr(datos.get('comprador'), 'rol') and datos['comprador'].rol != 4:
            raise ValueError(f"El comprador debe tener rol de Comprador (rol=4). Rol actual: {datos['comprador'].rol}")
        
        # IMPORTANTE: Generar HAWB secuencial basado en la base de datos
        # Ignorar el HAWB del archivo y usar el próximo número en secuencia
        datos['hawb'] = self._generar_hawb_secuencial()
        
        # Asegurar que los campos opcionales tengan valores por defecto
        datos.setdefault('peso_total', 0)
        datos.setdefault('cantidad_total', 0)
        datos.setdefault('valor_total', 0)
        datos.setdefault('costo_servicio', 0)
        datos.setdefault('estado', 'pendiente')
        
        # Remover costo_extra si existe (no es parte del modelo)
        datos.pop('costo_extra', None)
        
        # Crear el envío
        envio = Envio.objects.create(**datos)
        
        # Crear el producto asociado si existe
        if producto_datos and producto_datos.get('descripcion'):
            Producto.objects.create(envio=envio, **producto_datos)
            # Recalcular totales
            envio.calcular_totales()
        
        # Crear notificación cuando se asigna un envío a un comprador
        if envio.comprador and envio.comprador.es_comprador:
            crear_notificacion_envio_asignado(envio)
        
        # Generar embedding solo si se solicita (evitar en importaciones masivas)
        if generar_embedding:
            try:
                generar_embedding_envio(envio)
            except Exception as e_embed:
                # No fallar la importación si falla el embedding
                print(f"Advertencia: No se pudo generar embedding para envío {envio.hawb}: {str(e_embed)}")
        
        return envio
    
    def _generar_embeddings_batch(self, envios: List[Envio]):
        """
        Genera embeddings para múltiples envíos de forma más eficiente.
        Esto es más rápido que generar uno por uno porque permite mejor manejo de errores
        y no bloquea el proceso principal.
        """
        from apps.busqueda.utils_embeddings import generar_embedding_envio
        
        total = len(envios)
        exitosos = 0
        errores = 0
        
        print(f"Generando embeddings para {total} envíos...")
        
        for i, envio in enumerate(envios, 1):
            try:
                generar_embedding_envio(envio)
                exitosos += 1
                
                # Mostrar progreso cada 10 envíos
                if i % 10 == 0:
                    print(f"Progreso embeddings: {i}/{total} ({exitosos} exitosos, {errores} errores)")
                    
            except Exception as e:
                errores += 1
                print(f"Error generando embedding para envío {envio.hawb}: {str(e)}")
                # Continuar con el siguiente envío
                continue
        
        print(f"✅ Embeddings generados: {exitosos} exitosos, {errores} errores de {total} total")
    
    def _generar_hawb_secuencial(self) -> str:
        """Genera el próximo HAWB en secuencia basado en la base de datos"""
        from django.db.models import Max
        import re
        
        # Obtener el último HAWB de la base de datos
        ultimo_envio = Envio.objects.all().aggregate(Max('hawb'))
        ultimo_hawb = ultimo_envio['hawb__max']
        
        if not ultimo_hawb:
            # Si no hay envíos, empezar desde HAWB00001
            return 'HAWB00001'
        
        # Extraer el número del HAWB (asumiendo formato HAWBXXXXX)
        match = re.search(r'(\d+)$', ultimo_hawb)
        if match:
            numero = int(match.group(1))
            nuevo_numero = numero + 1
            # Mantener el mismo formato (rellenar con ceros a la izquierda)
            longitud = len(match.group(1))
            prefijo = ultimo_hawb[:match.start()]
            return f"{prefijo}{str(nuevo_numero).zfill(longitud)}"
        else:
            # Si no se puede extraer número, generar uno nuevo
            return f"HAWB{str(Envio.objects.count() + 1).zfill(5)}"


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



















