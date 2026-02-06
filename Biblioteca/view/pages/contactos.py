import flet as ft
from model.database import Database


class ContactosPage(ft.Column):
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
                ft.Text(msg),
                bgcolor=ft.Colors.GREEN_500 if ok else ft.Colors.RED_500
            )
            self._page.snack_bar.open = True
            self._page.update()

        # =========================
        # UI - Inputs
        # =========================
        self.search_input = ft.TextField(
            hint_text="Buscar en todo...",
            prefix_icon=ft.Icons.SEARCH,
            width=360,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        self.tipo_dd = ft.Dropdown(
            width=260,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            value="TODOS",
            options=[
                ft.dropdown.Option("TODOS"),
                ft.dropdown.Option("INSTITUCION"),
                ft.dropdown.Option("PROFESOR"),
                ft.dropdown.Option("ESCUELA"),
                ft.dropdown.Option("COLEGIO"),
                ft.dropdown.Option("UNIVERSIDAD"),
                ft.dropdown.Option("ASOCIACION"),
            ],
        )

        # =========================
        # Tabla
        # =========================
        self.contactos_table = ft.DataTable(
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, "#d0d7de"),
            border_radius=8,
            heading_row_color="#e3f2fd",
            heading_row_height=48,
            data_row_min_height=52,
            data_row_max_height=52,
            column_spacing=30,
            horizontal_margin=16,
            columns=[
                ft.DataColumn(label=ft.Text("Tipo", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Nombre", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Correo", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Teléfono", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Descripción", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD, color="#0d47a1")),
            ],
            rows=[],
        )

        self._contactos_cache = []

        # =========================
        # Dialog form (Editar)
        # =========================
        def open_editar_dialog(contacto: dict):
            self.abrir_dialogo_editar_contacto(contacto)

        def close_dialog(dlg: ft.AlertDialog):
            dlg.open = False
            self._page.update()

        # =========================
        # Acciones
        # =========================
        def action_button(icon, bgcolor, tooltip, on_click=None):
            return ft.Container(
                width=36,
                height=36,
                bgcolor=bgcolor,
                border_radius=6,
                alignment=ft.Alignment.CENTER,
                tooltip=tooltip,
                on_click=on_click,
                content=ft.Icon(icon, color=ft.Colors.WHITE, size=18),
            )

        def confirmar_eliminar(id_contacto: int):
            def eliminar(e):
                try:
                    self._db.eliminar_contacto(id_contacto)
                    snack("🗑️ Contacto eliminado")
                    dlg.open = False
                    self._page.update()
                    cargar_contactos()
                except Exception as ex:
                    snack(f"Error: {ex}", ok=False)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Eliminar contacto"),
                content=ft.Text("¿Seguro que querés eliminar este contacto?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: close_dialog(dlg)),
                    ft.ElevatedButton("Eliminar", bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, on_click=eliminar),
                ],
            )
            self._page.overlay.append(dlg)
            dlg.open = True
            self._page.update()

        # =========================
        # Build row
        # =========================
        def link_cell(text_value: str, url: str):
            if not text_value:
                return ft.DataCell(ft.Text(""))
            return ft.DataCell(
                ft.TextButton(
                    text_value,
                    on_click=lambda e: self._page.launch_url(url),
                    style=ft.ButtonStyle(
                        padding=0,
                        color=ft.Colors.BLUE_700,
                    ),
                )
            )

        def build_row(c: dict) -> ft.DataRow:
            desc = (c.get("descripcion") or "").strip()
            desc_short = (desc[:70] + "…") if len(desc) > 70 else desc

            correo_val = (c.get("correo", "") or "").strip()
            telefono_val = (c.get("telefono", "") or "").strip()
            whatsapp_num = "".join([ch for ch in telefono_val if ch.isdigit()])
            whatsapp_url = f"https://wa.me/{whatsapp_num}" if whatsapp_num else ""

            return ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(c.get("tipo", "") or "")),
                    ft.DataCell(ft.Text(c.get("nombre", "") or "")),
                    link_cell(correo_val, f"mailto:{correo_val}" if correo_val else ""),
                    link_cell(telefono_val, whatsapp_url),
                    ft.DataCell(ft.Text(desc_short)),
                    ft.DataCell(
                        ft.Row(
                            [
                                action_button(
                                    ft.Icons.EDIT,
                                    ft.Colors.ORANGE,
                                    "Editar",
                                    lambda e, cc=c: open_editar_dialog(cc),
                                ),
                                action_button(
                                    ft.Icons.DELETE,
                                    ft.Colors.RED,
                                    "Eliminar",
                                    lambda e, i=int(c["id_contacto"]): confirmar_eliminar(i),
                                ),
                            ],
                            spacing=10,
                        )
                    ),
                ]
            )

        # =========================
        # Filtros
        # =========================
        def match_tipo(c: dict, tipo: str) -> bool:
            tipo = (tipo or "TODOS").strip().upper()
            if tipo == "TODOS":
                return True
            return (c.get("tipo") or "").strip().upper() == tipo

        def match_texto(c: dict, q: str) -> bool:
            if not q:
                return True
            valores = [
                c.get("tipo", ""),
                c.get("nombre", ""),
                c.get("correo", ""),
                c.get("telefono", ""),
                c.get("descripcion", ""),
            ]
            haystack = " | ".join([(v or "") for v in valores]).lower()
            return q in haystack

        def aplicar_filtros(q=None, tipo=None):
            q = (q if q is not None else (self.search_input.value or "")).strip().lower()
            tipo = (tipo if tipo is not None else (self.tipo_dd.value or "TODOS")).strip().upper()

            filas = []
            for c in self._contactos_cache:
                if match_tipo(c, tipo) and match_texto(c, q):
                    filas.append(build_row(c))

            self.contactos_table.rows = filas
            self._page.update()

        # =========================
        # Cargar datos
        # =========================
        def cargar_contactos():
            self._contactos_cache = self._db.get_contactos()
            aplicar_filtros()

        self._cargar_contactos = cargar_contactos

        # Eventos
        def on_search_change(e):
            aplicar_filtros(q=e.control.value, tipo=self.tipo_dd.value)

        def on_tipo_change(e):
            aplicar_filtros(q=self.search_input.value, tipo=e.control.value)

        self.search_input.on_change = on_search_change
        self.tipo_dd.on_change = on_tipo_change

        # Botón nuevo
        btn_nuevo = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.ADD), ft.Text("Crear contacto")], spacing=8),
            on_click=self.abrir_dialogo_crear_contacto,
        )

        # Header (estilo Home)
        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Row(
                [
                    ft.Text("Contactos", size=22, weight=ft.FontWeight.BOLD, color="#38638f"),
                    btn_nuevo,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        container = ft.Container(
            content=ft.Column(
                [
                    header,
                    ft.Row(
                        [self.search_input, self.tipo_dd],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=12,
                    ),
                    ft.Row([self.contactos_table], alignment=ft.MainAxisAlignment.CENTER),
                ],
                spacing=20,
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            expand=True,
        )

        self.controls = [ft.Row([container], expand=True)]

        # Cargar al entrar
        cargar_contactos()

    # =========================
    # Crear Contacto con Diálogo
    # =========================
    def abrir_dialogo_crear_contacto(self, e=None):
        INPUT_STYLE = dict(
            width=320,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        self.crear_tipo_dd = ft.Dropdown(
            label="Tipo *",
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
            value="INSTITUCION",
            options=[
                ft.dropdown.Option("INSTITUCION"),
                ft.dropdown.Option("PROFESOR"),
                ft.dropdown.Option("ESCUELA"),
                ft.dropdown.Option("COLEGIO"),
                ft.dropdown.Option("UNIVERSIDAD"),
                ft.dropdown.Option("ASOCIACION"),
            ],
        )

        self.crear_nombre_input = ft.TextField(label="Nombre", autofocus=True, **INPUT_STYLE)
        self.crear_correo_input = ft.TextField(label="Correo electrónico", **INPUT_STYLE)
        self.crear_telefono_input = ft.TextField(label="Teléfono", **INPUT_STYLE)
        self.crear_descripcion_input = ft.TextField(
            label="Descripción",
            multiline=True,
            min_lines=3,
            max_lines=6,
            width=680,
            bgcolor="#f5f7fa",
            border_radius=8,
        )

        btn_guardar = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.CHECK), ft.Text("Guardar")], spacing=8),
            bgcolor="#0b495c",
            color=ft.Colors.WHITE,
            on_click=self.crear_contacto,
        )

        header_row = ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.CONTACT_MAIL, size=22, color="#1B6F7A"),
                    bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN),
                    width=40,
                    height=40,
                    border_radius=8,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column([
                    ft.Text("Crear contacto", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Completa los datos del contacto", size=12, color="#666")
                ], spacing=2)
            ], spacing=10),
            ft.Container(
                content=ft.Icon(ft.Icons.CLOSE, size=18, color="#666"),
                width=36,
                height=36,
                alignment=ft.Alignment.CENTER,
                on_click=self.cerrar_dialogo_contacto,
                border_radius=8,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        form_column = ft.Column([
            ft.Text("Información", size=14, weight=ft.FontWeight.BOLD, color="#0b495c"),
            self.crear_tipo_dd,
            self.crear_nombre_input,
            ft.Row([self.crear_correo_input, self.crear_telefono_input], spacing=12),
            self.crear_descripcion_input,
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        content = ft.Column([
            header_row,
            ft.Divider(height=8, color="transparent"),
            form_column,
            ft.Divider(height=6, color="transparent"),
            ft.Row([
                ft.TextButton("Cancelar", on_click=self.cerrar_dialogo_contacto),
                btn_guardar
            ], alignment=ft.MainAxisAlignment.END, spacing=12)
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        self.dialog_contacto = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                width=780,
                padding=ft.padding.all(18),
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                content=content,
            )
        )

        self._page.overlay.clear()
        self._page.overlay.append(self.dialog_contacto)
        self.dialog_contacto.open = True
        self._page.update()

    def crear_contacto(self, e):
        try:
            tipo = (self.crear_tipo_dd.value or "").strip().upper()
            correo_val = (self.crear_correo_input.value or "").strip()

            if not tipo:
                self._page.snack_bar = ft.SnackBar(ft.Text("El tipo es obligatorio."), bgcolor=ft.Colors.RED_500)
                self._page.snack_bar.open = True
                self._page.update()
                return

            if correo_val and "@" not in correo_val:
                self._page.snack_bar = ft.SnackBar(ft.Text("El correo debe contener '@'."), bgcolor=ft.Colors.RED_500)
                self._page.snack_bar.open = True
                self._page.update()
                return

            self._db.crear_contacto(
                tipo=tipo,
                institucion="N/A",
                nombre=(self.crear_nombre_input.value or "").strip() or None,
                correo=correo_val or None,
                telefono=(self.crear_telefono_input.value or "").strip() or None,
                descripcion=(self.crear_descripcion_input.value or "").strip() or None,
            )

            self._page.snack_bar = ft.SnackBar(ft.Text("✅ Contacto guardado correctamente"), bgcolor=ft.Colors.GREEN_500)
            self._page.snack_bar.open = True
            self.cerrar_dialogo_contacto()
            if hasattr(self, "_cargar_contactos"):
                self._cargar_contactos()

        except Exception as ex:
            self._page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.Colors.RED_500)
            self._page.snack_bar.open = True
            self._page.update()

    # =========================
    # Editar Contacto con Diálogo
    # =========================
    def abrir_dialogo_editar_contacto(self, contacto: dict):
        self._edit_contacto_id = int(contacto["id_contacto"])
        self._edit_contacto_institucion = (contacto.get("institucion") or "N/A")

        INPUT_STYLE = dict(
            width=320,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        self.editar_tipo_dd = ft.Dropdown(
            label="Tipo *",
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
            value=(contacto.get("tipo") or "INSTITUCION"),
            options=[
                ft.dropdown.Option("INSTITUCION"),
                ft.dropdown.Option("PROFESOR"),
                ft.dropdown.Option("ESCUELA"),
                ft.dropdown.Option("COLEGIO"),
                ft.dropdown.Option("UNIVERSIDAD"),
                ft.dropdown.Option("ASOCIACION"),
            ],
        )

        self.editar_nombre_input = ft.TextField(
            label="Nombre",
            value=(contacto.get("nombre") or ""),
            **INPUT_STYLE,
        )

        self.editar_correo_input = ft.TextField(
            label="Correo electrónico",
            value=(contacto.get("correo") or ""),
            **INPUT_STYLE,
        )

        self.editar_telefono_input = ft.TextField(
            label="Teléfono",
            value=(contacto.get("telefono") or ""),
            **INPUT_STYLE,
        )

        self.editar_descripcion_input = ft.TextField(
            label="Descripción",
            multiline=True,
            min_lines=3,
            max_lines=6,
            width=680,
            bgcolor="#f5f7fa",
            border_radius=8,
            value=(contacto.get("descripcion") or ""),
        )

        btn_guardar = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.CHECK), ft.Text("Guardar")], spacing=8),
            bgcolor="#0b495c",
            color=ft.Colors.WHITE,
            on_click=self.guardar_edicion_contacto,
        )

        header_row = ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.EDIT, size=22, color="#1B6F7A"),
                    bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN),
                    width=40,
                    height=40,
                    border_radius=8,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column([
                    ft.Text("Editar contacto", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Actualiza los datos del contacto", size=12, color="#666")
                ], spacing=2)
            ], spacing=10),
            ft.Container(
                content=ft.Icon(ft.Icons.CLOSE, size=18, color="#666"),
                width=36,
                height=36,
                alignment=ft.Alignment.CENTER,
                on_click=self.cerrar_dialogo_editar_contacto,
                border_radius=8,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        form_column = ft.Column([
            ft.Text("Información", size=14, weight=ft.FontWeight.BOLD, color="#0b495c"),
            self.editar_tipo_dd,
            self.editar_nombre_input,
            ft.Row([self.editar_correo_input, self.editar_telefono_input], spacing=12),
            self.editar_descripcion_input,
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        content = ft.Column([
            header_row,
            ft.Divider(height=8, color="transparent"),
            form_column,
            ft.Divider(height=6, color="transparent"),
            ft.Row([
                ft.TextButton("Cancelar", on_click=self.cerrar_dialogo_editar_contacto),
                btn_guardar
            ], alignment=ft.MainAxisAlignment.END, spacing=12)
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        self.dialog_contacto_editar = ft.AlertDialog(
            modal=True,
            content=ft.Container(
                width=780,
                padding=ft.padding.all(18),
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                content=content,
            )
        )

        self._page.overlay.clear()
        self._page.overlay.append(self.dialog_contacto_editar)
        self.dialog_contacto_editar.open = True
        self._page.update()

    def guardar_edicion_contacto(self, e):
        try:
            print("[EDIT] Iniciando guardar_edicion_contacto...")
            tipo = (self.editar_tipo_dd.value or "").strip().upper()
            correo_val = (self.editar_correo_input.value or "").strip()

            print(f"[EDIT] tipo={tipo}, correo={correo_val}, id={self._edit_contacto_id}")

            if not tipo:
                self._page.snack_bar = ft.SnackBar(ft.Text("El tipo es obligatorio."), bgcolor=ft.Colors.RED_500)
                self._page.snack_bar.open = True
                self._page.update()
                return

            if correo_val and "@" not in correo_val:
                self._page.snack_bar = ft.SnackBar(ft.Text("El correo debe contener '@'."), bgcolor=ft.Colors.RED_500)
                self._page.snack_bar.open = True
                self._page.update()
                return

            print("[EDIT] Llamando a _db.editar_contacto()...")
            self._db.editar_contacto(
                id_contacto=self._edit_contacto_id,
                tipo=tipo,
                institucion=self._edit_contacto_institucion,
                nombre=(self.editar_nombre_input.value or "").strip() or None,
                correo=correo_val or None,
                telefono=(self.editar_telefono_input.value or "").strip() or None,
                descripcion=(self.editar_descripcion_input.value or "").strip() or None,
            )
            print("[EDIT] Contacto actualizado en BD")

            self._page.snack_bar = ft.SnackBar(ft.Text("✅ Contacto actualizado"), bgcolor=ft.Colors.GREEN_500)
            self._page.snack_bar.open = True
            self.cerrar_dialogo_editar_contacto()
            if hasattr(self, "_cargar_contactos"):
                self._cargar_contactos()
            print("[EDIT] Contacto actualizado completamente")

        except Exception as ex:
            print(f"[EDIT] ERROR: {ex}")
            import traceback
            traceback.print_exc()
            self._page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.Colors.RED_500)
            self._page.snack_bar.open = True
            self._page.update()

    def cerrar_dialogo_editar_contacto(self, e=None):
        if hasattr(self, "dialog_contacto_editar") and self.dialog_contacto_editar:
            self.dialog_contacto_editar.open = False
            self._page.update()

    def cerrar_dialogo_contacto(self, e=None):
        if hasattr(self, "dialog_contacto") and self.dialog_contacto:
            self.dialog_contacto.open = False
            self._page.update()
