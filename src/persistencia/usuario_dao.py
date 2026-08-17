from src.modelos.usuario import Usuario
from src.persistencia.conexion_bd import ConexionBD
from src.servicios.gestor_seguridad import GestorSeguridad


class UsuarioDAO:

    def guardar(self, usuario):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                contrasenia_hash = GestorSeguridad.generar_hash(
                    usuario.contrasenia_hash
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

            conexion.commit()
            return usuario

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
                        id_usuario,
                        nombre,
                        apellido,
                        correo_electronico,
                        "contraseña_hash",
                        edad,
                        tipo_usuario,
                        fecha_registro
                    FROM usuarios
                    WHERE correo_electronico = %s
                """

                cursor.execute(consulta, (correo,))
                fila = cursor.fetchone()

                if fila is None:
                    return None

                return Usuario(
                    id_usuario=fila[0],
                    nombre=fila[1],
                    apellido=fila[2],
                    correo_electronico=fila[3],
                    contrasenia_hash=fila[4],
                    edad=fila[5],
                    tipo_usuario=fila[6],
                    fecha_registro=fila[7],
                )

        finally:
            conexion.close()

    def iniciar_sesion(self, correo, contrasenia):
        usuario = self.buscar_por_correo(correo)

        if usuario is None:
            return None

        contrasenia_valida = GestorSeguridad.verificar_contrasenia(
            contrasenia,
            usuario.contrasenia_hash,
        )

        if not contrasenia_valida:
            return None

        return usuario

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