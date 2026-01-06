import flet as ft
from model.database import Database


def main(page: ft.Page):
    page.title = "Biblioteca - Flet"
    page.appbar = ft.AppBar(
    title=ft.Text("📚 Biblioteca"),
    center_title=False,
    bgcolor=ft.Colors.BLUE_600,
    actions=[
    ft.TextButton(
        content=ft.Row(
            controls=[ft.Icon(ft.Icons.HOME), ft.Text("Inicio")],
            spacing=5
        ),
        tooltip="Inicio"
    ),
    ft.TextButton(
        content=ft.Row(
            controls=[ft.Icon(ft.Icons.BOOK), ft.Text("Libros")],
            spacing=5
        ),
        tooltip="Libros"
    ),
    ft.TextButton(
        content=ft.Row(
            controls=[ft.Icon(ft.Icons.PERSON), ft.Text("Autores")],
            spacing=5
        ),
        tooltip="Autores"
    ),
    ft.TextButton(
        content=ft.Row(
            controls=[ft.Icon(ft.Icons.LOGOUT), ft.Text("Salir")],
            spacing=5
        ),
        tooltip="Salir"
    ),
],    leading=ft.IconButton(ft.Icons.MENU, tooltip="Menú")
)


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

    

    container = ft.Container(
        content=ft.Column(controls=[button_show_libros, libros_table], spacing=20),
        padding=20,
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

#Ejecutar la app
ft.app(target=main)
