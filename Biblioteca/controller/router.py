import flet as ft
from view.pages.home import HomePage
from view.pages.categorias import CategoriasPage
from view.components.navbar import NavBar  
from view.pages.createlib import CrearLibroPage
from view.pages.autores import AutoresPage
from view.pages.ubicacionView import UbicacionView

class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.appbar = NavBar(self.navigate)

        #Rutas
        self.routes = {
            "/": HomePage,
            "/categorias": CategoriasPage,
             "/createlib": CrearLibroPage,
             "/autores": AutoresPage,
             "/ubicacion": UbicacionView,
        }

        self.navigate("/")  

    def navigate(self, route: str):
        self.page.controls.clear()
        self.page.add(self.routes.get(route, self.not_found)(self.navigate, self.page))
        self.page.update()

    def not_found(self, navigate, page):
        return ft.Column([ft.Text("404 - Página no encontrada")])
