import flet as ft
from model.database import Database


class SolicitudPage(ft.Column):
	def __init__(self, navigate, page: ft.Page):
		super().__init__()
		self._page = page
		self.navigate = navigate
		self.db = Database()
		self.dialog = None
		self.solicitud_editando = None
		self._solicitudes_cache = []

		self.btn_crear = ft.ElevatedButton(
			content=ft.Row(
				[ft.Icon(ft.Icons.ADD), ft.Text("Crear solicitud")],
				spacing=8,
			),
			on_click=self.abrir_dialogo_crear,
		)

		self.search_input = ft.TextField(
			hint_text="Buscar solicitud...",
			prefix_icon=ft.Icons.SEARCH,
			width=320,
			height=44,
			bgcolor="#f5f7fa",
			border_radius=8,
			border_color="#cfd8dc",
			focused_border_color="#1976d2",
			text_size=14,
			on_change=self.on_search_change,
		)

		self.solicitudes_table = ft.DataTable(
			bgcolor=ft.Colors.WHITE,
			border=ft.border.all(1, "#d0d7de"),
			border_radius=8,
			width=990,
			heading_row_color="#e3f2fd",
			heading_row_height=48,
			data_row_min_height=52,
			data_row_max_height=52,
			column_spacing=80,
			horizontal_margin=24,
			columns=[
				ft.DataColumn(
					ft.Text("Descripción", weight=ft.FontWeight.BOLD, color="#0d47a1")
				),
				ft.DataColumn(
					ft.Text("Autor", weight=ft.FontWeight.BOLD, color="#0d47a1")
				),
				ft.DataColumn(
					ft.Text("Fecha registro", weight=ft.FontWeight.BOLD, color="#0d47a1")
				),
				ft.DataColumn(
					ft.Text("Activo", weight=ft.FontWeight.BOLD, color="#0d47a1")
				),
				ft.DataColumn(
					ft.Text("Acciones", weight=ft.FontWeight.BOLD, color="#0d47a1")
				),
			],
			rows=[],
		)

		header = ft.Container(
			padding=ft.padding.symmetric(horizontal=20, vertical=12),
			bgcolor="#aedff4",
			border_radius=8,
			content=ft.Row(
				[
					ft.Text(
						"Solicitudes Registradas",
						size=22,
						weight=ft.FontWeight.BOLD,
						color="#38638f",
					),
					self.btn_crear,
				],
				alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
			),
		)

		container = ft.Container(
			content=ft.Column(
				[
					header,
					ft.Row([self.search_input], alignment=ft.MainAxisAlignment.END),
					ft.Row([self.solicitudes_table], alignment=ft.MainAxisAlignment.CENTER),
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
				alignment=ft.MainAxisAlignment.CENTER,
				expand=True,
			)
		]

		self.mostrar_solicitudes()

	def action_button(self, icon, bgcolor, tooltip, on_click=None):
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

	def _is_activo(self, activo_value):
		return bool(activo_value) and str(activo_value).strip().lower() not in ("0", "false")

	def _format_fecha(self, fecha_value):
		if not fecha_value:
			return "N/A"
		fecha_str = str(fecha_value)
		if "T" in fecha_str:
			return fecha_str.split("T")[0]
		if " " in fecha_str:
			return fecha_str.split(" ")[0]
		return fecha_str

	def on_search_change(self, e):
		texto = (e.control.value or "").lower().strip()
		self.solicitudes_table.rows.clear()

		for sol in self._solicitudes_cache:
			descripcion = (sol.get("descripcion", "") or "").lower()
			autor = (sol.get("autor", "") or "").lower()
			fecha = (str(sol.get("fecha_registro", "")) or "").lower()
			if not texto or texto in descripcion or texto in autor or texto in fecha:
				self.solicitudes_table.rows.append(self._build_row(sol))

		self._page.update()

	def abrir_dialogo_crear(self, e):
		self.solicitud_editando = None
		self._abrir_dialogo("Crear solicitud")

	def abrir_dialogo_editar(self, solicitud):
		self.solicitud_editando = solicitud
		self._abrir_dialogo("Editar solicitud", solicitud)

	def _abrir_dialogo(self, titulo, solicitud=None):
		descripcion_value = solicitud.get("descripcion", "") if solicitud else ""
		autor_value = solicitud.get("autor", "") if solicitud else ""
		fecha_registro_value = solicitud.get("fecha_registro", "") if solicitud else ""
		is_activo = self._is_activo(solicitud.get("activo")) if solicitud else True

		self.autor_input = ft.TextField(
			label="Autor",
			value=autor_value,
			width=300,
		)
		self.descripcion_input = ft.TextField(
			label="Descripción",
			value=descripcion_value,
			multiline=True,
			min_lines=2,
			max_lines=3,
			width=300,
			autofocus=True,
		)

		self.activo_switch = ft.Switch(label="Activo", value=is_activo)
		controles = [
			ft.Row(
				[
					self.autor_input,
					ft.Container(
						content=self.activo_switch,
						width=120,
						alignment=ft.Alignment.CENTER_LEFT,
					),
				],
				spacing=12,
				alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
			),
			self.descripcion_input,
		]

		contenido_principal = ft.Column(
			controles,
			spacing=10,
			horizontal_alignment=ft.CrossAxisAlignment.START,
		)
		acciones = ft.Row(
			[
				ft.TextButton("Cancelar", on_click=self.cerrar_dialogo),
				ft.ElevatedButton(
					content=ft.Row([ft.Icon(ft.Icons.CHECK), ft.Text("Guardar")], spacing=8),
					bgcolor="#0b495c",
					color=ft.Colors.WHITE,
					on_click=self.guardar_solicitud,
				),
			],
			alignment=ft.MainAxisAlignment.END,
			spacing=10,
		)

		content = ft.Container(
			width=520,
			height=300,
			padding=ft.padding.all(14),
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
										content=ft.Icon(ft.Icons.DESCRIPTION, size=22, color="#1B6F7A"),
										bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.GREEN),
										width=40,
										height=40,
										border_radius=8,
										alignment=ft.Alignment.CENTER,
									),
									ft.Column(
										[
											ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD),
											ft.Text("Información de la solicitud", size=12, color="#666"),
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
								on_click=self.cerrar_dialogo,
								border_radius=8,
							),
						],
						alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
					),
					ft.Divider(height=6, color="transparent"),
					contenido_principal,
					ft.Divider(height=6, color="transparent"),
					acciones,
				],
				spacing=8,
			),
		)

		self.dialog = ft.AlertDialog(modal=True, content=content)
		self._page.overlay.clear()
		self._page.overlay.append(self.dialog)
		self.dialog.open = True
		self._page.update()

	def cerrar_dialogo(self, e=None):
		if self.dialog:
			self.dialog.open = False
			self._page.update()

	def guardar_solicitud(self, e):
		descripcion = (self.descripcion_input.value or "").strip()
		autor = (self.autor_input.value or "").strip()

		if not descripcion:
			self.descripcion_input.error_text = "La descripción es obligatoria"
			self._page.update()
			return
		self.descripcion_input.error_text = None

		if self.solicitud_editando:
			activo = 1 if getattr(self, "activo_switch", None) and self.activo_switch.value else 0
			self.db.update_solicitud(
				self.solicitud_editando["id_solicitud"],
				descripcion,
				autor,
				activo,
			)
		else:
			activo = 1 if getattr(self, "activo_switch", None) and self.activo_switch.value else 0
			self.db.set_solicitud(descripcion, autor, activo)

		self._page.snack_bar = ft.SnackBar(ft.Text("✅ Solicitud guardada"), bgcolor=ft.Colors.GREEN_500)
		self._page.snack_bar.open = True

		self.cerrar_dialogo()
		self.mostrar_solicitudes()

	def _build_row(self, sol):
		is_activo = self._is_activo(sol.get("activo"))
		return ft.DataRow(
			cells=[
				ft.DataCell(ft.Text(sol.get("descripcion", ""), text_align=ft.TextAlign.CENTER)),
				ft.DataCell(ft.Text(sol.get("autor", ""), text_align=ft.TextAlign.CENTER)),
				ft.DataCell(ft.Text(self._format_fecha(sol.get("fecha_registro")), text_align=ft.TextAlign.CENTER)),
				ft.DataCell(
					ft.Text(
						"Activo" if is_activo else "Inactivo",
						color=ft.Colors.GREEN if is_activo else ft.Colors.RED,
						text_align=ft.TextAlign.CENTER,
					)
				),
				ft.DataCell(
					ft.Row(
						[
							self.action_button(
								ft.Icons.EDIT,
								ft.Colors.ORANGE,
								"Editar",
								lambda e, s=sol: self.abrir_dialogo_editar(s),
							),
							self.action_button(
								ft.Icons.DELETE,
								ft.Colors.RED,
								"Eliminar",
								lambda e, s=sol: self.confirmar_eliminar(s),
							),
						],
						spacing=10,
						alignment=ft.MainAxisAlignment.CENTER,
					)
				),
			]
		)

	def confirmar_eliminar(self, solicitud):
		def eliminar(e):
			try:
				id_solicitud = (
					solicitud.get("id_solicitud")
					or solicitud.get("id")
					or solicitud.get("idSolicitud")
				)
				if not id_solicitud:
					self._page.snack_bar = ft.SnackBar(
						ft.Text("No se pudo identificar la solicitud"),
						bgcolor=ft.Colors.RED_500,
					)
					self._page.snack_bar.open = True
					self._page.update()
					return

				self.db.eliminar_solicitud(int(id_solicitud))
				self._page.snack_bar = ft.SnackBar(ft.Text("🗑️ Solicitud eliminada"), bgcolor=ft.Colors.GREEN_500)
				self._page.snack_bar.open = True
				dlg.open = False
				self._page.update()
				self.mostrar_solicitudes()
			except Exception as ex:
				self._page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.Colors.RED_500)
				self._page.snack_bar.open = True
				self._page.update()

		dlg = ft.AlertDialog(
			modal=True,
			title=ft.Text("Eliminar solicitud"),
			content=ft.Text("¿Seguro que querés eliminar esta solicitud?"),
			actions=[
				ft.TextButton("Cancelar", on_click=lambda e: self._cerrar_dialogo_confirmacion(dlg)),
				ft.ElevatedButton("Eliminar", bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, on_click=eliminar),
			],
		)
		self._page.overlay.append(dlg)
		dlg.open = True
		self._page.update()

	def _cerrar_dialogo_confirmacion(self, dlg):
		dlg.open = False
		self._page.update()

	def mostrar_solicitudes(self):
		self.solicitudes_table.rows.clear()
		self._solicitudes_cache = self.db.get_solicitudes()

		for sol in self._solicitudes_cache:
			self.solicitudes_table.rows.append(self._build_row(sol))

		self._page.update()
