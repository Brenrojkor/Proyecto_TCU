import flet as ft
from model.database import Database

class CrearLibroPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self.db = Database()

        # ---- Inputs (según dbo.Libro) ----
        self.titulo_input = ft.TextField(label="Título *", width=320, autofocus=True)
        self.isbn_input = ft.TextField(label="ISBN", width=320)

        self.anio_input = ft.TextField(
            label="Año de publicación",
            width=320,
            keyboard_type=ft.KeyboardType.NUMBER
        )

        self.edicion_input = ft.TextField(label="Edición", width=320)

        self.tipo_input = ft.TextField(label="Tipo *", width=320)

        self.descripcion_input = ft.TextField(
            label="Descripción",
            multiline=True,
            min_lines=2,
            max_lines=3,
            width=320
        )

        # ---- Categorías (FK: id_categoria) ----
        cats = self.db.get_categorias()  # debe traer id_categoria y nombre

        self.categoria_dd = ft.Dropdown(
            label="Categoría *",
            width=320,
            options=[
                ft.dropdown.Option(key=str(c["id_categoria"]), text=c["nombre"])
                for c in cats
            ]
        )

        # ---- Botones ----
        self.btn_cancelar = ft.TextButton(
            content=ft.Text("Cancelar"),
            on_click=lambda e: self.navigate("/")
        )

        self.btn_crear = ft.ElevatedButton(
            content=ft.Row(
                controls=[ft.Icon(ft.Icons.CHECK), ft.Text("Crear libro")],
                spacing=8
            ),
            on_click=self.crear_libro
        )

        form = ft.Column(
            controls=[
                self.titulo_input,
                self.isbn_input,
                self.anio_input,
                self.edicion_input,
                self.tipo_input,
                self.descripcion_input,
                self.categoria_dd,
                ft.Row(
                    controls=[self.btn_cancelar, self.btn_crear],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            spacing=12,
            tight=True
        )

        container = ft.Container(
            content=form,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            width=650
        )

        self.controls = [
            ft.Row([container], alignment=ft.MainAxisAlignment.CENTER, expand=True)
        ]

    def crear_libro(self, e):
        try:
            titulo = (self.titulo_input.value or "").strip()
            tipo = (self.tipo_input.value or "").strip()

            if not titulo:
                self.mostrar_error("El título es obligatorio.")
                return

            if not tipo:
                self.mostrar_error("El tipo es obligatorio.")
                return

            if not self.categoria_dd.value:
                self.mostrar_error("Debe seleccionar una categoría.")
                return

            anio = (self.anio_input.value or "").strip()
            anio_publicacion = int(anio) if anio else None

            self.db.crear_libro(
                titulo=titulo,
                isbn=(self.isbn_input.value or "").strip(),
                anio_publicacion=anio_publicacion,
                edicion=(self.edicion_input.value or "").strip(),
                tipo=tipo,
                descripcion=(self.descripcion_input.value or "").strip(),
                id_categoria=int(self.categoria_dd.value),
                activo=1
            )

            self._page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Libro guardado correctamente"),
                bgcolor=ft.Colors.GREEN_500
            )
            self._page.snack_bar.open = True
            self._page.update()

            self.navigate("/")

        except ValueError:
            self.mostrar_error("El año de publicación debe ser un número válido.")
        except Exception as ex:
            self.mostrar_error(str(ex))

    def mostrar_error(self, mensaje: str):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error"),
            content=ft.Text(mensaje),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: self.cerrar_dialogo(dialog))],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def cerrar_dialogo(self, dialog: ft.AlertDialog):
        dialog.open = False
        self._page.update()
