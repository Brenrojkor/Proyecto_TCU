from model.database import Database
from datetime import datetime, timedelta
import os

class EstadisticasController:
    def __init__(self):
        self.db = Database()
    
    def get_libros_por_año(self):
        cursor = self.db.cursor
        cursor.execute("""
            SELECT anio_publicacion as año, COUNT(*) as cantidad
            FROM Libro
            WHERE anio_publicacion IS NOT NULL
            GROUP BY anio_publicacion
            ORDER BY anio_publicacion DESC
        """)
        return [{"año": row[0], "cantidad": row[1]} for row in cursor.fetchall()]
    
    def get_libros_por_mes(self):
        cursor = self.db.cursor
        cursor.execute("""
            SELECT anio_publicacion as año, COUNT(*) as cantidad
            FROM Libro
            WHERE anio_publicacion IS NOT NULL
            GROUP BY anio_publicacion
            ORDER BY anio_publicacion DESC
        """)
        meses = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun", 
                7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}
        return [{"año": row[0], "mes": 1, "mes_nom": "General", "cantidad": row[1]} for row in cursor.fetchall()]
    
    def get_libros_por_semana(self, año):
        cursor = self.db.cursor
        cursor.execute("""
            SELECT id_libro, COUNT(*) as cantidad
            FROM Libro
            WHERE anio_publicacion = ?
            GROUP BY id_libro
        """, año)
        results = cursor.fetchall()
        semana_group = []
        for i in range(0, len(results), 4):
            batch = results[i:i+4]
            semana_group.append({"semana": (i // 4) + 1, "cantidad": sum(r[1] for r in batch)})
        return semana_group if semana_group else [{"semana": 1, "cantidad": 0}]
    
    def get_libros_por_fecha(self, año, mes):
        cursor = self.db.cursor
        cursor.execute("""
            SELECT TOP 30 id_libro, titulo FROM Libro
            WHERE anio_publicacion = ?
            ORDER BY id_libro DESC
        """, año)
        results = cursor.fetchall()
        return [{"fecha": f"Libro {row[0]}", "cantidad": 1} for row in results]
    
    # ================================
    # NUEVOS MÉTODOS: Préstamos por período
    # ================================
    def get_prestamos_por_dia(self, fecha=None):
        """Obtiene préstamos por día actual o fecha especificada"""
        if fecha is None:
            fecha = datetime.now().date()
        
        cursor = self.db.cursor
        cursor.execute("""
            SELECT CAST(fecha_prestamo AS DATE) as fecha,
                   COUNT(*) as cantidad
            FROM Prestamos
            WHERE CAST(fecha_prestamo AS DATE) = ?
            GROUP BY CAST(fecha_prestamo AS DATE)
        """, (fecha,))
        
        results = cursor.fetchall()
        return [{"fecha": row[0], "cantidad": row[1]} for row in results]
    
    def get_prestamos_por_semana_reporte(self, semana=None, año=None):
        """Obtiene préstamos por semana del año actual o especificado"""
        if año is None:
            año = datetime.now().year
        
        if semana is None:
            # Calcular semana actual
            hoy = datetime.now().date()
            semana = hoy.isocalendar()[1]
        
        cursor = self.db.cursor
        cursor.execute("""
            SELECT DATEPART(week, fecha_prestamo) as semana,
                   CAST(fecha_prestamo AS DATE) as fecha,
                   COUNT(*) as cantidad
            FROM Prestamos
            WHERE YEAR(fecha_prestamo) = ? AND DATEPART(week, fecha_prestamo) = ?
            GROUP BY DATEPART(week, fecha_prestamo), CAST(fecha_prestamo AS DATE)
            ORDER BY CAST(fecha_prestamo AS DATE)
        """, (año, semana))
        
        results = cursor.fetchall()
        return [{"semana": row[0], "fecha": row[1], "cantidad": row[2]} for row in results]
    
    def get_prestamos_semanas_del_año(self, año=None):
        """Obtiene todos los préstamos agrupados por semana del año"""
        if año is None:
            año = datetime.now().year
        
        cursor = self.db.cursor
        cursor.execute("""
            SELECT DATEPART(week, fecha_prestamo) as semana,
                   COUNT(*) as cantidad
            FROM Prestamos
            WHERE YEAR(fecha_prestamo) = ?
            GROUP BY DATEPART(week, fecha_prestamo)
            ORDER BY DATEPART(week, fecha_prestamo)
        """, (año,))
        
        results = cursor.fetchall()
        return [{"semana": row[0], "cantidad": row[1]} for row in results]
    
    def get_prestamos_por_mes_reporte(self, año=None):
        """Obtiene préstamos por mes del año actual o especificado"""
        if año is None:
            año = datetime.now().year
        
        cursor = self.db.cursor
        cursor.execute("""
            SELECT MONTH(fecha_prestamo) as mes,
                   COUNT(*) as cantidad
            FROM Prestamos
            WHERE YEAR(fecha_prestamo) = ?
            GROUP BY MONTH(fecha_prestamo)
            ORDER BY MONTH(fecha_prestamo)
        """, (año,))
        
        results = cursor.fetchall()
        meses_dict = {1:"Ene", 2:"Feb", 3:"Mar", 4:"Abr", 5:"May", 6:"Jun", 
                     7:"Jul", 8:"Ago", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dic"}
        return [{"mes": row[0], "mes_nombre": meses_dict.get(row[0], ""), "cantidad": row[1]} for row in results]
    
    def get_dias_del_mes(self, año=None, mes=None):
        """Obtiene préstamos por día del mes especificado"""
        if año is None:
            año = datetime.now().year
        if mes is None:
            mes = datetime.now().month
        
        cursor = self.db.cursor
        cursor.execute("""
            SELECT DAY(fecha_prestamo) as dia,
                   CAST(fecha_prestamo AS DATE) as fecha,
                   COUNT(*) as cantidad
            FROM Prestamos
            WHERE YEAR(fecha_prestamo) = ? AND MONTH(fecha_prestamo) = ?
            GROUP BY DAY(fecha_prestamo), CAST(fecha_prestamo AS DATE)
            ORDER BY DAY(fecha_prestamo)
        """, (año, mes))
        
        results = cursor.fetchall()
        return [{"dia": row[0], "fecha": row[1], "cantidad": row[2]} for row in results]
    
    def get_años_con_prestamos(self):
        """Obtiene todos los años que tienen préstamos registrados"""
        cursor = self.db.cursor
        cursor.execute("""
            SELECT DISTINCT YEAR(fecha_prestamo) as año
            FROM Prestamos
            WHERE fecha_prestamo IS NOT NULL
            ORDER BY YEAR(fecha_prestamo) DESC
        """)
        return [row[0] for row in cursor.fetchall()]
    
    def get_libros_filtrados(self, filtro_tipo, filtro_valor):
        cursor = self.db.cursor
        
        if filtro_tipo == "año":
            cursor.execute("""
                SELECT id_libro, titulo, isbn, anio_publicacion, tipo, descripcion, id_categoria
                FROM Libro
                WHERE anio_publicacion = ?
            """, filtro_valor)
        
        elif filtro_tipo == "mes":
            año, mes = filtro_valor
            cursor.execute("""
                SELECT id_libro, titulo, isbn, anio_publicacion, tipo, descripcion, id_categoria
                FROM Libro
                WHERE anio_publicacion = ?
            """, año)
        
        elif filtro_tipo == "semana":
            año, semana = filtro_valor
            cursor.execute("""
                SELECT id_libro, titulo, isbn, anio_publicacion, tipo, descripcion, id_categoria
                FROM Libro
                WHERE anio_publicacion = ?
            """, año)
        

        elif filtro_tipo == "fecha":
            cursor.execute("""
                SELECT id_libro, titulo, isbn, anio_publicacion, tipo, descripcion, id_categoria
                FROM Libro
                WHERE anio_publicacion = ?
            """, filtro_valor)
        
        cols = [desc[0] for desc in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]
    
    def exportar_excel(self, filtro_tipo, filtro_valor):
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            
            libros = self.get_libros_filtrados(filtro_tipo, filtro_valor)
            
            wb = Workbook()
            ws = wb.active
            ws.title = "Libros"
            
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=11)
            border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                           top=Side(style='thin'), bottom=Side(style='thin'))
            
            headers = ["ID", "Título", "ISBN", "Año", "Tipo", "Descripción"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col)
                cell.value = header
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = border
            
            for row_idx, libro in enumerate(libros, 2):
                ws.cell(row=row_idx, column=1).value = libro.get('id_libro', '')
                ws.cell(row=row_idx, column=2).value = libro.get('titulo', '')
                ws.cell(row=row_idx, column=3).value = libro.get('isbn', '')
                ws.cell(row=row_idx, column=4).value = libro.get('anio_publicacion', '')
                ws.cell(row=row_idx, column=5).value = libro.get('tipo', '')
                ws.cell(row=row_idx, column=6).value = libro.get('descripcion', '')
            
            ws.column_dimensions['A'].width = 8
            ws.column_dimensions['B'].width = 30
            ws.column_dimensions['C'].width = 15
            ws.column_dimensions['D'].width = 8
            ws.column_dimensions['E'].width = 12
            ws.column_dimensions['F'].width = 30
            
            descargas = os.path.expanduser("~\\Downloads")
            os.makedirs(descargas, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"estadisticas_{filtro_tipo}_{timestamp}.xlsx"
            filepath = os.path.join(descargas, filename)
            
            wb.save(filepath)
            return filepath
        except Exception as e:
            raise Exception(f"Error al exportar: {str(e)}")
