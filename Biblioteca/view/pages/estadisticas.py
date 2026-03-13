import flet as ft
from controller.estadisticas_controller import EstadisticasController
from datetime import datetime, timedelta
import math

class EstadisticasView(ft.Column):

    def __init__(self, navigate, page=None):
        super().__init__()

        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 20
        self.padding = 20
        self.bgcolor = "#f5f7fa"

        self.navigate = navigate
        self.page_ref = page
        self.controller = EstadisticasController()

        # Estado
        self.tab_actual = "dia"
        self.años_con_prestamos = []
        self.año_seleccionado = datetime.now().year
        self.mes_seleccionado = datetime.now().month
        self.semana_seleccionada = datetime.now().isocalendar()[1]

        self.meses_dict = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
            5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
            9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }

        self._cargar_datos()

        # HEADER
        header = ft.Row(
            [
                ft.Icon(ft.Icons.TRENDING_UP, size=28, color="#1976d2"),
                ft.Text("Estadísticas de Préstamos",
                        size=24,
                        weight="bold",
                        color="#263238")
            ]
        )

        # Tabs
        self.tab_buttons = {}
        tabs = self._crear_tabs()

        # Filtros
        self.selector_row = self._crear_selector_filtros()

        # Área de contenido
        self.contenido_area = ft.Container(
            expand=True,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=20,
            shadow=ft.BoxShadow(
                blur_radius=6,
                color="#00000012",
                offset=ft.Offset(0, 2),
            ),
        )

        self.controls = [
            header,
            tabs,
            self.selector_row,
            self.contenido_area
        ]

        self._actualizar_tabs()

    # =========================
    # CARGA INICIAL
    # =========================

    def _cargar_datos(self):
        try:
            self.años_con_prestamos = self.controller.get_años_con_prestamos()
            if not self.años_con_prestamos:
                self.años_con_prestamos = [datetime.now().year]
        except:
            self.años_con_prestamos = [datetime.now().year]

    # =========================
    # TABS
    # =========================

    def _crear_tabs(self):

        def click_tab(nombre):
            def handler(e):
                self.tab_actual = nombre
                self._actualizar_tabs()
                self._cargar_contenido()
            return handler

        config = {
            "dia": ("📅 Día", "#FF9800"),
            "semana": ("📊 Semana", "#2196F3"),
            "mes": ("📈 Mes", "#4CAF50"),
        }

        botones = []

        for key, (label, color) in config.items():
            btn = ft.ElevatedButton(
                label,
                on_click=click_tab(key),
                bgcolor=color,
                width=120,
                height=40,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    color=ft.Colors.WHITE,
                )
            )
            self.tab_buttons[key] = btn
            botones.append(btn)

        return ft.Row(botones, spacing=15)

    def _actualizar_tabs(self):
        colores = {
            "dia": "#FF9800",
            "semana": "#2196F3",
            "mes": "#4CAF50"
        }

        for nombre, btn in self.tab_buttons.items():
            btn.bgcolor = colores[nombre] if nombre == self.tab_actual else "#CFD8DC"

        self._actualizar_selector()
        if self.page_ref:
            self.page_ref.update()

    # =========================
    # FILTROS
    # =========================

    def _crear_selector_filtros(self):

        años_opciones = [
            ft.dropdown.Option(str(a), str(a))
            for a in sorted(self.años_con_prestamos, reverse=True)
        ]

        self.dropdown_año = ft.Dropdown(
            width=150,
            label="Año",
            options=años_opciones,
            value=str(self.año_seleccionado),
            on_select=self._on_año_change
        )

        self.dropdown_mes = ft.Dropdown(
            width=150,
            label="Mes",
            options=[
                ft.dropdown.Option(str(i), self.meses_dict[i])
                for i in range(1, 13)
            ],
            value=str(self.mes_seleccionado),
            on_select=self._on_mes_change
        )

        self.dropdown_semana = ft.Dropdown(
            width=150,
            label="Semana",
            options=[
                ft.dropdown.Option(str(i), f"Semana {i}")
                for i in range(1, 53)
            ],
            value=str(self.semana_seleccionada),
            on_select=self._on_semana_change
        )

        self.btn_aplicar = ft.ElevatedButton(
            "Cargar",
            on_click=lambda e: self._cargar_contenido(),
            bgcolor="#1976d2",
            color="white"
        )

        return ft.Row(spacing=15)

    def _actualizar_selector(self):
        self.selector_row.controls.clear()

        if self.tab_actual == "dia":
            self.selector_row.controls.extend([
                ft.Text("Mostrando datos del día actual"),
                self.btn_aplicar
            ])
        elif self.tab_actual == "semana":
            self.selector_row.controls.extend([
                self.dropdown_año,
                self.dropdown_semana,
                self.btn_aplicar
            ])
        else:
            self.selector_row.controls.extend([
                self.dropdown_año,
                self.dropdown_mes,
                self.btn_aplicar
            ])

        if self.page_ref:
            self.page_ref.update()

    # Eventos Dropdown

    def _on_año_change(self, e):
        self.año_seleccionado = int(e.control.value)

    def _on_mes_change(self, e):
        self.mes_seleccionado = int(e.control.value)

    def _on_semana_change(self, e):
        self.semana_seleccionada = int(e.control.value)

    # =========================
    # CONTENIDO
    # =========================

    def _cargar_contenido(self):
        if self.tab_actual == "dia":
            self._mostrar_estadisticas_dia()
        elif self.tab_actual == "semana":
            self._mostrar_estadisticas_semana()
        else:
            self._mostrar_estadisticas_mes()

    # =========================
    # MÉTRICA
    # =========================

    def _crear_metrica(self, valor, etiqueta, color):
        return ft.Container(
            content=ft.Column([
                ft.Text(valor, size=26, weight="bold", color=color),
                ft.Text(etiqueta, size=12, color="#666"),
            ], spacing=4, horizontal_alignment="center"),
            padding=15,
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            width=150,
            height=90,
            shadow=ft.BoxShadow(
                blur_radius=6,
                color="#00000012",
                offset=ft.Offset(0, 2),
            ),
        )

    # =========================
    # DÍA
    # =========================

    def _mostrar_estadisticas_dia(self):
        hoy = datetime.now().date()
        datos = self.controller.get_prestamos_por_dia(hoy)
        total = datos[0]["cantidad"] if datos else 0

        metricas = ft.Row([
            self._crear_metrica(str(total), "Préstamos Hoy", "#FF9800"),
            self._crear_metrica(hoy.strftime("%d/%m/%Y"), "Fecha", "#2196F3")
        ], spacing=20)

        self.contenido_area.content = metricas
        if self.page_ref:
            self.page_ref.update()

    # =========================
    # SEMANA
    # =========================

    def _mostrar_estadisticas_semana(self):
        datos = self.controller.get_prestamos_por_semana_reporte(
            self.semana_seleccionada,
            self.año_seleccionado
        )

        if not datos:
            self.contenido_area.content = ft.Text("No hay datos disponibles")
            if self.page_ref:
                self.page_ref.update()
            return

        total = sum(d["cantidad"] for d in datos)
        max_cantidad = max(d["cantidad"] for d in datos)

        barras = []

        for item in datos:
            cantidad = item["cantidad"]
            altura = (cantidad / max_cantidad) * 150 if max_cantidad else 10

            barras.append(
                ft.Column([
                    ft.Container(
                        height=altura,
                        width=40,
                        bgcolor="#2196F3",
                        border_radius=6
                    ),
                    ft.Text(str(cantidad), size=11)
                ],
                horizontal_alignment="center")
            )

        self.contenido_area.content = ft.Column([
            self._crear_metrica(str(total), "Total Semana", "#2196F3"),
            ft.Row(barras, spacing=15)
        ], spacing=20)

        if self.page_ref:
            self.page_ref.update()

    # =========================
    # MES
    # =========================

    def _mostrar_estadisticas_mes(self):
        datos = self.controller.get_dias_del_mes(
            self.año_seleccionado,
            self.mes_seleccionado
        )

        if not datos:
            self.contenido_area.content = ft.Text("No hay datos disponibles")
            if self.page_ref:
                self.page_ref.update()
            return

        total = sum(d["cantidad"] for d in datos)
        max_cantidad = max(d["cantidad"] for d in datos)

        barras = []

        for item in datos:
            cantidad = item["cantidad"]
            altura = (cantidad / max_cantidad) * 150 if max_cantidad else 10

            barras.append(
                ft.Column([
                    ft.Container(
                        height=altura,
                        width=25,
                        bgcolor="#4CAF50",
                        border_radius=4
                    ),
                    ft.Text(str(item["dia"]), size=10)
                ],
                horizontal_alignment="center")
            )

        self.contenido_area.content = ft.Column([
            self._crear_metrica(str(total), "Total Mes", "#4CAF50"),
            ft.Row(barras, wrap=True, spacing=10)
        ], spacing=20)

        if self.page_ref:
            self.page_ref.update()