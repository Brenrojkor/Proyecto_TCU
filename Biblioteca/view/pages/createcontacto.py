import flet as ft
from model.database import Database


class CrearContactoPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self.db = Database()

        # =========================
        # Estilos reutilizados
        # =========================
        INPUT_STYLE = dict(
            width=320,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        # =========================
        # Inputs
        # =========================
        self.tipo_dd = ft.Dropdown(
            label="Tipo *",
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
            value="INSTITUCION",
            options=[
                ft.dropdown.Option("INSTITUCION"),
                ft.dropdown.Option("PROFESOR"),
                ft.dropdown.Option("ESCUELA"),
                ft.dropdown.Option("COLEGIO"),
                ft.dropdown.Option("UNIVERSIDAD"),
                ft.dropdown.Option("ASOCIACION"),
            ],
        )

        self.nombre_input = ft.TextField(
            label="Nombre",
            autofocus=True,
            **INPUT_STYLE
        )

        self.correo_input = ft.TextField(
            label="Correo electrónico",
            **INPUT_STYLE
        )

        self.telefono_input = ft.TextField(
            label="Teléfono",
            **INPUT_STYLE
        )

        self.descripcion_input = ft.TextField(
            label="Descripción",
            multiline=True,
            min_lines=2,
            max_lines=3,
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
        )

        # =========================
        # Botones
        # =========================
        self.btn_cancelar = ft.TextButton(
            "Cancelar",
            on_click=lambda e: navigate("/contactos"),
        )

        self.btn_crear = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(ft.Icons.SAVE), ft.Text("Guardar contacto")],
                spacing=6,
            ),
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            on_click=self.crear_contacto,
        )

        # =========================
        # Header
        # =========================
        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Text(
                "Crear nuevo contacto",
                size=22,
                weight=ft.FontWeight.BOLD,
                color="#38638f",
            ),
        )

        # =========================
        # Formulario
        # =========================
        form = ft.Column(
            controls=[
                self.tipo_dd,
                self.nombre_input,
                self.correo_input,
                self.telefono_input,
                self.descripcion_input,
                ft.Row(
                    [self.btn_cancelar, self.btn_crear],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            spacing=14,
        )

        container = ft.Container(
            content=ft.Column(
                [header, form],
                spacing=20,
            ),
            padding=24,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            width=700,
        )

        self.controls = [
            ft.Row([container], alignment=ft.MainAxisAlignment.CENTER, expand=True)
        ]

    # =========================
    # Lógica
    # =========================
    def crear_contacto(self, e):
        try:
            tipo = (self.tipo_dd.value or "").strip().upper()
            correo_val = (self.correo_input.value or "").strip()

            if not tipo:
                self.mostrar_error("El tipo es obligatorio.")
                return

            if correo_val and "@" not in correo_val:
                self.mostrar_error("El correo electrónico debe contener '@'.")
                return

            self.db.crear_contacto(
                tipo=tipo,
                institucion="N/A",
                nombre=(self.nombre_input.value or "").strip() or None,
                correo=correo_val or None,
                telefono=(self.telefono_input.value or "").strip() or None,
                descripcion=(self.descripcion_input.value or "").strip() or None,
            )

            self._page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Contacto guardado correctamente"),
                bgcolor=ft.Colors.GREEN_500,
            )
            self._page.snack_bar.open = True
            self._page.update()

            self.navigate("/contactos")

        except Exception as ex:
            self.mostrar_error(str(ex))

    def mostrar_error(self, mensaje: str):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error"),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self.cerrar_dialogo(dialog))
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def cerrar_dialogo(self, dialog: ft.AlertDialog):
        dialog.open = False
        self._page.update()
