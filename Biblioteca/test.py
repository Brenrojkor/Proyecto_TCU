from model.database import Database

db = Database()
libros = db.get_libros()
for libro in libros:
    print(libro)

