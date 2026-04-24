import pyodbc


class Database:
    def __init__(self):
        self.server = 'bibliotecati0.database.windows.net'
        self.database = 'Biblioteca'
        self.username = 'Dbadmin'
        self.password = 'Biblioteca12'
        self.driver = '{ODBC Driver 18 for SQL Server}'

        # Conexión a la base de datos
        self.conn = pyodbc.connect(
            f'DRIVER={self.driver};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            f'Encrypt=yes;'
        )

        # Cursor para ejecutar consultas
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

    def get_solicitudes(self):
        self.cursor.execute("EXEC sp_VerSolicitudes")
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
        
    def set_solicitud(self, descripcion, autor, activo):
        self.cursor.execute(
            "EXEC sp_CrearSolicitud @descripcion = ?, @autor = ?, @activo = ?",
            (
                descripcion if descripcion else None,
                autor if autor else None,
                activo
            )
        )
        self.conn.commit()
        
    def set_usuarios(self, nombre_completo, identificacion, discapacidad,
                    provincia, canton, distrito, rango_edad,
                    sexo, curso, anio, grupo, telefono, activo, comentario):
        """Crea un usuario nuevo."""
        try:
            self.cursor.execute(
                "EXEC sp_CrearUsuario @nombre_completo = ?, @identificacion = ?, @discapacidad = ?, @provincia = ?, @canton = ?, @distrito = ?, @rango_edad = ?, @sexo = ?, @curso = ?, @anio = ?, @grupo = ?, @telefono = ?, @activo = ?, @comentario = ?",
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
                    telefono if telefono else None,
                    activo,
                    comentario if comentario else None,
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
            "EXEC sp_ActualizarUsuario @id_usuario = ?, @nombre_completo = ?, @identificacion = ?, @discapacidad = ?, @provincia = ?, @canton = ?, @distrito = ?, @rango_edad = ?, @sexo = ?, @curso = ?, @anio = ?, @grupo = ?, @telefono = ?, @activo = ?, @comentario = ?",
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
        
    def update_solicitud(self, id_solicitud, descripcion, autor, activo):
        self.cursor.execute(
            "EXEC sp_ActualizarSolicitud @id_solicitud = ?, @descripcion = ?, @autor = ?, @activo = ?",
            (
                id_solicitud,
                descripcion if descripcion else None,
                autor if autor else None,
                activo
            )
        )
        self.conn.commit()

    def eliminar_solicitud(self, id_solicitud: int):
        self.cursor.execute(
            "EXEC sp_EliminarSolicitud @id_solicitud = ?",
            (int(id_solicitud),)
        )
        self.conn.commit()
        
    def eliminar_categoria(self, id_categoria: int):
        self.cursor.execute(
            "EXEC sp_EliminarCategoria @id_categoria = ?",
            (int(id_categoria),)
        )
        self.conn.commit()
        
    def eliminar_autor(self, id_autor: int):
        self.cursor.execute(
            "EXEC sp_EliminarAutor @id_autor = ?",
            (int(id_autor),)
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
            "EXEC sp_ActualizarCategoria @id_categoria = ?, @nombre = ?, @descripcion = ?",
            (id_categoria, nombre, descripcion if descripcion else None)
        )
        self.conn.commit()

    def update_autor(self, id_autor, nombre_completo, nacionalidad):
        self.cursor.execute(
            "EXEC sp_ActualizarAutor @id_autor = ?, @nombre_completo = ?, @nacionalidad = ?",
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
        
        self.cursor.execute(
            "EXEC sp_CrearLibro @titulo = ?, @isbn = ?, @anio_publicacion = ?, @edicion = ?, @tipo = ?, @descripcion = ?, @id_categoria = ?, @activo = ?, @autores_ids_csv = ?, @clasificacion_dui = ?, @codigo_barras = ?",
            (
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
            )
        )
        self.conn.commit()
        print("[DB] Libro creado y guardado exitosamente")


    # =========================
    #   PDFs (DIGITAL)
    # =========================
    def upsert_libro_pdf(self, id_libro: int, nombre_archivo: str, contenido: bytes):
        self.cursor.execute(
            "EXEC sp_UpsertLibroPDF @id_libro = ?, @nombre_archivo = ?, @contenido = ?",
            (id_libro, nombre_archivo, contenido)
        )
        self.conn.commit()

    def get_libro_pdf(self, id_libro: int):
        self.cursor.execute("EXEC sp_GetLibroPDF @id_libro = ?", (id_libro,))
        row = self.cursor.fetchone()

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
        cur.execute("SELECT 1 FROM libros_pdf WHERE id_libro = %s LIMIT 1", (id_libro,))
        row = cur.fetchone()
        cur.close()
        return bool(row)

    # =========================
    # LIBROS - Detalles y Desactivar
    # =========================
    def get_libro_detalle(self, id_libro: int):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM libros WHERE id_libro = %s", (id_libro,))
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
    codigo_barras=None,   
):
         self.cursor.execute(
             "EXEC sp_ActualizarLibro @id_libro = ?, @titulo = ?, @isbn = ?, @anio_publicacion = ?, @edicion = ?, @tipo = ?, @descripcion = ?, @id_categoria = ?, @autores_ids_csv = ?, @clasificacion_dui = ?, @codigo_barras = ?",
             (
                 id_libro,
                 titulo,
                 isbn if isbn else None,
                 anio_publicacion,
                 edicion if edicion else None,
                 tipo,
                 descripcion if descripcion else None,
                 id_categoria,
                 autores_ids_csv,
                 clasificacion_dui,
                 codigo_barras
             )
         )
         self.conn.commit()

    def get_autores_libro(self, id_libro: int):
        try:
            self.cursor.execute("EXEC sp_GetAutoresLibro @id_libro = ?", (id_libro,))
            row = self.cursor.fetchone()
            
            if row and row[0]:
                return row[0]
            return ""
        except Exception:
            return ""

    # =========================
    # Toggle Activo/Inactivo
    # =========================
    def set_libro_activo(self, id_libro: int, activo: int):
        self.cursor.execute(
            "EXEC sp_SetLibroActivo @id_libro = ?, @activo = ?",
            (id_libro, int(activo))
        )
        self.conn.commit()
        
        
    def set_usuario_activo(self, id_usuario: int, activo: int):
        self.cursor.execute(
            "EXEC sp_SetUsuarioActivo @id_usuario = ?, @activo = ?",
            (id_usuario, int(activo))
        )
        self.conn.commit()

    # =========================
    # CONTACTOS
    # =========================
    def get_contactos(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM contactos")
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
            "EXEC sp_EliminarContacto @id_contacto = ?",
            (int(id_contacto),)
        )
        self.conn.commit()
    # =========================
    # NOTIFICACIONES - Reservas próximas a vencer
    # =========================
    def get_reservas_proximas_vencer(self, dias_anticipacion: int = 3):
        """Obtiene las reservas que están próximas a su fecha de devolución"""
        self.cursor.execute("EXEC sp_GetReservasProximasVencer @dias_anticipacion = ?", (dias_anticipacion,))
        
        columnas = [col[0] for col in self.cursor.description]
        data = [dict(zip(columnas, fila)) for fila in self.cursor.fetchall()]
        return data

    def actualizar_fecha_devolucion(self, id_reserva: int, nueva_fecha: str):
        """Actualiza la fecha de devolución de una reserva"""
        self.cursor.execute(
            "EXEC sp_ActualizarFechaDevolucion @id_reserva = ?, @nueva_fecha = ?",
            (id_reserva, nueva_fecha)
        )
        self.conn.commit()

    def get_reservas_vencidas(self):
        """Obtiene las reservas que ya pasaron su fecha de devolución"""
        cur = self.conn.cursor()
        try:
            cur.execute("""
                SELECT 
                    r.id_prestamo as id_reserva,
                    l.titulo as libro_titulo,
                    u.identificacion as cedula_usuario,
                    r.fecha_prestamo,
                    r.fecha_devolucion_esperada as fecha_devolucion,
                    r.estado,
                    (CURRENT_DATE - r.fecha_devolucion_esperada::date) as dias_vencidos
                WHERE r.estado IN ('PRESTADO', 'NO DEVUELTO')
                    AND r.fecha_devolucion_esperada IS NOT NULL
                    AND r.fecha_devolucion_esperada::date < CURRENT_DATE
            """)
        
        except Exception as e:
            print(f"Error en get_reservas_vencidas: {e}")
            cur.close()
            return []
        
        columnas = [col[0] for col in cur.description]
        data = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
        cur.close()
        return data

    # =========================
    # PRÉSTAMOS (RESERVAS)
    # =========================

    def get_prestamos(self):
        cur = self.conn.cursor()
        try:
            cur.execute("""
                SELECT 
                    p.id_prestamo,
                    p.id_libro,
                    l.titulo as libro_titulo,
                    u.identificacion as identificacion_usuario,
                    p.fecha_devolucion_esperada,
                    p.fecha_devolucion_real,
                    p.observaciones
            """)
            columnas = [col[0] for col in cur.description]
            data = [dict(zip(columnas, fila)) for fila in cur.fetchall()]
            cur.close()
            return data
        except Exception as ex:
            import traceback
            print(f"Error al obtener préstamos: {ex}")
            print(traceback.format_exc())
            try:
                cur.close()
            except:
                pass
            return []

    def crear_prestamo(self, id_libro, identificacion, fecha_devolucion_esperada):
        """Crea un nuevo préstamo"""
        self.cursor.execute(
            "EXEC sp_CrearPrestamo @id_libro = ?, @identificacion = ?, @fecha_devolucion_esperada = ?",
            (id_libro, identificacion, fecha_devolucion_esperada)
        )
        self.conn.commit()

    def actualizar_devolucion_prestamo(self, id_prestamo, observaciones=None):
        """Marca un préstamo como devuelto"""
        self.cursor.execute(
            "EXEC sp_ActualizarDevolucionPrestamo @id_prestamo = ?, @observaciones = ?",
            (id_prestamo, observaciones)
        )
        self.conn.commit()

    def actualizar_fecha_devolucion_esperada(self, id_prestamo: int, nueva_fecha: str):
        """Actualiza la fecha de devolución esperada de un préstamo (renovación)."""
        self.cursor.execute(
            "EXEC sp_ActualizarFechaDevolucionEsperada @id_prestamo = ?, @nueva_fecha = ?",
            (id_prestamo, nueva_fecha)
        )
        self.conn.commit()

    def marcar_no_devuelto(self, id_prestamo: int, observaciones: str = None):
        """Marca explícitamente un préstamo como NO DEVUELTO."""
        self.cursor.execute(
            "EXEC sp_MarcarNoDevuelto @id_prestamo = ?, @observaciones = ?",
            (id_prestamo, observaciones)
        )
        self.conn.commit()

    def get_historial_prestamos_usuario(self, identificacion):
        """Obtiene el historial de préstamos de un usuario por identificación"""
        self.cursor.execute("EXEC sp_GetHistorialPrestamosUsuario @identificacion = ?", (identificacion,))
        columnas = [col[0] for col in self.cursor.description]
        data = [dict(zip(columnas, fila)) for fila in self.cursor.fetchall()]
        return data
    # =========================
    # NOTIFICACIONES - Préstamos
    # =========================
    def get_prestamos_proximos_vencer(self, dias_anticipacion: int = 3):
        """"Obtiene los préstamos próximos a vencer en los próximos 'dias_anticipacion' días."""
        self.cursor.execute("EXEC sp_GetPrestamosProximosVencer @dias = ?", (dias_anticipacion,))
        columnas = [col[0] for col in self.cursor.description]
        data = [dict(zip(columnas, fila)) for fila in self.cursor.fetchall()]
        return data

    def get_prestamos_vencidos(self):
        """"Obtiene los préstamos que ya vencieron y aún no se devolvieron."""
        self.cursor.execute("EXEC sp_GetPrestamosVencidos")
        columnas = [col[0] for col in self.cursor.description]
        data = [dict(zip(columnas, fila)) for fila in self.cursor.fetchall()]
        return data
