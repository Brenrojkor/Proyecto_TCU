import flet as ft
from view.pages.contactos import ContactosPage
from view.pages.home import HomePage
from view.pages.categorias import CategoriasPage
from view.components.navbar import NavBar  
from view.pages.createlib import CrearLibroPage
from view.pages.createcontacto import CrearContactoPage
from view.pages.reservas import ReservasPage
from view.pages.autores import AutoresPage

from view.pages.login import LoginPage
from view.pages.registro import RegistroPage
from view.pages.usuarios import UsuariosPage
from view.pages.detallelib import DetalleLibroPage
from view.pages.editarlib import EditarLibroPage
from view.pages.estadisticas import EstadisticasView
from view.pages.notificaciones import NotificacionesPage

class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.container = None

        #Rutas
        self.routes = {
            "/": HomePage,
            "/contactos": ContactosPage,
            "/categorias": CategoriasPage,
             "/createlib": CrearLibroPage,
             "/createcontacto": CrearContactoPage,
             "/reservas": ReservasPage,
             "/autores": AutoresPage,
             "/login": LoginPage,
             "/registro": RegistroPage,
             "/usuarios": UsuariosPage,
             "/libro": DetalleLibroPage,
             "/editlib": EditarLibroPage,
             "/estadisticas": EstadisticasView,
             "/notificaciones": NotificacionesPage,
        }

    def set_container(self, container: ft.Column):
            self.container = container

    def navigate(self, route: str):
        self.container.controls.clear()

        # Extraer parámetro si existe (ej: /libro/123 -> /libro, 123)
        route_base = route
        param = None
        
        parts = route.rstrip("/").split("/")
        if len(parts) > 2 and parts[-1].isdigit():
            # Detectar si hay parámetro numérico
            param = int(parts[-1])
            route_base = "/" + parts[1] if len(parts) > 1 else "/"

        view_class = self.routes.get(route_base, self.not_found)
        
        # Pasar parámetro si existe
        if param is not None and route_base in ["/libro", "/editlib"]:
            self.container.controls.append(view_class(self.navigate, self.page, param))
        else:
            self.container.controls.append(view_class(self.navigate, self.page))

        self.page.update()

    def not_found(self, navigate, page):
         return ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[ft.Text("404 - Página no encontrada")]
        )
        
