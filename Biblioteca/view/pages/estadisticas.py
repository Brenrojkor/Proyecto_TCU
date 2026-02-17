import flet as ft
from controller.estadisticas_controller import EstadisticasController
from datetime import datetime, timedelta
import math

class EstadisticasView(ft.Column):
    def __init__(self, navigate, page=None):
        super().__init__()
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO
        
        # Colores coherentes con la interfaz
        self.color_principal = "#1976d2"
        self.color_secundario = "#1565c0"
        self.color_fondo = "#f5f7fa"
        self.color_exito = "#4CAF50"
        self.color_error = "#F44336"
        
        self.navigate = navigate
        self.page_ref = page
        self.controller = EstadisticasController()
        self.padding = 0
        self.spacing = 0
        self.bgcolor = self.color_fondo
        
        # Estado
        self.años_con_prestamos = []
        self.tab_actual = "dia"  # dia, semana, mes
        self.año_seleccionado = datetime.now().year
        self.mes_seleccionado = datetime.now().month
        self.semana_seleccionada = datetime.now().isocalendar()[1]
        
        self.meses_dict = {1:"Enero", 2:"Febrero", 3:"Marzo", 4:"Abril", 
                          5:"Mayo", 6:"Junio", 7:"Julio", 8:"Agosto",
                          9:"Septiembre", 10:"Octubre", 11:"Noviembre", 12:"Diciembre"}
        
        # Cargar datos iniciales
        self._cargar_datos()
        
        # =====================
        # HEADER
        # =====================
        header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.TRENDING_UP, size=28, color="#1976d2"),
                ft.Text(
                    "Estadísticas de Préstamos",
                    size=24,
                    weight="bold",
                    color="#263238"
                ),
            ], alignment="start", vertical_alignment="center", spacing=15),
            bgcolor=ft.Colors.WHITE,
            padding=20,
            margin=ft.margin.only(left=20, right=20, bottom=15),
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color="#00000015",
                offset=ft.Offset(0, 2),
            )
        )
        
        # =====================
        # TABS - Día, Semana, Mes
        # =====================
        self.tab_buttons = {}
        tab_container = self._crear_tab_buttons()
        
        # =====================
        # SELECTORS PARA FILTROS
        # =====================
        selector_container = self._crear_selector_filtros()
        
        # =====================
        # ÁREA DE CONTENIDO
        # =====================
        self.contenido_inner = ft.Column([
            ft.Icon(ft.Icons.FAVORITE_BORDER, size=48, color="#CCC"),
            ft.Text("Selecciona un período para ver las estadísticas", 
                   size=14, color="#999", weight="w500"),
        ], alignment="center", horizontal_alignment="center", spacing=15)
        
        self.contenido_area = ft.Container(
            content=self.contenido_inner,
            expand=True,
            bgcolor=ft.Colors.WHITE,
            padding=40,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color="#00000015",
                offset=ft.Offset(0, 2),
            )
        )
        
        # Mensaje
        self.mensaje = ft.Text("", size=12, weight="w500")
        self.mensaje_container = ft.Container(
            content=self.mensaje,
            padding=12,
            margin=ft.margin.only(left=20, right=20, bottom=15),
            border_radius=8,
            visible=False,
        )
        
        # Layout principal
        self.controls = [
            ft.Container(
                content=ft.Column([
                    header,
                    self.mensaje_container,
                    tab_container,
                    selector_container,
                    ft.Container(
                        content=self.contenido_area,
                        expand=True,
                        margin=ft.margin.only(left=20, right=20, bottom=20),
                    ),
                ], expand=True, spacing=0),
                expand=True,
                bgcolor=self.color_fondo,
                padding=ft.padding.only(top=20, left=20, right=20),
            )
        ]
    
    def _cargar_datos(self):
        """Carga datos iniciales"""
        try:
            self.años_con_prestamos = self.controller.get_años_con_prestamos()
            if not self.años_con_prestamos:
                self.años_con_prestamos = [datetime.now().year]
            self.año_seleccionado = self.años_con_prestamos[0]
        except Exception as e:
            print(f"Error cargando datos: {e}")
            self.años_con_prestamos = [datetime.now().year]
    
    def _crear_tab_buttons(self):
        """Crea los botones de pestañas"""
        def click_tab(nombre):
            def handler(e):
                self.tab_actual = nombre
                self._actualizar_tabs()
                self._cargar_contenido()
            return handler
        
        button_style = dict(
            height=44,
            width=140,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                color=ft.Colors.WHITE,
            )
        )
        
        tabs = {
            "dia": ("📅 Por Día", "#FF9800"),
            "semana": ("📊 Por Semana", "#2196F3"),
            "mes": ("📈 Por Mes", "#4CAF50"),
        }
        
        botones = []
        for key, (label, color) in tabs.items():
            btn = ft.ElevatedButton(
                label,
                on_click=click_tab(key),
                bgcolor=color,
                **button_style
            )
            self.tab_buttons[key] = btn
            botones.append(btn)
        
        return ft.Container(
            content=ft.Row(botones, spacing=15, wrap=False, alignment="center"),
            padding=ft.padding.symmetric(vertical=15),
            margin=ft.margin.only(left=20, right=20, bottom=15),
        )
    
    def _crear_selector_filtros(self):
        """Crea los selectores de filtro según la pestaña"""
        dropdown_style = dict(
            width=200,
            height=40,
            bgcolor=self.color_fondo,
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color=self.color_principal,
            text_size=13,
        )
        
        # Dropdown de año
        años_opciones = [ft.dropdown.Option(str(a), str(a)) for a in sorted(self.años_con_prestamos, reverse=True)]
        self.dropdown_año = ft.Dropdown(
            label="Año",
            options=años_opciones,
            value=str(self.año_seleccionado),
            on_select=self._on_año_change,
            **dropdown_style
        )
        
        # Dropdown de mes
        meses_opciones = [ft.dropdown.Option(str(i), self.meses_dict[i]) for i in range(1, 13)]
        self.dropdown_mes = ft.Dropdown(
            label="Mes",
            options=meses_opciones,
            value=str(self.mes_seleccionado),
            on_select=self._on_mes_change,
            **dropdown_style
        )
        
        # Dropdown de semana
        semanas_opciones = [ft.dropdown.Option(str(i), f"Semana {i}") for i in range(1, 53)]
        self.dropdown_semana = ft.Dropdown(
            label="Semana",
            options=semanas_opciones,
            value=str(self.semana_seleccionada),
            on_select=self._on_semana_change,
            **dropdown_style
        )
        
        # Botón para aplicar
        self.btn_aplicar = ft.ElevatedButton(
            "Cargar",
            on_click=self._on_aplicar_click,
            width=140,
            height=40,
            bgcolor=self.color_principal,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                color=ft.Colors.WHITE,
            )
        )
        
        # Contenedor con selector dinámico
        self.selector_content = ft.Row(
            [self.dropdown_año, self.dropdown_mes, self.btn_aplicar],
            spacing=15,
            alignment="center",
            wrap=False,
        )
        
        return ft.Container(
            content=self.selector_content,
            padding=15,
            margin=ft.margin.only(left=20, right=20, bottom=15),
            border_radius=8,
            bgcolor=self.color_fondo,
        )
    
    def _actualizar_tabs(self):
        """Actualiza estilos de los tabs"""
        tab_colores = {
            "dia": ("#FF9800", "#FFB74D"),
            "semana": ("#2196F3", "#64B5F6"),
            "mes": ("#4CAF50", "#81C784"),
        }
        
        for nombre, btn in self.tab_buttons.items():
            if nombre == self.tab_actual:
                btn.bgcolor = tab_colores[nombre][0]
            else:
                btn.bgcolor = tab_colores[nombre][1]
        
        # Actualizar selector
        self._actualizar_selector_filtros()
        self.update()
    
    def _actualizar_selector_filtros(self):
        """Actualiza los elementos del selector según la pestaña"""
        controles = []
        
        if self.tab_actual == "dia":
            controles = [
                ft.Text("Mostrando préstamos del día de hoy", size=12, color="#666"),
                self.btn_aplicar
            ]
        elif self.tab_actual == "semana":
            controles = [
                self.dropdown_año,
                self.dropdown_semana,
                self.btn_aplicar
            ]
        elif self.tab_actual == "mes":
            controles = [
                self.dropdown_año,
                self.dropdown_mes,
                self.btn_aplicar
            ]
        
        self.selector_content.controls = controles
        self.update()
    
    def _on_año_change(self, e):
        self.año_seleccionado = int(self.dropdown_año.value)
    
    def _on_mes_change(self, e):
        self.mes_seleccionado = int(self.dropdown_mes.value)
    
    def _on_semana_change(self, e):
        self.semana_seleccionada = int(self.dropdown_semana.value)
    
    def _on_aplicar_click(self, e):
        """Carga el contenido según la pestaña"""
        self._cargar_contenido()
    
    def _cargar_contenido(self):
        """Carga el contenido según la pestaña activa"""
        try:
            if self.tab_actual == "dia":
                self._mostrar_estadisticas_dia()
            elif self.tab_actual == "semana":
                self._mostrar_estadisticas_semana()
            elif self.tab_actual == "mes":
                self._mostrar_estadisticas_mes()
        except Exception as ex:
            self._mostrar_mensaje(f"❌ Error: {str(ex)}", "error")
    
    def _mostrar_estadisticas_dia(self):
        """Muestra estadísticas del día actual"""
        hoy = datetime.now().date()
        datos = self.controller.get_prestamos_por_dia(hoy)
        
        if not datos or datos[0]["cantidad"] == 0:
            total = 0
        else:
            total = datos[0]["cantidad"]
        
        # Crear tarjetas de métrica
        metricas = ft.Row([
            self._crear_metrica(f"{total}", "Préstamos Hoy", "#FF9800"),
            self._crear_metrica(f"{hoy.strftime('%d/%m/%Y')}", "Fecha", "#2196F3"),
        ], spacing=20, alignment="center", wrap=True)
        
        # Crear tabla detallada
        if total > 0:
            tabla = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Hora", weight="bold", color="#1976d2")),
                    ft.DataColumn(ft.Text("Libro", weight="bold", color="#1976d2")),
                    ft.DataColumn(ft.Text("Usuario", weight="bold", color="#1976d2")),
                    ft.DataColumn(ft.Text("Estado", weight="bold", color="#1976d2")),
                ],
                rows=[
                    ft.DataRow([
                        ft.Text("--:--", size=12),
                        ft.Text(f"Préstamo {i+1}", size=12),
                        ft.Text("--", size=12),
                        ft.Text("Activo", size=12, color="#4CAF50"),
                    ])
                    for i in range(min(5, total))
                ],
                column_spacing=20,
                data_row_min_height=45,
            )
            
            contenido = ft.Column([
                ft.Text(f"Préstamos del {hoy.strftime('%d de %B de %Y').replace(' de ', ' de ').upper()}", 
                       size=20, weight="bold", color="#263238"),
                ft.Divider(height=2, color="#e0e0e0"),
                metricas,
                ft.Container(
                    content=ft.Column([
                        ft.Text("Detalle de Préstamos", size=14, weight="bold", color="#263238"),
                        ft.Column([tabla], scroll="auto"),
                    ], spacing=15),
                    padding=20,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=4,
                        color="#00000010",
                        offset=ft.Offset(0, 1),
                    ),
                ),
            ], spacing=20)
        else:
            contenido = ft.Column([
                metricas,
                ft.Divider(height=2, color="#e0e0e0"),
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=48, color="#999"),
                        ft.Text("No hay préstamos registrados para hoy", 
                               size=14, color="#999", weight="w500", text_align="center"),
                    ], alignment="center", horizontal_alignment="center", spacing=10),
                    padding=30,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=4,
                        color="#00000010",
                        offset=ft.Offset(0, 1),
                    ),
                ),
            ], spacing=20, horizontal_alignment="center")
        
        self.contenido_area.content = ft.Column([
            contenido,
        ], scroll="auto", spacing=0)
        self._mostrar_mensaje(f"✓ Mostrando datos del {hoy.strftime('%d/%m/%Y')}", "exito")
        self.update()
    
    def _mostrar_estadisticas_semana(self):
        """Muestra estadísticas por semana"""
        datos = self.controller.get_prestamos_por_semana_reporte(self.semana_seleccionada, self.año_seleccionado)
        
        if not datos:
            self.contenido_area.content = ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=48, color="#999"),
                        ft.Text(f"No hay préstamos para la semana {self.semana_seleccionada} de {self.año_seleccionado}",
                               size=14, color="#999", weight="w500", text_align="center"),
                    ], alignment="center", horizontal_alignment="center", spacing=10),
                    padding=40,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=4,
                        color="#00000010",
                        offset=ft.Offset(0, 1),
                    ),
                ),
            ], alignment="center", horizontal_alignment="center")
            self._mostrar_mensaje("⚠️ No hay datos disponibles", "advertencia")
            self.update()
            return
        
        # Calcular estadísticas
        total = sum(d["cantidad"] for d in datos)
        promedio = total / len(datos) if datos else 0
        máximo = max(d["cantidad"] for d in datos) if datos else 0
        
        # Metricas
        metricas = ft.Row([
            self._crear_metrica(f"{total}", "Total Préstamos", "#2196F3"),
            self._crear_metrica(f"{len(datos)}", "Días", "#4CAF50"),
            self._crear_metrica(f"{round(promedio, 1)}", "Promedio", "#FF9800"),
            self._crear_metrica(f"{máximo}", "Máximo", "#F44336"),
        ], spacing=15, alignment="center", wrap=True)
        
        # Gráfica de barras simplificada
        max_cantidad = máximo if máximo > 0 else 1
        barras = []
        for item in datos:
            fecha = item["fecha"]
            cantidad = item["cantidad"]
            altura = max(80, (cantidad / max_cantidad) * 220)
            dia = fecha.day if hasattr(fecha, 'day') else int(str(fecha).split('-')[2])
            
            barra = ft.Column([
                ft.Container(
                    content=ft.Text(str(cantidad), size=12, weight="bold", color=ft.Colors.WHITE, text_align="center"),
                    width=60,
                    height=altura,
                    bgcolor="#2196F3",
                    border_radius=8,
                    alignment=ft.Alignment.CENTER,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=4,
                        color="#2196F315",
                        offset=ft.Offset(0, 2),
                    ),
                ),
                ft.Text(f"Día {dia}", size=11, weight="bold", text_align="center", color="#263238"),
            ], spacing=8, horizontal_alignment="center")
            barras.append(barra)
        
        contenido = ft.Column([
            ft.Text(f"Semana {self.semana_seleccionada} - {self.año_seleccionado}",
                   size=20, weight="bold", color="#263238"),
            ft.Divider(height=2, color="#e0e0e0"),
            metricas,
            ft.Container(
                content=ft.Column([
                    ft.Text("Distribución de Préstamos", size=14, weight="bold", color="#263238"),
                    ft.Row(barras, spacing=20, wrap=True, alignment="center"),
                ], spacing=15),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=4,
                    color="#00000010",
                    offset=ft.Offset(0, 1),
                ),
            ),
        ], spacing=20)
        
        self.contenido_area.content = ft.Column([
            contenido,
        ], scroll="auto", spacing=0)
        self._mostrar_mensaje(f"✓ Semana {self.semana_seleccionada} de {self.año_seleccionado}", "exito")
        self.update()
    
    def _mostrar_estadisticas_mes(self):
        """Muestra estadísticas por mes"""
        datos = self.controller.get_dias_del_mes(self.año_seleccionado, self.mes_seleccionado)
        
        if not datos:
            self.contenido_area.content = ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=48, color="#999"),
                        ft.Text(f"No hay préstamos para {self.meses_dict[self.mes_seleccionado]} de {self.año_seleccionado}",
                               size=14, color="#999", weight="w500", text_align="center"),
                    ], alignment="center", horizontal_alignment="center", spacing=10),
                    padding=40,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=12,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=4,
                        color="#00000010",
                        offset=ft.Offset(0, 1),
                    ),
                ),
            ], alignment="center", horizontal_alignment="center")
            self._mostrar_mensaje("⚠️ No hay datos disponibles", "advertencia")
            self.update()
            return
        
        # Calcular estadísticas
        total = sum(d["cantidad"] for d in datos)
        promedio = total / len(datos) if datos else 0
        máximo = max(d["cantidad"] for d in datos) if datos else 0
        
        # Metricas
        metricas = ft.Row([
            self._crear_metrica(f"{total}", "Total Préstamos", "#4CAF50"),
            self._crear_metrica(f"{len(datos)}", "Días Activos", "#2196F3"),
            self._crear_metrica(f"{round(promedio, 1)}", "Promedio Diario", "#FF9800"),
            self._crear_metrica(f"{máximo}", "Máximo Diario", "#F44336"),
        ], spacing=15, alignment="center", wrap=True)
        
        # Gráfica de barras por día
        max_cantidad = máximo if máximo > 0 else 1
        barras = []
        for item in datos:
            cantidad = item["cantidad"]
            altura = max(80, (cantidad / max_cantidad) * 220)
            dia = item["dia"]
            
            barra = ft.Column([
                ft.Container(
                    content=ft.Text(str(cantidad), size=11, weight="bold", color=ft.Colors.WHITE, text_align="center"),
                    width=55,
                    height=altura,
                    bgcolor="#4CAF50",
                    border_radius=8,
                    alignment=ft.Alignment.CENTER,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=4,
                        color="#4CAF5015",
                        offset=ft.Offset(0, 2),
                    ),
                ),
                ft.Text(f"{dia}", size=10, weight="bold", text_align="center", color="#263238"),
            ], spacing=8, horizontal_alignment="center")
            barras.append(barra)
        
        # Agrupar barras en filas
        filas_barras = []
        for i in range(0, len(barras), 7):
            filas_barras.append(ft.Row(barras[i:i+7], spacing=15, wrap=True, alignment="center"))
        
        contenido = ft.Column([
            ft.Text(f"{self.meses_dict[self.mes_seleccionado]} de {self.año_seleccionado}",
                   size=20, weight="bold", color="#263238"),
            ft.Divider(height=2, color="#e0e0e0"),
            metricas,
            ft.Container(
                content=ft.Column([
                    ft.Text("Distribución de Préstamos por Día", size=14, weight="bold", color="#263238"),
                    ft.Column(filas_barras, spacing=20),
                ], spacing=15),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=4,
                    color="#00000010",
                    offset=ft.Offset(0, 1),
                ),
            ),
        ], spacing=20)
        
        self.contenido_area.content = ft.Column([
            contenido,
        ], scroll="auto", spacing=0)
        self._mostrar_mensaje(f"✓ {self.meses_dict[self.mes_seleccionado]} de {self.año_seleccionado}", "exito")
        self.update()
    
    def _crear_metrica(self, valor, etiqueta, color):
        """Crea una tarjeta de métrica mejorada"""
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(valor, size=32, weight="bold", color=ft.Colors.WHITE),
                    padding=10,
                    bgcolor=color,
                    border_radius=10,
                    width=120,
                    height=70,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Text(etiqueta, size=11, color="#666", weight="w500", text_align="center"),
            ], alignment="center", horizontal_alignment="center", spacing=8),
            width=160,
            height=130,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=15,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color="#00000010",
                offset=ft.Offset(0, 2),
            ),
            border=ft.border.all(1, "#f0f0f0"),
        )
    
    def _mostrar_mensaje(self, texto, tipo="info"):
        """Muestra un mensaje"""
        colores_mapa = {
            "exito": {"color": self.color_exito, "bg": "#E8F5E9"},
            "error": {"color": self.color_error, "bg": "#FFEBEE"},
            "advertencia": {"color": "#FF9800", "bg": "#FFF3E0"},
            "info": {"color": self.color_principal, "bg": "#E3F2FD"}
        }
        
        config = colores_mapa.get(tipo, colores_mapa["info"])
        self.mensaje.value = texto
        self.mensaje.color = config["color"]
        self.mensaje_container.bgcolor = config["bg"]
        self.mensaje_container.visible = bool(texto)
        self.update()
