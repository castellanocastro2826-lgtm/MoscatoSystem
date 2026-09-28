# -*- coding: utf-8 -*-
import sys

file_path = 'src/views/admin/vista_admin.py'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

import re
content = re.sub(r'\"Gesti.n de Mesas\"', '\"Gestión de Mesas\"', content)
content = re.sub(r'\"Auditor.a de Sistema\"', '\"Auditoría de Sistema\"', content)
content = re.sub(r'\"An.lisis de Producto\"', '\"Análisis de Producto\"', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done fixing encoding!')
