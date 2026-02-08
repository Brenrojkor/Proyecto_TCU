import pyodbc


class Database:
    def __init__(self):
        self.server = 'bibliotecati0.database.windows.net'
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

    def set_autores(self, nombre_completo, nacionalidad):
        self.cursor.execute(
            "EXEC sp_CrearAutor @nombre_completo = ?, @nacionalidad = ?",
            (nombre_completo, nacionalidad if nacionalidad else None)
        )
        self.conn.commit()
        
    def set_usuarios(self, nombre_completo, identificacion, discapacidad,
                    provincia, canton, distrito, rango_edad,
                    sexo, curso, anio, grupo, telefono, activo, comentario):
        """Crea un usuario nuevo."""
        try:
            self.cursor.execute(
                """EXEC dbo.CrearUsuarioBiblioteca
                @nombre_completo = ?,
                @identificacion = ?,
                @discapacidad = ?,
                @provincia = ?,
                @canton = ?,
                @distrito = ?,
                @rango_edad = ?,
                @sexo = ?,
                @curso = ?,
                @anio = ?,
                @grupo = ?,
                @telefono = ?,
                @activo = ?,
                @comentario = ?""",
                (
                    nombre_completo,
                    identificacion,
                    discapacidad,
                    provincia,
                    canton,
                    distrito,
                    rango_edad,
                    sexo,
                    curso,
                    anio,
                    grupo,
                    telefono,
                    activo,
                    comentario,
                ),
            )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e


    def update_usuario_biblioteca(
        self,
        id_usuario,
        nombre_completo,
        identificacion,
        discapacidad,
        provincia,
        canton,
        distrito,
        rango_edad,
        sexo,
        curso,
        anio,
        grupo,
        telefono=None,
        activo=1,
        comentario=None
    ):
        self.cursor.execute(
            """
            EXEC sp_EditarUsuarioBiblioteca
                @id_usuario = ?,
                @nombre_completo = ?,
                @identificacion = ?,
                @discapacidad = ?,
                @provincia = ?,
                @canton = ?,
                @distrito = ?,
                @rango_edad = ?,
                @sexo = ?,
                @curso = ?,
                @anio = ?,
                @grupo = ?,
                @telefono = ?,
                @activo = ?,
                @comentario = ?
            """,
            (
                id_usuario,
                nombre_completo,
                identificacion,
                discapacidad,
                provincia,
                canton,
                distrito,
                rango_edad,
                sexo,
                curso,
                anio,
                grupo,
                telefono if telefono else None,
                activo,
                comentario if comentario else None
            )
        )
        self.conn.commit()
        
        
    def get_usuario_detalle(self, id_usuario: int):
        try:
            cur = self.conn.cursor()
            cur.execute(
                "EXEC dbo.sp_ObtenerDetalleUsuario @id_usuario = ?",
                (id_usuario,)
            )
            row = cur.fetchone()

            if row:
                columnas = [col[0] for col in cur.description] if cur.description else []
                cur.close()
                return dict(zip(columnas, row))

            cur.close()
        except Exception:
            pass

        # Fallback por si el SP falla
        usuarios = self.get_usuarios()
        for usuario in usuarios:
            if int(usuario.get("id_usuario", 0)) == id_usuario:
                return usuario

        return None

        

    def update_categoria(self, id_categoria, nombre, descripcion):
        self.cursor.execute(
            "EXEC sp_EditarCategoria @id_categoria = ?, @nombre = ?, @descripcion = ?",
            (id_categoria, nombre, descripcion if descripcion else None)
        )
        self.conn.commit()

    def update_autor(self, id_autor, nombre_completo, nacionalidad):
        self.cursor.execute(
            "EXEC sp_EditarAutor @id_autor = ?, @nombre_completo = ?, @nacionalidad = ?",
            (id_autor, nombre_completo, nacionalidad if nacionalidad else None)
        )
        self.conn.commit()

    def crear_libro(
        self,
        titulo,
        isbn,
        anio_publicacion,
        edicion,
        tipo,
        descripcion,
        id_categoria,
        activo=1,
        autores_ids_csv=None,
        clasificacion_dui=None,
        codigo_barras=None,
    ):
        print("[DB] crear_libro() iniciado")
        print(f"[DB] Parámetros: titulo={titulo}, tipo={tipo}, categoria={id_categoria}")
        
        sql_query = """EXEC sp_CrearLibro 
        @titulo = ?, @isbn = ?, @anio_publicacion = ?, @edicion = ?,
        @tipo = ?, @descripcion = ?, @id_categoria = ?, @activo = ?,
        @autores_ids_csv = ?, @clasificacion_dui = ?, @codigo_barras = ?"""

        values = [
            titulo,
            isbn if isbn else None,
            anio_publicacion,
            edicion if edicion else None,
            tipo,
            descripcion if descripcion else None,
            id_categoria,
            activo,
            autores_ids_csv,
            clasificacion_dui,
            codigo_barras
        ]

        print(f"[DB] SQL: {sql_query}")
        print(f"[DB] Values: {values}")
        
        self.cursor.execute(sql_query, values)
        self.conn.commit()
        print("[DB] Libro creado y guardado exitosamente")


    # =========================
    #   PDFs (DIGITAL)
    # =========================
    def upsert_libro_pdf(self, id_libro: int, nombre_archivo: str, contenido: bytes):
        cur = self.conn.cursor()
        cur.execute(
            "EXEC dbo.sp_UpsertLibroPDF @id_libro = ?, @nombre_archivo = ?, @contenido = ?, @content_type = ?",
            (id_libro, nombre_archivo, pyodbc.Binary(contenido), "application/pdf"),
        )

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

    # =========================
    # LIBROS - Detalles y Desactivar
    # =========================
    def get_libro_detalle(self, id_libro: int):
        try:
            cur = self.conn.cursor()
            cur.execute("EXEC dbo.sp_ObtenerDetalleLibro @id_libro = ?", (id_libro,))
            row = cur.fetchone()

            if row:
                columnas = [col[0] for col in cur.description] if cur.description else []
                cur.close()
                return dict(zip(columnas, row))

            cur.close()
        except Exception:
            pass

        libros = self.get_libros()
        for libro in libros:
            if int(libro.get("id_libro", 0)) == id_libro:
                return libro
        return None

    def desactivar_libro(self, id_libro: int):
        self.cursor.execute(
            "EXEC sp_DesactivarLibro @id_libro = ?",
            (id_libro,)
        )
        self.conn.commit()
        
    def desactivar_usuario(self, id_usuario: int):
        self.cursor.execute(
            "EXEC sp_DesactivarUsuario @id_usuario = ?",
            (id_usuario,)
        )
        self.conn.commit()

    def update_libro(
         self,
    id_libro,
    titulo,
    isbn,
    anio_publicacion,
    edicion,
    tipo,
    descripcion,
    id_categoria,
    autores_ids_csv=None,
    clasificacion_dui=None,
    codigo_barras=None,   # ✅ NUEVO
):
         param_str = """
        @id_libro = ?, @titulo = ?, @isbn = ?, @anio_publicacion = ?,
        @edicion = ?, @tipo = ?, @descripcion = ?, @id_categoria = ?,
        @autores_ids_csv = ?, @clasificacion_dui = ?, @codigo_barras = ?
    """

         values = [
        id_libro,
        titulo,
        isbn,
        anio_publicacion,
        edicion,
        tipo,
        descripcion,
        id_categoria,
        autores_ids_csv,
        clasificacion_dui,
        codigo_barras if codigo_barras else None,  # ✅ NUEVO
    ]

         self.cursor.execute(f"EXEC sp_EditarLibro {param_str}", values)
         self.conn.commit()

    def get_autores_libro(self, id_libro: int):
        """Obtiene los IDs de los autores de un libro específico"""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT STRING_AGG(CAST(id_autor AS VARCHAR), ',') as autores_ids
                FROM Libro_Autor
                WHERE id_libro = ?
            """, (id_libro,))
            row = cur.fetchone()
            cur.close()
            
            if row and row[0]:
                return row[0]
            return ""
        except Exception:
            return ""

    # =========================
    # Toggle Activo/Inactivo
    # =========================
    def set_libro_activo(self, id_libro: int, activo: int):
        cur = self.conn.cursor()
        cur.execute(
            "EXEC dbo.sp_SetLibroActivo @id_libro = ?, @activo = ?",
            (id_libro, int(activo))
        )

        try:
            while cur.nextset():
                pass
        except Exception:
            pass

        self.conn.commit()
        cur.close()
        
        
    def set_usuario_activo(self, id_usuario: int, activo: int):
        cur = self.conn.cursor()
        cur.execute(
            "EXEC dbo.sp_SetUsuarioActivo @id_usuario = ?, @activo = ?",
            (id_usuario, int(activo))
        )

        try:
            while cur.nextset():
                pass
        except Exception:
            pass

        self.conn.commit()
        cur.close()

    # =========================
    # CONTACTOS
    # =========================
    def get_contactos(self):
        cur = self.conn.cursor()
        cur.execute("EXEC dbo.sp_VerContactos")
        columnas = [col[0] for col in cur.description]
        data = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
        cur.close()
        return data

    def crear_contacto(self, tipo, institucion, nombre=None, correo=None, telefono=None, descripcion=None):
        self.cursor.execute(
            "EXEC dbo.sp_CrearContacto @tipo = ?, @institucion = ?, @nombre = ?, @correo = ?, @telefono = ?, @descripcion = ?",
            (
                tipo,
                institucion,
                nombre if nombre else None,
                correo if correo else None,
                telefono if telefono else None,
                descripcion if descripcion else None,
            )
        )
        self.conn.commit()

    def editar_contacto(self, id_contacto, tipo, institucion, nombre=None, correo=None, telefono=None, descripcion=None):
        cur = self.conn.cursor()
        cur.execute(
            "EXEC dbo.sp_EditarContacto @id_contacto = ?, @tipo = ?, @institucion = ?, @nombre = ?, @correo = ?, @telefono = ?, @descripcion = ?",
            (
                int(id_contacto),
                tipo,
                institucion,
                nombre if nombre else None,
                correo if correo else None,
                telefono if telefono else None,
                descripcion if descripcion else None,
            )
        )
        self.conn.commit()
        cur.close()

    def eliminar_contacto(self, id_contacto: int):
        self.cursor.execute(
            "EXEC dbo.sp_EliminarContacto @id_contacto = ?",
            (int(id_contacto),)
        )
        self.conn.commit()

    # =========================
    # NOTIFICACIONES - Reservas próximas a vencer
    # =========================
    def get_reservas_proximas_vencer(self, dias_anticipacion: int = 3):
        """Obtiene las reservas que están próximas a su fecha de devolución"""
        cur = self.conn.cursor()
        try:
            # Intentar usar un stored procedure si existe
            cur.execute(
                "EXEC dbo.sp_ObtenerReservasProximasVencer @dias = ?",
                (dias_anticipacion,)
            )
        except Exception:
            # Si no existe el SP, usar query directa
            cur.execute("""
                SELECT 
                    r.id_reserva,
                    l.titulo as libro_titulo,
                    u.cedula as cedula_usuario,
                    u.nombre as nombre_usuario,
                    r.fecha_prestamo,
                    r.fecha_devolucion,
                    r.estado,
                    DATEDIFF(day, GETDATE(), r.fecha_devolucion) as dias_restantes
                FROM Reservas r
                INNER JOIN Libros l ON r.id_libro = l.id_libro
                INNER JOIN Usuarios u ON r.id_usuario = u.id_usuario
                WHERE r.estado = 'PRESTADO'
                    AND r.fecha_devolucion IS NOT NULL
                    AND DATEDIFF(day, GETDATE(), r.fecha_devolucion) <= ?
                    AND DATEDIFF(day, GETDATE(), r.fecha_devolucion) >= 0
                ORDER BY r.fecha_devolucion ASC
            """, (dias_anticipacion,))
        
        columnas = [col[0] for col in cur.description]
        data = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
        cur.close()
        return data

    def actualizar_fecha_devolucion(self, id_reserva: int, nueva_fecha: str):
        """Actualiza la fecha de devolución de una reserva"""
        cur = self.conn.cursor()
        try:
            # Intentar usar un stored procedure si existe
            cur.execute(
                "EXEC dbo.sp_ActualizarFechaDevolucion @id_reserva = ?, @nueva_fecha = ?",
                (id_reserva, nueva_fecha)
            )
        except Exception:
            # Si no existe el SP, usar query directa
            cur.execute("""
                UPDATE Reservas 
                SET fecha_devolucion = ? 
                WHERE id_reserva = ?
            """, (nueva_fecha, id_reserva))
        
        self.conn.commit()
        cur.close()

    def get_reservas_vencidas(self):
        """Obtiene las reservas que ya pasaron su fecha de devolución"""
        cur = self.conn.cursor()
        try:
            cur.execute("EXEC dbo.sp_ObtenerReservasVencidas")
        except Exception:
            cur.execute("""
                SELECT 
                    r.id_reserva,
                    l.titulo as libro_titulo,
                    u.cedula as cedula_usuario,
                    u.nombre as nombre_usuario,
                    r.fecha_prestamo,
                    r.fecha_devolucion,
                    r.estado,
                    DATEDIFF(day, r.fecha_devolucion, GETDATE()) as dias_vencidos
                FROM Reservas r
                INNER JOIN Libros l ON r.id_libro = l.id_libro
                INNER JOIN Usuarios u ON r.id_usuario = u.id_usuario
                WHERE r.estado IN ('PRESTADO', 'NO DEVUELTO')
                    AND r.fecha_devolucion IS NOT NULL
                    AND r.fecha_devolucion < CAST(GETDATE() AS DATE)
                ORDER BY r.fecha_devolucion ASC
            """)
        
        columnas = [col[0] for col in cur.description]
        data = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
        cur.close()
        return data