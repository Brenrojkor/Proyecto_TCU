import flet as ft
from model.database import Database


class AutoresPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.db = Database()
        self.dialog = None
        self.autor_editando = None
        
        # Botón crear
        self.btn_crear = ft.ElevatedButton(
            "Agregar",
            icon=ft.Icons.ADD,
            on_click=self.abrir_dialogo_crear
        )

        # Tabla
        self.autores_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Apellido")),
                ft.DataColumn(ft.Text("Nacionalidad")),
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
                    self.autores_table
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

        self.mostrar_autores()
        
    # ─────────────── DIÁLOGOS ───────────────

    def abrir_dialogo_crear(self, e):
        self.autor_editando = None
        self._abrir_dialogo("Agregar autor")

    def abrir_dialogo_editar(self, autor):
        self.autor_editando = autor
        self._abrir_dialogo("Editar autor", autor)

    def _abrir_dialogo(self, titulo, autor=None):
        self.nombre_input = ft.TextField(
            label="Nombre",
            value=autor["nombre"] if autor else "",
            autofocus=True,
            width=320
        )

        self.apellido_input = ft.TextField(
            label="Apellido",
            value=autor.get("apellido", "") if autor else "",
            width=320
        )

        self.nacionalidad_input = ft.TextField(
            label="Nacionalidad",
            value=autor.get("nacionalidad", "") if autor else "",
            width=320
        )

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo),
            content=ft.Column(
                [self.nombre_input, self.apellido_input, self.nacionalidad_input],
                spacing=12,
                tight=True
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=self.cerrar_dialogo),
                ft.ElevatedButton(
                    "Guardar",
                    icon=ft.Icons.CHECK,
                    on_click=self.guardar_autor  # RENOMBRADO
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

    def mostrar_autores(self):
        self.autores_table.rows.clear()

        for autor in self.db.get_autores():
            self.autores_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(autor["id_autor"]))),
                        ft.DataCell(ft.Text(autor["nombre"])),
                        ft.DataCell(ft.Text(autor.get("apellido", ""))),
                        ft.DataCell(ft.Text(autor.get("nacionalidad", ""))),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda e, a=autor: self.abrir_dialogo_editar(a)
                            )
                        )
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

        try:
            if self.autor_editando:
                self.db.update_autor(
                    self.autor_editando["id_autor"],
                    nombre,
                    apellido,
                    nacionalidad
                )
                mensaje = "Autor actualizado correctamente"
            else:
                self.db.set_autores(nombre, apellido, nacionalidad)
                mensaje = "Autor creado correctamente"

            self.cerrar_dialogo()
            self.mostrar_autores()

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