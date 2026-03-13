import flet as ft
from model.database import Database

import os
import sys
import tempfile
import json
from datetime import datetime
from openpyxl import Workbook
import math

class UsuariosPage(ft.Column):
    def __init__(self, navigate, page: ft.Page, query_params: dict = None):
        super().__init__()
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self._page = page
        self.navigate = navigate
        self.db = Database()
        self.dialog = None
        self.usuario_editando = None
        self._usuarios_cache = []
        self._usuarios_filtrados = []
        self._page_size = 5
        
        # Restaurar página desde query params si existen
        initial_page = 1
        if query_params and isinstance(query_params, dict) and "page" in query_params:
            try:
                initial_page = max(1, int(query_params["page"]))
            except (ValueError, TypeError):
                initial_page = 1
        
        self._pagina_actual = initial_page

        # =========================
        # Métricas
        # =========================
        self.total_usuarios = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#263238")
        self.usuarios_grupo = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#263238")
        self.usuarios_activos = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#263238")

        # Botones de acción (estilo reservas)
        self.btn_crear = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD_ROUNDED, size=20),
                ft.Text("Crear usuario", size=14, weight=ft.FontWeight.W_500)
            ], spacing=8),
            on_click=self.abrir_dialogo_crear,
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            height=48,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=2,
            ),
        )
        self.btn_refrescar = ft.IconButton(
            icon=ft.Icons.REFRESH_ROUNDED,
            icon_color=ft.Colors.WHITE,
            bgcolor="#1976d2",
            tooltip="Refrescar datos",
            on_click=lambda e: self.mostrar_usuarios(),
            icon_size=24,
            height=48,
            width=48,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )

        # Input de búsqueda
        self.search_input = ft.TextField(
            hint_text="Buscar usuario...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            width=500,
            height=50,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border_color="#e0e0e0",
            focused_border_color="#1976d2",
            focused_border_width=2,
            text_size=14,
            content_padding=ft.padding.only(left=15, right=15, top=10, bottom=10),
            on_change=lambda e: self.mostrar_usuarios(reset_pagina=True),
        )

        self.estado_dd = ft.Dropdown(
            width=200,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            value="TODOS",
            label="Filtrar",
            text_size=14,
            options=[
                ft.dropdown.Option("TODOS", "Todos"),
                ft.dropdown.Option("ACTIVOS", "Activos"),
                ft.dropdown.Option("INACTIVOS", "Inactivos"),
            ],
        )
        self.estado_dd.on_change = lambda e: self.mostrar_usuarios(reset_pagina=True)

        # Tabla de usuarios
        self.usuarios_table = ft.DataTable(
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, "#e0e0e0"),
            border_radius=12,
            width=1300,
            heading_row_color="#f5f7fa",
            heading_row_height=56,
            data_row_min_height=60,
            data_row_max_height=65,
            column_spacing=30,
            horizontal_margin=20,
            divider_thickness=0.5,
            columns=[
                ft.DataColumn(ft.Text("Nombre completo", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
                ft.DataColumn(ft.Text("Identificación", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
                ft.DataColumn(ft.Text("Provincia", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
                ft.DataColumn(ft.Text("Teléfono", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
                ft.DataColumn(ft.Text("Año", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
            ],
            rows=[],
        )

        # =========================
        # Cards de estadísticas (estilo reservas)
        # =========================
        def crear_stat_card(titulo, valor_widget, icon, color, bgcolor):
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(icon, color=ft.Colors.WHITE, size=28),
                            bgcolor=color,
                            width=56,
                            height=56,
                            border_radius=12,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column([
                            valor_widget,
                            ft.Text(titulo, size=13, color="#757575", weight=ft.FontWeight.W_500),
                        ], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
                    ], alignment=ft.MainAxisAlignment.START, spacing=15),
                ], spacing=0),
                bgcolor=bgcolor,
                border=ft.border.all(1, "#e0e0e0"),
                border_radius=12,
                padding=20,
                width=250,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
            )

        stats_row = ft.Row([
            crear_stat_card("Total Usuarios", self.total_usuarios, ft.Icons.PEOPLE_ROUNDED, "#5e35b1", ft.Colors.WHITE),
            crear_stat_card("Usuarios Activos", self.usuarios_activos, ft.Icons.CHECK_CIRCLE_ROUNDED, "#2e7d32", ft.Colors.WHITE),
            crear_stat_card("Usuarios en Grupo", self.usuarios_grupo, ft.Icons.GROUPS_ROUNDED, "#1976d2", ft.Colors.WHITE),
        ], spacing=20, scroll=ft.ScrollMode.AUTO)

        # =========================
        # Paginación
        # =========================
        self._pagination_label = ft.Text("Página 1 de 1", size=12, color="#546e7a")

        def change_page(delta: int):
            total = max(1, math.ceil(len(self._usuarios_filtrados) / self._page_size))
            self._pagina_actual = min(max(1, self._pagina_actual + delta), total)
            self.mostrar_usuarios()

        self._btn_prev = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            icon_color="#546e7a",
            tooltip="Anterior",
            on_click=lambda e: change_page(-1),
        )
        self._btn_next = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            icon_color="#546e7a",
            tooltip="Siguiente",
            on_click=lambda e: change_page(1),
        )

        # =========================
        # Header estilo reservas
        # =========================
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row([
                        ft.Icon(ft.Icons.PEOPLE_ROUNDED, color="#1565c0", size=32),
                        ft.Text("Gestión de Usuarios", size=26, weight=ft.FontWeight.BOLD, color="#263238"),
                    ], spacing=12),
                    ft.Row([self.btn_refrescar, self.btn_crear], spacing=12),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(horizontal=30, vertical=20),
            margin=ft.margin.symmetric(horizontal=30),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

        # Barra de filtros
        # Función para abrir archivo en la app por defecto
        def open_file_default_app(path: str):
            try:
                if sys.platform.startswith("win"):
                    os.startfile(path)
                elif sys.platform == "darwin":
                    os.system(f'open "{path}"')
                else:
                    os.system(f'xdg-open "{path}"')
            except Exception as ex:
                self.snack(f"No se pudo abrir el archivo: {ex}")

        # Exportar usuarios a Excel
        def exportar_excel_usuarios(e=None):
            if not self._usuarios_cache:
                self._usuarios_cache = self.db.get_usuarios()

            usuarios = list(self._usuarios_cache or [])
            # Recolectar todas las claves
            all_keys = set()
            for u in usuarios:
                if isinstance(u, dict):
                    all_keys.update(u.keys())

            # Excluir identificador interno
            if "id_usuario" in all_keys:
                all_keys.discard("id_usuario")

            # Orden específico de columnas solicitado
            preferred = [
                "nombre_completo",
                "identificacion",
                "discapacidad",
                "provincia",
                "canton",
                "distrito",
                "rangoedad",
                "sexo",
                "grupo",
                "anio",
                "telefono",
                "activo",
                "fecha_registro",
            ]
            keys = [k for k in preferred if k in all_keys]

            def human(k: str) -> str:
                mapping = {
                    "nombre_completo": "Nombre Completo",
                    "identificacion": "Identificación",
                    "discapacidad": "Discapacidad",
                    "provincia": "Provincia",
                    "canton": "Cantón",
                    "distrito": "Distrito",
                    "rangoedad": "Rango de Edad",
                    "sexo": "Sexo",
                    "grupo": "Grupo",
                    "anio": "Año",
                    "telefono": "Teléfono",
                    "activo": "Activo",
                    "fecha_registro": "Fecha de Registro",
                }
                return mapping.get(k.lower(), k.replace("_", " ").title())

            headers = [human(k) for k in keys]

            wb = Workbook()
            ws = wb.active
            ws.title = "Usuarios"
            
            # Importar estilos
            from openpyxl.styles import Border, Side, PatternFill, Font, Alignment
            
            # Estilos
            header_fill = PatternFill(start_color="1976d2", end_color="1976d2", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=12)
            header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            
            # Bordes
            thin_border = Border(
                left=Side(style='thin', color="cccccc"),
                right=Side(style='thin', color="cccccc"),
                top=Side(style='thin', color="cccccc"),
                bottom=Side(style='thin', color="cccccc")
            )
            
            # Rellenos alternados
            row_fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
            row_fill_light = PatternFill(start_color="f5f7fa", end_color="f5f7fa", fill_type="solid")
            
            # Agregar encabezados con estilo
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col)
                cell.value = header
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = header_alignment
                cell.border = thin_border
            
            ws.row_dimensions[1].height = 25

            def serialize(v, key=""):
                if v is None:
                    return ""
                # Formato especial para fecha_registro: día-mes-año
                if key == "fecha_registro":
                    if isinstance(v, datetime):
                        return v.strftime("%d-%m-%Y")
                    if isinstance(v, str):
                        try:
                            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                            return dt.strftime("%d-%m-%Y")
                        except:
                            return v
                # Normalizar booleanos y 0/1 a Sí/No
                if isinstance(v, bool):
                    return "Sí" if v else "No"
                if isinstance(v, (int, float)) and v in (0, 1):
                    return "Sí" if v == 1 else "No"
                if isinstance(v, str):
                    vs = v.strip().lower()
                    if vs in ("true", "false", "1", "0"):
                        return "Sí" if vs in ("true", "1") else "No"
                if isinstance(v, (list, tuple)):
                    return ", ".join([str(x) for x in v])
                if isinstance(v, dict):
                    try:
                        return json.dumps(v, ensure_ascii=False)
                    except Exception:
                        return str(v)
                if isinstance(v, bytes):
                    return "<BINARY>"
                if isinstance(v, datetime):
                    return v.isoformat()
                return str(v)

            for row_idx, u in enumerate(usuarios, 2):
                # Serializar con el key para formato especial de fecha
                row_data = [serialize(u.get(k), k) if isinstance(u, dict) else "" for k in keys]
                
                # Determinar relleno (alternado)
                current_fill = row_fill_light if row_idx % 2 == 0 else row_fill_white
                
                for col_idx, value in enumerate(row_data, 1):
                    cell = ws.cell(row=row_idx, column=col_idx)
                    cell.value = value
                    cell.fill = current_fill
                    cell.border = thin_border
                    cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

            # Ajustar ancho de columnas automáticamente
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width

            nombre = f"usuarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            out_path = os.path.join(tempfile.gettempdir(), nombre)
            try:
                wb.save(out_path)
                self.snack(f"Excel generado: {nombre}")
                open_file_default_app(out_path)
            except Exception as ex:
                self.snack(f"No se pudo generar Excel: {ex}")

        btn_descargar_excel = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.DOWNLOAD), ft.Text("Descargar Excel")], spacing=8),
            on_click=exportar_excel_usuarios,
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            height=44,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )

        filtros_bar = ft.Container(
            content=ft.Row(
                [self.search_input, self.estado_dd, btn_descargar_excel],
                alignment=ft.MainAxisAlignment.START,
                spacing=15,
            ),
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

        # Contenedor de tabla
        tabla_container = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=self.usuarios_table,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Container(
                        content=ft.Row(
                            [self._btn_prev, self._pagination_label, self._btn_next],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=6,
                        ),
                        padding=ft.padding.only(top=8),
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            margin=ft.margin.symmetric(horizontal=30),
            expand=True,
        )

        # Layout principal
        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        header,
                        ft.Container(content=stats_row, padding=ft.padding.symmetric(horizontal=30)),
                        ft.Container(content=filtros_bar, padding=ft.padding.symmetric(horizontal=30)),
                        ft.Container(content=tabla_container, padding=0, expand=True),
                    ],
                    spacing=20,
                    expand=True,
                ),
                bgcolor="#f5f7fa",
                padding=ft.padding.symmetric(vertical=20),
                expand=True,
            )
        ]
        self.mostrar_usuarios()

    def snack(self, msg: str):
        self._page.snack_bar = ft.SnackBar(ft.Text(msg))
        self._page.snack_bar.open = True
        self._page.update()

    def toggle_activo(self, id_usuario: int, estado_actual: bool):
        nuevo_estado = 0 if estado_actual else 1
        try:
            self.db.set_usuario_activo(id_usuario, nuevo_estado)
            self.snack("Usuario activado ✅" if nuevo_estado == 1 else "Usuario desactivado ✅")
            self.mostrar_usuarios()
        except Exception as ex:
            self.snack(f"Error al actualizar estado: {ex}")

    # Botón de acción para tabla
    def action_button(self, icon, bgcolor, tooltip, on_click=None):
        return ft.Container(width=36, height=36, bgcolor=bgcolor, border_radius=6, tooltip=tooltip,
                            on_click=on_click, alignment=ft.Alignment.CENTER,
                            content=ft.Icon(icon, color=ft.Colors.WHITE, size=18))

    # =========================
    # Ver historial de usuario
    # =========================
    def ver_historial_usuario(self, identificacion):
        if not identificacion:
            self.snack("❌ No se encontró la identificación", ok=False)
            return
        
        try:
            print(f"Buscando historial para identificación: {identificacion}")
            historial = self.db.get_historial_prestamos_usuario(identificacion)
            print(f"Historial obtenido: {len(historial)} registros")
            
            if not historial:
                # Obtener nombre del usuario
                usuario = next((u for u in self._usuarios_cache if u.get("identificacion") == identificacion), None)
                nombre_usuario = usuario.get("nombre_completo", "Usuario") if usuario else "Usuario"
                
                # Mostrar ventana emergente cuando no hay historial
                dlg_sin_historial = ft.AlertDialog(
                    modal=True,
                    title=ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, color="#ff9800", size=24),
                        ft.Text("Sin Historial", size=18, weight=ft.FontWeight.BOLD)
                    ], spacing=8),
                    content=ft.Text(
                        f"No hay historial de préstamos para: {nombre_usuario}",
                        size=13,
                        color="#263238",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    actions=[
                        ft.ElevatedButton(
                            "Cerrar",
                            on_click=lambda e: setattr(dlg_sin_historial, "open", False) or self._page.update(),
                            bgcolor="#1976d2",
                            color=ft.Colors.WHITE,
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.CENTER,
                )
                
                self._page.overlay.append(dlg_sin_historial)
                dlg_sin_historial.open = True
                self._page.update()
                return
            
            # Tabla de historial
            historial_table = ft.DataTable(
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, "#e0e0e0"),
                border_radius=8,
                heading_row_color="#f5f7fa",
                heading_row_height=48,
                data_row_min_height=50,
                column_spacing=20,
                columns=[
                    ft.DataColumn(label=ft.Text("Libro", weight=ft.FontWeight.BOLD, size=12)),
                    ft.DataColumn(label=ft.Text("Préstamo", weight=ft.FontWeight.BOLD, size=12)),
                    ft.DataColumn(label=ft.Text("Devolución", weight=ft.FontWeight.BOLD, size=12)),
                    ft.DataColumn(label=ft.Text("Estado", weight=ft.FontWeight.BOLD, size=12)),
                    ft.DataColumn(label=ft.Text("Observaciones", weight=ft.FontWeight.BOLD, size=12)),
                ],
                rows=[],
            )
            
            for item in historial:
                estado = item.get("estado_calculado") or item.get("estado", "PRESTADO")
                estado_color = "#2e7d32" if estado == "DEVUELTO" else "#d32f2f" if estado == "NO DEVUELTO" else "#1976d2"
                
                fecha_prestamo = item.get("fecha_prestamo", "")
                if hasattr(fecha_prestamo, 'strftime'):
                    fecha_prestamo = fecha_prestamo.strftime("%Y-%m-%d")
                
                fecha_dev = item.get("fecha_devolucion_real") or item.get("fecha_devolucion_esperada", "")
                if hasattr(fecha_dev, 'strftime'):
                    fecha_dev = fecha_dev.strftime("%Y-%m-%d")
                
                observaciones = item.get("observaciones", "") or ""
                
                historial_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item.get("libro_titulo", "")[:30], size=12)),
                        ft.DataCell(ft.Text(str(fecha_prestamo), size=12)),
                        ft.DataCell(ft.Text(str(fecha_dev) if fecha_dev else "—", size=12)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(estado, color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD),
                                bgcolor=estado_color,
                                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                border_radius=6,
                            )
                        ),
                        ft.DataCell(ft.Text(observaciones[:40] + ("..." if len(observaciones) > 40 else ""), size=12, color="#546e7a")),
                    ])
                )
            
            usuario_nombre = historial[0].get("nombre_usuario", "Usuario")
            
            # Función para exportar a Excel/CSV
            def exportar_excel(e):
                try:
                    from openpyxl import Workbook
                    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
                    import subprocess
                    import sys
                    
                    # Crear workbook
                    wb = Workbook()
                    ws = wb.active
                    ws.title = "Historial Préstamos"
                    
                    # Estilos
                    header_fill = PatternFill(start_color="1976d2", end_color="1976d2", fill_type="solid")
                    header_font = Font(bold=True, color="FFFFFF", size=12)
                    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                    
                    # Bordes
                    thin_border = Border(
                        left=Side(style='thin', color="cccccc"),
                        right=Side(style='thin', color="cccccc"),
                        top=Side(style='thin', color="cccccc"),
                        bottom=Side(style='thin', color="cccccc")
                    )
                    
                    # Rellenos alternados para filas
                    row_fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
                    row_fill_light = PatternFill(start_color="f5f7fa", end_color="f5f7fa", fill_type="solid")
                    
                    headers = ['Usuario', 'Libro', 'Préstamo', 'Devolución', 'Estado', 'Observaciones']
                    for col, header in enumerate(headers, 1):
                        cell = ws.cell(row=1, column=col)
                        cell.value = header
                        cell.fill = header_fill
                        cell.font = header_font
                        cell.alignment = header_alignment
                        cell.border = thin_border
                    
                    # Agregar datos
                    for row_idx, item in enumerate(historial, 2):
                        estado = item.get("estado_calculado") or item.get("estado", "PRESTADO")
                        
                        fecha_prestamo = item.get("fecha_prestamo", "")
                        if hasattr(fecha_prestamo, 'strftime'):
                            fecha_prestamo = fecha_prestamo.strftime("%Y-%m-%d")
                        
                        fecha_dev = item.get("fecha_devolucion_real") or item.get("fecha_devolucion_esperada", "")
                        if hasattr(fecha_dev, 'strftime'):
                            fecha_dev = fecha_dev.strftime("%Y-%m-%d")
                        elif not fecha_dev:
                            fecha_dev = "Pendiente"
                        
                        observaciones = item.get("observaciones", "") or ""
                        
                        # Determinar relleno (alternado)
                        current_fill = row_fill_light if row_idx % 2 == 0 else row_fill_white
                        
                        # Determinar color de estado
                        if estado == "DEVUELTO":
                            estado_fill = PatternFill(start_color="c8e6c9", end_color="c8e6c9", fill_type="solid")
                        elif estado == "NO DEVUELTO":
                            estado_fill = PatternFill(start_color="ffcdd2", end_color="ffcdd2", fill_type="solid")
                        else:
                            estado_fill = PatternFill(start_color="bbdefb", end_color="bbdefb", fill_type="solid")
                        
                        # Celda de Usuario
                        cell = ws.cell(row=row_idx, column=1)
                        cell.value = item.get("nombre_usuario", "")
                        cell.fill = current_fill
                        cell.border = thin_border
                        cell.alignment = Alignment(horizontal="left", vertical="center")
                        
                        # Celda de Libro
                        cell = ws.cell(row=row_idx, column=2)
                        cell.value = item.get("libro_titulo", "")
                        cell.fill = current_fill
                        cell.border = thin_border
                        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
                        
                        # Celda de Préstamo
                        cell = ws.cell(row=row_idx, column=3)
                        cell.value = str(fecha_prestamo)
                        cell.fill = current_fill
                        cell.border = thin_border
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                        
                        # Celda de Devolución
                        cell = ws.cell(row=row_idx, column=4)
                        cell.value = str(fecha_dev)
                        cell.fill = current_fill
                        cell.border = thin_border
                        cell.alignment = Alignment(horizontal="center", vertical="center")
                        
                        # Celda de Estado
                        cell = ws.cell(row=row_idx, column=5)
                        cell.value = estado
                        cell.fill = estado_fill
                        cell.border = thin_border
                        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                        cell.font = Font(bold=True, size=10)
                        
                        # Celda de Observaciones
                        cell = ws.cell(row=row_idx, column=6)
                        cell.value = observaciones
                        cell.fill = current_fill
                        cell.border = thin_border
                        cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
                    
                    # Ajustar ancho y altura de columnas
                    ws.column_dimensions['A'].width = 25
                    ws.column_dimensions['B'].width = 35
                    ws.column_dimensions['C'].width = 15
                    ws.column_dimensions['D'].width = 15
                    ws.column_dimensions['E'].width = 12
                    ws.column_dimensions['F'].width = 40
                    ws.row_dimensions[1].height = 25
                    
                    # Guardar en temp
                    nombre = f"historial_{identificacion}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    out_path = os.path.join(tempfile.gettempdir(), nombre)
                    
                    wb.save(out_path)
                    self.snack(f"✅ Excel generado: {nombre}")
                    
                    # Abrir archivo
                    if sys.platform == 'win32':
                        os.startfile(out_path)
                    elif sys.platform == 'darwin':
                        subprocess.Popen(['open', out_path])
                    else:
                        subprocess.Popen(['xdg-open', out_path])
                    
                except Exception as ex:
                    import traceback
                    print(traceback.format_exc())
                    self.snack(f"❌ Error al exportar: {str(ex)}", ok=False)
            
            dlg_historial = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.HISTORY_ROUNDED, color="#1976d2", size=28),
                    ft.Text("Historial de Préstamos", size=20, weight=ft.FontWeight.BOLD)
                ]),
                content=ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Text(usuario_nombre, size=18, weight=ft.FontWeight.BOLD, color="#263238"),
                                ft.Text(f"ID: {identificacion}", size=14, color="#757575"),
                                ft.Text(f"Total de préstamos: {len(historial)}", size=14, weight=ft.FontWeight.W_500, color="#1976d2"),
                            ]),
                            bgcolor="#e3f2fd",
                            padding=12,
                            border_radius=8,
                        ),
                        ft.Container(
                            content=ft.Column([historial_table], scroll=ft.ScrollMode.AUTO),
                            height=260,
                        ),
                    ], spacing=12),
                    width=700,
                    height=420,
                ),
                actions=[
                    ft.ElevatedButton(
                        "Descargar",
                        icon=ft.Icons.DOWNLOAD_ROUNDED,
                        on_click=exportar_excel,
                        bgcolor="#1976d2",
                        color=ft.Colors.WHITE,
                        width=140,
                    ),
                    ft.ElevatedButton(
                        "Cerrar",
                        on_click=lambda e: setattr(dlg_historial, "open", False) or self._page.update(),
                        bgcolor="#1976d2",
                        color=ft.Colors.WHITE,
                        width=100,
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            self._page.overlay.append(dlg_historial)
            dlg_historial.open = True
            self._page.update()
            
        except Exception as ex:
            import traceback
            print(traceback.format_exc())
            self.snack(f"❌ Error: {str(ex)}", ok=False)

    # Abrir diálogo
    def abrir_dialogo_crear(self, e):
        self.usuario_editando = None
        self._crear_dialogo()

    def abrir_dialogo_editar(self, usuario):
        self.usuario_editando = usuario
        self._editar_dialogo(usuario)

    def _crear_dialogo(self):
        INPUT_STYLE = dict(width=320, height=48, bgcolor="#f5f7fa", border_radius=8, border_color="#cfd8dc",
                           focused_border_color="#1976d2", text_size=14)
        SHORT_INPUT = dict(width=200, height=48, bgcolor="#f5f7fa", border_radius=8, border_color="#cfd8dc", text_size=14)
        TINY_INPUT = dict(width=120, height=48, bgcolor="#f5f7fa", border_radius=8, border_color="#cfd8dc", text_size=14)

        # Campos vacíos para crear
        self.nombre_input = ft.TextField(label="Nombre completo *", value="", autofocus=True, **INPUT_STYLE)
        self.identificacion_input = ft.TextField(label="Identificación", value="", **INPUT_STYLE)
        self.provincia_input = ft.TextField(label="Provincia", value="", **INPUT_STYLE)
        self.canton_input = ft.TextField(label="Cantón", value="", **INPUT_STYLE)
        self.distrito_input = ft.TextField(label="Distrito", value="", **INPUT_STYLE)
        self.rango_edad_input = ft.TextField(label="Rango de edad", value="", **SHORT_INPUT)
        self.sexo_input = ft.TextField(label="Sexo", value="", **TINY_INPUT)
        self.curso_input = ft.TextField(label="Curso", value="", **SHORT_INPUT)
        self.anio_input = ft.TextField(label="Año", value="", **TINY_INPUT)
        self.discapacidad_input = ft.Checkbox(label="Discapacidad", value=False)
        self.grupo_input = ft.Checkbox(label="Grupo", value=False)
        self.telefono_input = ft.TextField(label="Teléfono", value="", **INPUT_STYLE)
        self.comentario_input = ft.TextField(label="Comentario", value="", width=520, multiline=True, min_lines=2, max_lines=4, bgcolor="#f5f7fa", border_radius=8)

        self.btn_guardar = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.CHECK), ft.Text("Guardar")], spacing=8),
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            on_click=self.guardar_usuario,
        )

        header_row = ft.Row([
            ft.Row([ft.Container(content=ft.Icon(ft.Icons.PERSON, size=22, color="#1B6F7A"), bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN), width=40, height=40, border_radius=8, alignment=ft.Alignment.CENTER),
                    ft.Column([ft.Text("Crear usuario", size=18, weight=ft.FontWeight.BOLD), ft.Text("Completa los datos del usuario", size=12, color="#666")], spacing=2)], spacing=10),
            ft.Container(content=ft.Icon(ft.Icons.CLOSE, size=18, color="#666"), width=36, height=36, alignment=ft.Alignment.CENTER, on_click=self.cerrar_dialogo, border_radius=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        form_column = ft.Column([
            self.nombre_input,
            ft.Row([self.identificacion_input, self.telefono_input], spacing=12),
            ft.Row([self.provincia_input, ft.Container(content=self.canton_input, width=SHORT_INPUT['width']), ft.Container(content=self.distrito_input, width=SHORT_INPUT['width'])], spacing=12),
            ft.Row([self.rango_edad_input, self.sexo_input, self.anio_input, self.curso_input], spacing=12),
            ft.Row([self.discapacidad_input, self.grupo_input], spacing=20),
            self.comentario_input
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        content = ft.Column([
            header_row,
            ft.Divider(height=8, color="transparent"),
            form_column,
            ft.Divider(height=6, color="transparent"),
            ft.Row([
                ft.ElevatedButton("Cancelar", on_click=self.cerrar_dialogo, bgcolor="#757575", color=ft.Colors.WHITE),
                self.btn_guardar
            ], alignment=ft.MainAxisAlignment.END, spacing=12)
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        self.dialog = ft.AlertDialog(modal=True, content=ft.Container(width=780, padding=ft.padding.all(18), bgcolor=ft.Colors.WHITE, border_radius=12, content=content))

        self._page.overlay.clear()
        self._page.overlay.append(self.dialog)
        self.dialog.open = True
        self._page.update()

    def _editar_dialogo(self, usuario):
        INPUT_STYLE = dict(width=320, height=48, bgcolor="#f5f7fa", border_radius=8, border_color="#cfd8dc",
                           focused_border_color="#1976d2", text_size=14)
        SHORT_INPUT = dict(width=200, height=48, bgcolor="#f5f7fa", border_radius=8, border_color="#cfd8dc", text_size=14)
        TINY_INPUT = dict(width=120, height=48, bgcolor="#f5f7fa", border_radius=8, border_color="#cfd8dc", text_size=14)

        # Campos con datos del usuario
        self.nombre_input = ft.TextField(label="Nombre completo *", value=usuario.get("nombre_completo", ""), autofocus=True, **INPUT_STYLE)
        self.identificacion_input = ft.TextField(label="Identificación", value=usuario.get("identificacion", ""), **INPUT_STYLE)
        self.provincia_input = ft.TextField(label="Provincia", value=usuario.get("provincia", ""), **INPUT_STYLE)
        self.canton_input = ft.TextField(label="Cantón", value=usuario.get("canton", ""), **INPUT_STYLE)
        self.distrito_input = ft.TextField(label="Distrito", value=usuario.get("distrito", ""), **INPUT_STYLE)
        self.rango_edad_input = ft.TextField(label="Rango de edad", value=usuario.get("rango_edad", ""), **SHORT_INPUT)
        self.sexo_input = ft.TextField(label="Sexo", value=usuario.get("sexo", ""), **TINY_INPUT)
        self.curso_input = ft.TextField(label="Curso", value=usuario.get("curso", ""), **SHORT_INPUT)
        self.anio_input = ft.TextField(label="Año", value=str(usuario.get("anio", "")), **TINY_INPUT)
        
        self.discapacidad_input = ft.Checkbox(
            label="Discapacidad",
            value=bool(usuario.get("discapacidad"))
        )

        self.grupo_input = ft.Checkbox(
            label="Grupo",
            value=bool(usuario.get("grupo"))
        )

        self.telefono_input = ft.TextField(label="Teléfono", value=usuario.get("telefono", ""), **INPUT_STYLE)
        self.comentario_input = ft.TextField(label="Comentario", value=usuario.get("comentario", ""), width=520, multiline=True, min_lines=2, max_lines=4, bgcolor="#f5f7fa", border_radius=8)

        self.btn_guardar = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.CHECK), ft.Text("Guardar")], spacing=8),
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            on_click=self.guardar_usuario,
        )

  

        header_row = ft.Row([
            ft.Row([ft.Container(content=ft.Icon(ft.Icons.PERSON, size=22, color="#1B6F7A"), bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN), width=40, height=40, border_radius=8, alignment=ft.Alignment.CENTER),
                    ft.Column([ft.Text("Editar usuario", size=18, weight=ft.FontWeight.BOLD), ft.Text("Completa los datos del usuario", size=12, color="#666")], spacing=2)], spacing=10),
            ft.Container(content=ft.Icon(ft.Icons.CLOSE, size=18, color="#666"), width=36, height=36, alignment=ft.Alignment.CENTER, on_click=self.cerrar_dialogo, border_radius=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        form_column = ft.Column([
            self.nombre_input,
            ft.Row([self.identificacion_input, self.telefono_input], spacing=12),
            ft.Row([self.provincia_input, ft.Container(content=self.canton_input, width=SHORT_INPUT['width']), ft.Container(content=self.distrito_input, width=SHORT_INPUT['width'])], spacing=12),
            ft.Row([self.rango_edad_input, self.sexo_input, self.anio_input, self.curso_input], spacing=12),
            ft.Row([self.discapacidad_input, self.grupo_input], spacing=20),
            self.comentario_input
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        content = ft.Column([
            header_row,
            ft.Divider(height=8, color="transparent"),
            form_column,
            ft.Divider(height=6, color="transparent"),
            ft.Row([
                ft.ElevatedButton("Cancelar", on_click=self.cerrar_dialogo, bgcolor="#757575", color=ft.Colors.WHITE),
                self.btn_guardar
            ], alignment=ft.MainAxisAlignment.END, spacing=12)
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        self.dialog = ft.AlertDialog(modal=True, content=ft.Container(width=780, padding=ft.padding.all(18), bgcolor=ft.Colors.WHITE, border_radius=12, content=content))

        self._page.overlay.clear()
        self._page.overlay.append(self.dialog)
        self.dialog.open = True
        self._page.update()

    

    def guardar_usuario(self, e=None):
        print(f"[DEBUG] guardar_usuario llamado, usuario_editando={self.usuario_editando}")
        try:
            self._page.snack_bar = ft.SnackBar(ft.Text("Procesando..."))
            self._page.snack_bar.open = True
            self._page.update()
        except Exception:
            pass

        try:
            try:
                self.btn_guardar.disabled = True
                self.btn_guardar.update()
            except Exception:
                pass

            # Validaciones simples
            nombre = (self.nombre_input.value or "").strip()
            if not nombre:
                self.nombre_input.error_text = "El nombre es obligatorio"
                try:
                    self.btn_guardar.disabled = False
                    self.btn_guardar.update()
                except Exception:
                    pass
                self._page.update()
                return
            self.nombre_input.error_text = None

            provincia_value = (self.provincia_input.value or "").strip()
            canton_text = (self.canton_input.value or "").strip()
            distrito_text = (self.distrito_input.value or "").strip()

            try:
                anio = int(self.anio_input.value) if (self.anio_input.value or "").strip() else None
            except Exception:
                self.anio_input.error_text = "Año inválido"
                self._page.update()
                return

            # Llamada al modelo
            try:
                if self.usuario_editando:
                    # Detectar ID del usuario
                    uid = None
                    for k in ("id_usuario", "id", "idUsuario", "ID"):
                        if isinstance(self.usuario_editando, dict) and self.usuario_editando.get(k) is not None:
                            uid = self.usuario_editando.get(k)
                            break
                    
                    if uid is None:
                        raise ValueError("No se encontró ID de usuario para edición")

                    print(f"[EDIT] Actualizando usuario ID={uid}, nombre={nombre}")
                    grupo_val = int(bool(self.grupo_input.value)) if self.grupo_input else 0
                    discapacidad_val = int(bool(self.discapacidad_input.value)) if self.discapacidad_input else 0
                    print(f"[EDIT] Valores checkboxes: grupo={grupo_val}, discapacidad={discapacidad_val}")
                    
                    self.db.update_usuario_biblioteca(
                        uid,
                        nombre,
                        self.identificacion_input.value or "",
                        discapacidad_val,
                        provincia_value,
                        canton_text,
                        distrito_text,
                        self.rango_edad_input.value or "",
                        self.sexo_input.value or "",
                        self.curso_input.value or "",
                        anio,
                        grupo_val,
                        self.telefono_input.value or "",
                        1,
                        self.comentario_input.value or "",
                    )
                    print(f"[EDIT] Usuario actualizado exitosamente")
                else:
                    print(f"[CREATE] Creando nuevo usuario: nombre={nombre}, id={id(self)}")
                    print(f"[CREATE] Parámetros: prov={provincia_value}, canton={canton_text}, distrito={distrito_text}")
                    try:
                        self.db.set_usuarios(
                            nombre_completo=nombre,
                            identificacion=self.identificacion_input.value or "",
                            discapacidad=int(bool(self.discapacidad_input.value)) if self.discapacidad_input else 0,
                            provincia=provincia_value,
                            canton=canton_text,
                            distrito=distrito_text,
                            rango_edad=self.rango_edad_input.value or "",
                            sexo=self.sexo_input.value or "",
                            curso=self.curso_input.value or "",
                            anio=anio,
                            grupo=int(bool(self.grupo_input.value)) if self.grupo_input else 0,
                            telefono=self.telefono_input.value or "",
                            activo=1,
                            comentario=self.comentario_input.value or "",
                        )
                        print(f"[CREATE] Usuario creado exitosamente")
                    except Exception as db_error:
                        print(f"[CREATE ERROR] Excepción en set_usuarios: {db_error}")
                        raise

                # Éxito
                self._page.snack_bar = ft.SnackBar(ft.Text("✅ Usuario guardado"), bgcolor="#1b5e20")
                self._page.snack_bar.open = True
                self.cerrar_dialogo()
                self.mostrar_usuarios()
                try:
                    self.btn_guardar.disabled = False
                    self.btn_guardar.update()
                except Exception:
                    pass
                return

            except Exception as ex:
                # Error en la capa de datos — mostrar al usuario y loguear
                try:
                    self.btn_guardar.disabled = False
                    self.btn_guardar.update()
                except Exception:
                    pass
                self._page.snack_bar = ft.SnackBar(ft.Text(f"Error guardando usuario: {ex}"), bgcolor="#b71c1c")
                self._page.snack_bar.open = True
                self._page.update()
                return

        except Exception as fatal_ex:
            # Capturar cualquier excepción inesperada dentro del handler
            try:
                self._page.snack_bar = ft.SnackBar(ft.Text(f"Error interno: {fatal_ex}"), bgcolor="#b71c1c")
                self._page.snack_bar.open = True
                self._page.update()
            except Exception:
                pass
            # además imprimir en consola para debugging local
            print("[usuarios.guardar_usuario] excepción inesperada:", fatal_ex)
            return

    def cerrar_dialogo(self, e=None):
        if self.dialog:
            self.dialog.open = False
            self._page.update()

    # Mostrar usuarios
    def mostrar_usuarios(self, reset_pagina: bool = False):
        # Función para crear celdas con links (identificación y teléfono)
        def link_cell(text_value: str, url: str):
            if not text_value:
                return ft.DataCell(ft.Text(""))
            return ft.DataCell(
                ft.TextButton(
                    text_value,
                    on_click=lambda e: self._page.launch_url(url),
                    style=ft.ButtonStyle(
                        padding=0,
                        color=ft.Colors.BLUE_700,
                    ),
                )
            )

        self.usuarios_table.rows.clear()
        self._usuarios_cache = self.db.get_usuarios()
        filtro = (self.search_input.value or "").lower()
        estado = (self.estado_dd.value or "TODOS").upper()

        total = len(self._usuarios_cache)
        en_grupo = len([u for u in self._usuarios_cache if str(u.get("grupo")).lower() not in ("", "0", "false", "none") and bool(u.get("grupo"))])
        activos = len([u for u in self._usuarios_cache if bool(u.get("activo")) and str(u.get("activo")).lower() not in ("0", "false")])
        self.total_usuarios.value = str(total)
        self.usuarios_grupo.value = str(en_grupo)
        self.usuarios_activos.value = str(activos)

        filtrados = []
        for usuario in self._usuarios_cache:
            texto = f'{usuario["nombre_completo"]} {usuario.get("identificacion","")}'.lower()
            if filtro and filtro not in texto:
                continue
            
            # Obtener estado actual del usuario
            activo_value = usuario.get("activo")
            is_activo = bool(activo_value) and str(activo_value).lower() not in ("0", "false")

            if estado == "ACTIVOS" and not is_activo:
                continue
            if estado == "INACTIVOS" and is_activo:
                continue

            filtrados.append(usuario)

        self._usuarios_filtrados = filtrados

        total_pages = max(1, math.ceil(len(filtrados) / self._page_size))
        if reset_pagina:
            self._pagina_actual = 1
        if self._pagina_actual > total_pages:
            self._pagina_actual = total_pages

        start = (self._pagina_actual - 1) * self._page_size
        end = start + self._page_size
        pagina_items = filtrados[start:end]

        for usuario in pagina_items:
            # Preparar identificación y teléfono para links
            identificacion_val = (usuario.get("identificacion", "") or "").strip()
            telefono_val = (usuario.get("telefono", "") or "").strip()
            whatsapp_num = "".join([ch for ch in telefono_val if ch.isdigit()])
            whatsapp_url = f"https://wa.me/{whatsapp_num}" if whatsapp_num else ""

            # Obtener estado actual del usuario
            activo_value = usuario.get("activo")
            is_activo = bool(activo_value) and str(activo_value).lower() not in ("0", "false")

            self.usuarios_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(usuario["nombre_completo"])),
                    link_cell(identificacion_val, f"tel:{identificacion_val}" if identificacion_val else ""),
                    ft.DataCell(ft.Text(usuario.get("provincia", ""))),
                    link_cell(telefono_val, whatsapp_url),
                    ft.DataCell(ft.Text(str(usuario.get("anio", "")))),
                    ft.DataCell(ft.Row([
                        self.action_button(
                            ft.Icons.VISIBILITY,
                            ft.Colors.BLUE,
                            "Detalles",
                            lambda e, id=usuario["id_usuario"]: self.navigate(f"/detalleusuario/{id}")
                        ),
                        self.action_button(
                            ft.Icons.HISTORY_ROUNDED,
                            "#6a1b9a",
                            "Ver historial",
                            lambda e, ident=identificacion_val: self.ver_historial_usuario(ident)
                        ),
                        self.action_button(ft.Icons.EDIT, ft.Colors.ORANGE, "Editar", lambda e, u=usuario: self.abrir_dialogo_editar(u)),
                        self.action_button(
                            ft.Icons.CHECK_CIRCLE if is_activo else ft.Icons.BLOCK,
                            ft.Colors.GREEN if is_activo else ft.Colors.RED,
                            "Desactivar" if is_activo else "Activar",
                            lambda e, id=usuario["id_usuario"], st=is_activo: self.toggle_activo(id, st)
                        ),
                    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER))
                ])
            )

        try:
            self._pagination_label.value = f"Página {self._pagina_actual} de {total_pages}"
            self._btn_prev.disabled = self._pagina_actual <= 1
            self._btn_next.disabled = self._pagina_actual >= total_pages
        except Exception:
            pass
        self._page.update()
