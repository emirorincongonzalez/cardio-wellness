from psycopg2 import IntegrityError

from src.modelos.cliente import Cliente
from src.persistencia.conexion_bd import ConexionBD
from src.servicios.gestor_seguridad import GestorSeguridad


class UsuarioDAO:

    def guardar(self, usuario):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                contrasenia_hash = (
                    GestorSeguridad.generar_hash(
                        usuario.contrasenia_hash
                    )
                )

                consulta = """
                    INSERT INTO usuarios (
                        nombre,
                        apellido,
                        correo_electronico,
                        "contraseña_hash",
                        edad,
                        tipo_usuario
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_usuario, fecha_registro
                """

                cursor.execute(
                    consulta,
                    (
                        usuario.nombre,
                        usuario.apellido,
                        usuario.correo_electronico,
                        contrasenia_hash,
                        usuario.edad,
                        usuario.tipo_usuario,
                    ),
                )

                resultado = cursor.fetchone()

                usuario.id_usuario = resultado[0]
                usuario.fecha_registro = resultado[1]

                if isinstance(usuario, Cliente):
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
                            usuario.id_usuario,
                            usuario.peso,
                            usuario.altura,
                            usuario.objetivo,
                        ),
                    )

                    resultado_cliente = cursor.fetchone()
                    usuario.fecha_ingreso = resultado_cliente[0]

            conexion.commit()
            return usuario

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
                    LEFT JOIN clientes c
                        ON u.id_usuario = c.id_usuario
                    WHERE u.correo_electronico = %s
                """

                cursor.execute(consulta, (correo,))
                fila = cursor.fetchone()

                if fila is None:
                    return None

                tipo_usuario = fila[6].strip().lower()

                if tipo_usuario == "cliente":
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

                raise ValueError(
                    f"Tipo de usuario no soportado: {tipo_usuario}"
                )

        finally:
            conexion.close()

    def iniciar_sesion(self, correo, contrasenia):
        usuario = self.buscar_por_correo(correo)

        if usuario is None:
            return None

        contrasenia_valida = (
            GestorSeguridad.verificar_contrasenia(
                contrasenia,
                usuario.contrasenia_hash,
            )
        )

        if not contrasenia_valida:
            return None

        return usuario

    def actualizar(self, usuario):
        if usuario.id_usuario is None:
            raise ValueError(
                "El usuario debe tener un id para actualizarse."
            )

        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                consulta = """
                    UPDATE usuarios
                    SET nombre = %s,
                        apellido = %s,
                        correo_electronico = %s,
                        edad = %s,
                        tipo_usuario = %s
                    WHERE id_usuario = %s
                """

                cursor.execute(
                    consulta,
                    (
                        usuario.nombre,
                        usuario.apellido,
                        usuario.correo_electronico,
                        usuario.edad,
                        usuario.tipo_usuario,
                        usuario.id_usuario,
                    ),
                )

                if cursor.rowcount == 0:
                    raise ValueError(
                        "No se encontró el usuario."
                    )

            conexion.commit()
            return usuario

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

                eliminado = cursor.rowcount > 0

            conexion.commit()
            return eliminado

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()