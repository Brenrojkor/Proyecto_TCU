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




