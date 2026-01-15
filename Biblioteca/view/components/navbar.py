import flet as ft

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

                      
                        ft.CircleAvatar(
                            content=ft.Icon(
                                ft.Icons.PERSON,
                                color=ft.Colors.WHITE,
                            ),
                            bgcolor="#1B6F7A",
                            radius=18,
                        ),
                    ],
                ),
            ],
        ),
    )