import flet as ft
from model.database import Database
from utils.notificaciones_manager import NotificacionesManager


def NavBar(page, navigate):
    notif_manager = NotificacionesManager()
    
    def get_notificaciones_count():
        try:
            db = Database()
            proximas = db.get_reservas_proximas_vencer(dias_anticipacion=3)
            vencidas = db.get_reservas_vencidas()
            return len(proximas) + len(vencidas)
        except:
            return 0

    total_count = get_notificaciones_count()
    notif_count = notif_manager.get_count_no_vistas(total_count)
    
    def ir_a_notificaciones(e):
        notif_manager.marcar_como_vistas(total_count)
        navigate("/notificaciones")

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
                ft.MenuItemButton(
                    content=ft.Container(
                        width=150,
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        content=ft.Text("Solicitudes"),
                    ),
                    on_click=lambda _: navigate("/solicitud"),
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
                    nav_item("Contactos", "/contactos"),
                    nav_item("Reservas", "/reservas"),
                    nav_item("Estadísticas", "/estadisticas"),
                    nav_item("Usuarios", "/usuarios"),

                    ft.Container(
                        content=ft.Stack(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.NOTIFICATIONS,
                                    icon_color=ft.Colors.WHITE,
                                    icon_size=28,
                                    tooltip="Notificaciones de devoluciones",
                                    on_click=ir_a_notificaciones,
                                ),
                                ft.Container(
                                    content=ft.Text(
                                        str(notif_count),
                                        size=11,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                    ),
                                    bgcolor=ft.Colors.RED_600,
                                    border_radius=10,
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                    top=8,
                                    right=8,
                                    visible=notif_count > 0,
                                ),
                            ]
                        ),
                        width=48,
                        height=48,
                    ),

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
