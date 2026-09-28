import sys

file_path = 'src/views/admin/vista_admin.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''from src.controllers.pedidos.controlador_registro_pedidos import RegistroPedidosController

class UnifiedDashboardWindow(ctk.CTkFrame):'''

replacement = '''from src.controllers.pedidos.controlador_registro_pedidos import RegistroPedidosController

from src.models.mesas.admin_mesas_model import AdminMesasModel
from src.views.mesas.admin_mesas_view import AdminMesasView
from src.controllers.mesas.admin_mesas_controller import AdminMesasController

class UnifiedDashboardWindow(ctk.CTkFrame):'''

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Imports patched successfully!')
else:
    print('Imports target not found.')
