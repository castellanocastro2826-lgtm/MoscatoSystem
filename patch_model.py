# -*- coding: utf-8 -*-
import sys

file_path = 'src/models/mesas/admin_mesas_model.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = 'query = "SELECT id_mesa, numero_mesa, estado, activo FROM mesas ORDER BY numero_mesa"'
replacement = '''query = """
            SELECT 
                m.id_mesa, 
                m.numero_mesa, 
                CASE 
                    WHEN (SELECT COUNT(*) FROM pedidos p WHERE p.id_mesa = m.id_mesa AND p.pagado = 0 AND p.estado_pedido != 'Cancelado') > 0 THEN 'Ocupada'
                    WHEN m.estado = '' OR m.estado IS NULL THEN 'Libre'
                    ELSE m.estado 
                END AS estado, 
                m.activo 
            FROM mesas m 
            ORDER BY m.numero_mesa
        """'''

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Patched query!')
else:
    print('Query not found')
