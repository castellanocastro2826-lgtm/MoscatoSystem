from datetime import datetime
import tkinter.messagebox as messagebox

class RegistroPedidosController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        # Connect view events to controller methods
        self.view.on_date_change = self.handle_date_change
        self.view.on_view_order = self.handle_view_order
        self.view.on_print_order = self.handle_print_order
        
        # Initial load
        self.cargar_datos(datetime.now())

    def cargar_datos(self, fecha):
        # 1. Load KPIs (Always for current month)
        kpis = self.model.obtener_kpis_mensuales()
        self.view.actualizar_kpis(kpis)
        
        # 2. Load Table (For selected date)
        historial_raw = self.model.obtener_historial_pedidos(fecha)
        
        # Iterar sobre los resultados para formatear y aplicar reglas lógicas
        historial_procesado = []
        for pedido in historial_raw:
            # Formatear el monto total
            total_num = float(pedido.get('total', 0.0))
            # Formato con signo de dólar y separador de miles con punto
            pedido['total_formateado'] = f"${int(total_num):,}".replace(',', '.')
            
            # Regla lógica para método de pago
            metodo = str(pedido.get("metodo_pago", "") or "PENDIENTE").upper()
            if metodo == "PENDIENTE" or not pedido.get("metodo_pago"):
                pedido['color_pago'] = "#FFCC00"  # Amarillo
                pedido['metodo_pago_desc'] = "PENDIENTE"
            else:
                pedido['color_pago'] = "#FFFFFF"  # Blanco
                pedido['metodo_pago_desc'] = metodo
                
            historial_procesado.append(pedido)
            
        self.view.renderizar_tabla(historial_procesado)

    def handle_date_change(self, selected_date):
        # selected_date is a datetime.date object
        self.cargar_datos(selected_date)

    def handle_view_order(self, id_pedido):
        detalle = self.model.obtener_detalle_pedido(id_pedido)
        self.view.mostrar_detalle_pedido(detalle, id_pedido)

    def handle_print_order(self, id_pedido):
        # En una implementación real, esto generaría un PDF o enviaría directo a la impresora ESC/POS
        messagebox.showinfo(
            "Imprimir Comanda", 
            f"Se ha enviado la comanda #{id_pedido} a la impresora.", 
            parent=self.view.parent
        )

