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

    def set_categorias(self, nombre, descripcion):
        self.cursor.execute(
            "EXEC sp_CrearCategoria @nombre = ?, @descripcion = ?",
            (nombre, descripcion if descripcion else None)
        )
        self.conn.commit()

    def update_categoria(self, id_categoria, nombre, descripcion):
        self.cursor.execute(
            "EXEC sp_EditarCategoria @id_categoria = ?, @nombre = ?, @descripcion = ?",
            (id_categoria, nombre, descripcion if descripcion else None)
        )
        self.conn.commit()

    def get_ubicaciones(self):
        self.cursor.execute("EXEC dbo.sp_VerUbicaciones")
        columnas = [col[0] for col in self.cursor.description]
        return [dict(zip(columnas, fila)) for fila in self.cursor.fetchall()]


    def crear_libro(self, titulo, isbn, anio_publicacion, edicion, tipo, descripcion, id_categoria, activo=1, autores_ids_csv=None,id_ubicacion=None):
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






