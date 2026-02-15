import flet as ft
from model.database import Database
from utils.notificaciones_manager import NotificacionesManager


def NavBar(page, navigate):
    notif_manager = NotificacionesManager()
    
    def get_notificaciones_count():
        try:
            db = Database()
            proximas = db.get_prestamos_proximos_vencer(dias_anticipacion=20)
            vencidas = db.get_prestamos_vencidos()
            return len(proximas) + len(vencidas)
        except:
            return 0

    total_count = get_notificaciones_count()
    notif_count = notif_manager.get_count_no_vistas(total_count)
    
    # Badge controls so we can update visibility/count dynamically
    badge_text = ft.Text(
        str(notif_count),
        size=11,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
    )
    badge_container = ft.Container(
        content=badge_text,
        bgcolor=ft.Colors.RED_600,
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=6, vertical=2),
        top=8,
        right=8,
        visible=notif_count > 0,
    )
    
    def ir_a_notificaciones(e):
        # Persist viewed count and clear badge immediately
        current_total = get_notificaciones_count()
        notif_manager.marcar_como_vistas(current_total)
        badge_text.value = "0"
        badge_container.visible = False
        page.update()
        navigate("/notificaciones")

    def refresh_badge():
        """Recalcula y refresca el badge con el estado actual."""
        current_total = get_notificaciones_count()
        unseen = notif_manager.get_count_no_vistas(current_total)
        badge_text.value = str(unseen)
        badge_container.visible = unseen > 0
        page.update()

    def on_nav_click(route: str):
        # Refrescar badge antes de navegar a cualquier vista
        refresh_badge()
        navigate(route)

    def nav_item(text, route):
        return ft.TextButton(
            content=ft.Text(
                text,
                color=ft.Colors.WHITE,
                size=16,
                weight=ft.FontWeight.W_600,
            ), 
            on_click=lambda _: on_nav_click(route),
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
                                badge_container,
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
