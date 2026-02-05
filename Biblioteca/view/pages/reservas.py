import flet as ft
from model.database import Database


class ReservasPage(ft.Column):
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
            hint_text="Buscar libro o cédula...",
            prefix_icon=ft.Icons.SEARCH,
            width=360,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        self.estado_dd = ft.Dropdown(
            width=260,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            value="TODOS",
            options=[
                ft.dropdown.Option("TODOS"),
                ft.dropdown.Option("PRESTADO"),
                ft.dropdown.Option("DEVUELTO"),
                ft.dropdown.Option("NO DEVUELTO"),
            ],
        )

        # =========================
        # Tabla
        # =========================
        self.reservas_table = ft.DataTable(
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
                ft.DataColumn(label=ft.Text("Libro", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Cédula Usuario", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Fecha Préstamo", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Fecha Devolución", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Estado", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD, color="#0d47a1")),
            ],
            rows=[],
        )

        self._reservas_cache = []

        # =========================
        # Dialog form (Registrar Devolución)
        # =========================
        def open_devolucion_dialog(reserva: dict):
            fecha_devolucion = ft.TextField(
                label="Fecha de Devolución",
                hint_text="YYYY-MM-DD",
                width=360,
                read_only=True,
                value=reserva.get("fecha_devolucion", ""),
            )

            observaciones = ft.TextField(
                label="Observaciones",
                multiline=True,
                min_lines=2,
                max_lines=4,
                width=360,
                bgcolor="#f5f7fa",
                border_radius=8,
            )

            def guardar(e):
                try:
                    # Aquí irá la lógica de actualizar devolución
                    snack("✅ Devolución registrada", ok=True)
                    dlg.open = False
                    self._page.update()
                    cargar_reservas()
                except Exception as ex:
                    snack(f"Error: {ex}", ok=False)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Registrar Devolución"),
                content=ft.Column(
                    [
                        ft.Text(f"Libro: {reserva.get('libro_titulo', 'N/A')}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"Cédula: {reserva.get('cedula_usuario', 'N/A')}"),
                        ft.Divider(height=10),
                        fecha_devolucion,
                        observaciones,
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

        def confirmar_eliminar(id_reserva: int):
            def eliminar(e):
                try:
                    # Aquí irá la lógica de eliminar
                    snack("🗑️ Registro eliminado", ok=True)
                    dlg.open = False
                    self._page.update()
                    cargar_reservas()
                except Exception as ex:
                    snack(f"Error: {ex}", ok=False)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Eliminar registro"),
                content=ft.Text("¿Seguro que querés eliminar este registro?"),
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
        def build_row(r: dict) -> ft.DataRow:
            estado = r.get("estado", "PRESTADO").upper()
            estado_color = "#ff9800" if estado == "NO DEVUELTO" else "#4caf50" if estado == "DEVUELTO" else "#2196f3"
            
            return ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(r.get("libro_titulo", "") or "")),
                    ft.DataCell(ft.Text(r.get("cedula_usuario", "") or "")),
                    ft.DataCell(ft.Text(r.get("fecha_prestamo", "") or "")),
                    ft.DataCell(ft.Text(r.get("fecha_devolucion", "") or "—")),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(estado, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                            bgcolor=estado_color,
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            border_radius=4,
                        )
                    ),
                    ft.DataCell(
                        ft.Row(
                            [
                                action_button(
                                    ft.Icons.EDIT,
                                    ft.Colors.ORANGE,
                                    "Registrar devolución",
                                    lambda e, rr=r: open_devolucion_dialog(rr),
                                ),
                                action_button(
                                    ft.Icons.DELETE,
                                    ft.Colors.RED,
                                    "Eliminar",
                                    lambda e, i=int(r.get("id_reserva", 0)): confirmar_eliminar(i),
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
        def match_estado(r: dict, estado: str) -> bool:
            estado = (estado or "TODOS").strip().upper()
            if estado == "TODOS":
                return True
            return (r.get("estado") or "").strip().upper() == estado

        def match_texto(r: dict, q: str) -> bool:
            if not q:
                return True
            valores = [
                r.get("libro_titulo", ""),
                r.get("cedula_usuario", ""),
                r.get("fecha_prestamo", ""),
                r.get("fecha_devolucion", ""),
            ]
            haystack = " | ".join([(v or "") for v in valores]).lower()
            return q in haystack

        def aplicar_filtros(q: str = "", estado: str = "TODOS"):
            q = (q or "").strip().lower()
            rows_filtradas = [
                r for r in self._reservas_cache
                if match_estado(r, estado) and match_texto(r, q)
            ]
            self.reservas_table.rows = [build_row(r) for r in rows_filtradas]
            self._page.update()

        # =========================
        # Cargar datos
        # =========================
        def cargar_reservas():
            try:
                # TODO: Reemplazar con la llamada real a la BD cuando esté lista
                # self._reservas_cache = self._db.get_reservas()
                self._reservas_cache = [
                    {
                        "id_reserva": 1,
                        "libro_titulo": "El Quijote",
                        "cedula_usuario": "123456789",
                        "fecha_prestamo": "2025-01-20",
                        "fecha_devolucion": "2025-01-27",
                        "estado": "DEVUELTO",
                    },
                    {
                        "id_reserva": 2,
                        "libro_titulo": "Don Juan Tenorio",
                        "cedula_usuario": "987654321",
                        "fecha_prestamo": "2025-01-22",
                        "fecha_devolucion": None,
                        "estado": "NO DEVUELTO",
                    },
                    {
                        "id_reserva": 3,
                        "libro_titulo": "La casa de los espíritus",
                        "cedula_usuario": "555555555",
                        "fecha_prestamo": "2025-02-01",
                        "fecha_devolucion": None,
                        "estado": "PRESTADO",
                    },
                ]
                aplicar_filtros(q=self.search_input.value, estado=self.estado_dd.value)
            except Exception as ex:
                snack(f"Error al cargar: {ex}", ok=False)

        def on_search_change(e):
            aplicar_filtros(q=self.search_input.value, estado=self.estado_dd.value)

        def on_estado_change(e):
            aplicar_filtros(q=self.search_input.value, estado=e.control.value)

        self.search_input.on_change = on_search_change
        self.estado_dd.on_change = on_estado_change

        # Botón nuevo (para cuando la otra compañera lo implemente)
        btn_nuevo = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.ADD), ft.Text("Nuevo préstamo")], spacing=8),
            on_click=lambda e: snack("Funcionalidad pendiente", ok=False),
        )

        # Header
        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Row(
                [
                    ft.Text("Préstamos y Devoluciones", size=22, weight=ft.FontWeight.BOLD, color="#38638f"),
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
                        [self.search_input, self.estado_dd],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=12,
                    ),
                    ft.Row([self.reservas_table], alignment=ft.MainAxisAlignment.CENTER),
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
        cargar_reservas()
