from src.modelos.rutina import Rutina
from src.persistencia.conexion_bd import ConexionBD


class RutinaDAO:

    def guardar(self, rutina):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                consulta = """
                    INSERT INTO rutinas (
                        nombre,
                        descripcion,
                        objetivo,
                        nivel,
                        duracion_semanas,
                        creado_por
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_rutina, fecha_creacion
                """

                cursor.execute(
                    consulta,
                    (
                        rutina.nombre,
                        rutina.descripcion,
                        rutina.objetivo,
                        rutina.nivel,
                        rutina.duracion_semanas,
                        rutina.creado_por,
                    ),
                )

                resultado = cursor.fetchone()
                rutina.id_rutina = resultado[0]
                rutina.fecha_creacion = resultado[1]

            conexion.commit()
            return rutina

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    def buscar_por_id(self, id_rutina):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id_rutina,
                        nombre,
                        descripcion,
                        objetivo,
                        nivel,
                        duracion_semanas,
                        creado_por,
                        fecha_creacion
                    FROM rutinas
                    WHERE id_rutina = %s
                    """,
                    (id_rutina,),
                )

                fila = cursor.fetchone()

                if fila is None:
                    return None

                return Rutina(
                    id_rutina=fila[0],
                    nombre=fila[1],
                    descripcion=fila[2],
                    objetivo=fila[3],
                    nivel=fila[4],
                    duracion_semanas=fila[5],
                    creado_por=fila[6],
                    fecha_creacion=fila[7],
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
                        id_rutina,
                        nombre,
                        descripcion,
                        objetivo,
                        nivel,
                        duracion_semanas,
                        creado_por,
                        fecha_creacion
                    FROM rutinas
                    ORDER BY id_rutina
                    """
                )

                filas = cursor.fetchall()

                return [
                    Rutina(
                        id_rutina=fila[0],
                        nombre=fila[1],
                        descripcion=fila[2],
                        objetivo=fila[3],
                        nivel=fila[4],
                        duracion_semanas=fila[5],
                        creado_por=fila[6],
                        fecha_creacion=fila[7],
                    )
                    for fila in filas
                ]

        finally:
            conexion.close()

    def eliminar_por_id(self, id_rutina):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM rutinas
                    WHERE id_rutina = %s
                    """,
                    (id_rutina,),
                )

            conexion.commit()

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()