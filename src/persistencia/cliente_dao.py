from psycopg2 import IntegrityError

from src.modelos.cliente import Cliente
from src.persistencia.conexion_bd import ConexionBD
from src.servicios.gestor_seguridad import GestorSeguridad


class ClienteDAO:

    def guardar(self, cliente):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                contrasenia_hash = (
                    GestorSeguridad.generar_hash(
                        cliente.contrasenia_hash
                    )
                )

                consulta_usuario = """
                    INSERT INTO usuarios (
                        nombre,
                        apellido,
                        correo_electronico,
                        "contraseña_hash",
                        edad,
                        tipo_usuario
                    )
                    VALUES (%s, %s, %s, %s, %s, 'cliente')
                    RETURNING id_usuario, fecha_registro
                """

                cursor.execute(
                    consulta_usuario,
                    (
                        cliente.nombre,
                        cliente.apellido,
                        cliente.correo_electronico,
                        contrasenia_hash,
                        cliente.edad,
                    ),
                )

                usuario_resultado = cursor.fetchone()

                cliente.id_usuario = usuario_resultado[0]
                cliente.fecha_registro = usuario_resultado[1]

                consulta_cliente = """
                    INSERT INTO clientes (
                        id_usuario,
                        peso,
                        altura,
                        objetivo
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING fecha_ingreso
                """

                cursor.execute(
                    consulta_cliente,
                    (
                        cliente.id_usuario,
                        cliente.peso,
                        cliente.altura,
                        cliente.objetivo,
                    ),
                )

                cliente.fecha_ingreso = cursor.fetchone()[0]

            conexion.commit()
            return cliente

        except IntegrityError as error:
            conexion.rollback()

            if error.pgcode == "23505":
                raise ValueError(
                    "El correo ya está registrado."
                ) from error

            raise

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    def buscar_por_id(self, id_usuario):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                consulta = """
                    SELECT
                        u.id_usuario,
                        u.nombre,
                        u.apellido,
                        u.correo_electronico,
                        u."contraseña_hash",
                        u.edad,
                        u.tipo_usuario,
                        u.fecha_registro,
                        c.peso,
                        c.altura,
                        c.objetivo,
                        c.fecha_ingreso
                    FROM usuarios u
                    JOIN clientes c
                        ON u.id_usuario = c.id_usuario
                    WHERE u.id_usuario = %s
                      AND u.tipo_usuario = 'cliente'
                """

                cursor.execute(consulta, (id_usuario,))
                fila = cursor.fetchone()

                if fila is None:
                    return None

                return self._crear_cliente_desde_fila(fila)

        finally:
            conexion.close()

    def buscar_por_correo(self, correo):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                consulta = """
                    SELECT
                        u.id_usuario,
                        u.nombre,
                        u.apellido,
                        u.correo_electronico,
                        u."contraseña_hash",
                        u.edad,
                        u.tipo_usuario,
                        u.fecha_registro,
                        c.peso,
                        c.altura,
                        c.objetivo,
                        c.fecha_ingreso
                    FROM usuarios u
                    JOIN clientes c
                        ON u.id_usuario = c.id_usuario
                    WHERE u.correo_electronico = %s
                      AND u.tipo_usuario = 'cliente'
                """

                cursor.execute(consulta, (correo,))
                fila = cursor.fetchone()

                if fila is None:
                    return None

                return self._crear_cliente_desde_fila(fila)

        finally:
            conexion.close()

    def listar(self):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                consulta = """
                    SELECT
                        u.id_usuario,
                        u.nombre,
                        u.apellido,
                        u.correo_electronico,
                        u."contraseña_hash",
                        u.edad,
                        u.tipo_usuario,
                        u.fecha_registro,
                        c.peso,
                        c.altura,
                        c.objetivo,
                        c.fecha_ingreso
                    FROM usuarios u
                    JOIN clientes c
                        ON u.id_usuario = c.id_usuario
                    WHERE u.tipo_usuario = 'cliente'
                    ORDER BY u.id_usuario
                """

                cursor.execute(consulta)
                filas = cursor.fetchall()

                return [
                    self._crear_cliente_desde_fila(fila)
                    for fila in filas
                ]

        finally:
            conexion.close()

    def actualizar(self, cliente):
        if cliente.id_usuario is None:
            raise ValueError(
                "El cliente debe tener un id para actualizarse."
            )

        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                consulta_usuario = """
                    UPDATE usuarios
                    SET nombre = %s,
                        apellido = %s,
                        correo_electronico = %s,
                        edad = %s
                    WHERE id_usuario = %s
                      AND tipo_usuario = 'cliente'
                """

                cursor.execute(
                    consulta_usuario,
                    (
                        cliente.nombre,
                        cliente.apellido,
                        cliente.correo_electronico,
                        cliente.edad,
                        cliente.id_usuario,
                    ),
                )

                if cursor.rowcount == 0:
                    raise ValueError(
                        "No se encontró el cliente."
                    )

                consulta_cliente = """
                    UPDATE clientes
                    SET peso = %s,
                        altura = %s,
                        objetivo = %s
                    WHERE id_usuario = %s
                """

                cursor.execute(
                    consulta_cliente,
                    (
                        cliente.peso,
                        cliente.altura,
                        cliente.objetivo,
                        cliente.id_usuario,
                    ),
                )

                if cursor.rowcount == 0:
                    raise ValueError(
                        "No se encontraron los datos del cliente."
                    )

            conexion.commit()
            return cliente

        except IntegrityError as error:
            conexion.rollback()

            if error.pgcode == "23505":
                raise ValueError(
                    "El correo ya está registrado."
                ) from error

            raise

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    def actualizar_contrasenia(
        self,
        id_usuario,
        contrasenia_actual,
        nueva_contrasenia,
    ):
        if not nueva_contrasenia:
            raise ValueError(
                "La nueva contraseña no puede estar vacía."
            )

        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT "contraseña_hash"
                    FROM usuarios
                    WHERE id_usuario = %s
                      AND tipo_usuario = 'cliente'
                    """,
                    (id_usuario,),
                )

                fila = cursor.fetchone()

                if fila is None:
                    return False

                hash_guardado = fila[0]

                contrasenia_valida = (
                    GestorSeguridad.verificar_contrasenia(
                        contrasenia_actual,
                        hash_guardado,
                    )
                )

                if not contrasenia_valida:
                    return False

                nuevo_hash = GestorSeguridad.generar_hash(
                    nueva_contrasenia
                )

                cursor.execute(
                    """
                    UPDATE usuarios
                    SET "contraseña_hash" = %s
                    WHERE id_usuario = %s
                    """,
                    (nuevo_hash, id_usuario),
                )

            conexion.commit()
            return True

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    @staticmethod
    def _crear_cliente_desde_fila(fila):
        return Cliente(
            id_usuario=fila[0],
            nombre=fila[1],
            apellido=fila[2],
            correo_electronico=fila[3],
            contrasenia_hash=fila[4],
            edad=fila[5],
            fecha_registro=fila[7],
            peso=fila[8],
            altura=fila[9],
            objetivo=fila[10],
            fecha_ingreso=fila[11],
        )

    def eliminar_por_id(self, id_usuario):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM usuarios
                    WHERE id_usuario = %s
                    """,
                    (id_usuario,),
                )

            conexion.commit()

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()