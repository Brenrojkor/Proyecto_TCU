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
from view.pages.detalleUsuario import DetalleUsuarioPage
from view.pages.editarlib import EditarLibroPage
from view.pages.estadisticas import EstadisticasView
from view.pages.notificaciones import NotificacionesPage
from view.pages.solicitud import SolicitudPage

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
             "/detalleusuario": DetalleUsuarioPage,
             "/editlib": EditarLibroPage,
             "/estadisticas": EstadisticasView,
             "/notificaciones": NotificacionesPage,
             "/solicitud": SolicitudPage,
        }

    def set_container(self, container: ft.Column):
            self.container = container

    def navigate(self, route: str):
        self.container.controls.clear()

        # Extraer query parameters de la URL (ej: /contactos?page=2)
        query_params = {}
        if "?" in route:
            route_base, query_string = route.split("?", 1)
            for param in query_string.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    query_params[key.strip()] = value.strip()
        else:
            route_base = route

        # Extraer parámetro si existe (ej: /libro/123 -> /libro, 123)
        param = None
        
        parts = route_base.rstrip("/").split("/")
        if len(parts) > 2 and parts[-1].isdigit():
            # Detectar si hay parámetro numérico
            param = int(parts[-1])
            route_base = "/" + parts[1] if len(parts) > 1 else "/"

        view_class = self.routes.get(route_base, self.not_found)
        
        # Pasar parámetros según la ruta
        if param is not None and route_base in ["/libro", "/editlib", "/detalleusuario"]:
            if query_params:
                self.container.controls.append(view_class(self.navigate, self.page, param, query_params))
            else:
                self.container.controls.append(view_class(self.navigate, self.page, param))
        elif route_base in ["/", "/contactos", "/categorias", "/usuarios", "/autores", "/solicitud"] and query_params:
            # Pasar query_params para mantener estado de paginación
            self.container.controls.append(view_class(self.navigate, self.page, query_params))
        else:
            self.container.controls.append(view_class(self.navigate, self.page))

        self.page.update()

    def not_found(self, navigate, page):
         return ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[ft.Text("404 - Página no encontrada")]
        )
        
