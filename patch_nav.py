# -*- coding: utf-8 -*-
import sys

file_path = 'src/views/admin/vista_admin.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if '("users", "Gestion de Usuarios", False, self._show_users),' in line:
        new_lines.append(line)
        # Verify it doesn't already have it
        if i + 1 < len(lines) and '"mesas"' not in lines[i+1]:
            new_lines.append('            ("mesas", "Gestión de Mesas", False, self._show_mesas),\n')
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done!')
