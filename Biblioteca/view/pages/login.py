import flet as ft
from model.database import Database

class LoginPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self._page = page
        self.navigate = navigate
        self._db = Database()

        def snack(msg: str, error: bool = False):
            bg_color = ft.Colors.RED if error else ft.Colors.GREEN
            self._page.snack_bar = ft.SnackBar(
                ft.Text(msg, color=ft.Colors.WHITE),
                bgcolor=bg_color,
            )
            self._page.snack_bar.open = True
            self._page.update()

        username_input = ft.TextField(
            label="Usuario",
            prefix_icon=ft.Icons.PERSON,
            width=300,
            height=50,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        password_input = ft.TextField(
            label="Contraseña",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            width=300,
            height=50,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        def on_login_click(e):
            username = (username_input.value or "").strip()
            password = (password_input.value or "").strip()

            if not username or not password:
                snack("Por favor completa todos los campos", error=True)
                return

            try:
                # Placeholder de autenticación
                if username == "admin" and password == "admin":
                    snack("Login exitoso ✅")
                    navigate("/home")
                else:
                    snack("Usuario o contraseña incorrectos", error=True)
            except Exception as ex:
                snack(f"Error: {ex}", error=True)

        btn_login = ft.ElevatedButton(
            content=ft.Text("Ingresar", size=16, weight=ft.FontWeight.BOLD),
            width=300,
            height=50,
            bgcolor="#0b495c",
            color=ft.Colors.WHITE,
            on_click=on_login_click,
        )

        btn_register = ft.TextButton(
            content=ft.Text("¿No tienes cuenta? Regístrate aquí"),
            on_click=lambda e: navigate("/registro"),
        )

        form_container = ft.Container(
            padding=32,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border=ft.border.all(1, "#d0d7de"),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            ),
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=120, color="#1B6F7A"),
                    ft.Divider(height=12, color="transparent"),

                    ft.Text(
                        "Iniciar Sesión",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color="#000000",
                        text_align=ft.TextAlign.CENTER,
                    ),

                    ft.Divider(height=8, color="transparent"),

                    ft.Text(
                        "Accede a tu cuenta para continuar",
                        size=14,
                        color="#666",
                        text_align=ft.TextAlign.CENTER,
                    ),

                    ft.Divider(height=20, color="transparent"),

                    username_input,
                    ft.Divider(height=12, color="transparent"),
                    password_input,
                    ft.Divider(height=20, color="transparent"),
                    btn_login,
                    ft.Divider(height=12, color="transparent"),
                    btn_register,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
        )
        
        container = ft.Container(
            content=ft.Column(
                [
                    ft.Divider(height=12, color="transparent"),
                    form_container,
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=20,
            bgcolor="#f8f9fa",
            expand=True,
        )

        self.controls = [container]
