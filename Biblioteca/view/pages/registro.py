import flet as ft
from model.database import Database
import re


class RegistroPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
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

        def is_valid_email(email: str) -> bool:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(pattern, email) is not None

        nombre_input = ft.TextField(
            label="Nombre completo",
            prefix_icon=ft.Icons.PERSON,
            width=300,
            height=50,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        email_input = ft.TextField(
            label="Correo electrónico",
            prefix_icon=ft.Icons.EMAIL,
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

        password_confirm_input = ft.TextField(
            label="Confirmar contraseña",
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            width=300,
            height=50,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        def on_register_click(e):
            nombre = (nombre_input.value or "").strip()
            email = (email_input.value or "").strip()
            password = (password_input.value or "").strip()
            password_confirm = (password_confirm_input.value or "").strip()

            # Validaciones
            if not nombre or not email or not password or not password_confirm:
                snack("Por favor completa todos los campos", error=True)
                return

            if len(nombre) < 3:
                snack("El nombre debe tener al menos 3 caracteres", error=True)
                return

            if not is_valid_email(email):
                snack("Por favor ingresa un correo válido", error=True)
                return

            if len(password) < 6:
                snack("La contraseña debe tener al menos 6 caracteres", error=True)
                return

            if password != password_confirm:
                snack("Las contraseñas no coinciden", error=True)
                return

            try:
                snack("¡Registro exitoso! Ahora puedes iniciar sesión ✅")
                nombre_input.value = ""
                email_input.value = ""
                password_input.value = ""
                password_confirm_input.value = ""
                self._page.update()
                import time
                time.sleep(1)
                navigate("/login")
            except Exception as ex:
                snack(f"Error: {ex}", error=True)

        btn_register = ft.ElevatedButton(
            content=ft.Text("Registrarse", size=16, weight=ft.FontWeight.BOLD),
            width=300,
            height=50,
            bgcolor="#0b495c",
            color=ft.Colors.WHITE,
            on_click=on_register_click,
        )

        btn_login = ft.TextButton(
            content=ft.Text("¿Ya tienes cuenta? Inicia sesión aquí"),
            on_click=lambda e: navigate("/login"),
        )

        form_container = ft.Container(
            padding=40,
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
                    ft.Icon(ft.Icons.APP_REGISTRATION, size=120, color="#1B6F7A"),
                    ft.Divider(height=20, color="transparent"),
                    ft.Text(
                        "Crear Cuenta",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color="#000000",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=10, color="transparent"),
                    ft.Text(
                        "Completa el formulario para registrarte",
                        size=14,
                        color="#666",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=30, color="transparent"),
                    nombre_input,
                    ft.Divider(height=16, color="transparent"),
                    email_input,
                    ft.Divider(height=16, color="transparent"),
                    password_input,
                    ft.Divider(height=16, color="transparent"),
                    password_confirm_input,
                    ft.Divider(height=24, color="transparent"),
                    btn_register,
                    ft.Divider(height=16, color="transparent"),
                    btn_login,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
        )

        container = ft.Container(
            content=ft.Column(
                [
                    ft.Divider(height=20, color="transparent"),
                    ft.Divider(height=20, color="transparent"),
                    form_container,
                    ft.Divider(height=40, color="transparent"),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=20,
            bgcolor="#f8f9fa",
            expand=True,
        )

        self.controls = [container]
