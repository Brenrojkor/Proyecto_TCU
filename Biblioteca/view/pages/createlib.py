import flet as ft
from model.database import Database


class CrearLibroPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self.db = Database()

        # =========================
        # Estilos reutilizados (HomePage)
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
        self.titulo_input = ft.TextField(
            label="Título *",
            autofocus=True,
            **INPUT_STYLE
        )

        self.isbn_input = ft.TextField(
            label="ISBN",
            **INPUT_STYLE
        )

        self.anio_input = ft.TextField(
            label="Año de publicación",
            hint_text="YYYY (ej: 2024)",
            keyboard_type=ft.KeyboardType.NUMBER,
            **INPUT_STYLE
        )

        self.edicion_input = ft.TextField(
            label="Edición",
            **INPUT_STYLE
        )

        self.tipo_dd = ft.Dropdown(
            label="Tipo *",
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
            options=[
                ft.dropdown.Option("FISICO"),
                ft.dropdown.Option("DIGITAL"),
            ],
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
        # Categorías
        # =========================
        cats = self.db.get_categorias()
        self.categoria_dd = ft.Dropdown(
            label="Categoría *",
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
            options=[
                ft.dropdown.Option(key=str(c["id_categoria"]), text=c["nombre"])
                for c in cats
            ],
        )

        # =========================
        # Ubicaciones
        # =========================
        ubis = self.db.get_ubicaciones()

        def ubicacion_text(u: dict) -> str:
            sala = u.get("sala", "")
            pasillo = u.get("pasillo") or "N/A"
            est = u.get("estanteria") or "N/A"
            nivel = u.get("nivel") or "N/A"
            desc = (u.get("descripcion") or "").strip()

            base = f"Sala {sala} | Pasillo {pasillo} | Estantería {est} | Nivel {nivel}"
            return f"{base} - {desc}" if desc else base

        self.ubicacion_dd = ft.Dropdown(
            label="Ubicación *",
            width=260,
            bgcolor="#f5f7fa",
            border_radius=8,
            options=[
                ft.dropdown.Option(
                    key=str(u["id_ubicacion"]),
                    text=ubicacion_text(u)
                )
                for u in ubis
            ],
        )

        self.btn_nueva_ubicacion = ft.IconButton(
            icon=ft.Icons.ADD_LOCATION_ALT,
            tooltip="Crear nueva ubicación",
            icon_color="#1976d2",
            on_click=lambda e: navigate("/ubicacion"),
        )

        # =========================
        # Autores
        # =========================
        self.autores_ids_input = ft.TextField(
            label="Autores (IDs separados por coma)",
            **INPUT_STYLE
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
                [ft.Icon(ft.Icons.SAVE), ft.Text("Guardar libro")],
                spacing=6,
            ),
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            on_click=self.crear_libro,
        )

        # =========================
        # Header (igual al HomePage)
        # =========================
        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Text(
                "Crear nuevo libro",
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
                self.titulo_input,
                self.isbn_input,
                self.anio_input,
                self.edicion_input,
                self.tipo_dd,
                self.descripcion_input,
                self.categoria_dd,
                ft.Row(
                    [self.ubicacion_dd, self.btn_nueva_ubicacion],
                    spacing=8,
                ),
                self.autores_ids_input,
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
    def crear_libro(self, e):
        try:
            titulo = (self.titulo_input.value or "").strip()
            tipo = (self.tipo_dd.value or "").strip()

            if not titulo:
                self.mostrar_error("El título es obligatorio.")
                return

            if not tipo:
                self.mostrar_error("El tipo es obligatorio.")
                return

            if not self.categoria_dd.value:
                self.mostrar_error("Debe seleccionar una categoría.")
                return

            if not self.ubicacion_dd.value:
                self.mostrar_error("Debe seleccionar una ubicación.")
                return

            anio = (self.anio_input.value or "").strip()
            anio_publicacion = int(anio) if anio else None

            autores_csv = (self.autores_ids_input.value or "").strip()

            self.db.crear_libro(
                titulo=titulo,
                isbn=(self.isbn_input.value or "").strip(),
                anio_publicacion=anio_publicacion,
                edicion=(self.edicion_input.value or "").strip(),
                tipo=tipo,
                descripcion=(self.descripcion_input.value or "").strip(),
                id_categoria=int(self.categoria_dd.value),
                activo=1,
                autores_ids_csv=autores_csv if autores_csv else None,
                id_ubicacion=int(self.ubicacion_dd.value),
            )

            self._page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Libro guardado correctamente"),
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
