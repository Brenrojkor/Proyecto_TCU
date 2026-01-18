import flet as ft
from model.database import Database
import os
import sys
import tempfile
import re
import subprocess


class EditarLibroPage(ft.Column):
    def __init__(self, navigate, page: ft.Page, id_libro: int):
        super().__init__()
        self._page = page
        self.navigate = navigate
        self.db = Database()
        self.id_libro = id_libro

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
        # Estilos
        # =========================
        INPUT_STYLE = dict(
            width=320,
            height=44,
            bgcolor="#f5f7fa",
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color="#1976d2",
            text_size=14,
        )

        # =========================
        # Cargar datos del libro
        # =========================
        libro = None
        try:
            libro = self.db.get_libro_detalle(id_libro)
        except Exception as ex:
            snack(f"Error cargando libro: {ex}")

        if not libro:
            self.controls = [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("Libro no encontrado", size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton(
                                "Volver",
                                on_click=lambda e: navigate("/"),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=20,
                    expand=True,
                )
            ]
            return

        # =========================
        # Inputs
        # =========================
        self.titulo_input = ft.TextField(
            label="Título *",
            value=libro.get("titulo", ""),
            **INPUT_STYLE
        )

        self.isbn_input = ft.TextField(
            label="ISBN",
            value=libro.get("isbn", "") or "",
            **INPUT_STYLE
        )

        self.anio_input = ft.TextField(
            label="Año de publicación",
            hint_text="YYYY (ej: 2024)",
            value=str(libro.get("anio_publicacion", "")) if libro.get("anio_publicacion") else "",
            keyboard_type=ft.KeyboardType.NUMBER,
            **INPUT_STYLE
        )

        self.edicion_input = ft.TextField(
            label="Edición",
            value=libro.get("edicion", "") or "",
            **INPUT_STYLE
        )

        self.tipo_dd = ft.Dropdown(
            label="Tipo *",
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
            value=libro.get("tipo", "").upper(),
            options=[
                ft.dropdown.Option("FISICO"),
                ft.dropdown.Option("DIGITAL"),
            ],
        )

        self.descripcion_input = ft.TextField(
            label="Descripción",
            value=libro.get("descripcion", "") or "",
            multiline=True,
            min_lines=2,
            max_lines=3,
            width=320,
            bgcolor="#f5f7fa",
            border_radius=8,
        )

        # =========================
        # Categorías
        # =========================
        cats = self.db.get_categorias()
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

        # =========================
        # Ubicaciones
        # =========================
        ubis = self.db.get_ubicaciones()

        def ubicacion_text(u: dict) -> str:
            sala = u.get("sala", "")
            pasillo = u.get("pasillo") or "N/A"
            est = u.get("estanteria") or "N/A"
            nivel = u.get("nivel") or "N/A"
            desc = (u.get("descripcion") or "").strip()

            base = f"Sala {sala} | Pasillo {pasillo} | Estantería {est} | Nivel {nivel}"
            return f"{base} - {desc}" if desc else base

        self.ubicacion_dd = ft.Dropdown(
            label="Ubicación *",
            width=260,
            bgcolor="#f5f7fa",
            border_radius=8,
            value=str(libro.get("id_ubicacion", "")),
            options=[
                ft.dropdown.Option(
                    key=str(u["id_ubicacion"]),
                    text=ubicacion_text(u)
                )
                for u in ubis
            ],
        )

        self.autores_ids_input = ft.TextField(
            label="Autores (IDs separados por coma)",
            value=libro.get("autores_ids", "") or "",
            **INPUT_STYLE
        )

        # =========================
        # PDF Management
        # =========================
        tiene_pdf = self.db.has_libro_pdf(id_libro)
        self.pdf_status = ft.Text(
            f"📄 PDF: {'Sí adjuntado' if tiene_pdf else 'No adjuntado'}",
            size=12,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREEN if tiene_pdf else ft.Colors.ORANGE,
        )

        def subir_nuevo_pdf(e):
            path = pick_pdf_windows()
            if not path:
                return

            if not path.lower().endswith(".pdf"):
                snack("Solo se permiten archivos PDF.")
                return

            with open(path, "rb") as f:
                pdf_bytes = f.read()

            self.db.upsert_libro_pdf(
                id_libro=id_libro,
                nombre_archivo=safe_filename(os.path.basename(path)),
                contenido=pdf_bytes,
            )

            snack("PDF actualizado correctamente ✅")
            self.pdf_status.value = "📄 PDF: Sí adjuntado"
            self.pdf_status.color = ft.Colors.GREEN
            self._page.update()

        self.btn_pdf = ft.ElevatedButton(
            "Cambiar/Subir PDF",
            on_click=subir_nuevo_pdf,
            icon=ft.Icons.UPLOAD_FILE,
        ) if self.tipo_dd.value == "DIGITAL" else ft.Container()

        # =========================
        # Botones
        # =========================
        self.btn_cancelar = ft.TextButton(
            "Cancelar",
            on_click=lambda e: navigate("/"),
        )

        self.btn_guardar = ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(ft.Icons.SAVE), ft.Text("Guardar cambios")],
                spacing=6,
            ),
            bgcolor="#1976d2",
            color=ft.Colors.WHITE,
            on_click=self.guardar_cambios,
        )

        # =========================
        # Header
        # =========================
        header = ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="#aedff4",
            border_radius=8,
            content=ft.Text(
                f"Editar libro: {libro.get('titulo', 'Sin título')}",
                size=22,
                weight=ft.FontWeight.BOLD,
                color="#38638f",
            ),
        )

        # =========================
        # Formulario
        # =========================
        form_controls = [
            self.titulo_input,
            self.isbn_input,
            self.anio_input,
            self.edicion_input,
            self.tipo_dd,
            self.descripcion_input,
            self.categoria_dd,
            self.ubicacion_dd,
            self.autores_ids_input,
        ]

        if self.tipo_dd.value == "DIGITAL":
            form_controls.extend([
                ft.Divider(),
                self.pdf_status,
                self.btn_pdf,
            ])

        form_controls.extend([
            ft.Divider(),
            ft.Row(
                [self.btn_cancelar, self.btn_guardar],
                alignment=ft.MainAxisAlignment.END,
            ),
        ])

        form = ft.Column(
            controls=form_controls,
            spacing=14,
        )

        container = ft.Container(
            content=ft.Column(
                [header, form],
                spacing=20,
            ),
            padding=24,
            bgcolor=ft.Colors.WHITE,
            border_radius=8,
            width=700,
        )

        self.controls = [
            ft.Row([container], alignment=ft.MainAxisAlignment.CENTER, expand=True)
        ]

    # =========================
    # Lógica
    # =========================
    def guardar_cambios(self, e):
        try:
            titulo = (self.titulo_input.value or "").strip()
            tipo = (self.tipo_dd.value or "").strip()

            if not titulo:
                self.mostrar_error("El título es obligatorio.")
                return

            if not tipo:
                self.mostrar_error("El tipo es obligatorio.")
                return

            if not self.categoria_dd.value:
                self.mostrar_error("Debe seleccionar una categoría.")
                return

            if not self.ubicacion_dd.value:
                self.mostrar_error("Debe seleccionar una ubicación.")
                return

            anio = (self.anio_input.value or "").strip()
            anio_publicacion = int(anio) if anio else None

            autores_csv = (self.autores_ids_input.value or "").strip()

            self.db.update_libro(
                id_libro=self.id_libro,
                titulo=titulo,
                isbn=(self.isbn_input.value or "").strip(),
                anio_publicacion=anio_publicacion,
                edicion=(self.edicion_input.value or "").strip(),
                tipo=tipo,
                descripcion=(self.descripcion_input.value or "").strip(),
                id_categoria=int(self.categoria_dd.value),
                autores_ids_csv=autores_csv if autores_csv else None,
                id_ubicacion=int(self.ubicacion_dd.value),
            )

            self._page.snack_bar = ft.SnackBar(
                content=ft.Text("✅ Cambios guardados correctamente"),
                bgcolor=ft.Colors.GREEN_500,
            )
            self._page.snack_bar.open = True
            self._page.update()

            self.navigate("/")

        except Exception as ex:
            self.mostrar_error(str(ex))

    def mostrar_error(self, mensaje: str):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error"),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: self.cerrar_dialogo(dialog))
            ],
        )
        self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def cerrar_dialogo(self, dialog: ft.AlertDialog):
        dialog.open = False
        self._page.update()
