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
        self.view.on_export_excel = self.handle_export_excel
        
        # Initial load asynchronously so UI renders first
        if hasattr(self.view, "after"):
            self.view.after(150, lambda: self.cargar_datos(datetime.now()))
        else:
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

    def handle_export_excel(self, fecha):
        from tkinter import filedialog
        
        historial = self.model.obtener_historial_pedidos(fecha)
        if not historial:
            messagebox.showinfo("Exportar", "No hay datos para exportar en esta fecha.", parent=self.view.parent)
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
            title="Guardar Registro de Pedidos",
            initialfile=f"ventas_{fecha.strftime('%Y_%m_%d')}.xlsx",
            parent=self.view.parent
        )
        
        if not file_path:
            return
            
        try:
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            src_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
            if src_dir not in sys.path:
                sys.path.insert(0, src_dir)
                
            from utils.excel_export import guardar_como_excel
            
            filas = [["ID Pedido", "Mesa", "Mesero", "Fecha", "Total", "Método Pago", "Estado"]]
            for p in historial:
                filas.append([
                    p.get("id_pedido", ""),
                    p.get("numero_mesa", ""),
                    p.get("nombre_mesero", ""),
                    p.get("fecha_pedido", ""),
                    float(p.get("total", 0)),
                    p.get("metodo_pago", ""),
                    p.get("estado_pedido", "")
                ])
                
            guardar_como_excel(file_path, filas, tipo="tabla")
            messagebox.showinfo("Exportar Excel", f"Se exportaron {len(historial)} registros con éxito a:\n{file_path}", parent=self.view.parent)
        except ImportError:
            messagebox.showerror("Exportar", "Falta la librería openpyxl.\nEjecuta: pip install openpyxl", parent=self.view.parent)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{e}", parent=self.view.parent)
