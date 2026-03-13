import flet as ft
from model.database import Database
import math


class SolicitudPage(ft.Column):
	def __init__(self, navigate, page: ft.Page, query_params: dict = None):
		super().__init__()
		self.expand = True
		self.scroll = ft.ScrollMode.AUTO
		self._page = page
		self.navigate = navigate
		self.db = Database()
		self.dialog = None
		self.solicitud_editando = None
		self._solicitudes_cache = []
		self._solicitudes_filtradas = []
		self._page_size = 5
		
		# Restaurar página desde query params si existen
		initial_page = 1
		if query_params and isinstance(query_params, dict) and "page" in query_params:
			try:
				initial_page = max(1, int(query_params["page"]))
			except (ValueError, TypeError):
				initial_page = 1
		
		self._pagina_actual = initial_page

		# Botones principales (estilo igual a reservas)
		self.btn_crear = ft.ElevatedButton(
			content=ft.Row([
				ft.Icon(ft.Icons.ADD_ROUNDED, size=20),
				ft.Text("Crear solicitud", size=14, weight=ft.FontWeight.W_500)
			], spacing=8),
			on_click=self.abrir_dialogo_crear,
			bgcolor="#1976d2",
			color=ft.Colors.WHITE,
			height=48,
			style=ft.ButtonStyle(
				shape=ft.RoundedRectangleBorder(radius=10),
				elevation=2,
			),
		)

		self.btn_refrescar = ft.IconButton(
			icon=ft.Icons.REFRESH_ROUNDED,
			icon_color=ft.Colors.WHITE,
			bgcolor="#1976d2",
			tooltip="Refrescar datos",
			on_click=lambda e: self.mostrar_solicitudes(),
			icon_size=24,
			height=48,
			width=48,
			style=ft.ButtonStyle(
				shape=ft.RoundedRectangleBorder(radius=10),
			),
		)

		# Controles de búsqueda y filtros (estilo reservas)
		self.search_input = ft.TextField(
			hint_text="Buscar por descripción, autor o fecha...",
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

		self.solicitudes_table = ft.DataTable(
			bgcolor=ft.Colors.WHITE,
			border=ft.border.all(1, "#e0e0e0"),
			border_radius=12,
			width=1200,
			heading_row_color="#f5f7fa",
			heading_row_height=56,
			data_row_min_height=60,
			data_row_max_height=65,
			column_spacing=30,
			horizontal_margin=20,
			divider_thickness=0.5,
			columns=[
				ft.DataColumn(label=ft.Container(content=ft.Text("Descripción", weight=ft.FontWeight.BOLD, color="#1565c0", size=13), padding=ft.padding.only(left=5))),
				ft.DataColumn(label=ft.Text("Autor", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
				ft.DataColumn(label=ft.Text("Fecha registro", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
				ft.DataColumn(label=ft.Text("Activo", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
				ft.DataColumn(label=ft.Text("Acciones", weight=ft.FontWeight.BOLD, color="#1565c0", size=13)),
			],
			rows=[],
		)

		# Widgets de métricas (estilo igual a reservas)
		self.total_solicitudes = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#263238")
		self.solicitudes_activas = ft.Text("0", size=32, weight=ft.FontWeight.BOLD, color="#263238")

		# Dropdown de estado (estilo igual a reservas)
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
				ft.dropdown.Option("ACTIVAS", "Activas"),
				ft.dropdown.Option("INACTIVAS", "Inactivas"),
			],
		)

		# =========================
		# Header estilo autores
		header = ft.Container(
			content=ft.Row(
				[
					ft.Row([
						ft.Icon(ft.Icons.CREATE, color="#1565c0", size=32),
						ft.Text("Gestión de Solicitudes", size=26, weight=ft.FontWeight.BOLD, color="#263238"),
					], spacing=12),
					ft.Row([
						self.btn_refrescar,
						self.btn_crear,
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
		# Cards de Estadísticas (idénticas a reservas)
		def crear_stat_card_local(titulo, valor_widget, icon, color, bgcolor):
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
			crear_stat_card_local("Total Solicitudes", self.total_solicitudes, ft.Icons.LIBRARY_BOOKS_ROUNDED, "#5e35b1", ft.Colors.WHITE),
			crear_stat_card_local("Solicitudes Activas", self.solicitudes_activas, ft.Icons.BOOK_ROUNDED, "#1976d2", ft.Colors.WHITE),
		], spacing=20, scroll=ft.ScrollMode.AUTO)

		# =========================
		# Paginación
		# =========================
		self._pagination_label = ft.Text("Página 1 de 1", size=12, color="#546e7a")

		def change_page(delta: int):
			total = max(1, math.ceil(len(self._solicitudes_filtradas) / self._page_size))
			self._pagina_actual = min(max(1, self._pagina_actual + delta), total)
			self.mostrar_solicitudes()

		self._btn_prev = ft.IconButton(
			icon=ft.Icons.CHEVRON_LEFT,
			icon_color="#546e7a",
			tooltip="Anterior",
			on_click=lambda e: change_page(-1),
		)
		self._btn_next = ft.IconButton(
			icon=ft.Icons.CHEVRON_RIGHT,
			icon_color="#546e7a",
			tooltip="Siguiente",
			on_click=lambda e: change_page(1),
		)

		# Barra de Filtros (igual a reservas: search a la izquierda, estado a la derecha)
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

		# Contenedor de Tabla con mismo ancho/márgenes que el header
		tabla_container = ft.Container(
			content=ft.Column(
				[
					ft.Container(
						content=self.solicitudes_table,
						alignment=ft.Alignment.CENTER,
					),
					ft.Container(
						content=ft.Row(
							[self._btn_prev, self._pagination_label, self._btn_next],
							alignment=ft.MainAxisAlignment.CENTER,
							spacing=6,
						),
						padding=ft.padding.only(top=8),
					),
				],
				scroll=ft.ScrollMode.AUTO,
			),
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

		container = ft.Container(
			content=ft.Column(
				[
					header,
					ft.Container(content=stats_row, padding=ft.padding.symmetric(horizontal=30)),
					ft.Container(content=filtros_bar, padding=ft.padding.symmetric(horizontal=30)),
					ft.Container(content=tabla_container, padding=0, alignment=ft.Alignment.CENTER, expand=True),
				],
				spacing=20,
				expand=True,
			),
			bgcolor="#f5f7fa",
			padding=ft.padding.symmetric(vertical=20),
			expand=True,
		)

		self.controls = [
			ft.Row(
				[container],
				alignment=ft.MainAxisAlignment.CENTER,
				expand=True,
			)
		]

		self.mostrar_solicitudes(reset_pagina=True)

		# asignar manejadores despues de crear widgets para evitar incompatibilidades de versión
		self.search_input.on_change = lambda e: self.mostrar_solicitudes(reset_pagina=True)
		self.estado_dd.on_change = lambda e: self.mostrar_solicitudes(reset_pagina=True)

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

	def crear_stat_card(self, title, value_text: ft.Text):
		return ft.Container(
			width=220,
			padding=ft.padding.all(12),
			bgcolor=ft.Colors.WHITE,
			border_radius=8,
			shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK)),
			content=ft.Column(
				[
					ft.Text(title, size=12, color="#546e7a"),
					value_text,
				],
				spacing=6,
			),
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
				ft.ElevatedButton("Cancelar", on_click=self.cerrar_dialogo, bgcolor="#757575", color=ft.Colors.WHITE),
				ft.ElevatedButton(
					content=ft.Row([ft.Icon(ft.Icons.CHECK), ft.Text("Guardar")], spacing=8),
					bgcolor="#1976d2",
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

		activo = 1 if getattr(self, "activo_switch", None) and self.activo_switch.value else 0
		try:
			if self.solicitud_editando:
				self.db.update_solicitud(
					self.solicitud_editando.get("id_solicitud"),
					descripcion,
					autor,
					activo,
				)
			else:
				self.db.set_solicitud(descripcion, autor, activo)

			self._page.snack_bar = ft.SnackBar(ft.Text("✅ Solicitud guardada"), bgcolor=ft.Colors.GREEN_500)
			self._page.snack_bar.open = True
			self.cerrar_dialogo()
			self.mostrar_solicitudes()
		except Exception as ex:
			self._page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor=ft.Colors.RED_500)
			self._page.snack_bar.open = True
			self._page.update()


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
				ft.ElevatedButton("Cancelar", on_click=lambda e: self._cerrar_dialogo_confirmacion(dlg), bgcolor="#757575", color=ft.Colors.WHITE),
				ft.ElevatedButton("Eliminar", bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, on_click=eliminar),
			],
		)
		self._page.overlay.append(dlg)
		dlg.open = True
		self._page.update()

	def _cerrar_dialogo_confirmacion(self, dlg):
		dlg.open = False
		self._page.update()

	def mostrar_solicitudes(self, reset_pagina: bool = False):
		self.solicitudes_table.rows.clear()
		self._solicitudes_cache = self.db.get_solicitudes() or []

		# métricas
		total = len(self._solicitudes_cache)
		activas = sum(1 for s in self._solicitudes_cache if self._is_activo(s.get("activo")))
		self.total_solicitudes.value = str(total)
		self.solicitudes_activas.value = str(activas)

		# filtros
		estado = (self.estado_dd.value or "TODOS").upper()
		texto = (self.search_input.value or "").lower().strip()

		filtradas = []
		for sol in self._solicitudes_cache:
			is_act = self._is_activo(sol.get("activo"))
			if estado == "ACTIVAS" and not is_act:
				continue
			if estado == "INACTIVAS" and is_act:
				continue
			descripcion = (sol.get("descripcion", "") or "").lower()
			autor = (sol.get("autor", "") or "").lower()
			fecha = (str(sol.get("fecha_registro", "")) or "").lower()
			if texto and texto not in descripcion and texto not in autor and texto not in fecha:
				continue
			filtradas.append(sol)

		self._solicitudes_filtradas = filtradas

		total_pages = max(1, math.ceil(len(filtradas) / self._page_size))
		if reset_pagina:
			self._pagina_actual = 1
		if self._pagina_actual > total_pages:
			self._pagina_actual = total_pages

		start = (self._pagina_actual - 1) * self._page_size
		end = start + self._page_size
		pagina_items = filtradas[start:end]

		for sol in pagina_items:
			self.solicitudes_table.rows.append(self._build_row(sol))

		self._pagination_label.value = f"Página {self._pagina_actual} de {total_pages}"
		self._btn_prev.disabled = self._pagina_actual <= 1
		self._btn_next.disabled = self._pagina_actual >= total_pages

		self._page.update()
