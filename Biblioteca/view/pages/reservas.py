import flet as ft
from model.database import Database
from datetime import datetime, timedelta
import math


class ReservasPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self._db = Database()

        # =========================
        # Helpers
        # =========================
        def snack(msg: str, ok: bool = True):
            self._page.snack_bar = ft.SnackBar(
                ft.Text(msg, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
                bgcolor="#2e7d32" if ok else "#c62828",
            )
            self._page.snack_bar.open = True
            self._page.update()

        # =========================
        # Estadísticas Cards
        # =========================
        self.total_prestamos = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#263238")
        self.prestamos_activos = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#263238")
        self.prestamos_vencidos = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#263238")
        self.libros_devueltos = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#263238")

        # =========================
        # UI - Inputs Mejorados
        # =========================
        self.search_input = ft.TextField(
            hint_text="Buscar por libro, cédula o usuario...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            width=500,
            height=50,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border_color="#e0e0e0",
            focused_border_color="#1976d2",
            focused_border_width=2,
            text_size=14,
            content_padding=ft.padding.only(left=15, right=15, top=10, bottom=10),
        )

        self.estado_dd = ft.Dropdown(
            width=200,
            height=50,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            border_color="#e0e0e0",
            focused_border_color="#1976d2",
            value="TODOS",
            label="Filtrar",
            text_size=14,
            options=[
                ft.dropdown.Option("TODOS", "Todos"),
                ft.dropdown.Option("PRESTADO", "Prestado"),
                ft.dropdown.Option("DEVUELTO", "Devuelto"),
                ft.dropdown.Option("NO DEVUELTO", "Vencido"),
                ft.dropdown.Option("A SALA", "A sala"),
            ],
        )

        # =========================
        # Tabla Mejorada
        # =========================
        self.reservas_table = ft.DataTable(
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, "#e0e0e0"),
            border_radius=12,
            width=1400,
            heading_row_color="#f5f7fa",
            heading_row_height=56,
            data_row_min_height=60,
            data_row_max_height=65,
            column_spacing=30,
            horizontal_margin=20,
            divider_thickness=0.5,
            columns=[
                ft.DataColumn(
                    label=ft.Container(
                        content=ft.Text("Libro", weight=ft.FontWeight.BOLD, color="#1565c0", size=13),
                        padding=ft.padding.only(left=5)
                    )
                ),
                ft.DataColumn(
                    label=ft.Text("Usuario", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)
                ),
                ft.DataColumn(
                    label=ft.Text("Préstamo", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)
                ),
                ft.DataColumn(
                    label=ft.Text("Devolución", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)
                ),
                ft.DataColumn(
                    label=ft.Text("Estado", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)
                ),
                ft.DataColumn(
                    label=ft.Text("Acciones", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)
                ),
            ],
            rows=[],
        )

        self._reservas_cache = []
        self._page_size = 5
        self._pagina_actual = 1
        self._reservas_filtradas = []

        # =========================
        # Build row Mejorado
        # =========================
        def build_row(r: dict) -> ft.DataRow:
            estado = (r.get("estado") or "PRESTADO").strip().upper()

            def format_fecha(valor):
                if not valor:
                    return ""
                if isinstance(valor, datetime):
                    return valor.strftime("%d-%m-%Y")
                if hasattr(valor, "strftime"):
                    try:
                        return valor.strftime("%d-%m-%Y")
                    except Exception:
                        pass
                s = str(valor).strip()
                formatos = [
                    "%Y-%m-%d",
                    "%Y-%m-%d %H:%M:%S",
                    "%d/%m/%Y",
                    "%d/%m/%Y %H:%M:%S",
                ]
                for fmt in formatos:
                    try:
                        return datetime.strptime(s, fmt).strftime("%d-%m-%Y")
                    except Exception:
                        pass
                try:
                    return datetime.fromisoformat(s).strftime("%d-%m-%Y")
                except Exception:
                    return s

            # Colores mejorados
            if estado == "DEVUELTO":
                estado_color = "#2e7d32"
                estado_icon = ""
                texto_estado = "Devuelto"
            elif estado == "NO DEVUELTO":
                estado_color = "#d32f2f"
                estado_icon = ""
                texto_estado = "Vencido"
            elif estado == "A SALA":
                estado_color = "#6a1b9a"
                estado_icon = ""
                texto_estado = "A sala"
            else:
                estado_color = "#1976d2"
                estado_icon = ""
                texto_estado = "Activo"

            # Calcular días restantes
            fecha_dev = r.get("fecha_devolucion_esperada")
            dias_info = ""
            if estado == "PRESTADO" and fecha_dev:
                try:
                    if isinstance(fecha_dev, str):
                        fecha_dev = datetime.strptime(fecha_dev, "%Y-%m-%d").date()
                    elif hasattr(fecha_dev, 'date'):
                        fecha_dev = fecha_dev.date()
                    
                    dias_restantes = (fecha_dev - datetime.now().date()).days
                    if dias_restantes > 0:
                        dias_info = f" ({dias_restantes}d)"
                    elif dias_restantes == 0:
                        dias_info = " (Hoy)"
                except:
                    pass

            return ft.DataRow(
                cells=[
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                r.get("libro_titulo", "Sin título")[:40] + ("..." if len(r.get("libro_titulo", "")) > 40 else ""),
                                size=13,
                                weight=ft.FontWeight.W_500,
                                color="#263238"
                            ),
                            padding=ft.padding.only(left=5)
                        )
                    ),
                    ft.DataCell(
                        ft.Column(
                            [
                                ft.Text(r.get("nombre_usuario", "")[:25], size=13, weight=ft.FontWeight.W_500, color="#263238"),
                                ft.Text(r.get("cedula_usuario", ""), size=11, color="#757575"),
                            ],
                            spacing=2,
                            tight=True
                        )
                    ),
                    ft.DataCell(
                        ft.Text(format_fecha(r.get("fecha_prestamo", "")), size=12, color="#546e7a")
                    ),
                    ft.DataCell(
                        ft.Text(format_fecha(r.get("fecha_devolucion", "—")) or "—", size=12, color="#546e7a")
                    ),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Text(texto_estado + dias_info, color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                                ],
                                spacing=5,
                                tight=True
                            ),
                            bgcolor=estado_color,
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            border_radius=8,
                        )
                    ),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=ft.Colors.WHITE, size=18),
                                    bgcolor="#2e7d32" if estado != "DEVUELTO" else "#9e9e9e",
                                    width=36,
                                    height=36,
                                    border_radius=8,
                                    alignment=ft.Alignment(0, 0),
                                    tooltip="Registrar devolución" if estado != "DEVUELTO" else "Ya devuelto",
                                    on_click=lambda e, rr=r: registrar_devolucion(rr) if estado != "DEVUELTO" else None,
                                ),
                                ft.Container(
                                    content=ft.Icon(ft.Icons.EVENT_AVAILABLE_ROUNDED, color=ft.Colors.WHITE, size=18),
                                    bgcolor="#0288d1",
                                    width=36,
                                    height=36,
                                    border_radius=8,
                                    alignment=ft.Alignment(0, 0),
                                    tooltip="Renovar préstamo",
                                    on_click=lambda e, rr=r: renovar_prestamo(rr) if estado != "DEVUELTO" else None,
                                ),
                                ft.Container(
                                    content=ft.Icon(ft.Icons.REPORT_ROUNDED, color=ft.Colors.WHITE, size=18),
                                    bgcolor="#d32f2f" if estado == "PRESTADO" else "#9e9e9e",
                                    width=36,
                                    height=36,
                                    border_radius=8,
                                    alignment=ft.Alignment(0, 0),
                                    tooltip="Marcar NO DEVUELTO" if estado == "PRESTADO" else "No disponible",
                                    on_click=lambda e, rr=r: marcar_no_devuelto(rr) if estado == "PRESTADO" else None,
                                ),
                                ft.Container(
                                    content=ft.Icon(ft.Icons.HISTORY_ROUNDED, color=ft.Colors.WHITE, size=18),
                                    bgcolor="#1976d2",
                                    width=36,
                                    height=36,
                                    border_radius=8,
                                    alignment=ft.Alignment(0, 0),
                                    tooltip="Ver historial del usuario",
                                    on_click=lambda e, rr=r: ver_historial_usuario(rr.get("cedula_usuario")),
                                ),
                                ft.Container(
                                    content=ft.Icon(ft.Icons.DELETE_ROUNDED, color=ft.Colors.WHITE, size=18),
                                    bgcolor="#d32f2f",
                                    width=36,
                                    height=36,
                                    border_radius=8,
                                    alignment=ft.Alignment(0, 0),
                                    tooltip="Eliminar préstamo",
                                    on_click=lambda e, i=r.get("id_reserva"): confirmar_eliminar(i),
                                ),
                            ],
                            spacing=8,
                        )
                    ),
                ]
            )

        # =========================
        # Cargar datos y actualizar estadísticas
        # =========================
        def cargar_reservas():
            try:
                self._reservas_cache = self._db.get_prestamos()

                for r in self._reservas_cache:
                    r["id_reserva"] = r.get("id_prestamo")
                    r["cedula_usuario"] = r.get("identificacion_usuario")

                    if not r.get("libro_titulo"):
                        r["libro_titulo"] = "Sin título"

                    # Formatear fechas
                    fecha_prestamo = r.get("fecha_prestamo")
                    if hasattr(fecha_prestamo, "strftime"):
                        r["fecha_prestamo"] = fecha_prestamo.strftime("%Y-%m-%d")

                    fecha_dev = r.get("fecha_devolucion_real") or r.get("fecha_devolucion_esperada")
                    if hasattr(fecha_dev, "strftime"):
                        r["fecha_devolucion"] = fecha_dev.strftime("%Y-%m-%d")
                    else:
                        r["fecha_devolucion"] = fecha_dev or ""
                    
                    # Calcular estado
                    if r.get("fecha_devolucion_real"):
                        # A SALA si se devolvió el mismo día
                        try:
                            fp = r.get("fecha_prestamo")
                            fr = r.get("fecha_devolucion_real")
                            if hasattr(fp, 'date'):
                                fp_date = fp.date()
                            elif isinstance(fp, str):
                                fp_date = datetime.strptime(fp, "%Y-%m-%d").date()
                            else:
                                fp_date = None

                            if hasattr(fr, 'date'):
                                fr_date = fr.date()
                            elif isinstance(fr, str):
                                fr_date = datetime.strptime(fr, "%Y-%m-%d").date()
                            else:
                                fr_date = None

                            if fp_date and fr_date and fp_date == fr_date:
                                r["estado"] = "A SALA"
                            else:
                                r["estado"] = "DEVUELTO"
                        except:
                            r["estado"] = "DEVUELTO"
                    elif r.get("fecha_devolucion_esperada"):
                        try:
                            fecha_esperada = r["fecha_devolucion_esperada"]
                            if isinstance(fecha_esperada, str):
                                fecha_esperada = datetime.strptime(fecha_esperada, "%Y-%m-%d").date()
                            elif hasattr(fecha_esperada, 'date'):
                                fecha_esperada = fecha_esperada.date()
                            
                            if fecha_esperada < datetime.now().date():
                                r["estado"] = "NO DEVUELTO"
                            else:
                                r["estado"] = "PRESTADO"
                        except:
                            r["estado"] = "PRESTADO"
                    else:
                        r["estado"] = "PRESTADO"

                # Actualizar estadísticas
                actualizar_estadisticas()
                aplicar_filtros(reset_pagina=True)

            except Exception as ex:
                import traceback
                print(traceback.format_exc())
                snack(f"Error al cargar préstamos: {ex}", ok=False)

        def actualizar_estadisticas():
            total = len(self._reservas_cache)
            activos = len([r for r in self._reservas_cache if r.get("estado") == "PRESTADO"])
            vencidos = len([r for r in self._reservas_cache if r.get("estado") == "NO DEVUELTO"])
            devueltos = len([r for r in self._reservas_cache if r.get("estado") == "DEVUELTO"])
            
            self.total_prestamos.value = str(total)
            self.prestamos_activos.value = str(activos)
            self.prestamos_vencidos.value = str(vencidos)
            self.libros_devueltos.value = str(devueltos)
            self._page.update()

        # =========================
        # Paginación
        # =========================
        pagination_label = ft.Text("Página 1 de 1", size=12, color="#546e7a")

        def change_page(delta: int):
            total = max(1, math.ceil(len(self._reservas_filtradas) / self._page_size))
            self._pagina_actual = min(max(1, self._pagina_actual + delta), total)
            aplicar_filtros()

        btn_prev = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            icon_color="#546e7a",
            tooltip="Anterior",
            on_click=lambda e: change_page(-1),
        )
        btn_next = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            icon_color="#546e7a",
            tooltip="Siguiente",
            on_click=lambda e: change_page(1),
        )

        # =========================
        # Filtros
        # =========================
        def aplicar_filtros(reset_pagina: bool = False):
            estado = self.estado_dd.value
            texto = (self.search_input.value or "").lower()

            filtradas = []
            for r in self._reservas_cache:
                if estado != "TODOS" and r.get("estado") != estado:
                    continue

                if texto:
                    contenido = f"{r.get('libro_titulo','')} {r.get('cedula_usuario','')}".lower()
                    if texto not in contenido:
                        continue

                filtradas.append(r)

            self._reservas_filtradas = filtradas

            total_pages = max(1, math.ceil(len(filtradas) / self._page_size))
            if reset_pagina:
                self._pagina_actual = 1
            if self._pagina_actual > total_pages:
                self._pagina_actual = total_pages

            start = (self._pagina_actual - 1) * self._page_size
            end = start + self._page_size
            pagina_items = filtradas[start:end]

            self.reservas_table.rows = [build_row(r) for r in pagina_items]

            pagination_label.value = f"Página {self._pagina_actual} de {total_pages}"
            btn_prev.disabled = self._pagina_actual <= 1
            btn_next.disabled = self._pagina_actual >= total_pages
            self._page.update()

        self.search_input.on_change = lambda e: aplicar_filtros(reset_pagina=True)
        self.estado_dd.on_change = lambda e: aplicar_filtros(reset_pagina=True)

        # =========================
        # Registrar devolución Mejorado
        # =========================
        def registrar_devolucion(reserva):
            observaciones_field = ft.TextField(
                label="Observaciones (opcional)",
                multiline=True,
                min_lines=3,
                max_lines=5,
                bgcolor="#f5f7fa",
                border_radius=8,
            )
            
            def guardar_devolucion(e):
                try:
                    self._db.actualizar_devolucion_prestamo(
                        int(reserva.get("id_reserva")),
                        observaciones=observaciones_field.value
                    )
                    snack("✅ Devolución registrada correctamente")
                    dlg.open = False
                    self._page.update()
                    cargar_reservas()
                except Exception as ex:
                    snack(f"❌ Error: {str(ex)}", ok=False)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color="#2e7d32", size=28),
                    ft.Text("Registrar Devolución", size=20, weight=ft.FontWeight.BOLD, color="#263238")
                ]),
                content=ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.BOOK_ROUNDED, color="#1976d2", size=20),
                                    ft.Text("Libro:", weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(reserva.get("libro_titulo", ""), size=14, color="#546e7a"),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.Icons.PERSON_ROUNDED, color="#1976d2", size=20),
                                    ft.Text("Usuario:", weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(reserva.get("cedula_usuario", ""), size=14, color="#546e7a"),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.Icons.CALENDAR_TODAY_ROUNDED, color="#1976d2", size=20),
                                    ft.Text("Fecha préstamo:", weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(reserva.get("fecha_prestamo", ""), size=14, color="#546e7a"),
                                ]),
                            ], spacing=10),
                            bgcolor="#e3f2fd",
                            padding=15,
                            border_radius=8,
                        ),
                        ft.Divider(height=20, color="transparent"),
                        observaciones_field,
                    ], tight=True, spacing=10),
                    width=500,
                ),
                actions=[
                    ft.TextButton(
                        "Cancelar",
                        on_click=lambda e: setattr(dlg, "open", False) or self._page.update()
                    ),
                    ft.ElevatedButton(
                        "Confirmar Devolución",
                        icon=ft.Icons.CHECK_ROUNDED,
                        on_click=guardar_devolucion,
                        bgcolor="#2e7d32",
                        color=ft.Colors.WHITE,
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            self._page.overlay.append(dlg)
            dlg.open = True
            self._page.update()

        # =========================
        # Renovar préstamo (extender fecha esperada)
        # =========================
        def renovar_prestamo(reserva: dict):
            # Calcular fecha base (hoy o la esperada si es futura)
            base_date = datetime.now().date()
            fecha_esperada = reserva.get("fecha_devolucion_esperada")
            try:
                if isinstance(fecha_esperada, str) and fecha_esperada:
                    parsed = datetime.strptime(fecha_esperada, "%Y-%m-%d").date()
                    base_date = parsed if parsed > base_date else base_date
                elif hasattr(fecha_esperada, "date") and fecha_esperada:
                    parsed = fecha_esperada.date()
                    base_date = parsed if parsed > base_date else base_date
            except Exception:
                pass

            sugerida = (base_date + timedelta(days=20)).strftime("%Y-%m-%d")

            nueva_fecha_field = ft.TextField(
                label="Nueva fecha de devolución",
                hint_text="YYYY-MM-DD",
                prefix_icon=ft.Icons.CALENDAR_TODAY_ROUNDED,
                value=sugerida,
                bgcolor="#f5f7fa",
                border_radius=8,
            )

            def confirmar_renovacion(e):
                try:
                    # Validar formato
                    datetime.strptime((nueva_fecha_field.value or "").strip(), "%Y-%m-%d")
                    self._db.actualizar_fecha_devolucion_esperada(
                        int(reserva.get("id_reserva")),
                        (nueva_fecha_field.value or "").strip()
                    )
                    snack("✅ Préstamo renovado correctamente")
                    dlg.open = False
                    self._page.update()
                    cargar_reservas()
                except ValueError:
                    snack("❌ Formato de fecha inválido. Use YYYY-MM-DD", ok=False)
                except Exception as ex:
                    snack(f"❌ Error: {str(ex)}", ok=False)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.EVENT_AVAILABLE_ROUNDED, color="#0288d1", size=28),
                    ft.Text("Renovar Préstamo", size=20, weight=ft.FontWeight.BOLD, color="#263238")
                ]),
                content=ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.BOOK_ROUNDED, color="#1976d2", size=20),
                                    ft.Text("Libro:", weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(reserva.get("libro_titulo", ""), size=14, color="#546e7a"),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.Icons.PERSON_ROUNDED, color="#1976d2", size=20),
                                    ft.Text("Usuario:", weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(reserva.get("cedula_usuario", ""), size=14, color="#546e7a"),
                                ]),
                            ], spacing=8),
                            bgcolor="#e3f2fd",
                            padding=12,
                            border_radius=8,
                        ),
                        ft.Divider(height=8, color="transparent"),
                        nueva_fecha_field,
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.INFO_ROUNDED, color="#1976d2", size=16),
                                ft.Text("Fecha sugerida: 20 días desde hoy", size=12, color="#757575", italic=True),
                            ]),
                            bgcolor="#e3f2fd",
                            padding=8,
                            border_radius=6,
                        ),
                    ], tight=True, spacing=10),
                    width=460,
                    height=260,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: setattr(dlg, "open", False) or self._page.update()),
                    ft.ElevatedButton(
                        "Renovar",
                        icon=ft.Icons.CHECK_ROUNDED,
                        on_click=confirmar_renovacion,
                        bgcolor="#0288d1",
                        color=ft.Colors.WHITE,
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            self._page.overlay.append(dlg)
            dlg.open = True
            self._page.update()

        # =========================
        # Marcar NO DEVUELTO
        # =========================
        def marcar_no_devuelto(reserva: dict):
            obs_field = ft.TextField(
                label="Observaciones (opcional)",
                multiline=True,
                min_lines=2,
                max_lines=4,
                bgcolor="#f5f7fa",
                border_radius=8,
            )

            def confirmar_no_devuelto(e):
                try:
                    self._db.marcar_no_devuelto(
                        int(reserva.get("id_reserva")),
                        obs_field.value
                    )
                    snack("⚠️ Marcado como NO DEVUELTO")
                    dlg.open = False
                    self._page.update()
                    cargar_reservas()
                except Exception as ex:
                    snack(f"❌ Error: {str(ex)}", ok=False)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.REPORT_ROUNDED, color="#d32f2f", size=28),
                    ft.Text("Marcar NO DEVUELTO", size=20, weight=ft.FontWeight.BOLD)
                ]),
                content=ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Icon(ft.Icons.BOOK_ROUNDED, color="#1976d2", size=20),
                                    ft.Text("Libro:", weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(reserva.get("libro_titulo", ""), size=14, color="#546e7a"),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.Icons.PERSON_ROUNDED, color="#1976d2", size=20),
                                    ft.Text("Usuario:", weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(reserva.get("cedula_usuario", ""), size=14, color="#546e7a"),
                                ]),
                            ], spacing=10),
                            bgcolor="#fdecea",
                            padding=15,
                            border_radius=8,
                        ),
                        ft.Divider(height=10, color="transparent"),
                        obs_field,
                    ], spacing=12),
                    width=500,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: setattr(dlg, "open", False) or self._page.update()),
                    ft.ElevatedButton(
                        "Confirmar",
                        icon=ft.Icons.CHECK_ROUNDED,
                        on_click=confirmar_no_devuelto,
                        bgcolor="#d32f2f",
                        color=ft.Colors.WHITE,
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            self._page.overlay.append(dlg)
            dlg.open = True
            self._page.update()

        # =========================
        # Ver historial de usuario
        # =========================
        def ver_historial_usuario(identificacion):
            if not identificacion:
                snack("❌ No se encontró la identificación", ok=False)
                return
            
            try:
                print(f"Buscando historial para identificación: {identificacion}")
                historial = self._db.get_historial_prestamos_usuario(identificacion)
                print(f"Historial obtenido: {len(historial)} registros")
                
                if not historial:
                    snack(f"ℹ️ No hay historial para la identificación {identificacion}")
                    return
                
                # Función para exportar a Excel/CSV
                def exportar_excel(e):
                    try:
                        import csv
                        from datetime import datetime
                        import os
                        
                        # Guardar en carpeta Downloads del usuario
                        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
                        nombre_archivo = os.path.join(downloads, f"historial_{identificacion}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                        
                        with open(nombre_archivo, 'w', newline='', encoding='utf-8-sig') as archivo:
                            writer = csv.writer(archivo)
                            writer.writerow(['Libro', 'Usuario', 'Identificación', 'Fecha Préstamo', 'Fecha Devolución Esperada', 'Fecha Devolución Real', 'Estado', 'Observaciones'])
                            
                            for item in historial:
                                estado = item.get("estado_calculado") or item.get("estado", "PRESTADO")
                                
                                fecha_prestamo = item.get("fecha_prestamo", "")
                                if hasattr(fecha_prestamo, 'strftime'):
                                    fecha_prestamo = fecha_prestamo.strftime("%Y-%m-%d")
                                
                                fecha_dev_esperada = item.get("fecha_devolucion_esperada", "")
                                if hasattr(fecha_dev_esperada, 'strftime'):
                                    fecha_dev_esperada = fecha_dev_esperada.strftime("%Y-%m-%d")
                                
                                fecha_dev_real = item.get("fecha_devolucion_real", "")
                                if hasattr(fecha_dev_real, 'strftime'):
                                    fecha_dev_real = fecha_dev_real.strftime("%Y-%m-%d")
                                elif not fecha_dev_real:
                                    fecha_dev_real = "Pendiente"
                                
                                writer.writerow([
                                    item.get("libro_titulo", ""),
                                    item.get("nombre_usuario", ""),
                                    identificacion,
                                    fecha_prestamo,
                                    fecha_dev_esperada,
                                    fecha_dev_real,
                                    estado,
                                    item.get("observaciones", "") or ""
                                ])
                        
                        # Mensaje de confirmación
                        snack(f"✅ Excel descargado exitosamente en Downloads")
                        
                        # Diálogo de confirmación adicional
                        dlg_descargado = ft.AlertDialog(
                            title=ft.Row([
                                ft.Icon(ft.Icons.CHECK_CIRCLE, color="#2e7d32", size=32),
                                ft.Text("Excel Descargado", size=18, weight=ft.FontWeight.BOLD)
                            ]),
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("El archivo se descargó correctamente en:", size=14),
                                    ft.Container(
                                        content=ft.Text(nombre_archivo, size=12, color="#1565c0", selectable=True),
                                        bgcolor="#e3f2fd",
                                        padding=10,
                                        border_radius=5,
                                    ),
                                ], spacing=10),
                                width=500,
                            ),
                            actions=[
                                ft.TextButton("OK", on_click=lambda e: setattr(dlg_descargado, "open", False) or self._page.update())
                            ],
                        )
                        
                        self._page.overlay.append(dlg_descargado)
                        dlg_descargado.open = True
                        self._page.update()
                        
                    except Exception as ex:
                        import traceback
                        print(traceback.format_exc())
                        snack(f"❌ Error al exportar: {str(ex)}", ok=False)
                
                # Tabla de historial
                historial_table = ft.DataTable(
                    bgcolor=ft.Colors.WHITE,
                    border=ft.border.all(1, "#e0e0e0"),
                    border_radius=8,
                    heading_row_color="#f5f7fa",
                    heading_row_height=48,
                    data_row_min_height=50,
                    column_spacing=20,
                    columns=[
                        ft.DataColumn(label=ft.Text("Libro", weight=ft.FontWeight.BOLD, size=12)),
                        ft.DataColumn(label=ft.Text("Préstamo", weight=ft.FontWeight.BOLD, size=12)),
                        ft.DataColumn(label=ft.Text("Devolución", weight=ft.FontWeight.BOLD, size=12)),
                        ft.DataColumn(label=ft.Text("Estado", weight=ft.FontWeight.BOLD, size=12)),
                    ],
                    rows=[],
                )
                
                for item in historial:
                    estado = item.get("estado_calculado") or item.get("estado", "PRESTADO")
                    estado_color = "#2e7d32" if estado == "DEVUELTO" else "#d32f2f" if estado == "NO DEVUELTO" else "#1976d2"
                    
                    fecha_prestamo = item.get("fecha_prestamo", "")
                    if hasattr(fecha_prestamo, 'strftime'):
                        fecha_prestamo = fecha_prestamo.strftime("%Y-%m-%d")
                    
                    fecha_dev = item.get("fecha_devolucion_real") or item.get("fecha_devolucion_esperada", "")
                    if hasattr(fecha_dev, 'strftime'):
                        fecha_dev = fecha_dev.strftime("%Y-%m-%d")
                    
                    historial_table.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(item.get("libro_titulo", "")[:30], size=12)),
                            ft.DataCell(ft.Text(str(fecha_prestamo), size=12)),
                            ft.DataCell(ft.Text(str(fecha_dev) if fecha_dev else "—", size=12)),
                            ft.DataCell(
                                ft.Container(
                                    content=ft.Text(estado, color=ft.Colors.WHITE, size=11, weight=ft.FontWeight.BOLD),
                                    bgcolor=estado_color,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                    border_radius=6,
                                )
                            ),
                        ])
                    )
                
                usuario_nombre = historial[0].get("nombre_usuario", "Usuario")
                
                dlg_historial = ft.AlertDialog(
                    modal=True,
                    title=ft.Row([
                        ft.Icon(ft.Icons.HISTORY_ROUNDED, color="#1976d2", size=28),
                        ft.Text("Historial de Préstamos", size=20, weight=ft.FontWeight.BOLD)
                    ]),
                    content=ft.Container(
                        content=ft.Column([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(usuario_nombre, size=18, weight=ft.FontWeight.BOLD, color="#263238"),
                                    ft.Text(f"ID: {identificacion}", size=14, color="#757575"),
                                    ft.Text(f"Total de préstamos: {len(historial)}", size=14, weight=ft.FontWeight.W_500, color="#1976d2"),
                                ]),
                                bgcolor="#e3f2fd",
                                padding=12,
                                border_radius=8,
                            ),
                            ft.Container(
                                content=ft.Column([historial_table], scroll=ft.ScrollMode.AUTO),
                                height=260,
                            ),
                        ], spacing=12),
                        width=600,
                        height=380,
                    ),
                    actions=[
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, size=18),
                                ft.Text("Descargar")
                            ], spacing=8),
                            on_click=exportar_excel,
                            bgcolor="#2e7d32",
                            color=ft.Colors.WHITE,
                        ),
                        ft.TextButton(
                            "Cerrar",
                            on_click=lambda e: setattr(dlg_historial, "open", False) or self._page.update()
                        ),
                    ],
                )
                
                self._page.overlay.append(dlg_historial)
                dlg_historial.open = True
                self._page.update()
                
            except Exception as ex:
                import traceback
                print(traceback.format_exc())
                snack(f"❌ Error: {str(ex)}", ok=False)

        # =========================
        # Confirmar eliminar
        # =========================
        def confirmar_eliminar(id_prestamo):
            def eliminar(e):
                try:
                    self._db.eliminar_prestamo(int(id_prestamo))
                    snack("🗑️ Préstamo eliminado correctamente")
                    dlg.open = False
                    self._page.update()
                    cargar_reservas()
                except Exception as ex:
                    snack(f"❌ Error: {str(ex)}", ok=False)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.WARNING_ROUNDED, color="#d32f2f", size=28),
                    ft.Text("Confirmar Eliminación", size=18, weight=ft.FontWeight.BOLD)
                ]),
                content=ft.Text("¿Estás seguro de que deseas eliminar este préstamo?\nEsta acción no se puede deshacer.", size=14),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: setattr(dlg, "open", False) or self._page.update()),
                    ft.ElevatedButton(
                        "Eliminar",
                        icon=ft.Icons.DELETE_ROUNDED,
                        on_click=eliminar,
                        bgcolor="#d32f2f",
                        color=ft.Colors.WHITE,
                    ),
                ],
            )
            
            self._page.overlay.append(dlg)
            dlg.open = True
            self._page.update()

        # =========================
        # Nuevo préstamo Mejorado
        # =========================
        def nuevo_prestamo(e):
            libros = self._db.get_libros()
            libros_activos = [l for l in libros if l.get("activo") == 1]
            
            # Cargar usuarios desde la base de datos
            try:
                usuarios = self._db.get_usuarios()
                usuarios_activos = [u for u in usuarios if u.get("activo") == 1]
            except Exception as ex:
                print(f"Error al cargar usuarios: {ex}")
                usuarios_activos = []

            libros_seleccionados = []
            usuarios_seleccionados = []

            def actualizar_dropdown_libros(lista):
                libro_dd.options = [
                    ft.dropdown.Option(
                        key=str(l["id_libro"]),
                        text=f"{l['titulo'][:50]}{'...' if len(l['titulo']) > 50 else ''}"
                    )
                    for l in lista
                ]

            def actualizar_dropdown_usuarios(lista):
                identificacion_dd.options = [
                    ft.dropdown.Option(
                        key=str(u.get("identificacion", "")),
                        text=f"{u.get('nombre_completo', 'Sin nombre')[:30]} - {u.get('identificacion', '')}"
                    )
                    for u in lista
                ] if lista else [ft.dropdown.Option("", "No hay usuarios disponibles")]

            def filtrar_libros(e):
                busqueda = (buscar_libro_input.value or "").lower().strip()
                if not busqueda:
                    actualizar_dropdown_libros(libros_activos)
                else:
                    actualizar_dropdown_libros([l for l in libros_activos if busqueda in l.get("titulo", "").lower()])
                self._page.update()

            def filtrar_usuarios(e):
                busqueda = (buscar_usuario_input.value or "").lower().strip()
                if not busqueda:
                    actualizar_dropdown_usuarios(usuarios_activos)
                else:
                    actualizar_dropdown_usuarios([
                        u for u in usuarios_activos
                        if busqueda in (u.get("nombre_completo", "").lower())
                        or busqueda in str(u.get("identificacion", "")).lower()
                    ])
                self._page.update()

            def actualizar_lista_libros():
                libros_seleccionados_column.controls.clear()
                for l in libros_seleccionados:
                    libros_seleccionados_column.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(l["texto"], size=13, color=ft.Colors.WHITE),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    icon_size=16,
                                    icon_color=ft.Colors.WHITE,
                                    on_click=lambda e, lid=l["id"]: remover_libro(lid),
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=8,
                            bgcolor="#1976d2",
                            border_radius=6,
                        )
                    )
                self._page.update()

            def actualizar_lista_usuarios():
                usuarios_seleccionados_column.controls.clear()
                for u in usuarios_seleccionados:
                    usuarios_seleccionados_column.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(u["texto"], size=13, color=ft.Colors.WHITE),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    icon_size=16,
                                    icon_color=ft.Colors.WHITE,
                                    on_click=lambda e, uid=u["id"]: remover_usuario(uid),
                                ),
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=8,
                            bgcolor="#1976d2",
                            border_radius=6,
                        )
                    )
                self._page.update()

            def agregar_libro(e):
                if not libro_dd.value:
                    return
                libro = next((l for l in libros_activos if str(l.get("id_libro")) == libro_dd.value), None)
                if not libro:
                    return
                libros_seleccionados.clear()
                libros_seleccionados.append({
                    "id": str(libro.get("id_libro")),
                    "texto": f"{libro.get('titulo', '')[:50]}{'...' if len(libro.get('titulo', '')) > 50 else ''}",
                })
                actualizar_lista_libros()
                libro_dd.value = None
                buscar_libro_input.value = ""
                actualizar_dropdown_libros(libros_activos)

            def agregar_usuario(e):
                if not identificacion_dd.value:
                    return
                usuario = next((u for u in usuarios_activos if str(u.get("identificacion", "")) == identificacion_dd.value), None)
                if not usuario:
                    return
                usuarios_seleccionados.clear()
                usuarios_seleccionados.append({
                    "id": str(usuario.get("identificacion", "")),
                    "texto": f"{usuario.get('nombre_completo', 'Sin nombre')[:30]} - {usuario.get('identificacion', '')}",
                })
                actualizar_lista_usuarios()
                identificacion_dd.value = None
                buscar_usuario_input.value = ""
                actualizar_dropdown_usuarios(usuarios_activos)

            def remover_libro(libro_id):
                libros_seleccionados[:] = [l for l in libros_seleccionados if l["id"] != libro_id]
                actualizar_lista_libros()

            def remover_usuario(usuario_id):
                usuarios_seleccionados[:] = [u for u in usuarios_seleccionados if u["id"] != usuario_id]
                actualizar_lista_usuarios()

            buscar_libro_input = ft.TextField(
                label="Buscar libro",
                hint_text="Escriba el título...",
                width=420,
                bgcolor="#f5f7fa",
                border_radius=8,
                on_change=filtrar_libros,
            )

            libro_dd = ft.Dropdown(
                label="Seleccione un libro *",
                width=420,
                bgcolor="#f5f7fa",
                border_radius=8,
                options=[],
            )

            btn_agregar_libro = ft.IconButton(
                icon=ft.Icons.ADD,
                bgcolor="#1976d2",
                icon_color=ft.Colors.WHITE,
                tooltip="Agregar libro",
                on_click=agregar_libro,
            )

            libros_seleccionados_column = ft.Column(spacing=4)

            libros_container = ft.Container(
                content=ft.Column([
                    ft.Row([buscar_libro_input, libro_dd, btn_agregar_libro], spacing=8),
                    ft.Text("Libro seleccionado:", size=12, color="#666"),
                    libros_seleccionados_column,
                ], spacing=8),
                padding=10,
                border=ft.border.all(1, "#cfd8dc"),
                border_radius=8,
                bgcolor="#fafafa",
            )

            buscar_usuario_input = ft.TextField(
                label="Buscar usuario",
                hint_text="Nombre o identificación...",
                width=420,
                bgcolor="#f5f7fa",
                border_radius=8,
                on_change=filtrar_usuarios,
            )

            identificacion_dd = ft.Dropdown(
                label="Seleccione un Usuario *",
                width=420,
                bgcolor="#f5f7fa",
                border_radius=8,
                options=[],
            )

            btn_agregar_usuario = ft.IconButton(
                icon=ft.Icons.ADD,
                bgcolor="#1976d2",
                icon_color=ft.Colors.WHITE,
                tooltip="Agregar usuario",
                on_click=agregar_usuario,
            )

            usuarios_seleccionados_column = ft.Column(spacing=4)

            usuarios_container = ft.Container(
                content=ft.Column([
                    ft.Row([buscar_usuario_input, identificacion_dd, btn_agregar_usuario], spacing=8),
                    ft.Text("Usuario seleccionado:", size=12, color="#666"),
                    usuarios_seleccionados_column,
                ], spacing=8),
                padding=10,
                border=ft.border.all(1, "#cfd8dc"),
                border_radius=8,
                bgcolor="#fafafa",
            )

            actualizar_dropdown_libros(libros_activos)
            actualizar_dropdown_usuarios(usuarios_activos)
            
            # Calcular fecha sugerida (20 días desde hoy)
            fecha_sugerida = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
            
            fecha_dev_input = ft.TextField(
                label="Fecha de Devolución Esperada *",
                value=fecha_sugerida,
                read_only=True,
                width=420,
                bgcolor="#f5f7fa",
                border_radius=8,
            )

            def on_date_change(e):
                if e.control.value:
                    fecha_dev_input.value = e.control.value.strftime("%Y-%m-%d")
                    self._page.update()

            date_picker = ft.DatePicker(
                on_change=on_date_change,
                first_date=datetime.now().date(),
                last_date=(datetime.now() + timedelta(days=365)).date(),
            )
            self._page.overlay.append(date_picker)

            def abrir_calendario(e):
                date_picker.open = True
                self._page.update()

            fecha_row = ft.Row(
                [
                    fecha_dev_input,
                    ft.IconButton(
                        icon=ft.Icons.CALENDAR_TODAY_ROUNDED,
                        tooltip="Seleccionar fecha",
                        on_click=abrir_calendario,
                    ),
                ],
                spacing=8,
            )

            def guardar(ev):
                # Validaciones
                if not libros_seleccionados:
                    snack("❌ Debe seleccionar un libro", ok=False)
                    return
                if not usuarios_seleccionados:
                    snack("❌ Debe seleccionar un usuario", ok=False)
                    return
                if not fecha_dev_input.value or not fecha_dev_input.value.strip():
                    snack("❌ Debe ingresar la fecha de devolución", ok=False)
                    return
                
                try:
                    # Validar formato de fecha
                    datetime.strptime(fecha_dev_input.value.strip(), "%Y-%m-%d")
                    
                    self._db.crear_prestamo(
                        int(libros_seleccionados[0]["id"]),
                        usuarios_seleccionados[0]["id"].strip(),
                        fecha_dev_input.value.strip()
                    )
                    snack("✅ Préstamo creado exitosamente")
                    dlg.open = False
                    self._page.update()
                    cargar_reservas()
                except ValueError:
                    snack("❌ Formato de fecha inválido. Use YYYY-MM-DD", ok=False)
                except Exception as ex:
                    import traceback
                    print(traceback.format_exc())
                    snack(f"❌ Error: {str(ex)}", ok=False)

            def guardar_a_sala(ev):
                # Validaciones iguales
                if not libros_seleccionados:
                    snack("❌ Debe seleccionar un libro", ok=False)
                    return
                if not usuarios_seleccionados:
                    snack("❌ Debe seleccionar un usuario", ok=False)
                    return

                try:
                    hoy_str = datetime.now().strftime("%Y-%m-%d")
                    # Crear préstamo normal con devolución esperada hoy
                    self._db.crear_prestamo(
                        int(libros_seleccionados[0]["id"]),
                        usuarios_seleccionados[0]["id"].strip(),
                        hoy_str,
                    )
                    # Buscar el préstamo recién creado
                    prestamos = self._db.get_prestamos()
                    candidato = None
                    for p in prestamos:
                        if (
                            int(p.get("id_libro", 0)) == int(libros_seleccionados[0]["id"])
                            and str(p.get("identificacion_usuario", "")).strip() == usuarios_seleccionados[0]["id"].strip()
                        ):
                            candidato = p
                            break
                    if not candidato:
                        snack("⚠️ No pude localizar el préstamo recién creado, pero se registró.")
                    else:
                        # Marcar devolución inmediata
                        self._db.actualizar_devolucion_prestamo(
                            int(candidato.get("id_prestamo")),
                            observaciones="Lectura en sala",
                        )
                    snack("✅ Préstamo 'A sala' registrado y devuelto hoy")
                    dlg.open = False
                    self._page.update()
                    cargar_reservas()
                except Exception as ex:
                    import traceback
                    print(traceback.format_exc())
                    snack(f"❌ Error: {str(ex)}", ok=False)

            dlg = ft.AlertDialog(
                modal=True,
                content=ft.Container(
                    width=1000,
                    height=520,
                    padding=ft.padding.all(16),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK)),
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Row(
                                        [
                                            ft.Container(
                                                content=ft.Icon(ft.Icons.ADD_CIRCLE_ROUNDED, size=22, color="#1B6F7A"),
                                                bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN),
                                                width=40,
                                                height=40,
                                                border_radius=8,
                                                alignment=ft.Alignment.CENTER,
                                            ),
                                            ft.Column(
                                                [
                                                    ft.Text("Nuevo Préstamo", size=16, weight=ft.FontWeight.BOLD),
                                                    ft.Text("Información del préstamo", size=12, color="#666"),
                                                ],
                                                spacing=2,
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.CLOSE, size=16, color="#666"),
                                        width=32,
                                        height=32,
                                        alignment=ft.Alignment.CENTER,
                                        on_click=lambda e: setattr(dlg, "open", False) or self._page.update(),
                                        border_radius=8,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Divider(height=8, color="transparent"),
                            ft.Text("Complete la información del préstamo:", size=14, color="#546e7a"),
                            libros_container,
                            usuarios_container,
                            fecha_row,
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.INFO_ROUNDED, color="#1976d2", size=16),
                                    ft.Text("Fecha sugerida: 20 días desde hoy", size=12, color="#757575", italic=True),
                                ]),
                                bgcolor="#e3f2fd",
                                padding=10,
                                border_radius=6,
                            ),
                            ft.Row(
                                [
                                    ft.TextButton("Cancelar", on_click=lambda e: setattr(dlg, "open", False) or self._page.update()),
                                    ft.ElevatedButton(
                                        "Crear Préstamo",
                                        icon=ft.Icons.CHECK_ROUNDED,
                                        on_click=guardar,
                                        bgcolor="#1976d2",
                                        color=ft.Colors.WHITE,
                                    ),
                                    ft.ElevatedButton(
                                        "Crear 'A sala'",
                                        icon=ft.Icons.SCHOOL_ROUNDED,
                                        on_click=guardar_a_sala,
                                        bgcolor="#6a1b9a",
                                        color=ft.Colors.WHITE,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.END,
                                spacing=10,
                            ),
                        ],
                        spacing=12,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ),
            )

            self._page.overlay.append(dlg)
            dlg.open = True
            self._page.update()

        # =========================
        # Botones de acción
        # =========================
        btn_nuevo = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD_ROUNDED, size=20),
                ft.Text("Nuevo Préstamo", size=14, weight=ft.FontWeight.W_500)
            ], spacing=8),
            on_click=nuevo_prestamo,
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            height=48,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=2,
            ),
        )
        
        btn_refrescar = ft.IconButton(
            icon=ft.Icons.REFRESH_ROUNDED,
            icon_color=ft.Colors.WHITE,
            bgcolor="#1976d2",
            tooltip="Refrescar datos",
            on_click=lambda e: cargar_reservas(),
            icon_size=24,
            height=48,
            width=48,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
        )

        # =========================
        # Cards de Estadísticas
        # =========================
        def crear_stat_card(titulo, valor_widget, icon, color, bgcolor):
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(icon, color=ft.Colors.WHITE, size=28),
                            bgcolor=color,
                            width=56,
                            height=56,
                            border_radius=12,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column([
                            valor_widget,
                            ft.Text(titulo, size=13, color="#757575", weight=ft.FontWeight.W_500),
                        ], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
                    ], alignment=ft.MainAxisAlignment.START, spacing=15),
                ], spacing=0),
                bgcolor=bgcolor,
                border=ft.border.all(1, "#e0e0e0"),
                border_radius=12,
                padding=20,
                width=250,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                ),
            )

        stats_row = ft.Row([
            crear_stat_card("Total Préstamos", self.total_prestamos, ft.Icons.LIBRARY_BOOKS_ROUNDED, "#5e35b1", ft.Colors.WHITE),
            crear_stat_card("Préstamos Activos", self.prestamos_activos, ft.Icons.BOOK_ROUNDED, "#1976d2", ft.Colors.WHITE),
            crear_stat_card("Préstamos Vencidos", self.prestamos_vencidos, ft.Icons.WARNING_ROUNDED, "#d32f2f", ft.Colors.WHITE),
            crear_stat_card("Libros Devueltos", self.libros_devueltos, ft.Icons.CHECK_CIRCLE_ROUNDED, "#2e7d32", ft.Colors.WHITE),
        ], spacing=20, scroll=ft.ScrollMode.AUTO)

        # =========================
        # Header/Encabezado
        # =========================
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row([
                        ft.Icon(ft.Icons.ASSIGNMENT_ROUNDED, color="#1565c0", size=32),
                        ft.Text("Gestión de Préstamos", size=26, weight=ft.FontWeight.BOLD, color="#263238"),
                    ], spacing=12),
                    ft.Row([
                        btn_refrescar,
                        btn_nuevo,
                    ], spacing=12),
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
        # Barra de Filtros
        # =========================
        filtros_bar = ft.Container(
            content=ft.Row(
                [
                    self.search_input,
                    self.estado_dd,
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=15,
            ),
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
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
        # Contenedor de Tabla
        # =========================
        tabla_container = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=self.reservas_table,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Container(
                    content=ft.Row(
                        [btn_prev, pagination_label, btn_next],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=6,
                    ),
                    padding=ft.padding.only(top=8),
                ),
            ], scroll=ft.ScrollMode.AUTO),
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

        # =========================
        # Layout Principal
        # =========================
        self.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        header,
                        ft.Container(
                            content=stats_row,
                            padding=ft.padding.symmetric(horizontal=30),
                        ),
                        ft.Container(
                            content=filtros_bar,
                            padding=ft.padding.symmetric(horizontal=30),
                        ),
                        ft.Container(
                            content=tabla_container,
                            padding=0,
                            alignment=ft.Alignment.CENTER,
                            expand=True,
                        ),
                    ],
                    spacing=20,
                    expand=True,
                ),
                bgcolor="#f5f7fa",
                padding=ft.padding.symmetric(vertical=20),
                expand=True,
            )
        ]

        cargar_reservas()
