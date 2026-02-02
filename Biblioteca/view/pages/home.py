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
            on_click=lambda e: navigate("/createlib"),
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
                # ✅ NUEVO: Código de barras ANTES de Título
                ft.DataColumn(label=ft.Text("Código de barras", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),

                ft.DataColumn(label=ft.Text("Título", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Clasificación DUI", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Categoría", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Autores", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Descripción", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("ISBN", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Tipo", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Activo", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
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
                            lambda e, i=id_libro: navigate(f"/editlib/{i}"),
                        ),
                        action_button(
                            ft.Icons.BLOCK if is_activo else ft.Icons.CHECK_CIRCLE,
                            ft.Colors.RED if is_activo else ft.Colors.GREEN,
                            "Desactivar" if is_activo else "Activar",
                            lambda e, i=id_libro, st=is_activo: toggle_activo(i, st),
                        ),
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                )
            )

            descripcion = (libro.get("descripcion", "") or "").strip()
            descripcion_short = (descripcion[:80] + "…") if len(descripcion) > 80 else descripcion

            autores = (libro.get("autores", "") or "").strip()
            autores_short = (autores[:60] + "…") if len(autores) > 60 else autores

            codigo_barras = (libro.get("codigo_barras", "") or "").strip()
            codigo_barras_short = (codigo_barras[:40] + "…") if len(codigo_barras) > 40 else codigo_barras

            return ft.DataRow(
                cells=[
                    # ✅ NUEVO: celda Código de barras primero
                    ft.DataCell(ft.Text(codigo_barras_short, text_align=ft.TextAlign.CENTER)),

                    ft.DataCell(ft.Text(libro.get("titulo", ""), text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text(libro.get("clasificacion_dui", "") or "", text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text(libro.get("categoria", ""), text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text(autores_short, text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text(descripcion_short, text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text(libro.get("isbn", ""), text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text(libro.get("tipo", ""), text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text("Sí" if is_activo else "No", text_align=ft.TextAlign.CENTER)),
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
