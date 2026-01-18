"""
Comando de gestión para evaluar el desempeño de módulos clave del sistema vía HTTP real.

Evalúa 14 operaciones del sistema midiendo:
- Tiempo de respuesta (promedio y máximo) y su categoría según Nielsen (1993)
- Uso promedio de CPU (%)
- Uso promedio de RAM (MB)

Los resultados se:
- Muestran por consola en forma de tabla/resumen
- Guardan en BD usando PruebaRendimientoCompleta.resultados_json
- Pueden exportarse a un archivo JSON con --exportar

IMPORTANTE:
- Este comando asume que existe una API HTTP accesible en --base-url
- Para endpoints protegidos, se puede pasar un token de autenticación con --token
  (se envía en el header Authorization: Bearer <token>)
- Los paths de cada operación deben ajustarse a la API real del proyecto.
"""

import time
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple

import psutil
import requests
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.metricas.models import PruebaRendimientoCompleta
from apps.metricas.services import MetricaRendimientoService


Usuario = get_user_model()


class Command(BaseCommand):
    help = "Pruebas de desempeño por módulo del sistema vía HTTP (14 operaciones clave)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--base-url",
            type=str,
            required=True,
            help="URL base de la API (por ejemplo: http://localhost:8000)",
        )
        parser.add_argument(
            "--token",
            type=str,
            default=None,
            help="Token para Authorization Bearer (opcional)",
        )
        parser.add_argument(
            "--iteraciones",
            type=int,
            default=30,
            help="Cantidad de iteraciones por operación (default: 30). "
                 "Si solo quieres 1 caso puntual, usar --iteraciones 1.",
        )
        parser.add_argument(
            "--exportar",
            action="store_true",
            help="Exportar resultados a archivo JSON",
        )

    # -------------------------------------------------------------------------
    # MÉTODOS PRINCIPALES
    # -------------------------------------------------------------------------

    def handle(self, *args, **options):
        base_url: str = options["base_url"].rstrip("/")
        token: str | None = options["token"]
        iteraciones: int = max(1, options["iteraciones"])
        exportar: bool = options["exportar"]

        usuario = Usuario.objects.filter(is_superuser=True).first() or Usuario.objects.first()
        if not usuario:
            self.stdout.write(self.style.ERROR("No hay usuarios en el sistema. Crea un usuario primero."))
            return

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 80))
        self.stdout.write(self.style.SUCCESS("PRUEBAS DE DESEMPEÑO POR MÓDULOS (HTTP REAL)"))
        self.stdout.write(self.style.SUCCESS("=" * 80 + "\n"))
        self.stdout.write(f"Usuario (referencia en BD): {usuario.username}")
        self.stdout.write(f"Base URL: {base_url}")
        self.stdout.write(f"Iteraciones por operación: {iteraciones}")
        self.stdout.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        session = requests.Session()
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        operaciones = self._definir_operaciones(base_url)
        resultados: Dict[str, Any] = {
            "config": {
                "base_url": base_url,
                "iteraciones": iteraciones,
                "fecha": datetime.now().isoformat(),
            },
            "operaciones": {},
            "resumen_global": {},
        }

        for codigo, config in operaciones.items():
            self.stdout.write(self.style.WARNING(f"\n▶ Ejecutando operación: {config['nombre']}"))
            try:
                datos_op = self._ejecutar_operacion(
                    session=session,
                    headers=headers,
                    metodo=config["metodo"],
                    url=config["url"],
                    payload=config.get("payload"),
                    iteraciones=iteraciones,
                    nombre_humano=config["nombre"],
                )
                resultados["operaciones"][codigo] = datos_op
                self._imprimir_resumen_operacion(codigo, config["nombre"], datos_op)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error ejecutando la operación: {str(e)}"))
                resultados["operaciones"][codigo] = {
                    "error": str(e),
                    "exitosas": 0,
                    "fallidas": iteraciones,
                }

        # Resumen global
        resultados["resumen_global"] = self._calcular_resumen_global(resultados["operaciones"])
        self._imprimir_resumen_global(resultados["resumen_global"])

        # Guardar en BD
        try:
            self._guardar_resultados_bd(resultados, usuario)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\nError guardando resultados en BD: {str(e)}"))

        # Exportar a JSON
        if exportar:
            try:
                self._exportar_resultados(resultados)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"\nError exportando resultados: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("\nPruebas de desempeño por módulos finalizadas.\n"))

    # -------------------------------------------------------------------------
    # DEFINICIÓN DE OPERACIONES
    # -------------------------------------------------------------------------

    def _definir_operaciones(self, base_url: str) -> Dict[str, Dict[str, Any]]:
        """
        Define las 14 operaciones a medir.

        IMPORTANTE: Ajustar los paths y métodos a los endpoints reales del proyecto.
        Aquí se colocan ejemplos típicos de una API REST que deben revisarse.
        """
        def url(path: str) -> str:
            return f"{base_url}{path}"

        return {
            # Autenticación / usuarios
            "ingresar_usuario": {
                "nombre": "Ingresar usuario (login)",
                "metodo": "POST",
                "url": url("/api/auth/login/"),  # TODO: ajustar al endpoint real
                "payload": {"username": "admin", "password": "admin"},  # TODO: credenciales válidas
            },
            "registrar_nuevo_usuario": {
                "nombre": "Registrar nuevo usuario",
                "metodo": "POST",
                "url": url("/api/usuarios/"),  # TODO
                "payload": {
                    "username": "usuario_test_performance",
                    "password": "Test1234!",
                    "email": "perf@example.com",
                },
            },
            "restablecer_contrasena": {
                "nombre": "Restablecer contraseña",
                "metodo": "POST",
                "url": url("/api/auth/password/reset/"),  # TODO
                "payload": {"email": "perf@example.com"},
            },
            "crear_nuevo_usuario": {
                "nombre": "Crear nuevo usuario (admin)",
                "metodo": "POST",
                "url": url("/api/admin/usuarios/"),  # TODO
                "payload": {
                    "username": "usuario_admin_perf",
                    "password": "Test1234!",
                    "email": "admin_perf@example.com",
                },
            },
            "listar_usuarios": {
                "nombre": "Listar usuarios",
                "metodo": "GET",
                "url": url("/api/usuarios/"),  # TODO
            },
            "modificar_perfil": {
                "nombre": "Modificar perfil",
                "metodo": "PATCH",
                "url": url("/api/usuarios/me/"),  # TODO
                "payload": {"first_name": "Usuario", "last_name": "PerfilPerf"},
            },
            # Envíos y productos
            "crear_nuevo_envio": {
                "nombre": "Crear nuevo envío",
                "metodo": "POST",
                "url": url("/api/envios/"),  # TODO
                "payload": {
                    "hawb": "PERF-ENVIO-TEST",
                    "estado": "pendiente",
                    "productos": [
                        {
                            "descripcion": "Producto prueba perf",
                            "categoria": "general",
                            "peso": 1.5,
                            "cantidad": 1,
                            "valor": 100.0,
                        }
                    ],
                },
            },
            "modificar_envio": {
                "nombre": "Modificar envío",
                "metodo": "PATCH",
                "url": url("/api/envios/1/"),  # TODO: usar un ID de envío válido
                "payload": {"estado": "procesado"},
            },
            "crear_producto": {
                "nombre": "Crear producto",
                "metodo": "POST",
                "url": url("/api/productos/"),  # TODO
                "payload": {
                    "nombre": "Producto Perf",
                    "categoria": "general",
                    "precio": 10.0,
                },
            },
            "crear_tarifa": {
                "nombre": "Crear tarifa",
                "metodo": "POST",
                "url": url("/api/tarifas/"),  # TODO
                "payload": {
                    "nombre": "Tarifa Perf",
                    "precio": 5.0,
                    "activo": True,
                },
            },
            "importar_envios": {
                "nombre": "Importar envíos",
                "metodo": "POST",
                "url": url("/api/envios/importar/"),  # TODO
                "payload": {"archivo_id": 1},  # Ejemplo: referencia a archivo ya cargado
            },
            "exportar_envios": {
                "nombre": "Exportar envíos",
                "metodo": "GET",
                "url": url("/api/envios/exportar/"),  # TODO
            },
            "buscar_envios": {
                "nombre": "Buscar envíos (búsqueda básica)",
                "metodo": "GET",
                "url": url("/api/envios/?q=perf"),  # TODO
            },
            "buscar_semantica": {
                "nombre": "Buscar semánticamente",
                "metodo": "GET",
                "url": url("/api/busqueda/semantica/?q=perf"),  # TODO
            },
        }

    # -------------------------------------------------------------------------
    # EJECUCIÓN Y MEDICIÓN
    # -------------------------------------------------------------------------

    def _ejecutar_operacion(
        self,
        session: requests.Session,
        headers: Dict[str, str],
        metodo: str,
        url: str,
        payload: Any | None,
        iteraciones: int,
        nombre_humano: str,
    ) -> Dict[str, Any]:
        tiempos: List[float] = []
        cpu_muestras: List[float] = []
        ram_muestras: List[float] = []
        exitosas = 0
        fallidas = 0
        errores: List[Dict[str, Any]] = []

        for i in range(iteraciones):
            inicio = time.perf_counter()
            try:
                if metodo.upper() == "GET":
                    resp = session.get(url, headers=headers, timeout=30)
                elif metodo.upper() == "POST":
                    resp = session.post(url, headers=headers, data=json.dumps(payload or {}), timeout=30)
                elif metodo.upper() == "PATCH":
                    resp = session.patch(url, headers=headers, data=json.dumps(payload or {}), timeout=30)
                elif metodo.upper() == "PUT":
                    resp = session.put(url, headers=headers, data=json.dumps(payload or {}), timeout=30)
                elif metodo.upper() == "DELETE":
                    resp = session.delete(url, headers=headers, timeout=30)
                else:
                    raise ValueError(f"Método HTTP no soportado: {metodo}")
                fin = time.perf_counter()

                dur_ms = (fin - inicio) * 1000.0
                tiempos.append(dur_ms)

                # Medir recursos inmediatamente después de la operación.
                # Usamos métricas de TODO el sistema (no solo del proceso de este comando)
                # para capturar el efecto del servidor que atiende las peticiones HTTP.
                cpu_total = psutil.cpu_percent(interval=0.1)
                ram_total_mb = psutil.virtual_memory().used / (1024 * 1024)
                cpu_muestras.append(cpu_total)
                ram_muestras.append(ram_total_mb)

                if 200 <= resp.status_code < 300:
                    exitosas += 1
                else:
                    fallidas += 1
                    cuerpo = ""
                    try:
                        cuerpo = resp.text[:200]
                    except Exception:
                        cuerpo = "<sin cuerpo legible>"
                    errores.append(
                        {
                            "iteracion": i + 1,
                            "status_code": resp.status_code,
                            "url": url,
                            "respuesta": cuerpo,
                        }
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Iteración {i+1}: HTTP {resp.status_code} en {nombre_humano} "
                            f"URL={url}"
                        )
                    )
            except Exception as e:
                fin = time.perf_counter()
                dur_ms = (fin - inicio) * 1000.0
                tiempos.append(dur_ms)
                fallidas += 1
                errores.append(
                    {
                        "iteracion": i + 1,
                        "error": str(e),
                        "url": url,
                    }
                )
                self.stdout.write(self.style.ERROR(f"  Iteración {i+1}: error {str(e)}"))

        if tiempos:
            promedio_ms = sum(tiempos) / len(tiempos)
            max_ms = max(tiempos)
        else:
            promedio_ms = 0.0
            max_ms = 0.0

        cpu_promedio = sum(cpu_muestras) / len(cpu_muestras) if cpu_muestras else 0.0
        ram_promedio = sum(ram_muestras) / len(ram_muestras) if ram_muestras else 0.0

        categoria_tiempo = self._clasificar_tiempo(promedio_ms / 1000.0)
        calificacion_cpu = self._calificar_cpu(cpu_promedio)
        calificacion_ram = self._calificar_ram(ram_promedio)

        return {
            "nombre": nombre_humano,
            "iteraciones": iteraciones,
            "exitosas": exitosas,
            "fallidas": fallidas,
            "tiempos_ms": tiempos,
            "tiempo_promedio_ms": promedio_ms,
            "tiempo_maximo_ms": max_ms,
            "categoria_tiempo": categoria_tiempo,
            "cpu_promedio": cpu_promedio,
            "ram_promedio_mb": ram_promedio,
            "calificacion_cpu": calificacion_cpu,
            "calificacion_ram": calificacion_ram,
            "errores": errores,
        }

    # -------------------------------------------------------------------------
    # CLASIFICACIONES SEGÚN TABLAS PROPUESTAS
    # -------------------------------------------------------------------------

    def _clasificar_tiempo(self, segundos: float) -> str:
        """
        Ponderación del comportamiento temporal (Nielsen, 1993)
        0–1s: Excelente, 1–3s: Aceptable, 3–10s: Deficiente, >10s: Inaceptable
        """
        if segundos <= 1.0:
            return "Excelente"
        if segundos <= 3.0:
            return "Aceptable"
        if segundos <= 10.0:
            return "Deficiente"
        return "Inaceptable"

    def _calificar_cpu(self, cpu_percent: float) -> int:
        """
        Ponderación de utilización de CPU (Arcos et al., 2020)
        100% [0–0.5], 90% [0.6–1.5], 75% [1.6–2.5], 50% [2.6–3.5],
        20% [3.6–4.5], 0% [4.6–∞]
        """
        if 0 <= cpu_percent <= 0.5:
            return 100
        if 0.6 <= cpu_percent <= 1.5:
            return 90
        if 1.6 <= cpu_percent <= 2.5:
            return 75
        if 2.6 <= cpu_percent <= 3.5:
            return 50
        if 3.6 <= cpu_percent <= 4.5:
            return 20
        return 0

    def _calificar_ram(self, ram_mb: float) -> int:
        """
        Ponderación de utilización de RAM (Arcos et al., 2020)
        100% [0–150], 90% [151–250], 75% [251–350], 50% [351–450],
        25% [451–550], 0% [551–650]
        """
        if 0 <= ram_mb <= 150:
            return 100
        if 151 <= ram_mb <= 250:
            return 90
        if 251 <= ram_mb <= 350:
            return 75
        if 351 <= ram_mb <= 450:
            return 50
        if 451 <= ram_mb <= 550:
            return 25
        if 551 <= ram_mb <= 650:
            return 0
        # Si excede 650 MB, lo tratamos igualmente como 0 según la idea de "Malo"
        if ram_mb > 650:
            return 0
        return 0

    # -------------------------------------------------------------------------
    # RESÚMENES Y SALIDA
    # -------------------------------------------------------------------------

    def _imprimir_resumen_operacion(self, codigo: str, nombre: str, datos: Dict[str, Any]):
        if "tiempo_promedio_ms" not in datos:
            self.stdout.write(self.style.WARNING(f"  No hay métricas válidas para {nombre}."))
            return
        self.stdout.write(
            f"  - Tiempo medio: {datos['tiempo_promedio_ms']:.2f} ms "
            f"({datos['categoria_tiempo']})"
        )
        self.stdout.write(f"  - Tiempo máximo: {datos['tiempo_maximo_ms']:.2f} ms")
        self.stdout.write(f"  - CPU media: {datos['cpu_promedio']:.2f} % (score: {datos['calificacion_cpu']})")
        self.stdout.write(
            f"  - RAM media: {datos['ram_promedio_mb']:.2f} MB (score: {datos['calificacion_ram']})"
        )
        self.stdout.write(f"  - Iteraciones exitosas: {datos['exitosas']} / {datos['iteraciones']}")

    def _calcular_resumen_global(self, operaciones: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        tiempos_prom: List[float] = []
        cpu_prom: List[float] = []
        ram_prom: List[float] = []

        for op in operaciones.values():
            if "tiempo_promedio_ms" in op:
                tiempos_prom.append(op["tiempo_promedio_ms"])
                cpu_prom.append(op["cpu_promedio"])
                ram_prom.append(op["ram_promedio_mb"])

        if not tiempos_prom:
            return {}

        tiempo_global = sum(tiempos_prom) / len(tiempos_prom)
        cpu_global = sum(cpu_prom) / len(cpu_prom) if cpu_prom else 0.0
        ram_global = sum(ram_prom) / len(ram_prom) if ram_prom else 0.0

        return {
            "tiempo_promedio_ms_global": tiempo_global,
            "categoria_global_tiempo": self._clasificar_tiempo(tiempo_global / 1000.0),
            "cpu_promedio_global": cpu_global,
            "ram_promedio_mb_global": ram_global,
        }

    def _imprimir_resumen_global(self, resumen: Dict[str, Any]):
        if not resumen:
            self.stdout.write(self.style.WARNING("\nNo se pudo calcular un resumen global."))
            return
        self.stdout.write(self.style.SUCCESS("\n" + "-" * 80))
        self.stdout.write(self.style.SUCCESS("RESUMEN GLOBAL DE LAS 14 OPERACIONES"))
        self.stdout.write(self.style.SUCCESS("-" * 80))
        self.stdout.write(
            f"Tiempo medio global: {resumen['tiempo_promedio_ms_global']:.2f} ms "
            f"({resumen['categoria_global_tiempo']})"
        )
        self.stdout.write(f"CPU media global: {resumen['cpu_promedio_global']:.2f} %")
        self.stdout.write(f"RAM media global: {resumen['ram_promedio_mb_global']:.2f} MB")

    # -------------------------------------------------------------------------
    # PERSISTENCIA Y EXPORTACIÓN
    # -------------------------------------------------------------------------

    def _guardar_resultados_bd(self, resultados: Dict[str, Any], usuario):
        """Guarda los resultados en PruebaRendimientoCompleta.resultados_json"""

        prueba = PruebaRendimientoCompleta.objects.create(
            usuario_ejecutor=usuario,
            resultados_json=resultados,
            completada=True,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Resultados guardados en BD (PruebaRendimientoCompleta id={prueba.id})"
            )
        )

    def _exportar_resultados(self, resultados: Dict[str, Any]):
        """Exporta los resultados a un archivo JSON sencillo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resultados_rendimiento_modulos_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
        self.stdout.write(self.style.SUCCESS(f"\n✓ Resultados exportados a: {filename}"))

