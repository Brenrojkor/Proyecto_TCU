import flet as ft
from model.database import Database
import math


class ContactosPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self._page = page
        self.navigate = navigate
        self._db = Database()

        # =========================
        # Métricas
        # =========================
        self.total_contactos = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#263238")

        # =========================
        # Helpers
        # =========================
        def snack(msg: str, ok: bool = True):
            self._page.snack_bar = ft.SnackBar(
                ft.Text(msg),
                bgcolor=ft.Colors.GREEN_500 if ok else ft.Colors.RED_500
            )
            self._page.snack_bar.open = True
            self._page.update()

        # =========================
        # UI - Inputs
        # =========================
        self.search_input = ft.TextField(
            hint_text="Buscar en todo...",
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
        )

        self.tipo_dd = ft.Dropdown(
            width=260,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            value="TODOS",
            label="Filtrar",
            options=[
                ft.dropdown.Option("TODOS"),
                ft.dropdown.Option("INSTITUCION"),
                ft.dropdown.Option("PROFESOR"),
                ft.dropdown.Option("ESCUELA"),
                ft.dropdown.Option("COLEGIO"),
                ft.dropdown.Option("UNIVERSIDAD"),
                ft.dropdown.Option("ASOCIACION"),
            ],
        )

        # =========================
        # Tabla (estilo reservas)
        # =========================
        self.contactos_table = ft.DataTable(
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, "#e0e0e0"),
            border_radius=12,
            heading_row_color="#f5f7fa",
            heading_row_height=56,
            data_row_min_height=60,
            data_row_max_height=65,
            column_spacing=30,
            horizontal_margin=20,
            divider_thickness=0.5,
            columns=[
                ft.DataColumn(label=ft.Text("Tipo", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
                ft.DataColumn(label=ft.Text("Nombre", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
                ft.DataColumn(label=ft.Text("Correo", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
                ft.DataColumn(label=ft.Text("Teléfono", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
                ft.DataColumn(label=ft.Text("Descripción", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
                ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
            ],
            rows=[],
        )

        self._contactos_cache = []
        self._contactos_filtrados = []
        self._page_size = 5
        self._pagina_actual = 1

        # =========================
        # Dialog form (Editar)
        # =========================
        def open_editar_dialog(contacto: dict):
            self.abrir_dialogo_editar_contacto(contacto)

        def close_dialog(dlg: ft.AlertDialog):
            dlg.open = False
            self._page.update()

        # =========================
        # Acciones
        # =========================
        def action_button(icon, bgcolor, tooltip, on_click=None):
            return ft.Container(
                width=36,
                height=36,
                bgcolor=bgcolor,
                border_radius=6,
                alignment=ft.Alignment.CENTER,
                tooltip=tooltip,
                on_click=on_click,
                content=ft.Icon(icon, color=ft.Colors.WHITE, size=18),
            )

        def confirmar_eliminar(id_contacto: int):
            def eliminar(e):
                try:
                    self._db.eliminar_contacto(id_contacto)
                    snack("Contacto eliminado")
                    dlg.open = False
                    self._page.update()
                    cargar_contactos()
                except Exception as ex:
                    snack(f"Error: {ex}", ok=False)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Eliminar contacto"),
                content=ft.Text("¿Seguro que querés eliminar este contacto?"),
                actions=[
                    ft.ElevatedButton("Cancelar", on_click=lambda e: close_dialog(dlg), bgcolor="#757575", color=ft.Colors.WHITE),
                    ft.ElevatedButton("Eliminar", bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, on_click=eliminar),
                ],
            )
            self._page.overlay.append(dlg)
            dlg.open = True
            self._page.update()

        # =========================
        # Build row
        # =========================
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

        def build_row(c: dict) -> ft.DataRow:
            desc = (c.get("descripcion") or "").strip()
            desc_short = (desc[:70] + "…") if len(desc) > 70 else desc

            correo_val = (c.get("correo", "") or "").strip()
            telefono_val = (c.get("telefono", "") or "").strip()
            whatsapp_num = "".join([ch for ch in telefono_val if ch.isdigit()])
            whatsapp_url = f"https://wa.me/{whatsapp_num}" if whatsapp_num else ""

            return ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(c.get("tipo", "") or "")),
                    ft.DataCell(ft.Text(c.get("nombre", "") or "")),
                    link_cell(correo_val, f"mailto:{correo_val}" if correo_val else ""),
                    link_cell(telefono_val, whatsapp_url),
                    ft.DataCell(ft.Text(desc_short)),
                    ft.DataCell(
                        ft.Row(
                            [
                                action_button(
                                    ft.Icons.EDIT,
                                    ft.Colors.ORANGE,
                                    "Editar",
                                    lambda e, cc=c: open_editar_dialog(cc),
                                ),
                                action_button(
                                    ft.Icons.DELETE,
                                    ft.Colors.RED,
                                    "Eliminar",
                                    lambda e, i=int(c["id_contacto"]): confirmar_eliminar(i),
                                ),
                            ],
                            spacing=10,
                        )
                    ),
                ]
            )

        # =========================
        # Filtros
        # =========================
        def match_tipo(c: dict, tipo: str) -> bool:
            tipo = (tipo or "TODOS").strip().upper()
            if tipo == "TODOS":
                return True
            return (c.get("tipo") or "").strip().upper() == tipo

        def match_texto(c: dict, q: str) -> bool:
            if not q:
                return True
            valores = [
                c.get("tipo", ""),
                c.get("nombre", ""),
                c.get("correo", ""),
                c.get("telefono", ""),
                c.get("descripcion", ""),
            ]
            haystack = " | ".join([(v or "") for v in valores]).lower()
            return q in haystack

        # =========================
        # Paginación
        # =========================
        self._pagination_label = ft.Text("Página 1 de 1", size=12, color="#546e7a")

        def change_page(delta: int):
            total = max(1, math.ceil(len(self._contactos_filtrados) / self._page_size))
            self._pagina_actual = min(max(1, self._pagina_actual + delta), total)
            aplicar_filtros()

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

        def aplicar_filtros(q=None, tipo=None, reset_pagina: bool = False):
            q = (q if q is not None else (self.search_input.value or "")).strip().lower()
            tipo = (tipo if tipo is not None else (self.tipo_dd.value or "TODOS")).strip().upper()

            filtrados = []
            for c in self._contactos_cache:
                if match_tipo(c, tipo) and match_texto(c, q):
                    filtrados.append(c)

            self._contactos_filtrados = filtrados

            total_pages = max(1, math.ceil(len(filtrados) / self._page_size))
            if reset_pagina:
                self._pagina_actual = 1
            if self._pagina_actual > total_pages:
                self._pagina_actual = total_pages

            start = (self._pagina_actual - 1) * self._page_size
            end = start + self._page_size
            pagina_items = filtrados[start:end]

            self.contactos_table.rows = [build_row(c) for c in pagina_items]

            self._pagination_label.value = f"Página {self._pagina_actual} de {total_pages}"
            self._btn_prev.disabled = self._pagina_actual <= 1
            self._btn_next.disabled = self._pagina_actual >= total_pages
            self._page.update()

        # =========================
        # Cargar datos
        # =========================
        def cargar_contactos():
            self._contactos_cache = self._db.get_contactos()
            self.total_contactos.value = str(len(self._contactos_cache))
            aplicar_filtros(reset_pagina=True)

        self._cargar_contactos = cargar_contactos

        # Eventos
        def on_search_change(e):
            aplicar_filtros(q=e.control.value, tipo=self.tipo_dd.value, reset_pagina=True)

        def on_tipo_change(e):
            aplicar_filtros(q=self.search_input.value, tipo=e.control.value, reset_pagina=True)

        self.search_input.on_change = on_search_change
        self.tipo_dd.on_change = on_tipo_change

        # Botones de acción (estilo reservas)
        btn_nuevo = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD_ROUNDED, size=20),
                ft.Text("Crear contacto", size=14, weight=ft.FontWeight.W_500)
            ], spacing=8),
            on_click=self.abrir_dialogo_crear_contacto,
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            height=48,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=2,
            ),
        )

        btn_refrescar = ft.IconButton(
            icon=ft.Icons.REFRESH_ROUNDED,
            icon_color=ft.Colors.WHITE,
            bgcolor="#1976d2",
            tooltip="Refrescar datos",
            on_click=lambda e: cargar_contactos(),
            icon_size=24,
            height=48,
            width=48,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )

        # Cards de estadísticas (estilo reservas)
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
            crear_stat_card("Total Contactos", self.total_contactos, ft.Icons.PEOPLE_ROUNDED, "#5e35b1", ft.Colors.WHITE),
        ], spacing=20, scroll=ft.ScrollMode.AUTO)

        # Header estilo reservas
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row([
                        ft.Icon(ft.Icons.CONTACT_PHONE_ROUNDED, color="#1565c0", size=32),
                        ft.Text("Gestión de Contactos", size=26, weight=ft.FontWeight.BOLD, color="#263238"),
                    ], spacing=12),
                    ft.Row([
                        btn_refrescar,
                        btn_nuevo,
                    ], spacing=12),
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
        filtros_bar = ft.Container(
            content=ft.Row(
                [self.search_input, self.tipo_dd],
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
                        content=self.contactos_table,
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

        # Cargar al entrar
        cargar_contactos()

    # =========================
    # Crear Contacto con Diálogo
    # =========================
    def abrir_dialogo_crear_contacto(self, e=None):
        INPUT_STYLE = dict(
            width=320,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        self.crear_tipo_dd = ft.Dropdown(
            label="Tipo *",
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
            value="INSTITUCION",
            options=[
                ft.dropdown.Option("INSTITUCION"),
                ft.dropdown.Option("PROFESOR"),
                ft.dropdown.Option("ESCUELA"),
                ft.dropdown.Option("COLEGIO"),
                ft.dropdown.Option("UNIVERSIDAD"),
                ft.dropdown.Option("ASOCIACION"),
            ],
        )

        self.crear_nombre_input = ft.TextField(label="Nombre", autofocus=True, **INPUT_STYLE)
        self.crear_correo_input = ft.TextField(label="Correo electrónico", **INPUT_STYLE)
        self.crear_telefono_input = ft.TextField(label="Teléfono", **INPUT_STYLE)
        self.crear_descripcion_input = ft.TextField(
            label="Descripción",
            multiline=True,
            min_lines=3,
            max_lines=6,
            width=680,
            bgcolor="#f5f7fa",
            border_radius=8,
        )

        btn_guardar = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.CHECK), ft.Text("Guardar")], spacing=8),
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            on_click=self.crear_contacto,
        )

        header_row = ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.CONTACT_MAIL, size=22, color="#1B6F7A"),
                    bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN),
                    width=40,
                    height=40,
                    border_radius=8,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column([
                    ft.Text("Crear contacto", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Completa los datos del contacto", size=12, color="#666")
                ], spacing=2)
            ], spacing=10),
            ft.Container(
                content=ft.Icon(ft.Icons.CLOSE, size=18, color="#666"),
                width=36,
                height=36,
                alignment=ft.Alignment.CENTER,
                on_click=self.cerrar_dialogo_contacto,
                border_radius=8,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        form_column = ft.Column([
            ft.Text("Información", size=14, weight=ft.FontWeight.BOLD, color="#0b495c"),
            self.crear_tipo_dd,
            self.crear_nombre_input,
            ft.Row([self.crear_correo_input, self.crear_telefono_input], spacing=12),
            self.crear_descripcion_input,
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        content = ft.Column([
            header_row,
            ft.Divider(height=8, color="transparent"),
            form_column,
            ft.Divider(height=6, color="transparent"),
            ft.Row([
                ft.ElevatedButton("Cancelar", on_click=self.cerrar_dialogo_contacto, bgcolor="#757575", color=ft.Colors.WHITE),
                btn_guardar
            ], alignment=ft.MainAxisAlignment.END, spacing=12)
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        self.dialog_contacto = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                width=780,
                padding=ft.padding.all(18),
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                content=content,
            )
        )

        self._page.overlay.clear()
        self._page.overlay.append(self.dialog_contacto)
        self.dialog_contacto.open = True
        self._page.update()

    def crear_contacto(self, e):
        try:
            tipo = (self.crear_tipo_dd.value or "").strip().upper()
            correo_val = (self.crear_correo_input.value or "").strip()

            if not tipo:
                self._page.snack_bar = ft.SnackBar(ft.Text("El tipo es obligatorio."), bgcolor=ft.Colors.RED_500)
                self._page.snack_bar.open = True
                self._page.update()
                return

            if correo_val and "@" not in correo_val:
                self._page.snack_bar = ft.SnackBar(ft.Text("El correo debe contener '@'."), bgcolor=ft.Colors.RED_500)
                self._page.snack_bar.open = True
                self._page.update()
                return

            self._db.crear_contacto(
                tipo=tipo,
                institucion="N/A",
                nombre=(self.crear_nombre_input.value or "").strip() or None,
                correo=correo_val or None,
                telefono=(self.crear_telefono_input.value or "").strip() or None,
                descripcion=(self.crear_descripcion_input.value or "").strip() or None,
            )

            self._page.snack_bar = ft.SnackBar(ft.Text("✅ Contacto guardado correctamente"), bgcolor=ft.Colors.GREEN_500)
            self._page.snack_bar.open = True
            self.cerrar_dialogo_contacto()
            if hasattr(self, "_cargar_contactos"):
                self._cargar_contactos()

        except Exception as ex:
            self._page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.Colors.RED_500)
            self._page.snack_bar.open = True
            self._page.update()

    # =========================
    # Editar Contacto con Diálogo
    # =========================
    def abrir_dialogo_editar_contacto(self, contacto: dict):
        self._edit_contacto_id = int(contacto["id_contacto"])
        self._edit_contacto_institucion = (contacto.get("institucion") or "N/A")

        INPUT_STYLE = dict(
            width=320,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        self.editar_tipo_dd = ft.Dropdown(
            label="Tipo *",
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
            value=(contacto.get("tipo") or "INSTITUCION"),
            options=[
                ft.dropdown.Option("INSTITUCION"),
                ft.dropdown.Option("PROFESOR"),
                ft.dropdown.Option("ESCUELA"),
                ft.dropdown.Option("COLEGIO"),
                ft.dropdown.Option("UNIVERSIDAD"),
                ft.dropdown.Option("ASOCIACION"),
            ],
        )

        self.editar_nombre_input = ft.TextField(
            label="Nombre",
            value=(contacto.get("nombre") or ""),
            **INPUT_STYLE,
        )

        self.editar_correo_input = ft.TextField(
            label="Correo electrónico",
            value=(contacto.get("correo") or ""),
            **INPUT_STYLE,
        )

        self.editar_telefono_input = ft.TextField(
            label="Teléfono",
            value=(contacto.get("telefono") or ""),
            **INPUT_STYLE,
        )

        self.editar_descripcion_input = ft.TextField(
            label="Descripción",
            multiline=True,
            min_lines=3,
            max_lines=6,
            width=680,
            bgcolor="#f5f7fa",
            border_radius=8,
            value=(contacto.get("descripcion") or ""),
        )

        btn_guardar = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.CHECK), ft.Text("Guardar")], spacing=8),
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            on_click=self.guardar_edicion_contacto,
        )

        header_row = ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.EDIT, size=22, color="#1B6F7A"),
                    bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN),
                    width=40,
                    height=40,
                    border_radius=8,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column([
                    ft.Text("Editar contacto", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Actualiza los datos del contacto", size=12, color="#666")
                ], spacing=2)
            ], spacing=10),
            ft.Container(
                content=ft.Icon(ft.Icons.CLOSE, size=18, color="#666"),
                width=36,
                height=36,
                alignment=ft.Alignment.CENTER,
                on_click=self.cerrar_dialogo_editar_contacto,
                border_radius=8,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        form_column = ft.Column([
            ft.Text("Información", size=14, weight=ft.FontWeight.BOLD, color="#0b495c"),
            self.editar_tipo_dd,
            self.editar_nombre_input,
            ft.Row([self.editar_correo_input, self.editar_telefono_input], spacing=12),
            self.editar_descripcion_input,
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        content = ft.Column([
            header_row,
            ft.Divider(height=8, color="transparent"),
            form_column,
            ft.Divider(height=6, color="transparent"),
            ft.Row([
                ft.ElevatedButton("Cancelar", on_click=self.cerrar_dialogo_editar_contacto, bgcolor="#757575", color=ft.Colors.WHITE),
                btn_guardar
            ], alignment=ft.MainAxisAlignment.END, spacing=12)
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        self.dialog_contacto_editar = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                width=780,
                padding=ft.padding.all(18),
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                content=content,
            )
        )

        self._page.overlay.clear()
        self._page.overlay.append(self.dialog_contacto_editar)
        self.dialog_contacto_editar.open = True
        self._page.update()

    def guardar_edicion_contacto(self, e):
        try:
            print("[EDIT] Iniciando guardar_edicion_contacto...")
            tipo = (self.editar_tipo_dd.value or "").strip().upper()
            correo_val = (self.editar_correo_input.value or "").strip()

            print(f"[EDIT] tipo={tipo}, correo={correo_val}, id={self._edit_contacto_id}")

            if not tipo:
                self._page.snack_bar = ft.SnackBar(ft.Text("El tipo es obligatorio."), bgcolor=ft.Colors.RED_500)
                self._page.snack_bar.open = True
                self._page.update()
                return

            if correo_val and "@" not in correo_val:
                self._page.snack_bar = ft.SnackBar(ft.Text("El correo debe contener '@'."), bgcolor=ft.Colors.RED_500)
                self._page.snack_bar.open = True
                self._page.update()
                return

            print("[EDIT] Llamando a _db.editar_contacto()...")
            self._db.editar_contacto(
                id_contacto=self._edit_contacto_id,
                tipo=tipo,
                institucion=self._edit_contacto_institucion,
                nombre=(self.editar_nombre_input.value or "").strip() or None,
                correo=correo_val or None,
                telefono=(self.editar_telefono_input.value or "").strip() or None,
                descripcion=(self.editar_descripcion_input.value or "").strip() or None,
            )
            print("[EDIT] Contacto actualizado en BD")

            self._page.snack_bar = ft.SnackBar(ft.Text("✅ Contacto actualizado"), bgcolor=ft.Colors.GREEN_500)
            self._page.snack_bar.open = True
            self.cerrar_dialogo_editar_contacto()
            if hasattr(self, "_cargar_contactos"):
                self._cargar_contactos()
            print("[EDIT] Contacto actualizado completamente")

        except Exception as ex:
            print(f"[EDIT] ERROR: {ex}")
            import traceback
            traceback.print_exc()
            self._page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.Colors.RED_500)
            self._page.snack_bar.open = True
            self._page.update()

    def cerrar_dialogo_editar_contacto(self, e=None):
        if hasattr(self, "dialog_contacto_editar") and self.dialog_contacto_editar:
            self.dialog_contacto_editar.open = False
            self._page.update()

    def cerrar_dialogo_contacto(self, e=None):
        if hasattr(self, "dialog_contacto") and self.dialog_contacto:
            self.dialog_contacto.open = False
            self._page.update()
