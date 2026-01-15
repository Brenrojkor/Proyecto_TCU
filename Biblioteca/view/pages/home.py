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
        # Ver PDF (consulta SOLO al hacer click) + DEBUG EN TERMINAL
        # =========================
        def ver_pdf(id_libro: int):
            try:
                print(f"\n[DEBUG] ===== VER PDF =====")
                print(f"[DEBUG] id_libro: {id_libro}")

                data = self._db.get_libro_pdf(int(id_libro))
                print(f"[DEBUG] get_libro_pdf() -> {type(data)} | {data}")

                if not data:
                    print("[DEBUG] No hay data (None / vacío).")
                    snack("Este libro no tiene PDF aún.")
                    return

                nombre = (data.get("nombre_archivo") or f"libro_{id_libro}.pdf")
                contenido = data.get("contenido")

                print(f"[DEBUG] nombre_archivo: {nombre}")
                print(f"[DEBUG] contenido type: {type(contenido)}")

                if contenido is None:
                    print("[DEBUG] contenido es None")
                    snack("El PDF existe pero vino vacío desde la BD.")
                    return

                # ✅ pyodbc puede devolver memoryview
                pdf_bytes = bytes(contenido)
                print(f"[DEBUG] pdf_bytes len: {len(pdf_bytes)}")

                out_path = os.path.join(
                    tempfile.gettempdir(),
                    f"libro_{id_libro}_{safe_filename(nombre)}"
                )
                print(f"[DEBUG] out_path: {out_path}")

                with open(out_path, "wb") as f:
                    f.write(pdf_bytes)

                exists = os.path.exists(out_path)
                size = os.path.getsize(out_path) if exists else -1
                print(f"[DEBUG] file exists: {exists} | size: {size}")

                if (not exists) or size == 0:
                    snack("No se pudo crear el archivo temporal del PDF (0 bytes).")
                    return

                print("[DEBUG] Abriendo PDF con app por defecto…")
                open_file_default_app(out_path)

            except Exception as ex:
                print("[ERROR] ver_pdf:", ex)
                snack(f"Error abriendo PDF: {ex}")

        # =========================
        # Picker (PowerShell robusto + fallback Tkinter)
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
            hint_text="Buscar por título...",
            prefix_icon=ft.Icons.SEARCH,
            width=320,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )


        libros_table = ft.DataTable(
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, "#d0d7de"),
            border_radius=8,
            heading_row_color="#e3f2fd",
            heading_row_height=48,
            data_row_min_height=52,
            data_row_max_height=52,
            column_spacing=50,
            horizontal_margin=16,
            columns=[
                ft.DataColumn(label=ft.Text("Título", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
                ft.DataColumn(label=ft.Text("Categoría", text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD, color="#0d47a1")),
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
                            ft.Icons.BLOCK,
                            ft.Colors.RED,
                            "Desactivar",
                        ),
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                )
            )

            return ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(libro.get("titulo", ""), text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text(libro.get("categoria", ""), text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text(libro.get("isbn", ""), text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text(libro.get("tipo", ""), text_align=ft.TextAlign.CENTER)),
                    ft.DataCell(ft.Text("Sí" if libro.get("activo") else "No", text_align=ft.TextAlign.CENTER)),
                    documentos,
                    acciones,
                ]
            )

        # =========================
        # Filtro
        # =========================

        def filtrar_libros(texto):
            libros_table.rows.clear()
            q = (texto or "").strip().lower()

            for libro in self._libros_cache:
                if not q or q in (libro.get("titulo") or "").lower():
                    libros_table.rows.append(build_row(libro))

            self._page.update()

        def on_search_change(e):
            if not self._libros_cache:
                self._libros_cache = self._db.get_libros()
            filtrar_libros(e.control.value)

        search_input.on_change = on_search_change

        # =========================
        # Mostrar libros
        # =========================

        def mostrar_libros(e=None):
            libros_table.rows.clear()
            self._libros_cache = self._db.get_libros()

            for libro in self._libros_cache:
                libros_table.rows.append(build_row(libro))

            self._page.update()


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
                    ft.Row([search_input], alignment=ft.MainAxisAlignment.END),
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
