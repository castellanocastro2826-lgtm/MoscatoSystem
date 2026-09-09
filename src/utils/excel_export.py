import os
try:
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

def guardar_como_excel(ruta_excel: str, filas: list, tipo="tabla") -> bool:
    if not HAS_OPENPYXL:
        raise ImportError("openpyxl no esta instalado. Instálalo usando: pip install openpyxl")
        
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"
    
    # Escribir filas
    for fila in filas:
        ws.append(fila)
        
    # Estilos
    font_title = Font(name="Segoe UI", size=14, bold=True, color="333333")
    fill_title = PatternFill(start_color="EAEAEA", end_color="EAEAEA", fill_type="solid")
    
    font_header = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    fill_header = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    align_header = Alignment(horizontal="center", vertical="center")
    
    font_data = Font(name="Segoe UI", size=10)
    fill_zebra = PatternFill(start_color="F2F4F8", end_color="F2F4F8", fill_type="solid")
    align_data = Alignment(vertical="center", horizontal="left")
    
    borde_tenue = Side(border_style="thin", color="D9D9D9")
    borde_completo = Border(left=borde_tenue, right=borde_tenue, top=borde_tenue, bottom=borde_tenue)
    
    max_lengths = {}
    es_encabezado_siguiente = False
    data_row_counter = 0

    if tipo == "tabla":
        ws.freeze_panes = "A2"

    for row_idx, row in enumerate(ws.iter_rows(), start=1):
        # Ignorar filas totalmente vacias para estilos
        if not any(cell.value for cell in row):
            continue

        val = str(row[0].value) if row[0].value else ""
        
        # Logica para determinar el tipo de fila
        fila_tipo = "dato"
        
        if tipo == "tabla":
            if row_idx == 1:
                fila_tipo = "header"
            else:
                fila_tipo = "dato"
        else:
            # Multitabla
            if val.startswith("==="):
                fila_tipo = "titulo"
                es_encabezado_siguiente = True
                data_row_counter = 0
            elif es_encabezado_siguiente:
                fila_tipo = "header"
                es_encabezado_siguiente = False
            else:
                fila_tipo = "dato"
                data_row_counter += 1

        for col_idx, cell in enumerate(row, start=1):
            if cell.value is not None:
                cell.border = borde_completo
            
            if fila_tipo == "titulo":
                cell.font = font_title
                cell.fill = fill_title
                cell.alignment = Alignment(horizontal="left", vertical="center")
                cell.value = str(cell.value).replace("===", "").strip() if cell.value else ""
            elif fila_tipo == "header":
                cell.font = font_header
                cell.fill = fill_header
                cell.alignment = align_header
            else:
                cell.font = font_data
                cell.alignment = align_data
                if data_row_counter % 2 != 0 and tipo == "multitabla":
                    cell.fill = fill_zebra
                elif row_idx % 2 == 0 and tipo == "tabla":
                    cell.fill = fill_zebra
                    
            cell_len = len(str(cell.value)) if cell.value is not None else 0
            if col_idx not in max_lengths or cell_len > max_lengths[col_idx]:
                max_lengths[col_idx] = cell_len

        # Combinar celdas del titulo si es multitabla
        if fila_tipo == "titulo" and tipo == "multitabla":
            ws.merge_cells(start_row=row_idx, start_column=1, end_row=row_idx, end_column=2)

    # Ajuste automatico de columnas
    for col_idx, max_len in max_lengths.items():
        col_letter = get_column_letter(col_idx)
        adjusted_width = min(max_len + 5, 65)
        adjusted_width = max(adjusted_width, 12)
        ws.column_dimensions[col_letter].width = adjusted_width

    if tipo == "tabla":
        try:
            ws.auto_filter.ref = ws.dimensions
        except Exception:
            pass
            
    wb.save(ruta_excel)
    return True
