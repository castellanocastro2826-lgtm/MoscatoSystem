# -*- coding: utf-8 -*-
import sys

file_path = 'src/views/admin/vista_admin.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Imports
target_imports = '''from src.controllers.pedidos.controlador_registro_pedidos import RegistroPedidosController

class UnifiedDashboardWindow(ctk.CTkFrame):'''
replacement_imports = '''from src.controllers.pedidos.controlador_registro_pedidos import RegistroPedidosController

from src.models.mesas.admin_mesas_model import AdminMesasModel
from src.views.mesas.admin_mesas_view import AdminMesasView
from src.controllers.mesas.admin_mesas_controller import AdminMesasController

class UnifiedDashboardWindow(ctk.CTkFrame):'''
if target_imports in content:
    content = content.replace(target_imports, replacement_imports)
    print('Imports added')

# 2. Methods
target_methods = '''    def _show_analisis(self) -> None:
        self._activate_nav("orders")
        self._replace_main_panel()
        self._build_analisis_panel()

    def _build_registro_pedidos_panel(self):'''
replacement_methods = '''    def _show_analisis(self) -> None:
        self._activate_nav("orders")
        self._replace_main_panel()
        self._build_analisis_panel()

    def _show_mesas(self) -> None:
        self._activate_nav("mesas")
        self._replace_main_panel()
        self._build_mesas_panel()

    def _build_mesas_panel(self):
        self.main_panel = ctk.CTkFrame(self, fg_color=self.COLORS["wine_bg"], corner_radius=0)
        self.main_panel.grid(row=0, column=1, sticky="nsew")
        self.main_panel.grid_columnconfigure(0, weight=1)
        self.main_panel.grid_rowconfigure(0, weight=1)

        panel = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        panel.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(0, weight=1)

        vista_mesas = AdminMesasView(panel)
        modelo_mesas = AdminMesasModel()
        self.current_panel_controller = AdminMesasController(modelo_mesas, vista_mesas)

    def _build_registro_pedidos_panel(self):'''
if target_methods in content:
    content = content.replace(target_methods, replacement_methods)
    print('Methods added')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
