import flet as ft
from model.database import Database

class HomePage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page  # ⚠️ usar _page, no page
        db = Database()

        button_crear_libro = ft.ElevatedButton("Crear Libro")
        button_show_libros = ft.ElevatedButton("Mostrar Libros")
        
        libros_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Título")),
                ft.DataColumn(ft.Text("ISBN")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Autores")),
                ft.DataColumn(ft.Text("Ubicación"))
            ],
            rows=[]
        )

        def mostrar_libros(e):
            libros_table.rows.clear()
            libros = db.get_libros()
            for libro in libros:
                libros_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(libro["id_libro"]))),
                        ft.DataCell(ft.Text(libro["titulo"])),
                        ft.DataCell(ft.Text(libro.get("isbn", ""))),
                        ft.DataCell(ft.Text(libro["tipo"])),
                        ft.DataCell(ft.Text(libro.get("descripcion", ""))),
                        ft.DataCell(ft.Text(libro.get("categoria", ""))),
                        ft.DataCell(ft.Text(libro.get("autores", ""))),
                        ft.DataCell(ft.Text(libro.get("ubicacion", ""))),
                    ])
                )
            self._page.update()  # ⚠️ ahora usamos _page

        button_show_libros.on_click = mostrar_libros

        container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[button_crear_libro, button_show_libros],
                        spacing=20,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    libros_table
                ],
                spacing=20
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=8
        )

        self.controls = [
            ft.Row(
                controls=[container],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        ]
