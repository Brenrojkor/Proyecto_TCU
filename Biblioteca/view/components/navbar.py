import flet as ft

def NavBar(navigate):
    return ft.AppBar(
        title=ft.Text("📚 Biblioteca"),
        center_title=False,
        bgcolor=ft.Colors.BLUE_600,
        leading=ft.IconButton(ft.Icons.MENU, tooltip="Menú"),
        actions=[
            ft.TextButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.Icons.HOME), ft.Text("Inicio")],
                    spacing=5
                ),
                tooltip="Inicio",
                on_click=lambda _: navigate("/")
            ),
            ft.TextButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.Icons.BOOK), ft.Text("Libros")],
                    spacing=5
                ),
                tooltip="Libros",
                on_click=lambda _: navigate("/libros")
            ),
            ft.TextButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.Icons.ADD_CHART_SHARP), ft.Text("Categorías")],
                    spacing=5
                ),
                tooltip="Categorías",
                on_click=lambda _: navigate("/categorias")
            ),
            ft.TextButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.Icons.PERSON), ft.Text("Autores")],
                    spacing=5
                ),
                tooltip="Autores",
                on_click=lambda _: navigate("/autores")
            ),
            ft.TextButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.Icons.LOGOUT), ft.Text("Salir")],
                    spacing=5
                ),
                tooltip="Salir",
                on_click=lambda _: navigate("/logout")
            ),
        ]
    )
