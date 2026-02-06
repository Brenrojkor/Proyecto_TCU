import flet as ft
from model.database import Database

class UsuariosPage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self.db = Database()
        self.dialog = None
        self.usuario_editando = None

        # Botón crear usuario
        self.btn_crear = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.ADD), ft.Text("Crear usuario")], spacing=8),
            on_click=self.abrir_dialogo_crear,
        )

        # Input de búsqueda
        self.search_input = ft.TextField(
            hint_text="Buscar usuario...",
            prefix_icon=ft.Icons.SEARCH,
            width=320,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
            on_change=lambda e: self.mostrar_usuarios(),
        )

        # Tabla de usuarios
        self.usuarios_table = ft.DataTable(
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, "#d0d7de"),
            border_radius=8,
            width=1100,
            heading_row_color="#e3f2fd",
            heading_row_height=48,
            data_row_min_height=52,
            data_row_max_height=52,
            column_spacing=20,
            horizontal_margin=16,
            columns=[
                ft.DataColumn(ft.Text("Nombre completo", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(ft.Text("Identificación", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(ft.Text("Provincia", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(ft.Text("Cantón", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(ft.Text("Distrito", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(ft.Text("Activo", weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD, color="#0d47a1")),
            ],
            rows=[],
        )

        # Layout principal
        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Row([ft.Text("Usuarios Registrados", size=22, weight=ft.FontWeight.BOLD, color="#38638f"), self.btn_crear],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        )

        container = ft.Container(
            content=ft.Column([header,
                               ft.Row([self.search_input], alignment=ft.MainAxisAlignment.END),
                               ft.Row([self.usuarios_table], alignment=ft.MainAxisAlignment.CENTER)],
                              spacing=20),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            expand=True,
        )

        self.controls = [ft.Row([container], alignment=ft.MainAxisAlignment.CENTER, expand=True)]
        self.mostrar_usuarios()

    # Botón de acción para tabla
    def action_button(self, icon, bgcolor, tooltip, on_click=None):
        return ft.Container(width=36, height=36, bgcolor=bgcolor, border_radius=6, tooltip=tooltip,
                            on_click=on_click, alignment=ft.Alignment.CENTER,
                            content=ft.Icon(icon, color=ft.Colors.WHITE, size=18))

    # Abrir diálogo
    def abrir_dialogo_crear(self, e):
        self.usuario_editando = None
        self._crear_dialogo()

    def abrir_dialogo_editar(self, usuario):
        self.usuario_editando = usuario
        self._editar_dialogo(usuario)

    def _crear_dialogo(self):
        INPUT_STYLE = dict(width=320, height=48, bgcolor="#f5f7fa", border_radius=8, border_color="#cfd8dc",
                           focused_border_color="#1976d2", text_size=14)
        SHORT_INPUT = dict(width=200, height=48, bgcolor="#f5f7fa", border_radius=8, border_color="#cfd8dc", text_size=14)
        TINY_INPUT = dict(width=120, height=48, bgcolor="#f5f7fa", border_radius=8, border_color="#cfd8dc", text_size=14)

        # Campos vacíos para crear
        self.nombre_input = ft.TextField(label="Nombre completo *", value="", autofocus=True, **INPUT_STYLE)
        self.identificacion_input = ft.TextField(label="Identificación", value="", **INPUT_STYLE)
        self.provincia_input = ft.TextField(label="Provincia", value="", **INPUT_STYLE)
        self.canton_input = ft.TextField(label="Cantón", value="", **INPUT_STYLE)
        self.distrito_input = ft.TextField(label="Distrito", value="", **INPUT_STYLE)
        self.rango_edad_input = ft.TextField(label="Rango de edad", value="", **SHORT_INPUT)
        self.sexo_input = ft.TextField(label="Sexo", value="", **TINY_INPUT)
        self.curso_input = ft.TextField(label="Curso", value="", **SHORT_INPUT)
        self.anio_input = ft.TextField(label="Año", value="", **TINY_INPUT)
        self.discapacidad_input = ft.Checkbox(label="Discapacidad", value=False)
        self.grupo_input = ft.Checkbox(label="Grupo", value=False)
        self.activo_input = ft.Checkbox(label="Activo", value=True)
        self.telefono_input = ft.TextField(label="Teléfono", value="", **INPUT_STYLE)
        self.comentario_input = ft.TextField(label="Comentario", value="", width=520, multiline=True, min_lines=2, max_lines=4, bgcolor="#f5f7fa", border_radius=8)

        self.btn_guardar = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.CHECK), ft.Text("Guardar")], spacing=8),
            bgcolor="#0b495c",
            color=ft.Colors.WHITE,
            on_click=self.guardar_usuario,
        )

        header_row = ft.Row([
            ft.Row([ft.Container(content=ft.Icon(ft.Icons.PERSON, size=22, color="#1B6F7A"), bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN), width=40, height=40, border_radius=8, alignment=ft.Alignment.CENTER),
                    ft.Column([ft.Text("Crear usuario", size=18, weight=ft.FontWeight.BOLD), ft.Text("Completa los datos del usuario", size=12, color="#666")], spacing=2)], spacing=10),
            ft.Container(content=ft.Icon(ft.Icons.CLOSE, size=18, color="#666"), width=36, height=36, alignment=ft.Alignment.CENTER, on_click=self.cerrar_dialogo, border_radius=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        form_column = ft.Column([
            self.nombre_input,
            ft.Row([self.identificacion_input, self.telefono_input], spacing=12),
            ft.Row([self.provincia_input, ft.Container(content=self.canton_input, width=SHORT_INPUT['width']), ft.Container(content=self.distrito_input, width=SHORT_INPUT['width'])], spacing=12),
            ft.Row([self.rango_edad_input, self.sexo_input, self.anio_input, self.curso_input], spacing=12),
            ft.Row([self.discapacidad_input, self.grupo_input, self.activo_input], spacing=20),
            self.comentario_input
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        content = ft.Column([
            header_row,
            ft.Divider(height=8, color="transparent"),
            form_column,
            ft.Divider(height=6, color="transparent"),
            ft.Row([ft.TextButton("Cancelar", on_click=self.cerrar_dialogo), self.btn_guardar], alignment=ft.MainAxisAlignment.END, spacing=12)
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        self.dialog = ft.AlertDialog(modal=True, content=ft.Container(width=780, padding=ft.padding.all(18), bgcolor=ft.Colors.WHITE, border_radius=12, content=content))

        self._page.overlay.clear()
        self._page.overlay.append(self.dialog)
        self.dialog.open = True
        self._page.update()

    def _editar_dialogo(self, usuario):
        INPUT_STYLE = dict(width=320, height=48, bgcolor="#f5f7fa", border_radius=8, border_color="#cfd8dc",
                           focused_border_color="#1976d2", text_size=14)
        SHORT_INPUT = dict(width=200, height=48, bgcolor="#f5f7fa", border_radius=8, border_color="#cfd8dc", text_size=14)
        TINY_INPUT = dict(width=120, height=48, bgcolor="#f5f7fa", border_radius=8, border_color="#cfd8dc", text_size=14)

        # Campos con datos del usuario
        self.nombre_input = ft.TextField(label="Nombre completo *", value=usuario.get("nombre_completo", ""), autofocus=True, **INPUT_STYLE)
        self.identificacion_input = ft.TextField(label="Identificación", value=usuario.get("identificacion", ""), **INPUT_STYLE)
        self.provincia_input = ft.TextField(label="Provincia", value=usuario.get("provincia", ""), **INPUT_STYLE)
        self.canton_input = ft.TextField(label="Cantón", value=usuario.get("canton", ""), **INPUT_STYLE)
        self.distrito_input = ft.TextField(label="Distrito", value=usuario.get("distrito", ""), **INPUT_STYLE)
        self.rango_edad_input = ft.TextField(label="Rango de edad", value=usuario.get("rango_edad", ""), **SHORT_INPUT)
        self.sexo_input = ft.TextField(label="Sexo", value=usuario.get("sexo", ""), **TINY_INPUT)
        self.curso_input = ft.TextField(label="Curso", value=usuario.get("curso", ""), **SHORT_INPUT)
        self.anio_input = ft.TextField(label="Año", value=str(usuario.get("anio", "")), **TINY_INPUT)
        
        self.discapacidad_input = ft.Checkbox(
            label="Discapacidad",
            value=bool(usuario.get("discapacidad"))
        )

        self.grupo_input = ft.Checkbox(
            label="Grupo",
            value=bool(usuario.get("grupo"))
        )

        self.activo_input = ft.Checkbox(
            label="Activo",
            value=bool(usuario.get("activo", True))
        )
        self.telefono_input = ft.TextField(label="Teléfono", value=usuario.get("telefono", ""), **INPUT_STYLE)
        self.comentario_input = ft.TextField(label="Comentario", value=usuario.get("comentario", ""), width=520, multiline=True, min_lines=2, max_lines=4, bgcolor="#f5f7fa", border_radius=8)

        self.btn_guardar = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.CHECK), ft.Text("Guardar")], spacing=8),
            bgcolor="#0b495c",
            color=ft.Colors.WHITE,
            on_click=self.guardar_usuario,
        )

        # Prefill provincia y cantón directamente (sin carga asincrónica)
        prov_text = usuario.get("provincia") or usuario.get("provincia_nombre")
        if prov_text:
            self.provincia_input.value = prov_text
        
        canton_text = usuario.get("canton")
        if canton_text:
            self.canton_input.value = canton_text
            
        distrito_text = usuario.get("distrito")
        if distrito_text:
            self.distrito_input.value = distrito_text

        header_row = ft.Row([
            ft.Row([ft.Container(content=ft.Icon(ft.Icons.PERSON, size=22, color="#1B6F7A"), bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN), width=40, height=40, border_radius=8, alignment=ft.Alignment.CENTER),
                    ft.Column([ft.Text("Editar usuario", size=18, weight=ft.FontWeight.BOLD), ft.Text("Completa los datos del usuario", size=12, color="#666")], spacing=2)], spacing=10),
            ft.Container(content=ft.Icon(ft.Icons.CLOSE, size=18, color="#666"), width=36, height=36, alignment=ft.Alignment.CENTER, on_click=self.cerrar_dialogo, border_radius=8),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        form_column = ft.Column([
            self.nombre_input,
            ft.Row([self.identificacion_input, self.telefono_input], spacing=12),
            ft.Row([self.provincia_input, ft.Container(content=self.canton_input, width=SHORT_INPUT['width']), ft.Container(content=self.distrito_input, width=SHORT_INPUT['width'])], spacing=12),
            ft.Row([self.rango_edad_input, self.sexo_input, self.anio_input, self.curso_input], spacing=12),
            ft.Row([self.discapacidad_input, self.grupo_input, self.activo_input], spacing=20),
            self.comentario_input
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        content = ft.Column([
            header_row,
            ft.Divider(height=8, color="transparent"),
            form_column,
            ft.Divider(height=6, color="transparent"),
            ft.Row([ft.TextButton("Cancelar", on_click=self.cerrar_dialogo), self.btn_guardar], alignment=ft.MainAxisAlignment.END, spacing=12)
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        self.dialog = ft.AlertDialog(modal=True, content=ft.Container(width=780, padding=ft.padding.all(18), bgcolor=ft.Colors.WHITE, border_radius=12, content=content))

        self._page.overlay.clear()
        self._page.overlay.append(self.dialog)
        self.dialog.open = True
        self._page.update()

    # Helpers para carga segura de cantones y distritos
    def _safe_cargar_cantones(self, provincia_key, select_text_if_any=None):
        rows = self._cargar_cantones(provincia_key) or []
        if len(rows) == 1:
            self.canton_input.value = rows[0]
            self._cargar_distritos(rows[0])
        elif select_text_if_any:
            self.canton_input.value = select_text_if_any
            self._cargar_distritos(select_text_if_any)
        self._page.update()
        

    def _cargar_cantones(self, provincia_key):
        try:
            rows = self.db.get_cantones_por_provincia(provincia_key) or []
            names = []
            for r in rows:
                text = r.get("nombre") or r.get("canton") or str(r.get("id_canton") or r.get("id") or "")
                if text:
                    names.append(text)
            self._last_cantones = names
            if len(names) == 1 and not (self.canton_input.value or "").strip():
                self.canton_input.value = names[0]
            return names
        except Exception:
            self._last_cantones = []
            return []
        finally:
            self._page.update()

    def _cargar_distritos(self, canton_identifier_or_name, select_text_if_any=None):
        try:
            rows = self.db.get_distritos_por_canton(canton_identifier_or_name) or []
            names = []
            for r in rows:
                text = r.get("nombre") or r.get("distrito") or str(r.get("id_distrito") or r.get("id") or "")
                if text:
                    names.append(text)
            self._last_distritos = names
            if len(names) == 1 and not (self.distrito_input.value or "").strip():
                self.distrito_input.value = names[0]
            if select_text_if_any:
                self.distrito_input.value = select_text_if_any
            return names
        except Exception:
            self._last_distritos = []
            return []
        finally:
            self._page.update()

    def guardar_usuario(self, e=None):
        print(f"[DEBUG] guardar_usuario llamado, usuario_editando={self.usuario_editando}")
        try:
            self._page.snack_bar = ft.SnackBar(ft.Text("Procesando..."))
            self._page.snack_bar.open = True
            self._page.update()
        except Exception:
            pass

        try:
            try:
                self.btn_guardar.disabled = True
                self.btn_guardar.update()
            except Exception:
                pass

            # Validaciones simples
            nombre = (self.nombre_input.value or "").strip()
            if not nombre:
                self.nombre_input.error_text = "El nombre es obligatorio"
                try:
                    self.btn_guardar.disabled = False
                    self.btn_guardar.update()
                except Exception:
                    pass
                self._page.update()
                return
            self.nombre_input.error_text = None

            provincia_value = (self.provincia_input.value or "").strip()
            canton_text = (self.canton_input.value or "").strip()
            distrito_text = (self.distrito_input.value or "").strip()

            try:
                anio = int(self.anio_input.value) if (self.anio_input.value or "").strip() else None
            except Exception:
                self.anio_input.error_text = "Año inválido"
                self._page.update()
                return

            # Llamada al modelo
            try:
                if self.usuario_editando:
                    # Detectar ID del usuario
                    uid = None
                    for k in ("id_usuario", "id", "idUsuario", "ID"):
                        if isinstance(self.usuario_editando, dict) and self.usuario_editando.get(k) is not None:
                            uid = self.usuario_editando.get(k)
                            break
                    
                    if uid is None:
                        raise ValueError("No se encontró ID de usuario para edición")

                    print(f"[EDIT] Actualizando usuario ID={uid}, nombre={nombre}")
                    grupo_val = bool(self.grupo_input.value) if self.grupo_input else False
                    discapacidad_val = bool(self.discapacidad_input.value) if self.discapacidad_input else False
                    activo_val = bool(self.activo_input.value) if self.activo_input else True
                    print(f"[EDIT] Valores checkboxes: grupo={grupo_val}, discapacidad={discapacidad_val}, activo={activo_val}")
                    print(f"[EDIT] Valores checkboxes raw: grupo_input.value={self.grupo_input.value}, discapacidad_input.value={self.discapacidad_input.value}, activo_input.value={self.activo_input.value}")
                    
                    self.db.update_usuario_biblioteca(
                        uid,
                        nombre,
                        self.identificacion_input.value or "",
                        discapacidad_val,
                        provincia_value,
                        canton_text,
                        distrito_text,
                        self.rango_edad_input.value or "",
                        self.sexo_input.value or "",
                        self.curso_input.value or "",
                        anio,
                        grupo_val,
                        self.telefono_input.value or "",
                        activo_val,
                        self.comentario_input.value or "",
                    )
                    print(f"[EDIT] Usuario actualizado exitosamente")
                else:
                    print(f"[CREATE] Creando nuevo usuario: nombre={nombre}, id={id(self)}")
                    print(f"[CREATE] Parámetros: prov={provincia_value}, canton={canton_text}, distrito={distrito_text}")
                    try:
                        self.db.set_usuarios(
                            nombre_completo=nombre,
                            identificacion=self.identificacion_input.value or "",
                            discapacidad=bool(self.discapacidad_input.value) if self.discapacidad_input else False,
                            provincia=provincia_value,
                            canton=canton_text,
                            distrito=distrito_text,
                            rango_edad=self.rango_edad_input.value or "",
                            sexo=self.sexo_input.value or "",
                            curso=self.curso_input.value or "",
                            anio=anio,
                            grupo=bool(self.grupo_input.value) if self.grupo_input else False,
                            telefono=self.telefono_input.value or "",
                            activo=bool(self.activo_input.value) if self.activo_input else True,
                            comentario=self.comentario_input.value or "",
                        )
                        print(f"[CREATE] Usuario creado exitosamente")
                    except Exception as db_error:
                        print(f"[CREATE ERROR] Excepción en set_usuarios: {db_error}")
                        raise

                # Éxito
                self._page.snack_bar = ft.SnackBar(ft.Text("✅ Usuario guardado"), bgcolor="#1b5e20")
                self._page.snack_bar.open = True
                self.cerrar_dialogo()
                self.mostrar_usuarios()
                try:
                    self.btn_guardar.disabled = False
                    self.btn_guardar.update()
                except Exception:
                    pass
                return

            except Exception as ex:
                # Error en la capa de datos — mostrar al usuario y loguear
                try:
                    self.btn_guardar.disabled = False
                    self.btn_guardar.update()
                except Exception:
                    pass
                self._page.snack_bar = ft.SnackBar(ft.Text(f"Error guardando usuario: {ex}"), bgcolor="#b71c1c")
                self._page.snack_bar.open = True
                self._page.update()
                return

        except Exception as fatal_ex:
            # Capturar cualquier excepción inesperada dentro del handler
            try:
                self._page.snack_bar = ft.SnackBar(ft.Text(f"Error interno: {fatal_ex}"), bgcolor="#b71c1c")
                self._page.snack_bar.open = True
                self._page.update()
            except Exception:
                pass
            # además imprimir en consola para debugging local
            print("[usuarios.guardar_usuario] excepción inesperada:", fatal_ex)
            return

    def cerrar_dialogo(self, e=None):
        if self.dialog:
            self.dialog.open = False
            self._page.update()

    # Mostrar usuarios
    def mostrar_usuarios(self):
        self.usuarios_table.rows.clear()
        filtro = (self.search_input.value or "").lower()
        for usuario in self.db.get_usuarios():
            texto = f'{usuario["nombre_completo"]} {usuario.get("identificacion","")}'.lower()
            if filtro and filtro not in texto:
                continue
            self.usuarios_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(usuario["nombre_completo"])),
                    ft.DataCell(ft.Text(usuario.get("identificacion", ""))),
                    ft.DataCell(ft.Text(usuario.get("provincia", ""))),
                    ft.DataCell(ft.Text(usuario.get("canton", ""))),
                    ft.DataCell(ft.Text(usuario.get("distrito", ""))),
                    ft.DataCell(ft.Text("Sí" if usuario.get("activo", True) else "No")),
                    ft.DataCell(ft.Row([
                        self.action_button(ft.Icons.EDIT, ft.Colors.ORANGE, "Editar", lambda e, u=usuario: self.abrir_dialogo_editar(u)),
                        self.action_button(ft.Icons.BLOCK, ft.Colors.RED, "Desactivar")
                    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER))
                ])
            )
        self._page.update()
