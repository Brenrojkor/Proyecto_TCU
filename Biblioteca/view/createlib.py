import flet as ft
from model.database import Database

def create_libro_view(page: ft.Page, db: Database): 

    page.title = "Crear Libro - Biblioteca"
    page.appbar = ft.AppBar(
        title=ft.Text("📚 Crear Nuevo Libro"),
        center_title=False,
        bgcolor=ft.Colors.BLUE_600,
        leading=ft.IconButton(ft.Icons.ARROW_BACK, tooltip="Volver", on_click=lambda e: page.go("/")),
    )

    titulo_input = ft.TextField(label="Título", width=300)
    isbn_input = ft.TextField(label="ISBN", width=300)
    tipo_input = ft.TextField(label="Tipo", width=300)
    descripcion_input = ft.TextField(label="Descripción", width=300)
    categoria_input = ft.TextField(label="Categoría", width=300)
    autores_input = ft.TextField(label="Autores", width=300)
    ubicacion_input = ft.TextField(label="Ubicación", width=300)

    def crear_libro(e):
        db.crear_libro(
            titulo_input.value,
            isbn_input.value,
            tipo_input.value,
            descripcion_input.value,
            categoria_input.value,
            autores_input.value,
            ubicacion_input.value
        )
        page.snack_bar = ft.SnackBar(ft.Text("Libro creado exitosamente!"))
        page.snack_bar.open = True
        page.update()

    crear_button = ft.ElevatedButton("Crear Libro", on_click=crear_libro)

    container = ft.Container(
        content=ft.Column(
            controls=[
                titulo_input,
                isbn_input,
                tipo_input,
                descripcion_input,
                categoria_input,
                autores_input,
                ubicacion_input,
                crear_button
            ],
            spacing=10
        ),
        padding=ft.padding.all(20),
        bgcolor="white",
        border_radius=8
    )

    page.add(
        ft.Row(
            controls=[container],
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )
    )
    