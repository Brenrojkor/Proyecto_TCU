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
$dlg.Filter = "Archivos PDF (*.pdf)|*.pdf"
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
            content=ft.Row([ft.Icon(ft.Icons.ADD), ft.Text("Crear libro")], spacing=8),
            on_click=lambda e: navigate("/createlib")
        )

        button_show_libros = ft.ElevatedButton("Mostrar Libros")

        search_input = ft.TextField(
            hint_text="Buscar",
            prefix_icon=ft.Icons.SEARCH,
            width=300,
            dense=True
        )

        libros_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Título")),
                ft.DataColumn(ft.Text("ISBN")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Autores")),
                ft.DataColumn(ft.Text("Ubicación")),
                ft.DataColumn(ft.Text("Documentos")),
            ],
            rows=[]
        )

        self._libros_cache = []

        # =========================
        # Subir PDF + DEBUG EN TERMINAL
        # =========================
        def subir_pdf_para_libro(id_libro: int):
            print(f"\n[DEBUG] ===== SUBIR PDF =====")
            print(f"[DEBUG] id_libro: {id_libro}")

            path = pick_pdf_windows()
            print(f"[DEBUG] path seleccionado: {path}")

            if not path:
                print("[DEBUG] Cancelado por el usuario.")
                return

            if not path.lower().endswith(".pdf"):
                snack("Solo se permiten archivos PDF.")
                return

            try:
                with open(path, "rb") as f:
                    pdf_bytes = f.read()

                print(f"[DEBUG] bytes leídos: {len(pdf_bytes)}")

                if not pdf_bytes:
                    snack("El archivo seleccionado está vacío (0 bytes).")
                    return

                snack(f"Seleccionado: {os.path.basename(path)} ({len(pdf_bytes)} bytes)")

                self._db.upsert_libro_pdf(
                    id_libro=id_libro,
                    nombre_archivo=safe_filename(os.path.basename(path)),
                    contenido=pdf_bytes
                )

                print("[DEBUG] upsert_libro_pdf ejecutado OK")
                snack("PDF guardado en la base de datos ✅")

            except Exception as ex:
                print("[ERROR] subir_pdf_para_libro:", ex)
                snack(f"Error subiendo PDF: {ex}")

        # =========================
        # Construir filas (SIN has_libro_pdf)
        # =========================
        def build_row(libro: dict) -> ft.DataRow:
            id_libro = int(libro["id_libro"])
            tipo = (libro.get("tipo") or "").strip().upper()

            if tipo == "DIGITAL":
                btn_cargar = ft.ElevatedButton(
                    "Cargar PDF",
                    icon=ft.Icons.UPLOAD_FILE,
                    on_click=lambda e, i=id_libro: subir_pdf_para_libro(i)
                )

                btn_ver = ft.ElevatedButton(
                    "Ver PDF",
                    icon=ft.Icons.PICTURE_AS_PDF,
                    disabled=False,
                    on_click=lambda e, i=id_libro: ver_pdf(i)
                )

                documentos = ft.DataCell(
                    ft.Container(
                        width=260,
                        content=ft.Row([btn_cargar, btn_ver], spacing=8, wrap=False)
                    )
                )
            else:
                documentos = ft.DataCell(ft.Container(width=260, content=ft.Text("No aplica")))

            return ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(libro.get("id_libro", "")))),
                ft.DataCell(ft.Text(libro.get("titulo", ""))),
                ft.DataCell(ft.Text(libro.get("isbn", ""))),
                ft.DataCell(ft.Text(libro.get("tipo", ""))),
                ft.DataCell(ft.Text(libro.get("descripcion", ""))),
                ft.DataCell(ft.Text(libro.get("categoria", ""))),
                ft.DataCell(ft.Text(libro.get("autores", ""))),
                ft.DataCell(ft.Text(libro.get("ubicacion", ""))),
                documentos,
            ])

        # =========================
        # Filtro (usa cache)
        # =========================
        def filtrar_libros(texto):
            libros_table.rows.clear()
            q = (texto or "").strip().lower()

            if not q:
                for libro in self._libros_cache:
                    libros_table.rows.append(build_row(libro))
                self._page.update()
                return

            for libro in self._libros_cache:
                if q in (libro.get("titulo") or "").lower():
                    libros_table.rows.append(build_row(libro))

            self._page.update()

        def on_search_change(e):
            if not self._libros_cache:
                self._libros_cache = self._db.get_libros()
            filtrar_libros(e.control.value)

        search_input.on_change = on_search_change

        # =========================
        # Mostrar libros (1 consulta)
        # =========================
        def mostrar_libros(e):
            libros_table.rows.clear()
            self._libros_cache = self._db.get_libros()

            for libro in self._libros_cache:
                libros_table.rows.append(build_row(libro))

            if search_input.value:
                filtrar_libros(search_input.value)

            self._page.update()

        button_show_libros.on_click = mostrar_libros

        # =========================
        # Layout + Scroll
        # =========================
        scrollable_column = ft.Column([libros_table], scroll=ft.ScrollMode.AUTO)
        scrollable_row = ft.Row([scrollable_column], scroll=ft.ScrollMode.ALWAYS, expand=True)

        container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [button_crear_libro, button_show_libros, search_input],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=20
                    ),
                    scrollable_row
                ],
                spacing=20
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=8
        )

        self.controls = [
            ft.Row([container], alignment=ft.MainAxisAlignment.CENTER, expand=True)
        ]
