import flet as ft
from model.database import Database
from datetime import datetime, timedelta


class NotificacionesPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
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
            content=ft.Row([
                ft.Icon(ft.Icons.WARNING_ROUNDED, size=18, color=ft.Colors.WHITE),
                ft.Text("Próximas a Vencer", size=13, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
            ], spacing=8),
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            on_click=lambda e: cambiar_tipo("proximas"),
            height=44,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=2,
            ),
            expand=1,
        )
        
        btn_vencidas = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR_ROUNDED, size=18, color=ft.Colors.BLACK),
                ft.Text("Vencidas", size=13, weight=ft.FontWeight.W_500),
            ], spacing=8),
            bgcolor="#e0e0e0",
            color=ft.Colors.BLACK,
            on_click=lambda e: cambiar_tipo("vencidas"),
            height=44,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=0,
            ),
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

            usuario_nombre = (
                reserva.get("nombre_usuario")
                or reserva.get("nombre_completo")
                or reserva.get("usuario")
                or "N/A"
            )
            
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
                                    f"Nombre: {usuario_nombre}",
                                    size=13,
                                    color="#666",
                                ),
                                ft.Text(
                                    f"Cédula: {reserva.get('identificacion_usuario', reserva.get('cedula_usuario', 'N/A'))}",
                                    size=12,
                                    color="#888",
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
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.UPDATE, color=ft.Colors.WHITE, size=18),
                                        ft.Text("Extender", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                    ], spacing=6),
                                    bgcolor="#1976d2",
                                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                    width=120,
                                    border_radius=8,
                                    alignment=ft.Alignment.CENTER,
                                    on_click=lambda e, r=reserva: abrir_dialogo_extender_fecha(r),
                                ),
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.VISIBILITY, color=ft.Colors.WHITE, size=18),
                                        ft.Text("Ver", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                                    ], spacing=6),
                                    bgcolor="#00838f",
                                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                                    width=120,
                                    border_radius=8,
                                    alignment=ft.Alignment.CENTER,
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
            
            def format_ddmmyyyy(valor: str) -> str:
                if not valor:
                    return ""
                try:
                    return datetime.strptime(valor, "%Y-%m-%d").strftime("%d-%m-%Y")
                except Exception:
                    pass
                try:
                    return datetime.strptime(valor, "%d-%m-%Y").strftime("%d-%m-%Y")
                except Exception:
                    return str(valor)

            def parse_fecha_input(valor: str):
                if not valor:
                    return None
                v = str(valor).strip()
                try:
                    if "-" in v:
                        parts = v.split("-")
                        if len(parts[0]) == 4:
                            return datetime.strptime(v, "%Y-%m-%d")
                        return datetime.strptime(v, "%d-%m-%Y")
                    return datetime.strptime(v, "%d/%m/%Y")
                except Exception:
                    return None

            # Calcular fecha sugerida (20 días más)
            fecha_sugerida_str = ""
            try:
                fecha_obj = datetime.strptime(str(fecha_actual), "%Y-%m-%d")
                fecha_sugerida = fecha_obj + timedelta(days=20)
                fecha_sugerida_str = fecha_sugerida.strftime("%d-%m-%Y")
            except Exception:
                pass

            nueva_fecha_input = ft.TextField(
                label="Nueva Fecha de Devolución",
                hint_text="DD-MM-YYYY",
                value=fecha_sugerida_str,
                width=300,
                prefix_icon=ft.Icons.CALENDAR_MONTH,
            )

            def aplicar_suma_dias(dias: int):
                base = parse_fecha_input(nueva_fecha_input.value) or parse_fecha_input(str(fecha_actual))
                if not base:
                    base = datetime.now()
                nueva = base + timedelta(days=dias)
                nueva_fecha_input.value = nueva.strftime("%d-%m-%Y")
                self._page.update()

            quick_buttons = ft.Row(
                [
                    ft.OutlinedButton("+7 días", on_click=lambda e: aplicar_suma_dias(7)),
                    ft.OutlinedButton("+15 días", on_click=lambda e: aplicar_suma_dias(15)),
                    ft.OutlinedButton("+30 días", on_click=lambda e: aplicar_suma_dias(30)),
                ],
                spacing=8,
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
                
                # Validar y normalizar formato de fecha (acepta DD-MM-YYYY o YYYY-MM-DD)
                try:
                    if "-" in nueva_fecha:
                        parts = nueva_fecha.split("-")
                        if len(parts[0]) == 4:
                            fecha_obj = datetime.strptime(nueva_fecha, "%Y-%m-%d")
                        else:
                            fecha_obj = datetime.strptime(nueva_fecha, "%d-%m-%Y")
                    else:
                        fecha_obj = datetime.strptime(nueva_fecha, "%d/%m/%Y")
                    nueva_fecha = fecha_obj.strftime("%Y-%m-%d")
                except Exception:
                    snack("⚠️ Formato inválido. Usa DD-MM-YYYY", ok=False)
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
                            f"Fecha actual: {format_ddmmyyyy(str(fecha_actual))}",
                            size=13,
                            color="#888",
                        ),
                        ft.Divider(height=20),
                        nueva_fecha_input,
                        quick_buttons,
                        motivo_input,
                    ],
                    tight=True,
                    spacing=12,
                    width=460,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo(dlg)),
                    ft.ElevatedButton(
                        "Guardar",
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
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=32, color="#1565c0"),
                            ft.Text(
                                "Notificaciones de Devoluciones",
                                size=26,
                                weight=ft.FontWeight.BOLD,
                                color="#263238",
                            ),
                        ],
                        spacing=12,
                    ),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.REFRESH, size=18),
                            ft.Text("Actualizar", size=13, weight=ft.FontWeight.W_500),
                        ], spacing=8),
                        on_click=lambda e: self.cargar_notificaciones(),
                        bgcolor="#1976d2",
                        color=ft.Colors.WHITE,
                        height=44,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=2,
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(horizontal=30, vertical=20),
            margin=ft.margin.symmetric(horizontal=30),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
        )

        # =========================
        # Contenedor principal
        # =========================
        selector_container = ft.Container(
            content=self.selector_tabs,
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            margin=ft.margin.symmetric(horizontal=30),
        )

        notificaciones_card = ft.Container(
            content=self.notificaciones_container,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            margin=ft.margin.symmetric(horizontal=30),
            expand=True,
        )

        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        header,
                        selector_container,
                        notificaciones_card,
                    ],
                    spacing=20,
                    expand=True,
                ),
                bgcolor="#f5f7fa",
                padding=ft.padding.symmetric(vertical=20),
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
