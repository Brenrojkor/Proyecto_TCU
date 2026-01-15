import flet as ft
from model.database import Database


class CategoriasPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self.db = Database()
        self.dialog = None
        self.categoria_editando = None
        self._categorias_cache = []


        self.btn_crear = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD), ft.Text("Crear categoría")],
                spacing=8,
            ),
            on_click=self.abrir_dialogo_crear,
        )


        self.search_input = ft.TextField(
            hint_text="Buscar autor...",
            prefix_icon=ft.Icons.SEARCH,
            width=320,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
            on_change=lambda e: self.mostrar_autores(),
        )

     

        self.categorias_table = ft.DataTable(
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, "#d0d7de"),
            border_radius=8,
            width=990,
            heading_row_color="#e3f2fd",
            heading_row_height=48,
            data_row_min_height=52,
            data_row_max_height=52,
            column_spacing=80,   
            horizontal_margin=24,
            columns=[
                ft.DataColumn(
                    ft.Text("Nombre", weight=ft.FontWeight.BOLD, color="#0d47a1")
                ),
                ft.DataColumn(
                    ft.Text("Descripción", weight=ft.FontWeight.BOLD, color="#0d47a1")
                ),
                ft.DataColumn(
                    ft.Text("Acciones", weight=ft.FontWeight.BOLD, color="#0d47a1")
                ),
            ],
            rows=[],
        )

        # =========================
        # HEADER
        # =========================

        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Row(
                [
                    ft.Text(
                        "Categorías Registradas",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color="#38638f",
                    ),
                    self.btn_crear,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )


        container = ft.Container(
            content=ft.Column(
                [
                    header,
                    ft.Row(
                        [self.search_input],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    ft.Row(
                        [self.categorias_table],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                spacing=20,
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            expand=True,  
        )

        self.controls = [
            ft.Row(
                [container],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True,
            )
        ]

        self.mostrar_categorias()


    def action_button(self, icon, bgcolor, tooltip, on_click=None):
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

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo),
            content=ft.Column(
                [self.nombre_input, self.descripcion_input],
                spacing=12,
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.cerrar_dialogo),
                ft.ElevatedButton(
                    "Guardar",
                    icon=ft.Icons.CHECK,
                    on_click=self.guardar_categoria,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

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
            self.mostrar_error("El nombre es obligatorio.")
            return

        if self.categoria_editando:
            self.db.update_categoria(
                self.categoria_editando["id_categoria"],
                nombre,
                descripcion,
            )
        else:
            self.db.set_categorias(nombre, descripcion)

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


    def mostrar_categorias(self):
        self.categorias_table.rows.clear()
        self._categorias_cache = self.db.get_categorias()

        for cat in self._categorias_cache:
            self.categorias_table.rows.append(self._build_row(cat))

        self._page.update()
