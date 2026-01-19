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
        self.spacing = 15
        
        # Estado
        self.datos_año = []
        self.datos_mes = []
        self.años_disponibles = []
        self.meses_disponibles = [(1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"), 
                                   (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
                                   (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")]
        
        # Cargar datos iniciales
        self._cargar_datos()
        
        # Dropdown filtro tipo
        self.filtro_tipo = ft.Dropdown(
            label="Tipo de Análisis",
            value="año",
            options=[
                ft.dropdown.Option("año", "Por Año"),
                ft.dropdown.Option("mes", "Por Mes"),
                ft.dropdown.Option("semana", "Por Semana"),
                ft.dropdown.Option("fecha", "Por Fecha"),
            ],
            width=250,
        )
        
        # Dropdown filtro valor
        self.filtro_valor = ft.Dropdown(
            label="Seleccionar",
            width=250,
        )
        
        # Botón para actualizar opciones
        self.btn_actualizar_opciones = ft.ElevatedButton("Actualizar", on_click=self._actualizar_opciones_filtro_click, width=120)
        
        # Área de gráficas
        self.grafica_area = ft.Container(
            content=ft.Column([
                ft.Text("Selecciona un filtro para ver estadísticas", size=14, color="gray")
            ]),
            expand=True,
            border=ft.border.all(1, "lightgray"),
            padding=15,
        )
        
        # Botones
        self.btn_aplicar = ft.ElevatedButton("Aplicar", on_click=self._aplicar_filtro, width=120)
        self.btn_descargar = ft.ElevatedButton("Descargar Excel", on_click=self._descargar_excel, width=150)
        
        # Mensaje
        self.mensaje = ft.Text("", size=12, color="blue")
        
        # Actualizar opciones iniciales
        self._on_filtro_tipo_change(None)
        
        # Layout
        self.controls = [
            ft.Text("📊 Estadísticas de Libros", size=28, weight="bold"),
            ft.Row([
                ft.Column([
                    ft.Text("Filtros:", size=14, weight="bold"),
                    ft.Row([self.filtro_tipo, self.filtro_valor, self.btn_actualizar_opciones], spacing=10),
                    ft.Row([self.btn_aplicar, self.btn_descargar], spacing=10),
                ], spacing=10),
            ]),
            self.mensaje,
            ft.Divider(),
            self.grafica_area,
        ]
    
    def _cargar_datos(self):
        try:
            self.datos_año = self.controller.get_libros_por_año()
            self.datos_mes = self.controller.get_libros_por_mes()
            self.años_disponibles = [d["año"] for d in self.datos_año]
        except Exception as e:
            print(f"Error cargando datos: {e}")
    
    def _on_filtro_tipo_change(self, e):
        tipo = self.filtro_tipo.value
        opciones = []
        
        if tipo == "año" and self.años_disponibles:
            opciones = [ft.dropdown.Option(str(a), str(a)) for a in sorted(self.años_disponibles, reverse=True)]
        
        elif tipo == "mes":
            opciones = [ft.dropdown.Option(str(m[0]), m[1]) for m in self.meses_disponibles]
        
        elif tipo == "semana":
            opciones = [ft.dropdown.Option(str(i), f"Semana {i}") for i in range(1, 53)]
        
        elif tipo == "fecha":
            self.filtro_valor.label = "DD/MM/YYYY"
        
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
                self.mensaje.value = "⚠️ Selecciona un valor"
                self.update()
                return
            
            if tipo == "año":
                año = int(valor_str)
                datos = self.controller.get_libros_por_semana(año)
                self._mostrar_grafica_semana(datos, año)
                self.mensaje.value = f"✓ Mostrando semanas del año {año}"
            
            elif tipo == "mes":
                mes = int(valor_str)
                año = self.años_disponibles[0] if self.años_disponibles else datetime.now().year
                datos = self.controller.get_libros_por_fecha(año, mes)
                self._mostrar_grafica_fecha(datos, año, mes)
                self.mensaje.value = f"✓ Mostrando días del mes {mes}"
            
            elif tipo == "semana":
                semana = int(valor_str)
                año = self.años_disponibles[0] if self.años_disponibles else datetime.now().year
                self.mensaje.value = f"✓ Mostrando semana {semana} de {año}"
            
            elif tipo == "fecha":
                self.mensaje.value = f"✓ Filtrado por fecha {valor_str}"
            
            self.update()
        
        except Exception as ex:
            self.mensaje.value = f"❌ Error: {str(ex)}"
            self.update()
    
    def _mostrar_grafica_semana(self, datos, año):
        if not datos:
            self.grafica_area.content = ft.Column([
                ft.Text(f"No hay datos para el año {año}", size=14, color="gray")
            ])
            return
        
        columnas = []
        for i in range(0, len(datos), 4):
            batch = datos[i:i+4]
            fila = []
            for item in batch:
                semana = item["semana"]
                cantidad = item["cantidad"]
                altura = min(cantidad * 10, 200)
                
                fila.append(
                    ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Text(str(cantidad), size=12, weight="bold", text_align="center")
                            ], alignment="center"),
                            width=60,
                            height=altura,
                            bgcolor="lightblue",
                            border_radius=5,
                        ),
                        ft.Text(f"S{semana}", size=10, text_align="center"),
                    ], spacing=5, horizontal_alignment="center")
                )
            
            columnas.append(ft.Row(fila, spacing=15, wrap=True))
        
        self.grafica_area.content = ft.Column([
            ft.Text(f"Libros por Semana ({año})", size=16, weight="bold"),
            ft.Row([ft.Column(columnas, spacing=15, scroll="auto")], expand=True)
        ], spacing=10)
    
    def _mostrar_grafica_fecha(self, datos, año, mes):
        if not datos:
            self.grafica_area.content = ft.Column([
                ft.Text(f"No hay datos para {mes}/{año}", size=14, color="gray")
            ])
            return
        
        columnas = []
        for i in range(0, len(datos), 5):
            batch = datos[i:i+5]
            fila = []
            for item in batch:
                fecha = item["fecha"]
                cantidad = item["cantidad"]
                altura = min(cantidad * 20, 200)
                día = fecha.day if hasattr(fecha, 'day') else int(str(fecha).split('-')[2])
                
                fila.append(
                    ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Text(str(cantidad), size=11, weight="bold", text_align="center")
                            ], alignment="center"),
                            width=50,
                            height=altura,
                            bgcolor="lightgreen",
                            border_radius=5,
                        ),
                        ft.Text(f"{día}", size=9, text_align="center"),
                    ], spacing=3, horizontal_alignment="center")
                )
            
            columnas.append(ft.Row(fila, spacing=10, wrap=True))
        
        self.grafica_area.content = ft.Column([
            ft.Text(f"Libros por Día (Mes {mes})", size=16, weight="bold"),
            ft.Row([ft.Column(columnas, spacing=10, scroll="auto")], expand=True)
        ], spacing=10)
    
    def _descargar_excel(self, e):
        try:
            tipo = self.filtro_tipo.value
            valor_str = self.filtro_valor.value
            
            if not valor_str:
                self.mensaje.value = "⚠️ Selecciona un valor antes de descargar"
                self.update()
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
            self.mensaje.value = f"✓ Descargado: {filepath.split(chr(92))[-1]}"
        
        except Exception as ex:
            self.mensaje.value = f"❌ Error al descargar: {str(ex)}"
        
        self.update()
