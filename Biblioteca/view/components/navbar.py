import flet as ft

def NavBar(navigate):
    return ft.AppBar(
        title=ft.Text("📚 Biblioteca"),
        center_title=False,
        bgcolor=ft.Colors.BLUE_600,
        leading=ft.IconButton(ft.Icons.MENU, tooltip="Menú"),
        actions=[
            ft.TextButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.Icons.HOME), ft.Text("Inicio")],
                    spacing=5
                ),
                tooltip="Inicio",
                on_click=lambda _: navigate("/")
            ),
            ft.TextButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.Icons.BOOK), ft.Text("Libros")],
                    spacing=5
                ),
                tooltip="Libros",
                on_click=lambda _: navigate("/libros")
            ),
            ft.TextButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.Icons.ADD_CHART_SHARP), ft.Text("Categorías")],
                    spacing=5
                ),
                tooltip="Categorías",
                on_click=lambda _: navigate("/categorias")
            ),
            ft.TextButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.Icons.PERSON), ft.Text("Autores")],
                    spacing=5
                ),
                tooltip="Autores",
                on_click=lambda _: navigate("/autores")
            ),

            # ✅ ÚNICO AGREGADO: UBICACIÓN
            ft.TextButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.Icons.LOCATION_ON), ft.Text("Ubicación")],
                    spacing=5
                ),
                tooltip="Ubicación",
                on_click=lambda _: navigate("/ubicacion")
            ),

            ft.TextButton(
                content=ft.Row(
                    controls=[ft.Icon(ft.Icons.LOGOUT), ft.Text("Salir")],
                    spacing=5
                ),
                tooltip="Salir",
                on_click=lambda _: navigate("/logout")
            ),
        ]
    )
def NavBar(page, navigate):

    def nav_item(text, route):
        return ft.TextButton(
            content=ft.Text(
                text,
                color=ft.Colors.WHITE,
                size=16,
                weight=ft.FontWeight.W_600,
            ), 
            on_click=lambda _: navigate(route),
        )

    libros_menu = ft.MenuBar(
    style=ft.MenuStyle(
        bgcolor=ft.Colors.TRANSPARENT,
        elevation=0,
        padding=0,
    ),
    controls=[
        ft.SubmenuButton(
            content=ft.Row(
                spacing=4,
                controls=[
                    ft.Text(
                        "Libros",
                        color=ft.Colors.WHITE,
                        size=16,
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Icon(
                        ft.Icons.ARROW_DROP_DOWN,
                        color=ft.Colors.WHITE,
                        size=20,
                    ),
                ],
            ),
             controls=[
                ft.MenuItemButton(
                    content=ft.Container(
                        width=150,
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        content=ft.Text("Categorías"),
                    ),
                    on_click=lambda _: navigate("/categorias"),
                ),
                ft.MenuItemButton(
                    content=ft.Container(
                        width=150,
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        content=ft.Text("Autores"),
                    ),
                    on_click=lambda _: navigate("/autores"),
                ),
                      ],
        )
    ],
)


    return ft.Container(
    bgcolor="#0b495c",
    height=64,
    padding=ft.padding.symmetric(horizontal=24),
    content=ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(
                "Biblioteca Pública De Tibás",
                size=22,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
            ft.Row(
                spacing=20,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    nav_item("Inicio", "/"),
                    libros_menu,
                    nav_item("Dashboard", "/dashboard"),
                    nav_item("Usuarios", "/usuarios"),

                    # 👇 Avatar clickeable
                    ft.Container(
                        content=ft.CircleAvatar(
                            content=ft.Icon(
                                ft.Icons.PERSON,
                                color=ft.Colors.WHITE,
                            ),
                            bgcolor="#1B6F7A",
                            radius=18,
                        ),
                        on_click=lambda e: navigate("/login"),
                    ),
                ],
            ),
        ],
    ),
)
