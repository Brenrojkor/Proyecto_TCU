import flet as ft
from model.database import Database
import math


class CategoriasPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self._page = page
        self.navigate = navigate
        self.db = Database()
        self.dialog = None
        self.categoria_editando = None
        self._categorias_cache = []
        self._categorias_filtradas = []
        self._page_size = 5
        self._pagina_actual = 1

        # =========================
        # Métricas
        # =========================
        self.total_categorias = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#263238")


        self.btn_crear = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD_ROUNDED, size=20), ft.Text("Crear categoría", size=14, weight=ft.FontWeight.W_500)],
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
            hint_text="Buscar categoría...",
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
            on_change=lambda e: self.mostrar_categorias(reset_pagina=True),
        )

     

        self.categorias_table = ft.DataTable(
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
                ft.DataColumn(
                    ft.Text("Nombre", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)
                ),
                ft.DataColumn(
                    ft.Text("Descripción", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)
                ),
                ft.DataColumn(
                    ft.Text("Acciones", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)
                ),
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
            crear_stat_card("Total Categorías", self.total_categorias, ft.Icons.CATEGORY_ROUNDED, "#5e35b1", ft.Colors.WHITE),
        ], spacing=20, scroll=ft.ScrollMode.AUTO)

        # =========================
        # Paginación
        # =========================
        self._pagination_label = ft.Text("Página 1 de 1", size=12, color="#546e7a")

        def change_page(delta: int):
            total = max(1, math.ceil(len(self._categorias_filtradas) / self._page_size))
            self._pagina_actual = min(max(1, self._pagina_actual + delta), total)
            self.mostrar_categorias()

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
                        ft.Icon(ft.Icons.CATEGORY_ROUNDED, color=ft.Colors.BLUE_700, size=32),
                        ft.Text("Gestión de Categorías", size=26, weight=ft.FontWeight.BOLD, color="#263238"),
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
                        content=self.categorias_table,
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

        self.mostrar_categorias()


    def action_button(self, icon, bgcolor, tooltip, on_click=None):
        return ft.Container(
            height=34,
            padding=ft.padding.only(left=10, right=10, top=2, bottom=2),
            bgcolor=bgcolor,
            border_radius=4,
            alignment=ft.Alignment.CENTER,
            tooltip=tooltip,
            on_click=on_click,
            content=ft.Row(
                [
                    ft.Icon(icon, color=ft.Colors.WHITE, size=16),
                    ft.Text(tooltip, color=ft.Colors.WHITE, size=12),
                ],
                spacing=4,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )


    def on_search_change(self, e):
        texto = (e.control.value or "").lower().strip()
        self.categorias_table.rows.clear()

        for cat in self._categorias_cache:
            if not texto or texto in cat["nombre"].lower():
                self.categorias_table.rows.append(self._build_row(cat))

        self._page.update()


    def abrir_dialogo_crear(self, e):
        self.categoria_editando = None
        self._abrir_dialogo("Crear categoría")

    def abrir_dialogo_editar(self, categoria):
        self.categoria_editando = categoria
        self._abrir_dialogo("Editar categoría", categoria)

    def _abrir_dialogo(self, titulo, categoria=None):
        self.nombre_input = ft.TextField(
            label="Nombre",
            value=categoria["nombre"] if categoria else "",
            autofocus=True,
            width=320,
        )

        self.descripcion_input = ft.TextField(
            label="Descripción",
            value=categoria.get("descripcion", "") if categoria else "",
            multiline=True,
            min_lines=2,
            max_lines=3,
            width=320,
        )

        content = ft.Container(
            width=520,
            height=300,
            padding=ft.padding.all(14),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK)),
            content=ft.Column(
                [
                    ft.Row([
                        ft.Row([
                            ft.Container(content=ft.Icon(ft.Icons.LIST, size=22, color="#1B6F7A"), bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN), width=40, height=40, border_radius=8, alignment=ft.Alignment.CENTER),
                            ft.Column([ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD), ft.Text("Información de la categoría", size=12, color="#666")], spacing=2),
                        ], spacing=10),
                        ft.Container(content=ft.Icon(ft.Icons.CLOSE, size=16, color="#666"), width=32, height=32, alignment=ft.Alignment.CENTER, on_click=self.cerrar_dialogo, border_radius=8),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                    ft.Divider(height=6, color="transparent"),

                    ft.Column([self.nombre_input, self.descripcion_input], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),

                    ft.Divider(height=6, color="transparent"),

                    ft.Row([ft.ElevatedButton("Cancelar", on_click=self.cerrar_dialogo, bgcolor="#757575", color=ft.Colors.WHITE), ft.ElevatedButton(content=ft.Row([ft.Icon(ft.Icons.CHECK), ft.Text("Guardar")], spacing=8), bgcolor="#1976d2", color=ft.Colors.WHITE, on_click=self.guardar_categoria)], alignment=ft.MainAxisAlignment.END, spacing=10),
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


    def guardar_categoria(self, e):
        nombre = self.nombre_input.value.strip()
        descripcion = self.descripcion_input.value.strip()

        if not nombre:
            self.nombre_input.error_text = "El nombre es obligatorio"
            self._page.update()
            return
        else:
            self.nombre_input.error_text = None

        if self.categoria_editando:
            self.db.update_categoria(
                self.categoria_editando["id_categoria"],
                nombre,
                descripcion,
            )
        else:
            self.db.set_categorias(nombre, descripcion)

        # feedback
        self._page.snack_bar = ft.SnackBar(ft.Text("✅ Categoría guardada"), bgcolor=ft.Colors.GREEN_500)
        self._page.snack_bar.open = True

        self.cerrar_dialogo()
        self.mostrar_categorias()

    def mostrar_error(self, mensaje):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error"),
            content=ft.Text(mensaje),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: self._cerrar_error(dlg))],
        )

        self._page.overlay.append(dlg)
        dlg.open = True
        self._page.update()

    def _cerrar_error(self, dlg):
        dlg.open = False
        self._page.update()

    def confirmar_eliminar(self, categoria):
        def eliminar(e):
            try:
                id_categoria = categoria.get("id_categoria") or categoria.get("id")
                if not id_categoria:
                    self._page.snack_bar = ft.SnackBar(
                        ft.Text("No se pudo identificar la categoría"),
                        bgcolor=ft.Colors.RED_500,
                    )
                    self._page.snack_bar.open = True
                    self._page.update()
                    return

                self.db.eliminar_categoria(int(id_categoria))
                self._page.snack_bar = ft.SnackBar(ft.Text("🗑️ Categoría eliminada"), bgcolor=ft.Colors.GREEN_500)
                self._page.snack_bar.open = True
                dlg.open = False
                self._page.update()
                self.mostrar_categorias()
            except Exception as ex:
                self._page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.Colors.RED_500)
                self._page.snack_bar.open = True
                self._page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Eliminar categoría"),
            content=ft.Text("¿Seguro que querés eliminar esta categoría?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self._cerrar_dialogo_confirmacion(dlg)),
                ft.ElevatedButton("Eliminar", bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, on_click=eliminar),
            ],
        )
        self._page.overlay.append(dlg)
        dlg.open = True
        self._page.update()

    def _cerrar_dialogo_confirmacion(self, dlg):
        dlg.open = False
        self._page.update()

    def _build_row(self, cat):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(cat["nombre"], text_align=ft.TextAlign.CENTER)),
                ft.DataCell(ft.Text(cat.get("descripcion", ""), text_align=ft.TextAlign.CENTER)),
                ft.DataCell(
                    ft.Row(
                        [
                            self.action_button(
                                ft.Icons.EDIT,
                                ft.Colors.ORANGE,
                                "Editar",
                                lambda e, c=cat: self.abrir_dialogo_editar(c),
                            ),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ),
            ]
        )


    def mostrar_categorias(self, reset_pagina: bool = False):
        self.categorias_table.rows.clear()
        self._categorias_cache = self.db.get_categorias()

        self.total_categorias.value = str(len(self._categorias_cache))

        filtro = (self.search_input.value or "").lower().strip()

        filtradas = []
        for cat in self._categorias_cache:
            if filtro and filtro not in (cat.get("nombre", "") or "").lower():
                continue
            filtradas.append(cat)

        self._categorias_filtradas = filtradas

        total_pages = max(1, math.ceil(len(filtradas) / self._page_size))
        if reset_pagina:
            self._pagina_actual = 1
        if self._pagina_actual > total_pages:
            self._pagina_actual = total_pages

        start = (self._pagina_actual - 1) * self._page_size
        end = start + self._page_size
        pagina_items = filtradas[start:end]

        for cat in pagina_items:
            self.categorias_table.rows.append(self._build_row(cat))

        try:
            self._pagination_label.value = f"Página {self._pagina_actual} de {total_pages}"
            self._btn_prev.disabled = self._pagina_actual <= 1
            self._btn_next.disabled = self._pagina_actual >= total_pages
        except Exception:
            pass

        self._page.update()
