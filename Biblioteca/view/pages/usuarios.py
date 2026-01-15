import flet as ft
from model.database import Database

class UsuariosPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self.db = Database()
        self.dialog = None
        self.usuario_editando = None
        self._usuarios_cache = []

        # =========================
        # BOTÓN CREAR
        # =========================

        self.btn_crear = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(ft.Icons.ADD), ft.Text("Crear usuario")],
                spacing=8,
            ),
            on_click=self.abrir_dialogo_crear,
        )

        # =========================
        # BUSCADOR
        # =========================

        self.search_input = ft.TextField(
            hint_text="Buscar usuario...",
            prefix_icon=ft.Icons.SEARCH,
            width=320,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
            on_change=self.on_search_change,
        )

        # =========================
        # TABLA USUARIOS
        # =========================

        self.usuarios_table = ft.DataTable(
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, "#d0d7de"),
            border_radius=8,
            width=1100,
            heading_row_color="#e3f2fd",
            heading_row_height=48,
            data_row_min_height=52,
            data_row_max_height=52,
            column_spacing=50,
            horizontal_margin=16,
            columns=[
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(ft.Text("Email", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(ft.Text("Rol", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(ft.Text("Activo", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(ft.Text("Fecha registro", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, color="#0d47a1")),
            ],
            rows=[],
        )

        # =========================
        # HEADER
        # =========================

        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Row(
                [
                    ft.Text(
                        "Usuarios Registrados",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color="#38638f",
                    ),
                    self.btn_crear,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        container = ft.Container(
            content=ft.Column(
                [
                    header,
                    ft.Row([self.search_input], alignment=ft.MainAxisAlignment.END),
                    ft.Row([self.usuarios_table], alignment=ft.MainAxisAlignment.CENTER),
                ],
                spacing=20,
            ),
            padding=20,
            expand=True,
        )

        self.controls = [
            ft.Row([container], alignment=ft.MainAxisAlignment.CENTER, expand=True)
        ]

        self.mostrar_usuarios()

    # =========================
    # BOTÓN ACCIÓN
    # =========================

    def action_button(self, icon, color, tooltip, on_click=None):
        return ft.Container(
            width=36,
            height=36,
            bgcolor=color,
            border_radius=6,
            alignment=ft.Alignment.CENTER,
            tooltip=tooltip,
            on_click=on_click,
            content=ft.Icon(icon, color=ft.Colors.WHITE, size=18),
        )

    # =========================
    # BUSCAR
    # =========================

    def on_search_change(self, e):
        texto = (e.control.value or "").lower()
        self.usuarios_table.rows.clear()

        for u in self._usuarios_cache:
            if texto in u["Nombre"].lower() or texto in u["Email"].lower():
                self.usuarios_table.rows.append(self._build_row(u))

        self._page.update()

    # =========================
    # CRUD VISUAL
    # =========================

    def abrir_dialogo_crear(self, e):
        # aquí luego conectas con tu SP de crear usuario
        pass

    # =========================
    # TABLA
    # =========================

    def _format_fecha(self, fecha):
        """Formatea la fecha a formato: DD/MM/YYYY HH:MM"""
        if not fecha:
            return ""
        try:
            from datetime import datetime
            if isinstance(fecha, str):
                # Si es string, intenta parsear
                dt = datetime.fromisoformat(fecha)
            else:
                dt = fecha
            return dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            return str(fecha)

    def _build_row(self, u):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(u["Nombre"], text_align=ft.TextAlign.CENTER)),
                ft.DataCell(ft.Text(u["Email"], text_align=ft.TextAlign.CENTER)),
                ft.DataCell(ft.Text(u["Rol"], text_align=ft.TextAlign.CENTER)),
                ft.DataCell(ft.Text("Activo" if u["Activo"] else "Inactivo", text_align=ft.TextAlign.CENTER)),
                ft.DataCell(ft.Text(self._format_fecha(u["Fecha_Registro"]), text_align=ft.TextAlign.CENTER)),
                ft.DataCell(
                    ft.Row(
                        [
                            self.action_button(
                                ft.Icons.EDIT,
                                ft.Colors.ORANGE,
                                "Editar",
                            ),
                            self.action_button(
                                ft.Icons.BLOCK,
                                ft.Colors.RED,
                                "Activar / Desactivar",
                            ),
                        ],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER,
                    )
                ),
            ]
        )

    # =========================
    # CARGAR USUARIOS
    # =========================

    def mostrar_usuarios(self):
        self.usuarios_table.rows.clear()
        self._usuarios_cache = self.db.get_usuarios()  # ← sp_VerUsuarios_Seguro

        for u in self._usuarios_cache:
            self.usuarios_table.rows.append(self._build_row(u))

        self._page.update()
