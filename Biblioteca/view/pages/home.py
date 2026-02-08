import flet as ft
from model.database import Database

import os
import sys
import tempfile
import re
import subprocess


class HomePage(ft.Column):
    def __init__(self, navigate, page: ft.Page):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self._db = Database()

        # =========================
        # Helpers
        # =========================
        def snack(msg: str):
            self._page.snack_bar = ft.SnackBar(ft.Text(msg))
            self._page.snack_bar.open = True
            self._page.update()

        def safe_filename(name: str) -> str:
            name = (name or "").strip()
            name = re.sub(r"[^\w\-. ]+", "", name, flags=re.UNICODE)
            if not name.lower().endswith(".pdf"):
                name += ".pdf"
            return name[:150] if name else "documento.pdf"

        def open_file_default_app(path: str):
            try:
                if sys.platform.startswith("win"):
                    os.startfile(path)
                elif sys.platform == "darwin":
                    os.system(f'open "{path}"')
                else:
                    os.system(f'xdg-open "{path}"')
            except Exception as ex:
                print("[ERROR] open_file_default_app:", ex)
                snack(f"No se pudo abrir el archivo: {ex}")

        # =========================
        # Ver PDF
        # =========================
        def ver_pdf(id_libro: int):
            try:
                data = self._db.get_libro_pdf(int(id_libro))
                if not data:
                    snack("Este libro no tiene PDF aún.")
                    return

                nombre = (data.get("nombre_archivo") or f"libro_{id_libro}.pdf")
                contenido = data.get("contenido")
                if contenido is None:
                    snack("El PDF existe pero vino vacío desde la BD.")
                    return

                pdf_bytes = bytes(contenido)

                out_path = os.path.join(
                    tempfile.gettempdir(),
                    f"libro_{id_libro}_{safe_filename(nombre)}"
                )

                with open(out_path, "wb") as f:
                    f.write(pdf_bytes)

                open_file_default_app(out_path)

            except Exception as ex:
                print("[ERROR] ver_pdf:", ex)
                snack(f"Error abriendo PDF: {ex}")

        # =========================
        # Picker PDF
        # =========================
        def pick_pdf_windows() -> str | None:
            powershell_51 = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

            ps_script = r'''
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$owner = New-Object System.Windows.Forms.Form
$owner.Size = New-Object System.Drawing.Size(1,1)
$owner.StartPosition = "Manual"
$owner.Location = New-Object System.Drawing.Point(-32000,-32000)
$owner.TopMost = $true
$owner.ShowInTaskbar = $false
$owner.Opacity = 0
$owner.Show()

$dlg = New-Object System.Windows.Forms.OpenFileDialog
$dlg.Filter = "Archivos PDF (.pdf)|.pdf"
$dlg.Multiselect = $false
$dlg.Title = "Selecciona un archivo PDF"

$result = $dlg.ShowDialog($owner)
$owner.Close()

if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
    Write-Output $dlg.FileName
}
'''

            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".ps1", mode="w", encoding="utf-8") as tmp:
                    tmp.write(ps_script)
                    ps1_path = tmp.name

                creationflags = 0
                if sys.platform.startswith("win"):
                    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

                exe = powershell_51 if os.path.exists(powershell_51) else "powershell.exe"

                result = subprocess.run(
                    [exe, "-NoProfile", "-ExecutionPolicy", "Bypass", "-STA", "-File", ps1_path],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    creationflags=creationflags
                )

                try:
                    os.remove(ps1_path)
                except Exception:
                    pass

                if result.returncode == 0:
                    path = (result.stdout or "").strip()
                    if path:
                        return path

                err = (result.stderr or "").strip()
                if err:
                    snack(f"PowerShell no pudo abrir selector: {err[:180]}")

            except Exception as ex:
                snack(f"PowerShell falló: {ex}")

            try:
                from tkinter import Tk
                from tkinter.filedialog import askopenfilename

                root = Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                path = askopenfilename(
                    title="Selecciona un archivo PDF",
                    filetypes=[("PDF files", "*.pdf")]
                )
                root.destroy()
                return path if path else None
            except Exception as ex:
                snack(f"No se pudo abrir selector (Tkinter): {ex}")
                return None

        # =========================
        # UI
        # =========================
        button_crear_libro = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ADD),
                    ft.Text("Crear libro"),
                ],
                spacing=8,
            ),
            on_click=self.abrir_dialogo_crear_libro,
        )

        search_input = ft.TextField(
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

        # ✅ Dropdown para Activo/Inactivo/Todos
        estado_dd = ft.Dropdown(
            width=200,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            value="TODOS",
            options=[
                ft.dropdown.Option("TODOS"),
                ft.dropdown.Option("ACTIVOS"),
                ft.dropdown.Option("INACTIVOS"),
            ],
        )

        libros_table = ft.DataTable(
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, "#d0d7de"),
            border_radius=8,
            heading_row_color="#e3f2fd",
            heading_row_height=48,
            data_row_min_height=52,
            data_row_max_height=52,
            column_spacing=40,
            horizontal_margin=16,
            columns=[
                ft.DataColumn(label=ft.Text("Código de barras", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),

                ft.DataColumn(label=ft.Text("Título", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Clasificación DUI", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Categoría", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Autores", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("ISBN", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Tipo", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Documentos", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Acciones", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
            ],
            rows=[],
        )

        self._libros_cache = []

        # =========================
        # Subir PDF
        # =========================
        def subir_pdf_para_libro(id_libro: int):
            path = pick_pdf_windows()
            if not path:
                return

            if not path.lower().endswith(".pdf"):
                snack("Solo se permiten archivos PDF.")
                return

            with open(path, "rb") as f:
                pdf_bytes = f.read()

            self._db.upsert_libro_pdf(
                id_libro=id_libro,
                nombre_archivo=safe_filename(os.path.basename(path)),
                contenido=pdf_bytes,
            )

            snack("PDF guardado correctamente ✅")

        # =========================
        # Mostrar libros
        # =========================
        def mostrar_libros(e=None):
            libros_table.rows.clear()
            self._libros_cache = self._db.get_libros()
            aplicar_filtros()

        self._mostrar_libros = mostrar_libros

        # =========================
        # Toggle activo/inactivo
        # =========================
        def toggle_activo(libro_id: int, estado_actual: bool):
            nuevo_estado = 0 if estado_actual else 1
            try:
                self._db.set_libro_activo(libro_id, nuevo_estado)
                snack("Libro activado ✅" if nuevo_estado == 1 else "Libro desactivado ✅")
                mostrar_libros()
            except Exception as ex:
                snack(f"Error al actualizar estado: {ex}")

        # =========================
        # Construir filas
        # =========================
        def build_row(libro: dict) -> ft.DataRow:
            id_libro = int(libro["id_libro"])
            tipo = (libro.get("tipo") or "").strip().upper()

            # ---- Documentos ----
            if tipo == "DIGITAL":
                btn_cargar = ft.ElevatedButton(
                    content=ft.Row(
                        [ft.Icon(ft.Icons.UPLOAD_FILE), ft.Text("Cargar PDF")],
                        spacing=6,
                    ),
                    on_click=lambda e, i=id_libro: subir_pdf_para_libro(i),
                )

                btn_ver = ft.ElevatedButton(
                    content=ft.Row(
                        [ft.Icon(ft.Icons.PICTURE_AS_PDF), ft.Text("Ver PDF")],
                        spacing=6,
                    ),
                    on_click=lambda e, i=id_libro: ver_pdf(i),
                )

                documentos = ft.DataCell(
                    ft.Row(
                        [btn_cargar, btn_ver],
                        spacing=8,
                        alignment=ft.MainAxisAlignment.CENTER,
                        expand=True,
                    )
                )
            else:
                documentos = ft.DataCell(
                    ft.Row(
                        [ft.Text("No aplica", color=ft.Colors.GREY)],
                        alignment=ft.MainAxisAlignment.CENTER,
                        expand=True,
                    )
                )

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

            # ---- Activo robusto
            activo_value = libro.get("activo")
            is_activo = (
                activo_value == 1
                or activo_value is True
                or str(activo_value).strip().lower() in ("1", "true")
            )

            # ---- Acciones
            acciones = ft.DataCell(
                ft.Row(
                    [
                        action_button(
                            ft.Icons.VISIBILITY,
                            ft.Colors.BLUE,
                            "Detalles",
                            lambda e, i=id_libro: navigate(f"/libro/{i}"),
                        ),
                        action_button(
                            ft.Icons.EDIT,
                            ft.Colors.ORANGE,
                            "Modificar",
                            lambda e, i=id_libro: self.abrir_dialogo_editar_libro(i),
                        ),
                        action_button(
                            ft.Icons.CHECK_CIRCLE if is_activo else ft.Icons.BLOCK,
                            ft.Colors.GREEN if is_activo else ft.Colors.RED,
                            "Desactivar" if is_activo else "Activar",
                            lambda e, i=id_libro, st=is_activo: toggle_activo(i, st),
                        ),
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                )
            )

            autores = (libro.get("autores", "") or "").strip()
            autores_short = (autores[:60] + "…") if len(autores) > 60 else autores

            codigo_barras = (libro.get("codigo_barras", "") or "").strip()
            codigo_barras_short = (codigo_barras[:40] + "…") if len(codigo_barras) > 40 else codigo_barras

            return ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(codigo_barras_short, text_align=ft.TextAlign.CENTER)),

                    ft.DataCell(ft.Text(libro.get("titulo", ""), text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text(libro.get("clasificacion_dui", "") or "", text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text(libro.get("categoria", ""), text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text(autores_short, text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text(libro.get("isbn", ""), text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text(libro.get("tipo", ""), text_align=ft.TextAlign.CENTER)),
                    documentos,
                    acciones,
                ]
            )

        # =========================
        # Filtros combinados
        # =========================
        def libro_match_estado(libro: dict, estado: str) -> bool:
            activo_value = libro.get("activo")
            is_activo = (
                activo_value == 1
                or activo_value is True
                or str(activo_value).strip().lower() in ("1", "true")
            )

            estado = (estado or "TODOS").strip().upper()
            if estado == "ACTIVOS":
                return is_activo
            if estado == "INACTIVOS":
                return not is_activo
            return True

        def libro_match_texto(libro: dict, q: str) -> bool:
            if not q:
                return True

            activo_value = libro.get("activo")
            is_activo = (
                activo_value == 1
                or activo_value is True
                or str(activo_value).strip().lower() in ("1", "true")
            )

            valores = [
                libro.get("codigo_barras", ""),  # ✅ NUEVO (busqueda)
                libro.get("titulo", ""),
                libro.get("clasificacion_dui", ""),
                libro.get("categoria", ""),
                libro.get("autores", ""),
                libro.get("descripcion", ""),
                libro.get("isbn", ""),
                libro.get("tipo", ""),
                "si" if is_activo else "no",
                "activo" if is_activo else "inactivo",
            ]

            haystack = " | ".join([(v or "") for v in valores]).lower()
            return q in haystack

        # ✅ FIX: aceptar valores directos (evita leer value viejo)
        def aplicar_filtros(q=None, estado=None):
            libros_table.rows.clear()

            q = (q if q is not None else (search_input.value or "")).strip().lower()
            estado = (estado if estado is not None else (estado_dd.value or "TODOS")).strip().upper()

            for libro in self._libros_cache:
                if libro_match_estado(libro, estado) and libro_match_texto(libro, q):
                    libros_table.rows.append(build_row(libro))

            self._page.update()

        # ✅ FIX: usar e.control.value
        def on_search_change(e):
            if not self._libros_cache:
                self._libros_cache = self._db.get_libros()
            aplicar_filtros(q=e.control.value, estado=estado_dd.value)

        def on_estado_change(e):
            if not self._libros_cache:
                self._libros_cache = self._db.get_libros()
            aplicar_filtros(q=search_input.value, estado=e.control.value)

        search_input.on_change = on_search_change
        estado_dd.on_change = on_estado_change

        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Row(
                [
                    ft.Text(
                        "Libros Registrados",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color="#38638f",
                    ),
                    button_crear_libro,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

        container = ft.Container(
            content=ft.Column(
                [
                    header,
                    ft.Row(
                        [search_input, estado_dd],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=12,
                    ),
                    ft.Row([libros_table], alignment=ft.MainAxisAlignment.CENTER),
                ],
                spacing=20,
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            expand=True,
        )

        self.controls = [ft.Row([container], expand=True)]

        mostrar_libros()

    # ===========================
    # Métodos auxiliares para autores (Crear)
    # ===========================
    def actualizar_dropdown_autores_crear(self):
        self.autores_dropdown.options = [
            ft.dropdown.Option(key=str(a.get("id_autor")), text=a.get("nombre_completo", "Sin nombre"))
            for a in self.autores_todos
        ]
        if hasattr(self, '_page'):
            self._page.update()
    
    def filtrar_autores_crear(self, e):
        busqueda = (self.buscar_autor_input.value or "").strip().lower()
        if not busqueda:
            self.actualizar_dropdown_autores_crear()
            return
        
        autores_filtrados = [
            a for a in self.autores_todos
            if busqueda in a.get("nombre_completo", "").lower()
        ]
        
        self.autores_dropdown.options = [
            ft.dropdown.Option(key=str(a.get("id_autor")), text=a.get("nombre_completo", "Sin nombre"))
            for a in autores_filtrados
        ]
        self._page.update()
    
    def agregar_autor_crear(self, e):
        if not self.autores_dropdown.value:
            return
        
        autor_id = self.autores_dropdown.value
        # Verificar si ya está agregado
        if any(a["id"] == autor_id for a in self.autores_seleccionados):
            return
        
        # Buscar el nombre del autor
        autor = next((a for a in self.autores_todos if str(a.get("id_autor")) == autor_id), None)
        if not autor:
            return
        
        autor_nombre = autor.get("nombre_completo", "Sin nombre")
        self.autores_seleccionados.append({"id": autor_id, "nombre": autor_nombre})
        
        # Actualizar la vista
        self.actualizar_lista_autores_seleccionados_crear()
    
    def remover_autor_crear(self, autor_id):
        self.autores_seleccionados = [a for a in self.autores_seleccionados if a["id"] != autor_id]
        self.actualizar_lista_autores_seleccionados_crear()
    
    def actualizar_lista_autores_seleccionados_crear(self):
        self.autores_seleccionados_column.controls.clear()
        
        for autor in self.autores_seleccionados:
            self.autores_seleccionados_column.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(autor["nombre"], size=13),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color=ft.Colors.RED,
                            tooltip="Remover",
                            on_click=lambda e, aid=autor["id"]: self.remover_autor_crear(aid),
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=8,
                    bgcolor="#e3f2fd",
                    border_radius=6,
                )
            )
        
        self._page.update()
    
    # Helper methods para editar libro - Sistema de autores
    def actualizar_dropdown_autores_editar(self):
        """Actualiza el dropdown con la lista completa de autores para editar"""
        self.autores_dropdown.options = [
            ft.dropdown.Option(key=str(autor.get("id_autor")), text=autor.get("nombre_completo", "Sin nombre"))
            for autor in self.autores_todos
        ]
    
    def filtrar_autores_editar(self, e):
        """Filtra el dropdown de autores según el texto de búsqueda para editar"""
        busqueda = self.buscar_autor_input.value.lower()
        if busqueda:
            self.autores_dropdown.options = [
                ft.dropdown.Option(key=str(autor.get("id_autor")), text=autor.get("nombre_completo", "Sin nombre"))
                for autor in self.autores_todos
                if busqueda in autor.get("nombre_completo", "").lower()
            ]
        else:
            self.actualizar_dropdown_autores_editar()
        
        self._page.update()
    
    def agregar_autor_editar(self, e):
        """Agrega el autor seleccionado en el dropdown a la lista de seleccionados para editar"""
        if not self.autores_dropdown.value:
            return
        
        autor_id = self.autores_dropdown.value
        
        # Verificar si ya está agregado
        if any(a["id"] == autor_id for a in self.autores_seleccionados):
            self.snack("Este autor ya fue agregado", "warning")
            return
        
        # Buscar el nombre del autor
        autor = next((a for a in self.autores_todos if str(a.get("id_autor")) == autor_id), None)
        if autor:
            self.autores_seleccionados.append({
                "id": autor_id,
                "nombre": autor.get("nombre_completo", "Sin nombre")
            })
            self.actualizar_lista_autores_seleccionados_editar()
            self.buscar_autor_input.value = ""
            self.autores_dropdown.value = None
            self.actualizar_dropdown_autores_editar()
    
    def remover_autor_editar(self, autor_id):
        """Remueve un autor de la lista de seleccionados para editar"""
        self.autores_seleccionados = [a for a in self.autores_seleccionados if a["id"] != autor_id]
        self.actualizar_lista_autores_seleccionados_editar()
    
    def actualizar_lista_autores_seleccionados_editar(self):
        """Actualiza la lista visual de autores seleccionados para editar"""
        self.autores_seleccionados_column.controls.clear()
        
        for autor in self.autores_seleccionados:
            self.autores_seleccionados_column.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(autor["nombre"], size=13),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color=ft.Colors.RED,
                            tooltip="Remover",
                            on_click=lambda e, aid=autor["id"]: self.remover_autor_editar(aid),
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=8,
                    bgcolor="#e3f2fd",
                    border_radius=6,
                )
            )
        
        self._page.update()

    # ===========================
    # Crear Libro con Diálogo
    # ===========================
    def abrir_dialogo_crear_libro(self, e):
        INPUT_STYLE = dict(
            width=320,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        # Campos del formulario
        self.titulo_input = ft.TextField(label="Título *", autofocus=True, **INPUT_STYLE)
        self.isbn_input = ft.TextField(label="ISBN", **INPUT_STYLE)
        self.codigo_barras_input = ft.TextField(label="Código de barras", **INPUT_STYLE)
        self.anio_input = ft.TextField(label="Año de publicación", keyboard_type=ft.KeyboardType.NUMBER, **INPUT_STYLE)
        self.edicion_input = ft.TextField(label="Edición", **INPUT_STYLE)
        
        self.tipo_dd = ft.Dropdown(
            label="Tipo *",
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
            options=[
                ft.dropdown.Option("FISICO"),
                ft.dropdown.Option("DIGITAL"),
            ],
        )

        self.descripcion_input = ft.TextField(
            label="Descripción",
            multiline=True,
            min_lines=5,
            max_lines=8,
            width=680,
            bgcolor="#f5f7fa",
            border_radius=8,
        )

        cats = self._db.get_categorias()
        self.categoria_dd = ft.Dropdown(
            label="Categoría *",
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
            options=[
                ft.dropdown.Option(key=str(c["id_categoria"]), text=c["nombre"])
                for c in cats
            ],
        )

        self.clasificacion_dui_input = ft.TextField(label="Clasificación DUI *", **INPUT_STYLE)
        
        # Sistema de búsqueda y selección de autores
        self.autores_todos = self._db.get_autores()
        self.autores_seleccionados = []  # Lista de {id, nombre}
        
        self.buscar_autor_input = ft.TextField(
            label="Buscar autor",
            width=320,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            text_size=14,
            on_change=self.filtrar_autores_crear,
        )
        
        self.autores_dropdown = ft.Dropdown(
            label="Selecciona un autor",
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
            options=[],
        )
        
        self.btn_agregar_autor = ft.IconButton(
            icon=ft.Icons.ADD,
            bgcolor="#1976d2",
            icon_color=ft.Colors.WHITE,
            tooltip="Agregar autor",
            on_click=self.agregar_autor_crear,
        )
        
        self.autores_seleccionados_column = ft.Column(spacing=4)
        
        self.autores_container = ft.Container(
            content=ft.Column([
                ft.Row([self.buscar_autor_input, self.autores_dropdown, self.btn_agregar_autor], spacing=8),
                ft.Divider(height=8),
                ft.Text("Autores seleccionados:", size=12, weight=ft.FontWeight.BOLD, color="#666"),
                self.autores_seleccionados_column,
            ], spacing=8),
            padding=10,
            border=ft.border.all(1, "#cfd8dc"),
            border_radius=8,
            bgcolor="#fafafa",
        )
        
        # Inicializar dropdown con todos los autores
        self.actualizar_dropdown_autores_crear()

        self.btn_guardar = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.CHECK), ft.Text("Guardar")], spacing=8),
            bgcolor="#0b495c",
            color=ft.Colors.WHITE,
            on_click=self.crear_libro,
        )

        header_row = ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.BOOK, size=22, color="#1B6F7A"),
                    bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN),
                    width=40,
                    height=40,
                    border_radius=8,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column([
                    ft.Text("Crear libro", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Completa los datos del libro", size=12, color="#666")
                ], spacing=2)
            ], spacing=10),
            ft.Container(
                content=ft.Icon(ft.Icons.CLOSE, size=18, color="#666"),
                width=36,
                height=36,
                alignment=ft.Alignment.CENTER,
                on_click=self.cerrar_dialogo_libro,
                border_radius=8
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        form_column = ft.Column([
            # Sección: Información Básica
            ft.Text("Información Básica", size=14, weight=ft.FontWeight.BOLD, color="#0b495c"),
            self.titulo_input,
            ft.Row([self.tipo_dd, self.categoria_dd], spacing=12),
            
            # Sección: Identificadores
            ft.Text("Identificadores", size=14, weight=ft.FontWeight.BOLD, color="#0b495c"),
            self.clasificacion_dui_input,
            ft.Row([self.isbn_input, self.codigo_barras_input], spacing=12),
            
            # Sección: Detalles de Publicación
            ft.Text("Detalles de Publicación", size=14, weight=ft.FontWeight.BOLD, color="#0b495c"),
            ft.Row([self.anio_input, self.edicion_input], spacing=12),
            
            # Sección: Descripción y Autores
            ft.Text("Descripción y Autores", size=14, weight=ft.FontWeight.BOLD, color="#0b495c"),
            ft.Text("Selecciona los autores:", size=12, color="#666"),
            self.autores_container,
            self.descripcion_input,
            
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        content = ft.Column([
            header_row,
            ft.Divider(height=8, color="transparent"),
            form_column,
            ft.Divider(height=6, color="transparent"),
            ft.Row([ft.TextButton("Cancelar", on_click=self.cerrar_dialogo_libro), self.btn_guardar], alignment=ft.MainAxisAlignment.END, spacing=12)
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        self.dialog = ft.AlertDialog(
            modal=True,
            content=ft.Container(width=780, padding=ft.padding.all(18), bgcolor=ft.Colors.WHITE, border_radius=12, content=content)
        )

        self._page.overlay.clear()
        self._page.overlay.append(self.dialog)
        self.dialog.open = True
        self._page.update()

    # ===========================
    # Editar Libro con Diálogo
    # ===========================
    def abrir_dialogo_editar_libro(self, id_libro: int):
        libro = self._db.get_libro_detalle(int(id_libro))
        if not libro:
            self._page.snack_bar = ft.SnackBar(ft.Text("Libro no encontrado"), bgcolor="#b71c1c")
            self._page.snack_bar.open = True
            self._page.update()
            return

        self._edit_libro_id = int(id_libro)

        INPUT_STYLE = dict(
            width=320,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        self.titulo_input = ft.TextField(label="Título *", value=libro.get("titulo", ""), **INPUT_STYLE)
        self.isbn_input = ft.TextField(label="ISBN", value=libro.get("isbn", "") or "", **INPUT_STYLE)
        self.codigo_barras_input = ft.TextField(
            label="Código de barras",
            value=libro.get("codigo_barras", "") or "",
            **INPUT_STYLE,
        )
        self.anio_input = ft.TextField(
            label="Año de publicación",
            value=str(libro.get("anio_publicacion", "")) if libro.get("anio_publicacion") else "",
            keyboard_type=ft.KeyboardType.NUMBER,
            **INPUT_STYLE,
        )
        self.edicion_input = ft.TextField(label="Edición", value=libro.get("edicion", "") or "", **INPUT_STYLE)

        self.tipo_dd = ft.Dropdown(
            label="Tipo *",
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
            value=(libro.get("tipo", "") or "").upper(),
            options=[
                ft.dropdown.Option("FISICO"),
                ft.dropdown.Option("DIGITAL"),
            ],
        )

        self.descripcion_input = ft.TextField(
            label="Descripción",
            value=libro.get("descripcion", "") or "",
            multiline=True,
            min_lines=5,
            max_lines=8,
            width=680,
            bgcolor="#f5f7fa",
            border_radius=8,
        )

        cats = self._db.get_categorias()
        self.categoria_dd = ft.Dropdown(
            label="Categoría *",
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
            value=str(libro.get("id_categoria", "")),
            options=[
                ft.dropdown.Option(key=str(c["id_categoria"]), text=c["nombre"])
                for c in cats
            ],
        )

        self.clasificacion_dui_input = ft.TextField(
            label="Clasificación DUI *",
            value=libro.get("clasificacion_dui", "") or "",
            **INPUT_STYLE,
        )
        
        # Sistema de búsqueda y selección de autores para edición
        self.autores_todos = self._db.get_autores()
        
        # Obtener los IDs de los autores del libro desde la base de datos
        autores_ids_libro = self._db.get_autores_libro(int(id_libro))
        autores_ids_list = [id.strip() for id in autores_ids_libro.split(",") if id.strip()]
        
        # Inicializar autores seleccionados con los del libro
        self.autores_seleccionados = []
        for autor_id in autores_ids_list:
            autor = next((a for a in self.autores_todos if str(a.get("id_autor")) == autor_id), None)
            if autor:
                self.autores_seleccionados.append({
                    "id": str(autor.get("id_autor")),
                    "nombre": autor.get("nombre_completo", "Sin nombre")
                })
        
        self.buscar_autor_input = ft.TextField(
            label="Buscar autor",
            width=320,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            text_size=14,
            on_change=self.filtrar_autores_editar,
        )
        
        self.autores_dropdown = ft.Dropdown(
            label="Selecciona un autor",
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
            options=[],
        )
        
        self.btn_agregar_autor = ft.IconButton(
            icon=ft.Icons.ADD,
            bgcolor="#1976d2",
            icon_color=ft.Colors.WHITE,
            tooltip="Agregar autor",
            on_click=self.agregar_autor_editar,
        )
        
        self.autores_seleccionados_column = ft.Column(spacing=4)
        
        self.autores_container = ft.Container(
            content=ft.Column([
                ft.Row([self.buscar_autor_input, self.autores_dropdown, self.btn_agregar_autor], spacing=8),
                ft.Divider(height=8),
                ft.Text("Autores seleccionados:", size=12, weight=ft.FontWeight.BOLD, color="#666"),
                self.autores_seleccionados_column,
            ], spacing=8),
            padding=10,
            border=ft.border.all(1, "#cfd8dc"),
            border_radius=8,
            bgcolor="#fafafa",
        )
        
        # Inicializar dropdown y lista de seleccionados
        self.actualizar_dropdown_autores_editar()
        self.actualizar_lista_autores_seleccionados_editar()

        self.btn_guardar = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.Icons.CHECK), ft.Text("Guardar")], spacing=8),
            bgcolor="#0b495c",
            color=ft.Colors.WHITE,
            on_click=self.guardar_edicion_libro,
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
                    ft.Text("Editar libro", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Actualiza los datos del libro", size=12, color="#666")
                ], spacing=2)
            ], spacing=10),
            ft.Container(
                content=ft.Icon(ft.Icons.CLOSE, size=18, color="#666"),
                width=36,
                height=36,
                alignment=ft.Alignment.CENTER,
                on_click=self.cerrar_dialogo_libro,
                border_radius=8,
            ),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        form_column = ft.Column([
            ft.Text("Información Básica", size=14, weight=ft.FontWeight.BOLD, color="#0b495c"),
            self.titulo_input,
            ft.Row([self.tipo_dd, self.categoria_dd], spacing=12),

            ft.Text("Identificadores", size=14, weight=ft.FontWeight.BOLD, color="#0b495c"),
            self.clasificacion_dui_input,
            ft.Row([self.isbn_input, self.codigo_barras_input], spacing=12),

            ft.Text("Detalles de Publicación", size=14, weight=ft.FontWeight.BOLD, color="#0b495c"),
            ft.Row([self.anio_input, self.edicion_input], spacing=12),

            ft.Text("Descripción y Autores", size=14, weight=ft.FontWeight.BOLD, color="#0b495c"),
            ft.Text("Selecciona los autores:", size=12, color="#666"),
            self.autores_container,
            self.descripcion_input,
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        content = ft.Column([
            header_row,
            ft.Divider(height=8, color="transparent"),
            form_column,
            ft.Divider(height=6, color="transparent"),
            ft.Row([
                ft.TextButton("Cancelar", on_click=self.cerrar_dialogo_libro),
                self.btn_guardar
            ], alignment=ft.MainAxisAlignment.END, spacing=12)
        ], spacing=10, scroll=ft.ScrollMode.AUTO)

        self.dialog = ft.AlertDialog(
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
        self._page.overlay.append(self.dialog)
        self.dialog.open = True
        self._page.update()

    def guardar_edicion_libro(self, e):
        try:
            titulo = (self.titulo_input.value or "").strip()
            tipo = (self.tipo_dd.value or "").strip()

            if not titulo:
                self._page.snack_bar = ft.SnackBar(ft.Text("El título es obligatorio"), bgcolor="#b71c1c")
                self._page.snack_bar.open = True
                self._page.update()
                return

            if not tipo:
                self._page.snack_bar = ft.SnackBar(ft.Text("El tipo es obligatorio"), bgcolor="#b71c1c")
                self._page.snack_bar.open = True
                self._page.update()
                return

            if not self.categoria_dd.value:
                self._page.snack_bar = ft.SnackBar(ft.Text("Debe seleccionar una categoría"), bgcolor="#b71c1c")
                self._page.snack_bar.open = True
                self._page.update()
                return

            clasificacion_dui = (self.clasificacion_dui_input.value or "").strip()
            if not clasificacion_dui:
                self._page.snack_bar = ft.SnackBar(ft.Text("La Clasificación DUI es obligatoria"), bgcolor="#b71c1c")
                self._page.snack_bar.open = True
                self._page.update()
                return

            anio = (self.anio_input.value or "").strip()
            anio_publicacion = int(anio) if anio else None

            # Obtener IDs de autores seleccionados del nuevo sistema
            autores_csv = ",".join([a["id"] for a in self.autores_seleccionados])
            codigo_barras = (self.codigo_barras_input.value or "").strip()

            self._db.update_libro(
                id_libro=self._edit_libro_id,
                titulo=titulo,
                isbn=(self.isbn_input.value or "").strip(),
                anio_publicacion=anio_publicacion,
                edicion=(self.edicion_input.value or "").strip(),
                tipo=tipo,
                descripcion=(self.descripcion_input.value or "").strip(),
                id_categoria=int(self.categoria_dd.value),
                autores_ids_csv=autores_csv if autores_csv else None,
                clasificacion_dui=clasificacion_dui,
                codigo_barras=codigo_barras if codigo_barras else None,
            )

            self._page.snack_bar = ft.SnackBar(ft.Text("✅ Cambios guardados correctamente"), bgcolor="#1b5e20")
            self._page.snack_bar.open = True
            self.cerrar_dialogo_libro()
            if hasattr(self, "_mostrar_libros"):
                self._mostrar_libros()

        except Exception as ex:
            self._page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)[:150]}"), bgcolor="#b71c1c")
            self._page.snack_bar.open = True
            self._page.update()

    def crear_libro(self, e):
        try:
            print("[CREATE] Iniciando crear_libro...")
            titulo = (self.titulo_input.value or "").strip()
            tipo = (self.tipo_dd.value or "").strip()

            if not titulo:
                self._page.snack_bar = ft.SnackBar(ft.Text("El título es obligatorio"), bgcolor="#b71c1c")
                self._page.snack_bar.open = True
                self._page.update()
                return

            if not tipo:
                self._page.snack_bar = ft.SnackBar(ft.Text("El tipo es obligatorio"), bgcolor="#b71c1c")
                self._page.snack_bar.open = True
                self._page.update()
                return

            if not self.categoria_dd.value:
                self._page.snack_bar = ft.SnackBar(ft.Text("Debe seleccionar una categoría"), bgcolor="#b71c1c")
                self._page.snack_bar.open = True
                self._page.update()
                return

            clasificacion_dui = (self.clasificacion_dui_input.value or "").strip()
            if not clasificacion_dui:
                self._page.snack_bar = ft.SnackBar(ft.Text("La Clasificación DUI es obligatoria"), bgcolor="#b71c1c")
                self._page.snack_bar.open = True
                self._page.update()
                return

            anio = (self.anio_input.value or "").strip()
            anio_publicacion = int(anio) if anio else None

            # Obtener IDs de autores seleccionados
            autores_csv = ",".join([a["id"] for a in self.autores_seleccionados])

            codigo_barras = (self.codigo_barras_input.value or "").strip()

            print(f"[CREATE] Parámetros:")
            print(f"  - titulo: {titulo}")
            print(f"  - tipo: {tipo}")
            print(f"  - id_categoria: {self.categoria_dd.value}")
            print(f"  - clasificacion_dui: {clasificacion_dui}")
            print(f"  - anio_publicacion: {anio_publicacion}")

            print("[CREATE] Llamando a _db.crear_libro()...")
            resultado = self._db.crear_libro(
                titulo=titulo,
                isbn=(self.isbn_input.value or "").strip(),
                anio_publicacion=anio_publicacion,
                edicion=(self.edicion_input.value or "").strip(),
                tipo=tipo,
                descripcion=(self.descripcion_input.value or "").strip(),
                id_categoria=int(self.categoria_dd.value),
                activo=1,
                autores_ids_csv=autores_csv if autores_csv else None,
                clasificacion_dui=clasificacion_dui,
                codigo_barras=codigo_barras if codigo_barras else None,
            )
            print(f"[CREATE] Resultado: {resultado}")

            self._page.snack_bar = ft.SnackBar(ft.Text("✅ Libro guardado correctamente"), bgcolor="#1b5e20")
            self._page.snack_bar.open = True
            self.cerrar_dialogo_libro()

            if hasattr(self, "_mostrar_libros"):
                self._mostrar_libros()
            
        except Exception as ex:
            print(f"[CREATE] ERROR: {ex}")
            import traceback
            traceback.print_exc()
            self._page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)[:150]}"), bgcolor="#b71c1c")
            self._page.snack_bar.open = True
            self._page.update()

    def cerrar_dialogo_libro(self, e=None):
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.open = False
            self._page.update()
