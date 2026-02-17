import flet as ft
from model.database import Database
import math

class AutoresPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self.db = Database()
        self.dialog = None
        self.autor_editando = None
        self._autores_cache = []
        self._autores_filtrados = []
        self._page_size = 5
        self._pagina_actual = 1

        # =========================
        # Métricas
        # =========================
        self.total_autores = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#263238")


        self.btn_crear = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD_ROUNDED, size=20), ft.Text("Crear autor", size=14, weight=ft.FontWeight.W_500)],
                spacing=8,
            ),
            on_click=self.abrir_dialogo_crear,
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            height=48,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=2,
            ),
        )


        self.search_input = ft.TextField(
            hint_text="Buscar autor...",
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
            on_change=lambda e: self.mostrar_autores(reset_pagina=True),
        )


        self.autores_table = ft.DataTable(
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, "#e0e0e0"),
            border_radius=12,
            width=1200,
            heading_row_color="#f5f7fa",
            heading_row_height=56,
            data_row_min_height=60,
            data_row_max_height=65,
            column_spacing=30,
            horizontal_margin=20,
            divider_thickness=0.5,
            columns=[
                ft.DataColumn(ft.Text("Nombre Completo", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
                ft.DataColumn(ft.Text("Nacionalidad", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
            ],
            rows=[],
        )


        # =========================
        # Cards de estadísticas (estilo categorías)
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
            crear_stat_card("Total Autores", self.total_autores, ft.Icons.PEOPLE_ROUNDED, "#5e35b1", ft.Colors.WHITE),
        ], spacing=20, scroll=ft.ScrollMode.AUTO)

        # =========================
        # Paginación
        # =========================
        self._pagination_label = ft.Text("Página 1 de 1", size=12, color="#546e7a")

        def change_page(delta: int):
            total = max(1, math.ceil(len(self._autores_filtrados) / self._page_size))
            self._pagina_actual = min(max(1, self._pagina_actual + delta), total)
            self.mostrar_autores()

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
        # Header estilo categorías
        # =========================
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row([
                        ft.Icon(ft.Icons.CREATE, color="#1565c0", size=32),
                        ft.Text("Gestión de Autores", size=26, weight=ft.FontWeight.BOLD, color="#263238"),
                    ], spacing=12),
                    ft.Row([
                        self.btn_crear,
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
                [self.search_input],
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
                        content=self.autores_table,
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

        self.mostrar_autores()


    def action_button(self, icon, bgcolor, tooltip, on_click=None):
        return ft.Container(
            width=36,
            height=36,
            bgcolor=bgcolor,
            border_radius=6,
            tooltip=tooltip,
            on_click=on_click,
            alignment=ft.Alignment.CENTER,
            content=ft.Icon(icon, color=ft.Colors.WHITE, size=18),
        )


    def abrir_dialogo_crear(self, e):
        self.autor_editando = None
        self._abrir_dialogo("Crear autor")

    def abrir_dialogo_editar(self, autor):
        self.autor_editando = autor
        self._abrir_dialogo("Editar autor", autor)

    def _abrir_dialogo(self, titulo, autor=None):
        self.nombre_completo_input = ft.TextField(
            label="Nombre Completo",
            value=autor.get("nombre_completo", "") if autor else "",
            width=320,
            autofocus=True,
        )

        self.nacionalidad_input = ft.TextField(
            label="Nacionalidad",
            value=autor.get("nacionalidad", "") if autor else "",
            width=320,
        )

        content = ft.Container(
            width=520,
            height=320,
            padding=ft.padding.all(14),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK)),
            content=ft.Column(
                [
                    ft.Row([
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.CREATE, size=22, color="#1B6F7A"),
                                bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN),
                                width=40,
                                height=40,
                                border_radius=8,
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Column([ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD), ft.Text("Información del autor", size=12, color="#666")], spacing=2),
                        ], spacing=10),
                        ft.Container(content=ft.Icon(ft.Icons.CLOSE, size=16, color="#666"), width=32, height=32, alignment=ft.Alignment.CENTER, on_click=self.cerrar_dialogo, border_radius=8),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                    ft.Divider(height=6, color="transparent"),

                    ft.Column([self.nombre_completo_input, self.nacionalidad_input], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),

                    ft.Divider(height=6, color="transparent"),

                    ft.Row([ft.TextButton("Cancelar", on_click=self.cerrar_dialogo), ft.ElevatedButton(content=ft.Row([ft.Icon(ft.Icons.CHECK), ft.Text("Guardar")], spacing=8), bgcolor="#0b495c", color=ft.Colors.WHITE, on_click=self.guardar_autor)], alignment=ft.MainAxisAlignment.END, spacing=10),
                ],
                spacing=8,
            ),
        )

        self.dialog = ft.AlertDialog(modal=True, content=content)
        self._page.overlay.clear()
        self._page.overlay.append(self.dialog)
        self.dialog.open = True
        self._page.update()

    def cerrar_dialogo(self, e=None):
        if self.dialog:
            self.dialog.open = False
            self._page.update()


    def mostrar_autores(self, reset_pagina: bool = False):
        self.autores_table.rows.clear()
        autores = self.db.get_autores()
        self._autores_cache = autores or []
        self.total_autores.value = str(len(self._autores_cache))
        filtro = (self.search_input.value or "").lower().strip()

        filtrados = []
        for autor in self._autores_cache:
            texto = f'{autor.get("nombre_completo", "")} {autor.get("nacionalidad","")}'.lower()
            if filtro and filtro not in texto:
                continue
            filtrados.append(autor)

        self._autores_filtrados = filtrados

        total_pages = max(1, math.ceil(len(filtrados) / self._page_size))
        if reset_pagina:
            self._pagina_actual = 1
        if self._pagina_actual > total_pages:
            self._pagina_actual = total_pages

        start = (self._pagina_actual - 1) * self._page_size
        end = start + self._page_size
        pagina_items = filtrados[start:end]

        for autor in pagina_items:
            self.autores_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(autor.get("nombre_completo", ""))),
                        ft.DataCell(ft.Text(autor.get("nacionalidad", ""))),
                        ft.DataCell(
                            ft.Row(
                                [
                                    self.action_button(
                                        ft.Icons.EDIT,
                                        ft.Colors.ORANGE,
                                        "Editar",
                                        lambda e, a=autor: self.abrir_dialogo_editar(a),
                                    ),
                                    self.action_button(
                                        ft.Icons.BLOCK,
                                        ft.Colors.RED,
                                        "Desactivar",
                                    ),
                                ],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.CENTER,
                            )
                        ),
                    ]
                )
            )

        try:
            self._pagination_label.value = f"Página {self._pagina_actual} de {total_pages}"
            self._btn_prev.disabled = self._pagina_actual <= 1
            self._btn_next.disabled = self._pagina_actual >= total_pages
        except Exception:
            pass

        self._page.update()

    def guardar_autor(self, e):
        nombre_completo = self.nombre_completo_input.value.strip()
        nacionalidad = self.nacionalidad_input.value.strip()

        if not nombre_completo:
            self.nombre_completo_input.error_text = "El nombre completo es obligatorio"
            self._page.update()
            return
        else:
            self.nombre_completo_input.error_text = None

        if self.autor_editando:
            self.db.update_autor(
                self.autor_editando["id_autor"],
                nombre_completo,
                nacionalidad,
            )
        else:
            self.db.set_autores(nombre_completo, nacionalidad)

        # feedback
        self._page.snack_bar = ft.SnackBar(ft.Text("✅ Autor guardado correctamente"), bgcolor=ft.Colors.GREEN_500)
        self._page.snack_bar.open = True

        self.cerrar_dialogo()
        self.mostrar_autores()

    def mostrar_error(self, mensaje):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error"),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self._cerrar_error(dlg))
            ],
        )

        self._page.overlay.append(dlg)
        dlg.open = True
        self._page.update()

    def _cerrar_error(self, dlg):
        dlg.open = False
        self._page.update()
