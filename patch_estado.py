# -*- coding: utf-8 -*-
import sys

file_path = 'src/views/mesas/admin_mesas_view.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '''            servicio = mesa['estado']
            servicio_color = self.COLORS["success"] if servicio.lower() == "libre" else (
                self.COLORS["text_warm"] if servicio.lower() == "atencion" else self.COLORS["accent_soft"]
            )
            if not is_active:'''
replacement = '''            servicio = str(mesa.get('estado') or 'Libre').strip().capitalize()
            if not servicio:
                servicio = 'Libre'
                
            servicio_color = self.COLORS["success"] if servicio.lower() == "libre" else (
                self.COLORS["text_warm"] if servicio.lower() in ("atencion", "atención") else self.COLORS["accent_soft"]
            )
            if not is_active:'''

if target in content:
    content = content.replace(target, replacement)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Patched!')
else:
    print('Not found')
