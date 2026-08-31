from src.models.pedidos.modelo_analisis import AnalisisModel

class AnalisisController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        self.cargar_datos()

    def cargar_datos(self):
        data = self.model.get_dashboard_data()
        self.view.actualizar_dashboard(data)

