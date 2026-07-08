from __future__ import annotations

from datetime import datetime
import unicodedata
from typing import Any

from src.models.cocina.modelo_cocina import ModeloCocina
from src.views.cocina.vista_cocina import CocinaDesignWindow


class ControladorCocina:
    """Controlador MVC del monitor de cocina."""

    def __init__(self, vista: CocinaDesignWindow, modelo: ModeloCocina | None = None) -> None:
        self.vista = vista
        self.modelo = modelo or ModeloCocina()

    def actualizar_pantalla(self) -> None:
        """Consulta pedidos reales, actualiza vista y programa refresco automatico."""
        print("Iniciando consulta de pedidos activos...")
        pedidos_reales = self.modelo.obtener_pedidos_activos()
        print("Datos crudos del modelo:", pedidos_reales)
        pedidos_activos, tiempo_promedio, en_prep, pendientes = self._calcular_estadisticas(pedidos_reales)
        datos_mapeados = self._agrupar_items_a_tarjetas(pedidos_reales)
        print("Datos mapeados para la vista:", datos_mapeados)
        self.vista.actualizar_monitor(datos_mapeados, self.al_hacer_clic_en_listo)
        self.vista.actualizar_estadisticas(
            pedidos_activos=pedidos_activos,
            tiempo_promedio=tiempo_promedio,
            en_prep=en_prep,
            pendientes=pendientes,
        )
        self.vista.after(10000, self.actualizar_pantalla)

    def al_hacer_clic_en_listo(self, id_detalle: int) -> None:
        """Despacha el item pulsado y refresca la pantalla de inmediato."""
        self.modelo.actualizar_estado_item(id_detalle, "Listo")
        self.actualizar_pantalla()

    def _agrupar_items_a_tarjetas(self, filas: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Agrupa filas por id_pedido (si existe) o por numero_mesa para renderizar una tarjeta por pedido."""
        grupos: dict[str, dict[str, Any]] = {}

        for fila in filas:
            numero_mesa = str(fila.get("numero_mesa") or "Para llevar")
            id_pedido = fila.get("id_pedido")
            llave = f"pedido:{id_pedido}" if id_pedido not in (None, "") else f"mesa:{numero_mesa.strip().lower()}"

            if llave not in grupos:
                grupos[llave] = {
                    "id_detalle": int(fila.get("id_detalle") or 0),
                    "mesa": self._normalizar_mesa(numero_mesa),
                    "tiempo": self._formatear_hora(fila.get("fecha_envio_cocina")),
                    "estado": "PENDIENTE",
                    "estado_bg": "#C49315",
                    "borde": "#B8891D",
                    "items": [],
                    "detalle": "",
                }

            cantidad = int(fila.get("cantidad") or 1)
            nombre = str(fila.get("nombre") or "ITEM").upper()
            grupos[llave]["items"].append(f"{cantidad}x  {nombre}")

            detalle = str(fila.get("descripcion_preparacion") or "").strip()
            if detalle and not grupos[llave]["detalle"]:
                grupos[llave]["detalle"] = detalle

            hora_envio = self._formatear_hora(fila.get("fecha_envio_cocina"))
            if hora_envio and hora_envio < grupos[llave]["tiempo"]:
                grupos[llave]["tiempo"] = hora_envio

        return list(grupos.values())

    @staticmethod
    def _normalizar_mesa(numero_mesa: str) -> str:
        texto = str(numero_mesa or "").strip()
        if texto.lower() == "para llevar":
            return "#PARA LLEVAR"
        if texto.upper().startswith("T-"):
            return texto.upper()
        if texto.isdigit():
            return f"T-{int(texto):02d}"
        return f"T-{texto.upper()}"

    @staticmethod
    def _formatear_hora(valor: Any) -> str:
        if isinstance(valor, datetime):
            return valor.strftime("%H:%M")
        texto = str(valor or "")
        if len(texto) >= 16 and "-" in texto:
            return texto[11:16]
        return texto[:5] if texto else "--:--"

    def _calcular_estadisticas(self, filas: list[dict[str, Any]]) -> tuple[int, str, int, int]:
        pedidos_unicos: set[str] = set()
        pendientes = 0
        en_prep = 0
        tiempos_segundos: list[float] = []
        ahora = datetime.now()

        for fila in filas:
            id_pedido = fila.get("id_pedido")
            numero_mesa = str(fila.get("numero_mesa") or "").strip().lower()
            id_detalle = fila.get("id_detalle")

            if id_pedido not in (None, ""):
                pedidos_unicos.add(f"pedido:{id_pedido}")
            elif numero_mesa:
                pedidos_unicos.add(f"mesa:{numero_mesa}")
            elif id_detalle not in (None, ""):
                pedidos_unicos.add(f"detalle:{id_detalle}")

            estado_raw = fila.get("estado_item") or fila.get("estado") or ""
            estado = self._normalizar_estado(str(estado_raw))
            if estado == "pendiente":
                pendientes += 1
            if estado in {"en cocina", "en preparacion"}:
                en_prep += 1

            fecha_envio = self._parse_datetime(fila.get("fecha_envio_cocina"))
            if fecha_envio is not None:
                delta = (ahora - fecha_envio).total_seconds()
                if delta >= 0:
                    tiempos_segundos.append(delta)

        promedio = sum(tiempos_segundos) / len(tiempos_segundos) if tiempos_segundos else 0.0
        promedio_entero = int(round(promedio))
        minutos = promedio_entero // 60
        segundos = promedio_entero % 60
        tiempo_promedio = f"{minutos:02d}:{segundos:02d}"

        return len(pedidos_unicos), tiempo_promedio, en_prep, pendientes

    @staticmethod
    def _normalizar_estado(estado: str) -> str:
        texto = estado.strip().lower()
        texto = unicodedata.normalize("NFKD", texto)
        texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
        return " ".join(texto.split())

    @staticmethod
    def _parse_datetime(valor: Any) -> datetime | None:
        if isinstance(valor, datetime):
            return valor

        texto = str(valor or "").strip()
        if not texto:
            return None

        formatos = (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
        )
        for formato in formatos:
            try:
                return datetime.strptime(texto, formato)
            except ValueError:
                continue
        return None
