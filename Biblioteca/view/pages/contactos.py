import flet as ft
from model.database import Database


class ContactosPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self._db = Database()

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
            prefix_icon=ft.Icons.SEARCH,
            width=360,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        self.tipo_dd = ft.Dropdown(
            width=260,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            value="TODOS",
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
        # Tabla
        # =========================
        self.contactos_table = ft.DataTable(
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, "#d0d7de"),
            border_radius=8,
            heading_row_color="#e3f2fd",
            heading_row_height=48,
            data_row_min_height=52,
            data_row_max_height=52,
            column_spacing=30,
            horizontal_margin=16,
            columns=[
                ft.DataColumn(label=ft.Text("Tipo", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Nombre", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Correo", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Teléfono", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Descripción", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD, color="#0d47a1")),
            ],
            rows=[],
        )

        self._contactos_cache = []

        # =========================
        # Dialog form (Editar)
        # =========================
        def open_editar_dialog(contacto: dict):

            tipo = ft.Dropdown(
                label="Tipo *",
                width=360,
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

            nombre = ft.TextField(
                label="Nombre",
                width=360,
                value=(contacto.get("nombre") or ""),
            )

            correo = ft.TextField(
                label="Correo electrónico",
                width=360,
                value=(contacto.get("correo") or ""),
            )

            telefono = ft.TextField(
                label="Teléfono",
                width=360,
                value=(contacto.get("telefono") or ""),
            )

            descripcion = ft.TextField(
                label="Descripción",
                width=360,
                multiline=True,
                min_lines=2,
                max_lines=4,
                value=(contacto.get("descripcion") or ""),
            )

            def guardar(e):
                try:
                    t = (tipo.value or "").strip().upper()
                    if not t:
                        snack("El tipo es obligatorio.", ok=False)
                        return

                    self._db.editar_contacto(
                        id_contacto=int(contacto["id_contacto"]),
                        tipo=t,
                        institucion="N/A",
                        nombre=(nombre.value or "").strip() or None,
                        correo=(correo.value or "").strip() or None,
                        telefono=(telefono.value or "").strip() or None,
                        descripcion=(descripcion.value or "").strip() or None,
                    )
                    snack("✅ Contacto actualizado")

                    dlg.open = False
                    self._page.update()
                    cargar_contactos()
                except Exception as ex:
                    snack(f"Error: {ex}", ok=False)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Editar contacto"),
                content=ft.Column(
                    [
                        tipo,
                        nombre,
                        correo,
                        telefono,
                        descripcion,
                    ],
                    tight=True,
                    spacing=10,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: close_dialog(dlg)),
                    ft.ElevatedButton("Guardar", on_click=guardar),
                ],
            )

            self._page.overlay.append(dlg)
            dlg.open = True
            self._page.update()

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
                    snack("🗑️ Contacto eliminado")
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
                    ft.TextButton("Cancelar", on_click=lambda e: close_dialog(dlg)),
                    ft.ElevatedButton("Eliminar", bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, on_click=eliminar),
                ],
            )
            self._page.overlay.append(dlg)
            dlg.open = True
            self._page.update()

        # =========================
        # Build row
        # =========================
        def build_row(c: dict) -> ft.DataRow:
            desc = (c.get("descripcion") or "").strip()
            desc_short = (desc[:70] + "…") if len(desc) > 70 else desc

            return ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(c.get("tipo", "") or "")),
                    ft.DataCell(ft.Text(c.get("nombre", "") or "")),
                    ft.DataCell(ft.Text(c.get("correo", "") or "")),
                    ft.DataCell(ft.Text(c.get("telefono", "") or "")),
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

        def aplicar_filtros(q=None, tipo=None):
            q = (q if q is not None else (self.search_input.value or "")).strip().lower()
            tipo = (tipo if tipo is not None else (self.tipo_dd.value or "TODOS")).strip().upper()

            filas = []
            for c in self._contactos_cache:
                if match_tipo(c, tipo) and match_texto(c, q):
                    filas.append(build_row(c))

            self.contactos_table.rows = filas
            self._page.update()

        # =========================
        # Cargar datos
        # =========================
        def cargar_contactos():
            self._contactos_cache = self._db.get_contactos()
            aplicar_filtros()

        # Eventos
        def on_search_change(e):
            aplicar_filtros(q=e.control.value, tipo=self.tipo_dd.value)

        def on_tipo_change(e):
            aplicar_filtros(q=self.search_input.value, tipo=e.control.value)

        self.search_input.on_change = on_search_change
        self.tipo_dd.on_change = on_tipo_change

        # Botón nuevo
        btn_nuevo = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.ADD), ft.Text("Nuevo contacto")], spacing=8),
            on_click=lambda e: self.navigate("/createcontacto"),
        )

        # Header (estilo Home)
        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Row(
                [
                    ft.Text("Contactos", size=22, weight=ft.FontWeight.BOLD, color="#38638f"),
                    btn_nuevo,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        container = ft.Container(
            content=ft.Column(
                [
                    header,
                    ft.Row(
                        [self.search_input, self.tipo_dd],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=12,
                    ),
                    ft.Row([self.contactos_table], alignment=ft.MainAxisAlignment.CENTER),
                ],
                spacing=20,
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            expand=True,
        )

        self.controls = [ft.Row([container], expand=True)]

        # Cargar al entrar
        cargar_contactos()
