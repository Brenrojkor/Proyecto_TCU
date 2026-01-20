import flet as ft
from controller.estadisticas_controller import EstadisticasController
from datetime import datetime

class EstadisticasView(ft.Column):
    def __init__(self, navigate, page=None):
        super().__init__()
        self.navigate = navigate
        self.page_ref = page
        self.controller = EstadisticasController()
        self.expand = True
        self.padding = 20
        self.spacing = 20
        
        # Colores coherentes con la interfaz
        self.color_principal = "#0b495c"
        self.color_secundario = "#1B6F7A"
        self.color_acento = "#2196F3"
        self.color_fondo = "#f5f7fa"
        self.color_exito = "#4CAF50"
        
        # Estado
        self.datos_año = []
        self.datos_mes = []
        self.años_disponibles = []
        self.meses_disponibles = [(1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"), 
                                   (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
                                   (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")]
        
        # Cargar datos iniciales
        self._cargar_datos()
        
        # Estilos para inputs
        input_style = dict(
            width=200,
            height=40,
            bgcolor=self.color_fondo,
            border_radius=8,
            border_color="#cfd8dc",
            focused_border_color=self.color_acento,
            text_size=13,
        )
        
        # Dropdown filtro tipo
        self.filtro_tipo = ft.Dropdown(
            label="Tipo de Análisis",
            value="año",
            options=[
                ft.dropdown.Option("año", "Por Año"),
                ft.dropdown.Option("mes", "Por Mes"),
                ft.dropdown.Option("semana", "Por Semana"),
            ],
            **input_style
        )
        
        # Dropdown filtro valor
        self.filtro_valor = ft.Dropdown(
            label="Seleccionar",
            **input_style
        )
        
        # Botones con estilo mejorado
        button_style = dict(
            height=40,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                color=ft.Colors.WHITE,
            )
        )
        
        # Botón para actualizar opciones
        self.btn_actualizar_opciones = ft.ElevatedButton(
            "↻ Actualizar",
            on_click=self._actualizar_opciones_filtro_click,
            width=140,
            bgcolor=self.color_secundario,
            **button_style
        )
        
        # Área de gráficas con tarjeta mejorada
        self.grafica_area = ft.Container(
            content=ft.Column([
                ft.Text("Selecciona un filtro para ver estadísticas", size=14, color="#757575")
            ], alignment="center", horizontal_alignment="center"),
            expand=True,
            border_radius=0,
            padding=40,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(0, "transparent"),
        )
        
        # Botones principales
        self.btn_aplicar = ft.ElevatedButton(
            "📊 Aplicar",
            on_click=self._aplicar_filtro,
            width=140,
            bgcolor=self.color_acento,
            **button_style
        )
        
        self.btn_descargar = ft.ElevatedButton(
            "📥 Descargar Excel",
            on_click=self._descargar_excel,
            width=180,
            bgcolor=self.color_exito,
            **button_style
        )
        
        # Mensaje
        self.mensaje = ft.Text("", size=12, color=self.color_principal, weight="w500")
        self.mensaje_container = ft.Container(
            content=self.mensaje,
            padding=12,
            border_radius=8,
            visible=False,
        )
        
        # Actualizar opciones iniciales
        self._on_filtro_tipo_change(None)
        
        # Header con fondo de color
        header = ft.Container(
            content=ft.Row([
                ft.Text(
                    "📊 Estadísticas de Libros",
                    size=24,
                    weight="bold",
                    color=ft.Colors.WHITE
                ),
            ], alignment="start", vertical_alignment="center"),
            bgcolor="#ADD8E6",
            padding=20,
            border_radius=ft.border_radius.only(top_left=8, top_right=8),
            height=70
        )
        
        # Panel de filtros y gráficas juntos en una tarjeta
        content_container = ft.Container(
            content=ft.Column([
                # Panel de filtros
                ft.Container(
                    content=ft.Column([
                        ft.Text("Filtros", size=13, weight="bold", color=self.color_principal),
                        ft.Row([
                            self.filtro_tipo,
                            self.filtro_valor,
                            self.btn_actualizar_opciones
                        ], spacing=15, wrap=False, alignment="start"),
                        ft.Row([
                            self.btn_aplicar,
                            self.btn_descargar,
                        ], spacing=15),
                    ], spacing=12),
                    padding=20,
                    bgcolor="#f9f9f9",
                    border_radius=0,
                ),
                ft.Divider(height=1, color="#e0e0e0"),
                # Mensaje
                self.mensaje_container,
                # Área de gráficas
                self.grafica_area,
            ], spacing=0),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color="#00000015",
                offset=ft.Offset(0, 2),
            )
        )
        
        # Contenedor principal centrado
        main_container = ft.Container(
            content=ft.Column([
                header,
                content_container,
            ], spacing=0),
            width=1200,
            bgcolor=ft.Colors.TRANSPARENT,
        )
        
        # Layout
        self.controls = [
            ft.Row([
                main_container,
            ], alignment="center", expand=True)
        ]
    
    def _cargar_datos(self):
        try:
            self.datos_año = self.controller.get_libros_por_año()
            self.datos_mes = self.controller.get_libros_por_mes()
            self.años_disponibles = [d["año"] for d in self.datos_año]
        except Exception as e:
            print(f"Error cargando datos: {e}")
    
    def _mostrar_mensaje(self, texto, tipo="info"):
        """Muestra un mensaje con el estilo apropiado"""
        colores_mapa = {
            "exito": {"color": self.color_exito, "bg": "#E8F5E9"},
            "error": {"color": "#F44336", "bg": "#FFEBEE"},
            "advertencia": {"color": "#FF9800", "bg": "#FFF3E0"},
            "info": {"color": self.color_principal, "bg": "#E3F2FD"}
        }
        
        config = colores_mapa.get(tipo, colores_mapa["info"])
        self.mensaje.value = texto
        self.mensaje.color = config["color"]
        self.mensaje_container.bgcolor = config["bg"]
        self.mensaje_container.visible = bool(texto)
        self.update()
    
    def _on_filtro_tipo_change(self, e):
        tipo = self.filtro_tipo.value
        opciones = []
        
        if tipo == "año" and self.años_disponibles:
            opciones = [ft.dropdown.Option(str(a), str(a)) for a in sorted(self.años_disponibles, reverse=True)]
        
        elif tipo == "mes":
            opciones = [ft.dropdown.Option(str(m[0]), m[1]) for m in self.meses_disponibles]
        
        elif tipo == "semana":
            opciones = [ft.dropdown.Option(str(i), f"Semana {i}") for i in range(1, 53)]
        
        self.filtro_valor.options = opciones
        if opciones:
            self.filtro_valor.value = opciones[0].key
    
    def _actualizar_opciones_filtro_click(self, e):
        self._on_filtro_tipo_change(None)
    
    def _aplicar_filtro(self, e):
        try:
            tipo = self.filtro_tipo.value
            valor_str = self.filtro_valor.value
            
            if not valor_str:
                self._mostrar_mensaje("⚠️ Por favor selecciona un valor", "advertencia")
                return
            
            if tipo == "año":
                año = int(valor_str)
                datos = self.controller.get_libros_por_semana(año)
                self._mostrar_grafica_semana(datos, año)
                self._mostrar_mensaje(f"✓ Mostrando semanas del año {año}", "exito")
            
            elif tipo == "mes":
                mes = int(valor_str)
                año = self.años_disponibles[0] if self.años_disponibles else datetime.now().year
                datos = self.controller.get_libros_por_fecha(año, mes)
                self._mostrar_grafica_fecha(datos, año, mes)
                nombre_mes = self.meses_disponibles[mes-1][1]
                self._mostrar_mensaje(f"✓ Mostrando días de {nombre_mes} {año}", "exito")
            
            elif tipo == "semana":
                semana = int(valor_str)
                año = self.años_disponibles[0] if self.años_disponibles else datetime.now().year
                self._mostrar_mensaje(f"✓ Mostrando semana {semana} de {año}", "exito")
        
        except Exception as ex:
            self._mostrar_mensaje(f"❌ Error: {str(ex)}", "error")
    
    def _mostrar_grafica_semana(self, datos, año):
        if not datos:
            self.grafica_area.content = ft.Column([
                ft.Text(f"No hay datos para el año {año}", size=14, color="#757575", text_align="center")
            ], alignment="center", horizontal_alignment="center")
            return
        
        total_libros = sum(d["cantidad"] for d in datos)
        max_cantidad = max(d["cantidad"] for d in datos) if datos else 1
        
        # Encabezado con estadísticas
        estadisticas = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{total_libros}", size=24, weight="bold", color=self.color_acento),
                    ft.Text("Total de Libros", size=12, color="#757575"),
                ], alignment="center", horizontal_alignment="center"),
                width=150,
                height=80,
                bgcolor="#E3F2FD",
                border_radius=8,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{len(datos)}", size=24, weight="bold", color=self.color_exito),
                    ft.Text("Semanas con datos", size=12, color="#757575"),
                ], alignment="center", horizontal_alignment="center"),
                width=150,
                height=80,
                bgcolor="#E8F5E9",
                border_radius=8,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{max_cantidad}", size=24, weight="bold", color="#FF9800"),
                    ft.Text("Máximo por semana", size=12, color="#757575"),
                ], alignment="center", horizontal_alignment="center"),
                width=150,
                height=80,
                bgcolor="#FFF3E0",
                border_radius=8,
            ),
        ], spacing=20, alignment="center")
        
        # Gráficas en filas
        columnas = []
        for i in range(0, len(datos), 4):
            batch = datos[i:i+4]
            fila = []
            for item in batch:
                semana = item["semana"]
                cantidad = item["cantidad"]
                altura = max(50, (cantidad / max_cantidad) * 200)
                
                fila.append(
                    ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Text(str(cantidad), size=11, weight="bold", text_align="center", color=ft.Colors.WHITE)
                            ], alignment="center"),
                            width=65,
                            height=altura,
                            bgcolor=self.color_acento,
                            border_radius=6,
                            tooltip=f"Semana {semana}: {cantidad} libros",
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=3,
                                color="#00000015",
                                offset=ft.Offset(0, 1),
                            )
                        ),
                        ft.Text(f"S{semana}", size=10, text_align="center", weight="w500", color=self.color_principal),
                    ], spacing=8, horizontal_alignment="center")
                )
            
            columnas.append(ft.Row(fila, spacing=20, wrap=True, alignment="center"))
        
        self.grafica_area.content = ft.Column([
            ft.Text(f"Libros por Semana - {año}", size=16, weight="bold", color=self.color_principal),
            ft.Divider(height=2, color="#e0e0e0"),
            estadisticas,
            ft.Divider(height=2, color="#e0e0e0"),
            ft.Text("Detalle por Semana", size=13, weight="w500", color=self.color_principal),
            ft.Column(columnas, spacing=25, horizontal_alignment="center"),
        ], spacing=20, horizontal_alignment="center")
    
    def _mostrar_grafica_fecha(self, datos, año, mes):
        if not datos:
            self.grafica_area.content = ft.Column([
                ft.Text(f"No hay datos para {mes}/{año}", size=14, color="#757575", text_align="center")
            ], alignment="center", horizontal_alignment="center")
            return
        
        total_libros = sum(d["cantidad"] for d in datos)
        max_cantidad = max(d["cantidad"] for d in datos) if datos else 1
        
        # Encabezado con estadísticas
        estadisticas = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{total_libros}", size=24, weight="bold", color=self.color_acento),
                    ft.Text("Total del Mes", size=12, color="#757575"),
                ], alignment="center", horizontal_alignment="center"),
                width=150,
                height=80,
                bgcolor="#E3F2FD",
                border_radius=8,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{len(datos)}", size=24, weight="bold", color=self.color_exito),
                    ft.Text("Días con datos", size=12, color="#757575"),
                ], alignment="center", horizontal_alignment="center"),
                width=150,
                height=80,
                bgcolor="#E8F5E9",
                border_radius=8,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"{round(total_libros/len(datos), 1)}", size=24, weight="bold", color="#FF9800"),
                    ft.Text("Promedio diario", size=12, color="#757575"),
                ], alignment="center", horizontal_alignment="center"),
                width=150,
                height=80,
                bgcolor="#FFF3E0",
                border_radius=8,
            ),
        ], spacing=20, alignment="center")
        
        # Obtener nombre del mes
        nombre_mes = self.meses_disponibles[mes-1][1] if 1 <= mes <= 12 else str(mes)
        
        columnas = []
        for i in range(0, len(datos), 5):
            batch = datos[i:i+5]
            fila = []
            for item in batch:
                fecha = item["fecha"]
                cantidad = item["cantidad"]
                altura = max(40, (cantidad / max_cantidad) * 200)
                día = fecha.day if hasattr(fecha, 'day') else int(str(fecha).split('-')[2])
                
                fila.append(
                    ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Text(str(cantidad), size=10, weight="bold", text_align="center", color=ft.Colors.WHITE)
                            ], alignment="center"),
                            width=55,
                            height=altura,
                            bgcolor=self.color_secundario,
                            border_radius=6,
                            tooltip=f"Día {día}: {cantidad} libros",
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=3,
                                color="#00000015",
                                offset=ft.Offset(0, 1),
                            )
                        ),
                        ft.Text(f"{día}", size=9, text_align="center", weight="w500", color=self.color_principal),
                    ], spacing=6, horizontal_alignment="center")
                )
            
            columnas.append(ft.Row(fila, spacing=18, wrap=True, alignment="center"))
        
        self.grafica_area.content = ft.Column([
            ft.Text(f"Libros por Día - {nombre_mes} {año}", size=16, weight="bold", color=self.color_principal),
            ft.Divider(height=2, color="#e0e0e0"),
            estadisticas,
            ft.Divider(height=2, color="#e0e0e0"),
            ft.Text("Detalle por Día", size=13, weight="w500", color=self.color_principal),
            ft.Column(columnas, spacing=25, horizontal_alignment="center"),
        ], spacing=20, horizontal_alignment="center")
    
    def _descargar_excel(self, e):
        try:
            tipo = self.filtro_tipo.value
            valor_str = self.filtro_valor.value
            
            if not valor_str:
                self._mostrar_mensaje("⚠️ Selecciona un valor antes de descargar", "advertencia")
                return
            
            if tipo == "año":
                valor = int(valor_str)
            elif tipo == "mes":
                valor = int(valor_str)
            elif tipo == "semana":
                año = self.años_disponibles[0] if self.años_disponibles else datetime.now().year
                valor = (año, int(valor_str))
            else:
                valor = valor_str
            
            filepath = self.controller.exportar_excel(tipo, valor)
            archivo = filepath.split(chr(92))[-1]
            self._mostrar_mensaje(f"✓ Descargado: {archivo}", "exito")
        
        except Exception as ex:
            self._mostrar_mensaje(f"❌ Error al descargar: {str(ex)}", "error")
