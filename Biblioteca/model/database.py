import pyodbc

class Database:
    def __init__(self):
        self.server = 'bibliotecati.database.windows.net'
        self.database = 'Biblioteca'
        self.username = 'Dbadmin'
        self.password = 'Biblioteca12'  
        self.driver = '{ODBC Driver 18 for SQL Server}'

        #Conexión a Azure SQL
        self.conn = pyodbc.connect(
            f'DRIVER={self.driver};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            f'Encrypt=yes;'
        )
        self.cursor = self.conn.cursor()
    
    #Esto solo está llamando al procedimiento almacenado la lógica real para visualizar los libros viene de ese procedimiento en la BD
    def get_libros(self):
        self.cursor.execute("EXEC sp_VerLibros")
        columnas = [col[0] for col in self.cursor.description] 
        resultados = []
        for fila in self.cursor.fetchall():
            resultados.append(dict(zip(columnas, fila)))
        return resultados

