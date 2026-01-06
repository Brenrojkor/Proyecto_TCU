class AppController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        #Esto es para el botón
        self.view.button_show_libros.on_click = self.mostrar_libros

    def mostrar_libros(self, e=None):
        libros = self.model.get_libros()
        self.view.display_libros(libros)
