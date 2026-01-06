import flet as ft

class AppView:
    def __init__(self, page: ft.Page):
        self.page = page
        page.title = "Biblioteca"

        self.button_show_libros = ft.ElevatedButton("Mostrar Libros")
        self.libros_table = ft.DataTable(
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

        page.add(self.button_show_libros, self.libros_table)

    def display_libros(self, libros):
        # limpiar filas existentes
        self.libros_table.rows.clear()
        
        # agregar filas nuevas
        for libro in libros:
            self.libros_table.rows.append(
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
        self.page.update()
