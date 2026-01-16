import flet as ft
from model.database import Database


class UbicacionView(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self.db = Database()

        # =========================
        # Estilos (igual HomePage)
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
        self.sala_input = ft.TextField(
            label="Sala *",
            autofocus=True,
            **INPUT_STYLE
        )

        self.pasillo_input = ft.TextField(
            label="Pasillo",
            **INPUT_STYLE
        )

        self.estanteria_input = ft.TextField(
            label="Estantería",
            **INPUT_STYLE
        )

        self.nivel_input = ft.TextField(
            label="Nivel",
            **INPUT_STYLE
        )

        self.descripcion_input = ft.TextField(
            label="Descripción",
            multiline=True,
            min_lines=2,
            max_lines=3,
            max_length=255,
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
        )

        # =========================
        # Botones
        # =========================
        self.btn_cancelar = ft.TextButton(
            "Cancelar",
            on_click=lambda e: navigate("/"),
        )

        self.btn_crear = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(ft.Icons.SAVE), ft.Text("Guardar ubicación")],
                spacing=6,
            ),
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            on_click=self.crear_ubicacion,
        )

        # =========================
        # Header (igual HomePage)
        # =========================
        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Text(
                "Crear nueva ubicación",
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
                self.sala_input,
                self.pasillo_input,
                self.estanteria_input,
                self.nivel_input,
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
    # Lógica (SIN CAMBIOS)
    # =========================
    def crear_ubicacion(self, e):
        try:
            sala = (self.sala_input.value or "").strip()
            pasillo = (self.pasillo_input.value or "").strip()
            estanteria = (self.estanteria_input.value or "").strip()
            nivel = (self.nivel_input.value or "").strip()
            descripcion = (self.descripcion_input.value or "").strip()

            if not sala:
                self.mostrar_error("La sala es obligatoria.")
                return

            if len(sala) > 50:
                self.mostrar_error("La sala no puede exceder 50 caracteres.")
                return
            if pasillo and len(pasillo) > 50:
                self.mostrar_error("El pasillo no puede exceder 50 caracteres.")
                return
            if estanteria and len(estanteria) > 50:
                self.mostrar_error("La estantería no puede exceder 50 caracteres.")
                return
            if nivel and len(nivel) > 50:
                self.mostrar_error("El nivel no puede exceder 50 caracteres.")
                return
            if descripcion and len(descripcion) > 255:
                self.mostrar_error("La descripción no puede exceder 255 caracteres.")
                return

            self.db.crear_ubicacion(
                sala=sala,
                pasillo=pasillo if pasillo else None,
                estanteria=estanteria if estanteria else None,
                nivel=nivel if nivel else None,
                descripcion=descripcion if descripcion else None,
            )

            self._page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Ubicación guardada correctamente"),
                bgcolor=ft.Colors.GREEN_500,
            )
            self._page.snack_bar.open = True
            self._page.update()

            self.navigate("/")

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
