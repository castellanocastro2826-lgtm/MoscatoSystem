import sys

file_path = 'src/views/admin/vista_admin.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''    def _show_analisis(self) -> None:
        self._activate_nav("orders")
        self._replace_main_panel()
        self._build_analisis_panel()

    def _build_registro_pedidos_panel(self):'''

replacement = '''    def _show_analisis(self) -> None:
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

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Patched successfully!')
else:
    print('Target not found.')
