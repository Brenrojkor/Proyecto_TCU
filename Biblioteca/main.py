import flet as ft
from controller.router import Router
from model.database import Database
from view.components.navbar import NavBar


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "Biblioteca - Flet"
    page.bgcolor = ft.Colors.WHITE  

    page.padding = 0
    page.spacing = 0
    page.safe_area = False

    router = Router(page)
    content = ft.Column(expand=True)

    layout = ft.Column(
        spacing=0,
        expand=True,
        controls=[
            NavBar(page, router.navigate),  
            content
        ]
    )

    page.add(layout)

    router.set_container(content)
    router.navigate("/")


ft.app(target=main)
