import threading
import time
from typing import Any
from src.core.event_bus import event_bus
from src.models.pedidos.modelo_mesero import ModeloMesero

class ControladorMesero:
    def __init__(self, modelo: ModeloMesero):
        self.modelo = modelo
        self._polling = False
        self._thread = None
        self._last_orders = {}
        
    def cargar_catalogo(self) -> dict:
        return self.modelo.obtener_categorias_y_productos()
        
    def guardar_orden(self, orden: dict, usuario: str) -> int | None:
        return self.modelo.guardar_orden(orden, usuario)
        
    def start_polling(self, interval_sec: int = 5):
        if self._polling:
            return
        self._polling = True
        self._thread = threading.Thread(target=self._poll_loop, args=(interval_sec,), daemon=True)
        self._thread.start()
        
    def stop_polling(self):
        self._polling = False
        if self._thread:
            self._thread.join(timeout=1.0)
            
    def _poll_loop(self, interval_sec: int):
        while self._polling:
            try:
                ordenes = self.modelo.obtener_ordenes_pendientes()
                cambios = False
                
                # Check for state changes to emit events
                current_orders = {}
                for orden in ordenes:
                    id_pedido = int(orden.get("id_pedido") or 0)
                    estado = str(orden.get("estado_item") or orden.get("estado_pedido") or "")
                    current_orders[id_pedido] = estado
                    
                    last_estado = self._last_orders.get(id_pedido)
                    if last_estado is not None and last_estado != estado:
                        # Emite evento de que un pedido cambió de estado
                        event_bus.emit("pedido.listo", {"id_pedido": id_pedido, "estado_item": estado})
                        cambios = True
                        
                # Update last orders state
                self._last_orders = current_orders
                
                if cambios or not hasattr(self, '_first_poll_done'):
                    setattr(self, '_first_poll_done', True)
                    
                    # Group items by ticket for UI format
                    grouped = {}
                    for row in ordenes:
                        t = row.get("id_pedido")
                        if not t: continue
                        if t not in grouped:
                            grouped[t] = {
                                "ticket": row.get("ticket_numero") or t,
                                "mesa": row.get("mesa", "Mesa X"),
                                "estado": row.get("estado_pedido", ""),
                                "pagado": bool(row.get("pagado")),
                                "metodo_pago": row.get("metodo_pago") or "",
                                "id_pedido": row.get("id_pedido"),
                                "items": []
                            }
                        
                        grouped[t]["items"].append({
                            "id_detalle": row.get("id_detalle"),
                            "id_producto": row.get("id_producto"),
                            "nombre": row.get("nombre"),
                            "precio": row.get("precio"),
                            "cantidad": row.get("cantidad"),
                            "notas": row.get("descripcion_preparacion", ""),
                            "estado_item": row.get("estado_item", "")
                        })
                    
                    ordenes_agrupadas = list(grouped.values())
                    event_bus.emit("pedidos.pendientes_actualizados", {"ordenes": ordenes_agrupadas})
                    
            except Exception as e:
                import logging
                logging.error(f"Error in ControladorMesero polling: {e}", exc_info=True)
                
            time.sleep(interval_sec)

    def eliminar_item_pendiente(self, id_detalle: int) -> bool:
        return self.modelo.eliminar_item_pendiente(id_detalle)

    def cancelar_pedido_pendiente(self, id_pedido: int) -> bool:
        exito = self.modelo.cancelar_pedido_pendiente(id_pedido)
        if exito:
            from src.utils.event_bus import event_bus
            event_bus.publish("pedido.cancelado", {"id_pedido": id_pedido})
        return exito

    def consultar_ticket_por_id(self, id_pedido: int) -> int | None:
        return self.modelo.consultar_ticket_por_id(id_pedido)

