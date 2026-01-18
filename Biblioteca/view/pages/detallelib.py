import flet as ft
from model.database import Database


class DetalleLibroPage(ft.Column):
    def __init__(self, navigate, page: ft.Page, id_libro: int):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self._db = Database()
        self.id_libro = id_libro

        # =========================
        # Helpers
        # =========================
        def snack(msg: str):
            self._page.snack_bar = ft.SnackBar(ft.Text(msg))
            self._page.snack_bar.open = True
            self._page.update()

        def open_file_default_app(path: str):
            import os
            import sys
            try:
                if sys.platform.startswith("win"):
                    os.startfile(path)
                elif sys.platform == "darwin":
                    os.system(f'open "{path}"')
                else:
                    os.system(f'xdg-open "{path}"')
            except Exception as ex:
                snack(f"No se pudo abrir el archivo: {ex}")

        # =========================
        # Obtener datos del libro
        # =========================
        def cargar_libro():
            try:
                libro = self._db.get_libro_detalle(id_libro)
                return libro
            except Exception as ex:
                snack(f"Error cargando libro: {ex}")
                return None

        libro = cargar_libro()

        if not libro:
            # Mostrar error si no se encontró el libro
            self.controls = [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Libro no encontrado", size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton(
                                "Volver",
                                on_click=lambda e: navigate("/"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20,
                    expand=True,
                )
            ]
            return

        # =========================
        # Verificar si tiene PDF
        # =========================
        tiene_pdf = self._db.has_libro_pdf(id_libro)

        # =========================
        # Widgets
        # =========================
        titulo_text = ft.Text(libro.get("titulo", "Sin título"), size=28, weight=ft.FontWeight.BOLD)
        
        categoria_text = ft.Text(
            f"Categoría: {libro.get('categoria', 'N/A')}",
            size=14,
            color=ft.Colors.GREY_700
        )

        isbn_text = ft.Text(
            f"ISBN: {libro.get('isbn', 'N/A')}",
            size=14,
            color=ft.Colors.GREY_700
        )

        tipo_text = ft.Text(
            f"Tipo: {libro.get('tipo', 'N/A')}",
            size=14,
            color=ft.Colors.GREY_700
        )

        año_text = ft.Text(
            f"Año de Publicación: {libro.get('anio_publicacion', 'N/A')}",
            size=14,
            color=ft.Colors.GREY_700
        )

        edicion_text = ft.Text(
            f"Edición: {libro.get('edicion', 'N/A')}",
            size=14,
            color=ft.Colors.GREY_700
        )

        activo_value = libro.get("activo")
        is_activo = bool(activo_value) and str(activo_value).lower() not in ("0", "false")

        activo_text = ft.Text(
            f"Estado: {'✓ Activo' if is_activo else '✗ Inactivo'}",
            size=14,
            color=ft.Colors.GREEN if is_activo else ft.Colors.RED,
            weight=ft.FontWeight.BOLD
        )

        descripcion_text = ft.Text(
            libro.get("descripcion", "Sin descripción"),
            size=13,
            color=ft.Colors.GREY_800,
            selectable=True,
        )

        # PDF Section
        if libro.get("tipo", "").upper() == "DIGITAL":
            if tiene_pdf:
                pdf_info = self._db.get_libro_pdf(id_libro)
                pdf_section = ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("📄 Documento PDF Adjuntado", weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(f"Nombre: {pdf_info.get('nombre_archivo', 'N/A')}", size=12),
                            ft.Text(f"Fecha de carga: {pdf_info.get('fecha_subida', 'N/A')}", size=12, color=ft.Colors.GREY_700),
                        ],
                        spacing=8,
                    ),
                    padding=12,
                    bgcolor="#e8f5e9",
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.GREEN_200),
                )
            else:
                pdf_section = ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("⚠️ Sin documento PDF", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.ORANGE),
                            ft.Text("Este libro aún no tiene un PDF asociado.", size=12, color=ft.Colors.GREY_700),
                        ],
                        spacing=8,
                    ),
                    padding=12,
                    bgcolor="#fff3e0",
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.ORANGE_200),
                )
        else:
            pdf_section = ft.Container(
                content=ft.Text("📕 Libro Físico - No requiere PDF", size=12, color=ft.Colors.GREY_700),
                padding=12,
                bgcolor="#f5f5f5",
                border_radius=8,
            )

        # Header
        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.INFO, color="#38638f", size=32),
                    ft.Text("Detalles del Libro", size=24, weight=ft.FontWeight.BOLD, color="#38638f"),
                ],
                spacing=15,
            ),
        )

        # Action buttons
        btn_volver = ft.ElevatedButton(
            "Volver a libros",
            on_click=lambda e: navigate("/"),
            icon=ft.Icons.ARROW_BACK,
        )

        btn_editar = ft.ElevatedButton(
            "Editar libro",
            on_click=lambda e: navigate(f"/editlib/{id_libro}"),
            icon=ft.Icons.EDIT,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.ORANGE,
            ),
        )

        # Main container
        content = ft.Column(
            [
                header,
                ft.Container(
                    content=ft.Column(
                        [
                            titulo_text,
                            ft.Divider(height=20, color="transparent"),
                            ft.Text("Información General", weight=ft.FontWeight.BOLD, size=16),
                            ft.Column(
                                [
                                    categoria_text,
                                    isbn_text,
                                    tipo_text,
                                    año_text,
                                    edicion_text,
                                    activo_text,
                                ],
                                spacing=8,
                            ),
                            ft.Divider(height=20, color="transparent"),
                            ft.Text("Descripción", weight=ft.FontWeight.BOLD, size=16),
                            ft.Container(
                                content=descripcion_text,
                                padding=12,
                                bgcolor="#f5f5f5",
                                border_radius=8,
                            ),
                            ft.Divider(height=20, color="transparent"),
                            ft.Text("Documento", weight=ft.FontWeight.BOLD, size=16),
                            pdf_section,
                            ft.Divider(height=30, color="transparent"),
                        ],
                        spacing=12,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    padding=20,
                ),
                ft.Row(
                    [btn_volver, btn_editar],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=10,
            expand=True,
        )

        container = ft.Container(
            content=content,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            expand=True,
        )

        self.controls = [ft.Row([container], expand=True)]
