import flet as ft
from model.database import Database


class CategoriasPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.db = Database()
        self.dialog = None
        self.categoria_editando = None

        # Botón crear
        self.btn_crear = ft.ElevatedButton(
            "Nueva categoría",
            icon=ft.Icons.ADD,
            on_click=self.abrir_dialogo_crear
        )

        # Tabla
        self.categorias_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Acciones")),
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
            width=750
        )

        self.controls = [
            ft.Row(
                [container],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        ]

        self.mostrar_categorias()

    # ─────────────── DIÁLOGOS ───────────────

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
            width=320
        )

        self.descripcion_input = ft.TextField(
            label="Descripción",
            value=categoria.get("descripcion", "") if categoria else "",
            multiline=True,
            min_lines=2,
            max_lines=3,
            width=320
        )

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo),
            content=ft.Column(
                [self.nombre_input, self.descripcion_input],
                spacing=12,
                tight=True
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.cerrar_dialogo),
                ft.ElevatedButton(
                    "Guardar",
                    icon=ft.Icons.CHECK,
                    on_click=self.guardar_categoria
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        self._page.overlay.clear()
        self._page.overlay.append(self.dialog)
        self.dialog.open = True
        self._page.update()

    def cerrar_dialogo(self, e=None):
        if self.dialog:
            self.dialog.open = False
            self._page.update()

    # ─────────────── LÓGICA ───────────────

    def guardar_categoria(self, e):
        nombre = self.nombre_input.value.strip()
        descripcion = self.descripcion_input.value.strip()

        if not nombre:
            self.mostrar_error("El nombre es obligatorio.")
            return

        try:
            if self.categoria_editando:
                self.db.update_categoria(
                    self.categoria_editando["id_categoria"],
                    nombre,
                    descripcion
                )
                mensaje = "Categoría actualizada correctamente"
            else:
                self.db.set_categorias(nombre, descripcion)
                mensaje = "Categoría creada correctamente"

            self.cerrar_dialogo()
            self.mostrar_categorias()

            self._page.snack_bar = ft.SnackBar(
                content=ft.Text(mensaje),
                bgcolor=ft.Colors.GREEN_500
            )
            self._page.snack_bar.open = True
            self._page.update()

        except Exception as ex:
            self.mostrar_error(str(ex))

    def mostrar_error(self, mensaje):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error"),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton(
                    "Cerrar",
                    on_click=lambda e: self._cerrar_error(dlg)
                )
            ]
        )

        self._page.overlay.append(dlg)
        dlg.open = True
        self._page.update()

    def _cerrar_error(self, dlg):
        dlg.open = False
        self._page.update()

    def mostrar_categorias(self):
        self.categorias_table.rows.clear()

        for cat in self.db.get_categorias():
            self.categorias_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(cat["id_categoria"]))),
                        ft.DataCell(ft.Text(cat["nombre"])),
                        ft.DataCell(ft.Text(cat.get("descripcion", ""))),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda e, c=cat: self.abrir_dialogo_editar(c)
                            )
                        )
                    ]
                )
            )

        self._page.update()
