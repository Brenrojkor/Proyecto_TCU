import flet as ft
from model.database import Database

class AutoresPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self.db = Database()
        self.dialog = None
        self.autor_editando = None


        self.btn_crear = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD), ft.Text("Crear autor")],
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


        self.autores_table = ft.DataTable(
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, "#d0d7de"),
            border_radius=8,
             width=990,
            heading_row_color="#e3f2fd",
            heading_row_height=48,
            data_row_min_height=52,
            data_row_max_height=52,
            column_spacing=50,
            horizontal_margin=16,
            columns=[
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(ft.Text("Apellido", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(ft.Text("Nacionalidad", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, color="#0d47a1")),
            ],
            rows=[],
        )


        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Row(
                [
                    ft.Text(
                        "Autores Registrados",
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
                        [self.autores_table],
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
        self.nombre_input = ft.TextField(
            label="Nombre",
            value=autor["nombre"] if autor else "",
            width=320,
            autofocus=True,
        )

        self.apellido_input = ft.TextField(
            label="Apellido",
            value=autor.get("apellido", "") if autor else "",
            width=320,
        )

        self.nacionalidad_input = ft.TextField(
            label="Nacionalidad",
            value=autor.get("nacionalidad", "") if autor else "",
            width=320,
        )

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo),
            content=ft.Column(
                [self.nombre_input, self.apellido_input, self.nacionalidad_input],
                spacing=12,
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.cerrar_dialogo),
                ft.ElevatedButton(
                    "Guardar",
                    icon=ft.Icons.CHECK,
                    on_click=self.guardar_autor,
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


    def mostrar_autores(self):
        self.autores_table.rows.clear()
        filtro = (self.search_input.value or "").lower()

        for autor in self.db.get_autores():
            texto = f'{autor["nombre"]} {autor.get("apellido","")} {autor.get("nacionalidad","")}'.lower()
            if filtro and filtro not in texto:
                continue

            self.autores_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(autor["nombre"])),
                        ft.DataCell(ft.Text(autor.get("apellido", ""))),
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

        self._page.update()

    def guardar_autor(self, e):
        nombre = self.nombre_input.value.strip()
        apellido = self.apellido_input.value.strip()
        nacionalidad = self.nacionalidad_input.value.strip()

        if not nombre:
            self.mostrar_error("El nombre es obligatorio.")
            return

        if self.autor_editando:
            self.db.update_autor(
                self.autor_editando["id_autor"],
                nombre,
                apellido,
                nacionalidad,
            )
        else:
            self.db.set_autores(nombre, apellido, nacionalidad)

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
