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
        # Función para convertir IDs de autores a nombres
        # =========================
        def obtener_nombres_autores(autores_csv: str) -> str:
            if not autores_csv or autores_csv == "N/A":
                return "N/A"
            try:
                autores_list = self._db.get_autores()
                autores_dict = {str(a.get("id_autor", "")): a.get("nombre", "") for a in autores_list}
                ids = [id.strip() for id in str(autores_csv).split(",")]
                nombres = [autores_dict.get(id, "") for id in ids if id and autores_dict.get(id)]
                return ", ".join(nombres) if nombres else autores_csv
            except:
                return autores_csv

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
        pdf_info = None
        if libro.get("tipo", "").upper() == "DIGITAL":
            if tiene_pdf:
                pdf_info = self._db.get_libro_pdf(id_libro)
                fecha_subida = pdf_info.get('fecha_subida', 'N/A')
                if fecha_subida and fecha_subida != 'N/A':
                    try:
                        fecha_str = str(fecha_subida)
                        fecha_date = fecha_str.split(" ")[0] if " " in fecha_str else fecha_str.split("T")[0] if "T" in fecha_str else fecha_str
                        fecha_subida = fecha_date
                    except:
                        pass
                pdf_section = ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("📄 Documento PDF Adjuntado", weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(f"Nombre: {pdf_info.get('nombre_archivo', 'N/A')}", size=12),
                            ft.Text(f"Fecha de carga: {fecha_subida}", size=12, color=ft.Colors.GREY_700),
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

        # Header (estilo Contactos)
        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Row(
                [
                    ft.Text("Detalles del Libro", size=22, weight=ft.FontWeight.BOLD, color="#38638f"),
                    ft.Row([
                        ft.TextButton("Volver", on_click=lambda e: navigate("/")),
                        ft.ElevatedButton("Editar", icon=ft.Icons.EDIT, bgcolor=ft.Colors.ORANGE, color=ft.Colors.WHITE, on_click=lambda e: navigate(f"/editlib/{id_libro}")),
                    ], spacing=8),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        # Tarjeta principal con sombra (alineada al estilo de otras páginas)
        card = ft.Container(
            width=980,
            padding=24,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(1, "#d0d7de"),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=12, color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK)),
            content=ft.Row(
                [
                    # Columna izquierda: información principal (expandible)
                    ft.Container(
                        content=ft.Column([
                            titulo_text,
                            ft.Divider(height=6, color="transparent"),
                            ft.Row([
                                ft.Column([
                                    ft.Text("Información General", weight=ft.FontWeight.BOLD, size=16, color="#1976d2"),
                                    ft.Divider(height=8, color="transparent"),
                                    ft.Column([
                                        ft.Row([
                                            ft.Text("Categoría:", weight=ft.FontWeight.BOLD, size=13),
                                            ft.Text(libro.get('categoria', 'N/A'), size=13, color=ft.Colors.GREY_700),
                                        ]),
                                        ft.Row([
                                            ft.Text("ISBN:", weight=ft.FontWeight.BOLD, size=13),
                                            ft.Text(libro.get('isbn', 'N/A'), size=13, color=ft.Colors.GREY_700),
                                        ]),
                                        ft.Row([
                                            ft.Text("Tipo:", weight=ft.FontWeight.BOLD, size=13),
                                            ft.Text(libro.get('tipo', 'N/A'), size=13, color=ft.Colors.GREY_700),
                                        ]),
                                        ft.Row([
                                            ft.Text("Año de Publicación:", weight=ft.FontWeight.BOLD, size=13),
                                            ft.Text(str(libro.get('anio_publicacion', 'N/A')), size=13, color=ft.Colors.GREY_700),
                                        ]),
                                        ft.Row([
                                            ft.Text("Edición:", weight=ft.FontWeight.BOLD, size=13),
                                            ft.Text(libro.get('edicion', 'N/A'), size=13, color=ft.Colors.GREY_700),
                                        ]),
                                        ft.Row([
                                            ft.Text("Estado:", weight=ft.FontWeight.BOLD, size=13),
                                            ft.Text(
                                                f"{'✓ Activo' if is_activo else '✗ Inactivo'}",
                                                size=13,
                                                color=ft.Colors.GREEN if is_activo else ft.Colors.RED,
                                                weight=ft.FontWeight.BOLD
                                            ),
                                        ]),
                                    ], spacing=10),
                                ]),
                            ], alignment=ft.MainAxisAlignment.START),

                            ft.Divider(height=18, color="transparent"),

                            ft.Text("Descripción", weight=ft.FontWeight.BOLD, size=16, color="#1976d2"),
                            ft.Divider(height=8, color="transparent"),
                            ft.Container(
                                content=descripcion_text,
                                padding=12,
                                bgcolor="#f5f5f5",
                                border_radius=8,
                            ),

                            ft.Divider(height=8, color="transparent"),
                        ], spacing=12),
                        expand=True,
                    ),

                    # Columna derecha: PDF / metadata / acciones rápidas
                    ft.Container(
                        width=340,
                        padding=8,
                        content=ft.Column([
                            ft.Text("Información rápida", weight=ft.FontWeight.BOLD, size=14, color="#1976d2"),
                            ft.Divider(height=8, color="transparent"),
                            pdf_section,
                            ft.Divider(height=12, color="transparent"),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Autores", size=13, weight=ft.FontWeight.BOLD, color="#1976d2"),
                                    ft.Text(obtener_nombres_autores(libro.get("autores", "")), size=13, color=ft.Colors.GREY_700),
                                ], spacing=8),
                                padding=10,
                                bgcolor="#fafafa",
                                border_radius=8,
                            ),

                            ft.Divider(height=12, color="transparent"),

                            ft.ElevatedButton(
                                "Descargar PDF",
                                icon=ft.Icons.DOWNLOAD,
                                on_click=lambda e: open_file_default_app(pdf_info.get("nombre_archivo")) if (tiene_pdf and pdf_info) else None,
                                disabled=not (tiene_pdf and pdf_info),
                            ),

                        ], spacing=12),
                    ),
                ],
                spacing=20,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        )

        # Composición final
        wrapper = ft.Container(
            padding=20,
            content=ft.Column([
                header,
                ft.Divider(height=12, color="transparent"),
                ft.Row([card], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(height=18, color="transparent"),
            ], spacing=8, expand=True)
        )

        # Asignar controles
        self.controls = [wrapper]
