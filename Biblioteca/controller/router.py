import flet as ft
from view.pages.home import HomePage
from view.pages.categorias import CategoriasPage
from view.components.navbar import NavBar  
from view.pages.createlib import CrearLibroPage
from view.pages.autores import AutoresPage
from view.pages.ubicacionView import UbicacionView
from view.pages.login import LoginPage
from view.pages.registro import RegistroPage
from view.pages.usuarios import UsuariosPage

class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.container = None

        #Rutas
        self.routes = {
            "/": HomePage,
            "/categorias": CategoriasPage,
             "/createlib": CrearLibroPage,
             "/autores": AutoresPage,
             "/ubicacion": UbicacionView,
             "/login": LoginPage,
             "/registro": RegistroPage,
             "/usuarios": UsuariosPage,
             
        }

    def set_container(self, container: ft.Column):
            self.container = container

    def navigate(self, route: str):
        self.container.controls.clear()

        view = self.routes.get(route, self.not_found)
        self.container.controls.append(view(self.navigate, self.page))

        self.page.update()

    def not_found(self, navigate, page):
         return ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[ft.Text("404 - Página no encontrada")]
        )
        
