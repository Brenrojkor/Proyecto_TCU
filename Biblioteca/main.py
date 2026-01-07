import flet as ft
from controller.router import Router
from view.components.navbar import NavBar

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "Biblioteca - Flet"
    page.bgcolor = ft.Colors.BLACK  

    router = Router(page)

    page.appbar = NavBar(router.navigate)

    router.navigate("/")

ft.app(target=main)

