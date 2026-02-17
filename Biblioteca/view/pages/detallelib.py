import flet as ft
from model.database import Database
from datetime import datetime
import os
import tempfile


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

        def safe_filename(name: str) -> str:
            import re
            name = (name or "").strip()
            name = re.sub(r"[^\w\-. ]+", "", name, flags=re.UNICODE)
            if not name.lower().endswith(".pdf"):
                name += ".pdf"
            return name[:150] if name else "documento.pdf"

        def format_fecha(valor) -> str:
            if not valor:
                return "N/A"
            if isinstance(valor, datetime):
                return valor.strftime("%d-%m-%Y")
            if hasattr(valor, "strftime"):
                try:
                    return valor.strftime("%d-%m-%Y")
                except Exception:
                    pass
            s = str(valor).strip()
            formatos = [
                "%Y-%m-%d",
                "%Y-%m-%d %H:%M:%S",
                "%d/%m/%Y",
                "%d/%m/%Y %H:%M:%S",
            ]
            for fmt in formatos:
                try:
                    return datetime.strptime(s, fmt).strftime("%d-%m-%Y")
                except Exception:
                    pass
            try:
                return datetime.fromisoformat(s).strftime("%d-%m-%Y")
            except Exception:
                return s

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
                autores_dict = {str(a.get("id_autor", "")): a.get("nombre_completo", "") for a in autores_list}
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
                fecha_subida = format_fecha(pdf_info.get('fecha_subida', 'N/A'))
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

        def descargar_pdf(e=None):
            if not (tiene_pdf and pdf_info):
                snack("Este libro no tiene PDF.")
                return
            try:
                contenido = pdf_info.get("contenido")
                if contenido is None:
                    snack("El PDF está vacío.")
                    return
                pdf_bytes = bytes(contenido)
                nombre = safe_filename(pdf_info.get("nombre_archivo") or f"libro_{id_libro}.pdf")
                out_path = os.path.join(tempfile.gettempdir(), f"libro_{id_libro}_{nombre}")
                with open(out_path, "wb") as f:
                    f.write(pdf_bytes)
                open_file_default_app(out_path)
            except Exception as ex:
                snack(f"No se pudo descargar el PDF: {ex}")

        # Header (estilo páginas principales)
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row([
                        ft.Icon(ft.Icons.MENU_BOOK_ROUNDED, color="#1565c0", size=32),
                        ft.Text("Detalles del Libro", size=26, weight=ft.FontWeight.BOLD, color="#263238"),
                    ], spacing=12),
                    ft.Row([
                        ft.TextButton("Volver", on_click=lambda e: navigate("/")),
                    ], spacing=8),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(horizontal=30, vertical=20),
            margin=ft.margin.symmetric(horizontal=30),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

        # Tarjeta principal con sombra (alineada al estilo de otras páginas)
        card = ft.Container(
            width=1100,
            padding=24,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(1, "#e0e0e0"),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
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
                                content=ft.Row([
                                    ft.Icon(ft.Icons.DOWNLOAD, size=18),
                                    ft.Text("Descargar PDF", size=13, weight=ft.FontWeight.W_500),
                                ], spacing=8),
                                on_click=descargar_pdf,
                                disabled=not (tiene_pdf and pdf_info),
                                bgcolor="#1976d2",
                                color=ft.Colors.WHITE,
                                height=40,
                                width=170,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    elevation=2,
                                ),
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
            bgcolor="#f5f7fa",
            padding=ft.padding.symmetric(vertical=20),
            content=ft.Column(
                [
                    header,
                    ft.Container(
                        content=ft.Row([card], alignment=ft.MainAxisAlignment.CENTER),
                        padding=ft.padding.symmetric(horizontal=30),
                    ),
                ],
                spacing=20,
                expand=True,
            ),
            expand=True,
        )

        # Asignar controles
        self.controls = [wrapper]
