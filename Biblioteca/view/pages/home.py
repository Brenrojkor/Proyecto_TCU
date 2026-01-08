import flet as ft
from model.database import Database

class HomePage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page  # ⚠️ usar _page, no page
        db = Database()

        button_crear_libro = ft.ElevatedButton(
            content=ft.Row(
                controls=[ft.Icon(ft.Icons.ADD), ft.Text("Crear libro")],
                spacing=8
            ),
            on_click=lambda e: navigate("/createlib")
        )

        button_show_libros = ft.ElevatedButton("Mostrar Libros")

        search_input = ft.TextField(
            hint_text="Buscar ...",
            prefix_icon=ft.Icons.SEARCH,
            width=300,
            dense=True
        )

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

        # Cache
        self._libros_cache = []

        # ✅ FILTRO SOLO POR TITULO (lo que me pediste)
        def filtrar_libros(texto):
            q = (texto or "").strip().lower()
            libros_table.rows.clear()

            # Si está vacío: mostrar TODO
            if not q:
                for libro in self._libros_cache:
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
                self._page.update()
                return

            # Si hay texto: mostrar SOLO coincidencias por título
            for libro in self._libros_cache:
                titulo = str(libro.get("titulo", "")).lower()
                if q in titulo:
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

            self._page.update()

        # ✅ Para que funcione sin presionar "Mostrar Libros" primero
        def on_search_change(e):
            if not self._libros_cache:
                self._libros_cache = db.get_libros()
            filtrar_libros(e.control.value)

        search_input.on_change = on_search_change

        def mostrar_libros(e):
            libros_table.rows.clear()
            libros = db.get_libros()

            # guardar cache
            self._libros_cache = libros

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

            # si hay texto en buscador, aplica filtro
            if search_input.value:
                filtrar_libros(search_input.value)

            self._page.update()

        button_show_libros.on_click = mostrar_libros

        container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[button_crear_libro, button_show_libros, search_input],
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
