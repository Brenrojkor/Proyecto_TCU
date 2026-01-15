import pyodbc

class Database:
    def __init__(self):
        self.server = 'bibliotecati.database.windows.net'
        self.database = 'Biblioteca'
        self.username = 'Dbadmin'
        self.password = 'Biblioteca12'
        self.driver = '{ODBC Driver 18 for SQL Server}'

        self.conn = pyodbc.connect(
            f'DRIVER={self.driver};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            f'Encrypt=yes;'
        )
        self.cursor = self.conn.cursor()

    def get_libros(self):
        self.cursor.execute("EXEC sp_VerLibros")
        columnas = [col[0] for col in self.cursor.description]
        return [dict(zip(columnas, fila)) for fila in self.cursor.fetchall()]

    def get_categorias(self):
        self.cursor.execute("EXEC sp_VerCategorias")
        columnas = [col[0] for col in self.cursor.description]
        return [dict(zip(columnas, fila)) for fila in self.cursor.fetchall()]
      
    def get_autores(self):
        self.cursor.execute("EXEC sp_VerAutores")
        columnas = [col[0] for col in self.cursor.description]
        return [dict(zip(columnas, fila)) for fila in self.cursor.fetchall()]
    
    def get_usuarios(self):
        self.cursor.execute("EXEC sp_VerUsuarios")
        columnas = [col[0] for col in self.cursor.description]
        return [dict(zip(columnas, fila)) for fila in self.cursor.fetchall()]

    def set_categorias(self, nombre, descripcion):
        self.cursor.execute(
            "EXEC sp_CrearCategoria @nombre = ?, @descripcion = ?",
            (nombre, descripcion if descripcion else None)
        )
        self.conn.commit()
    
    def set_autores(self, nombre, apellido, nacionalidad):
        self.cursor.execute(
            "EXEC sp_CrearAutor @nombre = ?, @apellido = ?, @nacionalidad = ?",
            (nombre, apellido if apellido else None, nacionalidad if nacionalidad else None)
        )
        self.conn.commit()

    def update_categoria(self, id_categoria, nombre, descripcion):
        self.cursor.execute(
            "EXEC sp_EditarCategoria @id_categoria = ?, @nombre = ?, @descripcion = ?",
            (id_categoria, nombre, descripcion if descripcion else None)
        )
        self.conn.commit()
        
    def update_autor(self, id_autor, nombre, apellido, nacionalidad):
        self.cursor.execute(
            "EXEC sp_EditarAutor @id_autor = ?, @nombre = ?, @apellido = ?, @nacionalidad = ?",
            (id_autor, nombre, apellido if apellido else None, nacionalidad if nacionalidad else None)
        )
        self.conn.commit()

    def get_ubicaciones(self):
        self.cursor.execute("EXEC dbo.sp_VerUbicaciones")
        columnas = [col[0] for col in self.cursor.description]
        return [dict(zip(columnas, fila)) for fila in self.cursor.fetchall()]
    

    def crear_ubicacion(self, sala, pasillo=None, estanteria=None, nivel=None, descripcion=None):
        self.cursor.execute(
        "EXEC dbo.sp_CrearUbicacion @sala=?, @pasillo=?, @estanteria=?, @nivel=?, @descripcion=?",
        (sala, pasillo, estanteria, nivel, descripcion)
    )
        self.conn.commit()


    def crear_libro(self, titulo, isbn, anio_publicacion, edicion, tipo, descripcion, id_categoria,
                   activo=1, autores_ids_csv=None, id_ubicacion=None):
        """
        Ejecuta el stored procedure sp_CrearLibro.
        Solo maneja base de datos, sin UI.
        """
        param_str = "@titulo = ?, @isbn = ?, @anio_publicacion = ?, @edicion = ?, @tipo = ?, @descripcion = ?, @id_categoria = ?, @activo = ?, @autores_ids_csv = ?, @id_ubicacion = ?"

        values = [
            titulo,
            isbn if isbn else None,
            anio_publicacion if anio_publicacion else None,
            edicion if edicion else None,
            tipo,
            descripcion if descripcion else None,
            id_categoria,
            activo,
            autores_ids_csv if autores_ids_csv else None,
            id_ubicacion if id_ubicacion else None,
        ]

        self.cursor.execute(f"EXEC sp_CrearLibro {param_str}", values)
        self.conn.commit()

    # =========================
    #   PDFs (DIGITAL)
    # =========================
    def upsert_libro_pdf(self, id_libro: int, nombre_archivo: str, contenido: bytes):
        cur = self.conn.cursor()
        cur.execute(
            "EXEC dbo.sp_UpsertLibroPDF @id_libro = ?, @nombre_archivo = ?, @contenido = ?, @content_type = ?",
            (id_libro, nombre_archivo, pyodbc.Binary(contenido), "application/pdf"),
        )

        # ✅ Limpia resultsets pendientes (evita que el siguiente SP devuelva mal)
        try:
            while cur.nextset():
                pass
        except Exception:
            pass

        self.conn.commit()
        cur.close()

    def get_libro_pdf(self, id_libro: int):
        cur = self.conn.cursor()
        cur.execute("EXEC dbo.sp_GetLibroPDF @id_libro = ?", (id_libro,))
        row = cur.fetchone()
        cur.close()

        if not row:
            return None

        return {
            "nombre_archivo": row[0],
            "contenido": row[1],
            "content_type": row[2],
            "fecha_subida": row[3],
        }

    def has_libro_pdf(self, id_libro: int) -> bool:
        cur = self.conn.cursor()
        cur.execute("EXEC dbo.sp_HasLibroPDF @id_libro = ?", (id_libro,))
        row = cur.fetchone()
        cur.close()
        return bool(row[0]) if row else False
