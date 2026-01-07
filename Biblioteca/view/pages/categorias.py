import flet as ft
from model.database import Database


class CategoriasPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.db = Database()
        self.dialog = None

        #Botón
        self.btn_crear = ft.ElevatedButton(
            "Nueva categoría",
            icon=ft.Icons.ADD,
            on_click=self.abrir_dialogo
        )

        #La tabla
        self.categorias_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Descripción")),
            ],
            rows=[]
        )
        
        container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [self.btn_crear],
                        alignment=ft.MainAxisAlignment.END
                    ),
                    self.categorias_table
                ],
                spacing=20
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            width=650
        )

        self.controls = [
            ft.Row(
                [container],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        ]

        self.mostrar_categorias(None)

    #Esto es como la ventana modal

    def abrir_dialogo(self, e):
        self.nombre_input = ft.TextField(
            label="Nombre de la categoría",
            autofocus=True,
            width=320
        )

        self.descripcion_input = ft.TextField(
            label="Descripción (opcional)",
            multiline=True,
            min_lines=2,
            max_lines=3,
            width=320
        )

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Crear categoría"),
            content=ft.Column(
                [
                    self.nombre_input,
                    self.descripcion_input
                ],
                spacing=12,
                tight=True
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=self.cerrar_dialogo
                ),
                ft.ElevatedButton(
                    "Crear",
                    icon=ft.Icons.CHECK,
                    on_click=self.crear_categoria
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        #Modal
        self._page.overlay.append(self.dialog)
        self.dialog.open = True
        self._page.update()

    def cerrar_dialogo(self, e=None):
        if self.dialog:
            self.dialog.open = False
            self._page.update()

    #MÉTODOS

    def crear_categoria(self, e):
        nombre = self.nombre_input.value.strip()
        descripcion = self.descripcion_input.value.strip()

        if not nombre:
            self.mostrar_error("El nombre es obligatorio.")
            return

        try:
            self.db.set_categorias(nombre, descripcion)

            # cerrar diálogo
            self.cerrar_dialogo()

            # refrescar tabla
            self.mostrar_categorias(None)

            self._page.snack_bar = ft.SnackBar(
                content=ft.Text("Categoría creada correctamente"),
                bgcolor=ft.Colors.GREEN_500
            )
            self._page.snack_bar.open = True
            self._page.update()

        except Exception as ex:
            self.mostrar_error(str(ex))

    def mostrar_error(self, mensaje):
        error_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error"),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton(
                    "Cerrar",
                    on_click=lambda e: self.cerrar_error(error_dialog)
                )
            ]
        )

        self._page.overlay.append(error_dialog)
        error_dialog.open = True
        self._page.update()

    def cerrar_error(self, dialog):
        dialog.open = False
        self._page.update()

    def mostrar_categorias(self, e):
        self.categorias_table.rows.clear()

        for cat in self.db.get_categorias():
            self.categorias_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(cat["id_categoria"]))),
                        ft.DataCell(ft.Text(cat["nombre"])),
                        ft.DataCell(ft.Text(cat.get("descripcion", ""))),
                    ]
                )
            )

        self._page.update()


