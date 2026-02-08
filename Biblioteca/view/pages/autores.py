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
                ft.DataColumn(ft.Text("Nombre Completo", weight=ft.FontWeight.BOLD, color="#0d47a1")),
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


    def mostrar_autores(self):
        self.autores_table.rows.clear()
        filtro = (self.search_input.value or "").lower()

        for autor in self.db.get_autores():
            texto = f'{autor.get("nombre_completo", "")} {autor.get("nacionalidad","")}'.lower()
            if filtro and filtro not in texto:
                continue

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
