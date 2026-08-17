from src.modelos.cliente import Cliente
from src.persistencia.conexion_bd import ConexionBD
from src.servicios.gestor_seguridad import GestorSeguridad


class ClienteDAO:

    def guardar(self, cliente):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                contrasenia_hash = GestorSeguridad.generar_hash(
                    cliente.contrasenia_hash
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
                        id_usuario,
                        nombre,
                        apellido,
                        correo_electronico,
                        edad,
                        fecha_registro,
                        peso,
                        altura,
                        objetivo,
                        fecha_ingreso
                    FROM vw_clientes_completo
                    WHERE id_usuario = %s
                """

                cursor.execute(consulta, (id_usuario,))
                fila = cursor.fetchone()

                if fila is None:
                    return None

                return Cliente(
                    id_usuario=fila[0],
                    nombre=fila[1],
                    apellido=fila[2],
                    correo_electronico=fila[3],
                    contrasenia_hash=None,
                    edad=fila[4],
                    fecha_registro=fila[5],
                    peso=fila[6],
                    altura=fila[7],
                    objetivo=fila[8],
                    fecha_ingreso=fila[9],
                )

        finally:
            conexion.close()

    def listar(self):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id_usuario,
                        nombre,
                        apellido,
                        correo_electronico,
                        edad,
                        fecha_registro,
                        peso,
                        altura,
                        objetivo,
                        fecha_ingreso
                    FROM vw_clientes_completo
                    ORDER BY id_usuario
                    """
                )

                filas = cursor.fetchall()

                return [
                    Cliente(
                        id_usuario=fila[0],
                        nombre=fila[1],
                        apellido=fila[2],
                        correo_electronico=fila[3],
                        contrasenia_hash=None,
                        edad=fila[4],
                        fecha_registro=fila[5],
                        peso=fila[6],
                        altura=fila[7],
                        objetivo=fila[8],
                        fecha_ingreso=fila[9],
                    )
                    for fila in filas
                ]

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

            conexion.commit()

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()