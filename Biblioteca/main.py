import flet as ft
from model.database import Database

def main(page: ft.Page):
    page.title = "Biblioteca - Flet"

    db = Database()

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
        page.update()

    button_show_libros.on_click = mostrar_libros

    page.add(button_show_libros, libros_table)

#Ejecutar la app
ft.app(target=main)
