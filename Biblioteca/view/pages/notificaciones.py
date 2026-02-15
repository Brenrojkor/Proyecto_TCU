import flet as ft
from model.database import Database
from datetime import datetime, timedelta


class NotificacionesPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self.db = Database()
        self.dialog = None
        
        # =========================
        # Helper para mostrar mensajes
        # =========================
        def snack(msg: str, ok: bool = True):
            self._page.snack_bar = ft.SnackBar(
                ft.Text(msg),
                bgcolor=ft.Colors.GREEN_500 if ok else ft.Colors.RED_500
            )
            self._page.snack_bar.open = True
            self._page.update()

        # =========================
        # Selector de tipo de notificación
        # =========================
        self.tipo_seleccionado = "proximas"
        
        def cambiar_tipo(tipo: str):
            self.tipo_seleccionado = tipo
            btn_proximas.bgcolor = "#1976d2" if tipo == "proximas" else "#e0e0e0"
            btn_proximas.color = ft.Colors.WHITE if tipo == "proximas" else ft.Colors.BLACK
            btn_vencidas.bgcolor = "#d32f2f" if tipo == "vencidas" else "#e0e0e0"
            btn_vencidas.color = ft.Colors.WHITE if tipo == "vencidas" else ft.Colors.BLACK
            self.cargar_notificaciones()
            self._page.update()
        
        btn_proximas = ft.ElevatedButton(
            "⚠️ Próximas a Vencer",
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            on_click=lambda e: cambiar_tipo("proximas"),
            expand=1,
        )
        
        btn_vencidas = ft.ElevatedButton(
            "❌ Vencidas",
            bgcolor="#e0e0e0",
            color=ft.Colors.BLACK,
            on_click=lambda e: cambiar_tipo("vencidas"),
            expand=1,
        )
        
        self.selector_tabs = ft.Row(
            [btn_proximas, btn_vencidas],
            spacing=12,
        )

        # Contenedor para las listas de notificaciones
        self.notificaciones_container = ft.Column(
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        # =========================
        # Funciones para manejar las notificaciones
        # =========================
        def crear_tarjeta_notificacion(reserva: dict, es_vencida: bool = False):
            """Crea una tarjeta visual para cada notificación"""
            
            dias_info = ""
            color_estado = ""
            icono_estado = None
            
            if es_vencida:
                dias_vencidos = reserva.get("dias_vencidos", 0)
                dias_info = f"⚠️ Vencida hace {dias_vencidos} día(s)"
                color_estado = ft.Colors.RED_100
                icono_estado = ft.Icons.ERROR
            else:
                dias_restantes = reserva.get("dias_restantes", 0)
                if dias_restantes == 0:
                    dias_info = "⏰ Vence HOY"
                    color_estado = ft.Colors.ORANGE_100
                    icono_estado = ft.Icons.ALARM
                elif dias_restantes == 1:
                    dias_info = f"📅 Vence MAÑANA"
                    color_estado = ft.Colors.YELLOW_100
                    icono_estado = ft.Icons.CALENDAR_TODAY
                else:
                    dias_info = f"📅 Vence en {dias_restantes} días"
                    color_estado = ft.Colors.BLUE_100
                    icono_estado = ft.Icons.SCHEDULE
            
            return ft.Container(
                content=ft.Row(
                    [
                        # Ícono de estado
                        ft.Container(
                            content=ft.Icon(
                                icono_estado,
                                color=ft.Colors.RED if es_vencida else ft.Colors.ORANGE,
                                size=32,
                            ),
                            padding=16,
                        ),
                        # Información del libro y usuario
                        ft.Column(
                            [
                                ft.Text(
                                    reserva.get("libro_titulo", "Sin título"),
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color="#0d47a1",
                                ),
                                ft.Text(
                                    f"Usuario: {reserva.get('nombre_usuario', 'N/A')} (Cédula: {reserva.get('identificacion_usuario', reserva.get('cedula_usuario', 'N/A'))})",
                                    size=13,
                                    color="#666",
                                ),
                                ft.Text(
                                    f"Fecha préstamo: {reserva.get('fecha_prestamo', 'N/A')}",
                                    size=12,
                                    color="#888",
                                ),
                                ft.Text(
                                    f"Fecha devolución esperada: {reserva.get('fecha_devolucion_esperada', reserva.get('fecha_devolucion', 'N/A'))}",
                                    size=12,
                                    color="#888",
                                ),
                                ft.Text(
                                    dias_info,
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.RED if es_vencida else ft.Colors.ORANGE_800,
                                ),
                            ],
                            spacing=4,
                            expand=True,
                        ),
                        # Botones de acción
                        ft.Column(
                            [
                                ft.ElevatedButton(
                                    "Extender Fecha",
                                    icon=ft.Icons.UPDATE,
                                    on_click=lambda e, r=reserva: abrir_dialogo_extender_fecha(r),
                                    bgcolor="#1976d2",
                                    color=ft.Colors.WHITE,
                                ),
                                ft.OutlinedButton(
                                    "Ver Reserva",
                                    icon=ft.Icons.VISIBILITY,
                                    on_click=lambda e: navigate("/reservas"),
                                ),
                            ],
                            spacing=8,
                            horizontal_alignment=ft.CrossAxisAlignment.END,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=color_estado,
                padding=16,
                border_radius=8,
                border=ft.border.all(1, ft.Colors.GREY_400),
            )

        def abrir_dialogo_extender_fecha(reserva: dict):
            """Abre un diálogo para extender la fecha de devolución"""
            
            fecha_actual = reserva.get("fecha_devolucion_esperada", reserva.get("fecha_devolucion", ""))
            
            # Calcular fecha sugerida (20 días más)
            try:
                fecha_obj = datetime.strptime(fecha_actual, "%Y-%m-%d")
                fecha_sugerida = fecha_obj + timedelta(days=20)
                fecha_sugerida_str = fecha_sugerida.strftime("%Y-%m-%d")
            except:
                fecha_sugerida_str = ""

            nueva_fecha_input = ft.TextField(
                label="Nueva Fecha de Devolución",
                hint_text="YYYY-MM-DD",
                value=fecha_sugerida_str,
                width=300,
                prefix_icon=ft.Icons.CALENDAR_MONTH,
            )

            motivo_input = ft.TextField(
                label="Motivo de la extensión (opcional)",
                multiline=True,
                min_lines=2,
                max_lines=4,
                width=300,
            )

            def guardar_extension(e):
                nueva_fecha = nueva_fecha_input.value
                
                if not nueva_fecha:
                    snack("⚠️ Debes ingresar una fecha", ok=False)
                    return
                
                # Validar formato de fecha
                try:
                    datetime.strptime(nueva_fecha, "%Y-%m-%d")
                except:
                    snack("⚠️ Formato de fecha inválido. Usa YYYY-MM-DD", ok=False)
                    return
                
                try:
                    # Actualizar en la base de datos (préstamos)
                    self.db.actualizar_fecha_devolucion_esperada(
                        reserva.get("id_prestamo", reserva.get("id_reserva")),
                        nueva_fecha
                    )
                    
                    snack(f"✅ Fecha actualizada exitosamente a {nueva_fecha}", ok=True)
                    dlg.open = False
                    self._page.update()
                    
                    # Recargar notificaciones
                    self.cargar_notificaciones()
                    
                except Exception as ex:
                    snack(f"❌ Error al actualizar: {ex}", ok=False)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row(
                    [
                        ft.Icon(ft.Icons.UPDATE, color="#1976d2"),
                        ft.Text("Extender Fecha de Devolución"),
                    ],
                    spacing=8,
                ),
                content=ft.Column(
                    [
                        ft.Text(
                            f"Libro: {reserva.get('libro_titulo', 'N/A')}",
                            weight=ft.FontWeight.BOLD,
                            size=14,
                        ),
                        ft.Text(
                            f"Usuario: {reserva.get('nombre_usuario', 'N/A')}",
                            size=13,
                            color="#666",
                        ),
                        ft.Text(
                            f"Fecha actual: {fecha_actual}",
                            size=13,
                            color="#888",
                        ),
                        ft.Divider(height=20),
                        nueva_fecha_input,
                        motivo_input,
                    ],
                    tight=True,
                    spacing=12,
                    width=350,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo(dlg)),
                    ft.ElevatedButton(
                        "Guardar",
                        icon=ft.Icons.SAVE,
                        on_click=guardar_extension,
                        bgcolor="#1976d2",
                        color=ft.Colors.WHITE,
                    ),
                ],
            )

            self._page.overlay.append(dlg)
            dlg.open = True
            self._page.update()

        def cerrar_dialogo(dlg: ft.AlertDialog):
            dlg.open = False
            self._page.update()

        # =========================
        # Cargar notificaciones
        # =========================
        def cargar_notificaciones_proximas():
            """Carga las notificaciones de préstamos próximos a vencer"""
            try:
                reservas = self.db.get_prestamos_proximos_vencer(dias_anticipacion=20)
                
                self.notificaciones_container.controls.clear()
                
                if not reservas:
                    self.notificaciones_container.controls.append(
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=64, color=ft.Colors.GREEN),
                                    ft.Text(
                                        "¡No hay notificaciones!",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color="#666",
                                    ),
                                    ft.Text(
                                        "Todas las devoluciones están al día",
                                        size=14,
                                        color="#888",
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=12,
                            ),
                            padding=40,
                            alignment=ft.alignment.center,
                        )
                    )
                else:
                    for reserva in reservas:
                        self.notificaciones_container.controls.append(
                            crear_tarjeta_notificacion(reserva, es_vencida=False)
                        )
                
                self._page.update()
                
            except Exception as ex:
                snack(f"❌ Error al cargar notificaciones: {ex}", ok=False)

        def cargar_notificaciones_vencidas():
            """Carga las notificaciones de préstamos vencidos"""
            try:
                reservas = self.db.get_prestamos_vencidos()
                
                self.notificaciones_container.controls.clear()
                
                if not reservas:
                    self.notificaciones_container.controls.append(
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=64, color=ft.Colors.GREEN),
                                    ft.Text(
                                        "¡No hay reservas vencidas!",
                                        size=20,
                                        weight=ft.FontWeight.BOLD,
                                        color="#666",
                                    ),
                                    ft.Text(
                                        "Todas las devoluciones se realizaron a tiempo",
                                        size=14,
                                        color="#888",
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=12,
                            ),
                            padding=40,
                            alignment=ft.alignment.center,
                        )
                    )
                else:
                    for reserva in reservas:
                        self.notificaciones_container.controls.append(
                            crear_tarjeta_notificacion(reserva, es_vencida=True)
                        )
                
                self._page.update()
                
            except Exception as ex:
                snack(f"❌ Error al cargar notificaciones: {ex}", ok=False)

        # =========================
        # Guardar funciones como métodos de instancia
        # =========================
        self.cargar_notificaciones_proximas = cargar_notificaciones_proximas
        self.cargar_notificaciones_vencidas = cargar_notificaciones_vencidas
        self._snack = snack

        # =========================
        # Header
        # =========================
        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=28, color="#38638f"),
                            ft.Text(
                                "Notificaciones de Devoluciones",
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color="#38638f",
                            ),
                        ],
                        spacing=12,
                    ),
                    ft.ElevatedButton(
                        "Actualizar",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda e: self.cargar_notificaciones(),
                        bgcolor="#1976d2",
                        color=ft.Colors.WHITE,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        # =========================
        # Contenedor principal
        # =========================
        container = ft.Container(
            content=ft.Column(
                [
                    header,
                    self.selector_tabs,
                    self.notificaciones_container,
                ],
                spacing=20,
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            expand=True,
        )

        self.controls = [
            ft.Row(
                [container],
                expand=True,
            )
        ]

        # Cargar notificaciones al iniciar
        self.cargar_notificaciones()

    def cargar_notificaciones(self):
        """Carga las notificaciones según el tipo seleccionado"""
        if self.tipo_seleccionado == "proximas":
            self.cargar_notificaciones_proximas()
        elif self.tipo_seleccionado == "vencidas":
            self.cargar_notificaciones_vencidas()
