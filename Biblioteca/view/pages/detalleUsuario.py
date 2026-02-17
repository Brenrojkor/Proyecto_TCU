import flet as ft
from model.database import Database


class DetalleUsuarioPage(ft.Column):
    def __init__(self, navigate, page: ft.Page, id_usuario: int):
        super().__init__()
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self._page = page
        self.navigate = navigate
        self._db = Database()
        self.id_usuario = id_usuario

        # =========================
        # Helpers
        # =========================
        def snack(msg: str):
            self._page.snack_bar = ft.SnackBar(ft.Text(msg))
            self._page.snack_bar.open = True
            self._page.update()
            self._page.snack_bar = ft.SnackBar(ft.Text(msg))
            self._page.snack_bar.open = True
            self._page.update()

        # =========================
        # Obtener datos del usuario
        # =========================
        def cargar_usuario():
            try:
                usuario = self._db.get_usuario_detalle(id_usuario)
                return usuario
            except Exception as ex:
                snack(f"Error cargando usuario: {ex}")
                return None

        usuario = cargar_usuario()

        if not usuario:
            # Mostrar error si no se encontró el usuario
            self.controls = [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Usuario no encontrado", size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton(
                                "Volver",
                                on_click=lambda e: navigate("/usuarios"),
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
        # Widgets
        # =========================
        nombre_text = ft.Text(usuario.get("nombre_completo", "Sin nombre"), size=28, weight=ft.FontWeight.BOLD)

        # Obtener estado actual del usuario
        activo_value = usuario.get("activo")
        is_activo = bool(activo_value) and str(activo_value).lower() not in ("0", "false")

        activo_text = ft.Text(
            f"Estado: {'✓ Activo' if is_activo else '✗ Inactivo'}",
            size=14,
            color=ft.Colors.GREEN if is_activo else ft.Colors.RED,
            weight=ft.FontWeight.BOLD
        )

        comentario_text = ft.Text(
            usuario.get("comentario", "Sin comentario"),
            size=13,
            color=ft.Colors.GREY_800,
            selectable=True,
        )

        # Header (estilo páginas principales)
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row([
                        ft.Icon(ft.Icons.PEOPLE_ROUNDED, color="#1565c0", size=32),
                        ft.Text("Detalles del Usuario", size=26, weight=ft.FontWeight.BOLD, color="#263238"),
                    ], spacing=12),
                    ft.Row([
                        ft.TextButton("Volver", on_click=lambda e: navigate("/usuarios")),
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

        # Tarjeta principal con sombra
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
                    # Columna izquierda: información principal
                    ft.Container(
                        content=ft.Column([
                            nombre_text,
                            ft.Divider(height=6, color="transparent"),
                            ft.Row([
                                ft.Column([
                                    ft.Text("Información General", weight=ft.FontWeight.BOLD, size=16, color="#1976d2"),
                                    ft.Divider(height=8, color="transparent"),
                                    ft.Column([
                                        ft.Row([
                                            ft.Text("Identificación:", weight=ft.FontWeight.BOLD, size=13),
                                            ft.Text(usuario.get('identificacion', 'N/A'), size=13, color=ft.Colors.GREY_700),
                                        ]),
                                        ft.Row([
                                            ft.Text("Provincia:", weight=ft.FontWeight.BOLD, size=13),
                                            ft.Text(usuario.get('provincia', 'N/A'), size=13, color=ft.Colors.GREY_700),
                                        ]),
                                        ft.Row([
                                            ft.Text("Cantón:", weight=ft.FontWeight.BOLD, size=13),
                                            ft.Text(usuario.get('canton', 'N/A'), size=13, color=ft.Colors.GREY_700),
                                        ]),
                                        ft.Row([
                                            ft.Text("Distrito:", weight=ft.FontWeight.BOLD, size=13),
                                            ft.Text(usuario.get('distrito', 'N/A'), size=13, color=ft.Colors.GREY_700),
                                        ]),
                                        ft.Row([
                                            ft.Text("Teléfono:", weight=ft.FontWeight.BOLD, size=13),
                                            ft.Text(usuario.get('telefono', 'N/A'), size=13, color=ft.Colors.GREY_700),
                                        ]),
                                        ft.Row([
                                            ft.Text("Rango de Edad:", weight=ft.FontWeight.BOLD, size=13),
                                            ft.Text(usuario.get('rango_edad', 'N/A'), size=13, color=ft.Colors.GREY_700),
                                        ]),
                                        ft.Row([
                                            ft.Text("Sexo:", weight=ft.FontWeight.BOLD, size=13),
                                            ft.Text(usuario.get('sexo', 'N/A'), size=13, color=ft.Colors.GREY_700),
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

                            ft.Text("Comentario", weight=ft.FontWeight.BOLD, size=16, color="#1976d2"),
                            ft.Divider(height=8, color="transparent"),
                            ft.Container(
                                content=comentario_text,
                                padding=12,
                                bgcolor="#f5f5f5",
                                border_radius=8,
                            ),

                            ft.Divider(height=8, color="transparent"),
                        ], spacing=12),
                        expand=True,
                    ),

                    # Columna derecha: información adicional
                    ft.Container(
                        width=340,
                        padding=8,
                        content=ft.Column([
                            ft.Divider(height=8, color="transparent"),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Año", size=13, weight=ft.FontWeight.BOLD, color="#1976d2"),
                                    ft.Text(str(usuario.get("anio", "N/A")), size=13, color=ft.Colors.GREY_700),
                                    ft.Divider(height=8, color="transparent"),
                                    ft.Text("Curso", size=13, weight=ft.FontWeight.BOLD, color="#1976d2"),
                                    ft.Text(usuario.get("curso", "N/A"), size=13, color=ft.Colors.GREY_700),
                                ], spacing=8),
                                padding=10,
                                bgcolor="#fafafa",
                                border_radius=8,
                            ),

                            ft.Divider(height=12, color="transparent"),

                            ft.Text("Características", weight=ft.FontWeight.BOLD, size=14, color="#1976d2"),
                            ft.Divider(height=8, color="transparent"),
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([
                                        ft.Text("Discapacidad:", weight=ft.FontWeight.BOLD, size=13),
                                        ft.Text("Sí" if usuario.get("discapacidad") else "No", size=13, color=ft.Colors.GREY_700),
                                    ]),
                                    ft.Row([
                                        ft.Text("Grupo:", weight=ft.FontWeight.BOLD, size=13),
                                        ft.Text("Sí" if usuario.get("grupo") else "No", size=13, color=ft.Colors.GREY_700),
                                    ]),
                                ], spacing=8),
                                padding=10,
                                bgcolor="#fafafa",
                                border_radius=8,
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
