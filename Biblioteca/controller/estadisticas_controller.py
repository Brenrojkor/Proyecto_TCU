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
