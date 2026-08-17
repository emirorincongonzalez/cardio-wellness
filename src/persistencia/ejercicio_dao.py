from src.modelos.ejercicio_cardio import EjercicioCardio
from src.persistencia.conexion_bd import ConexionBD


class EjercicioDAO:

    def guardar(self, ejercicio):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                consulta = """
                    INSERT INTO ejercicios (
                        nombre,
                        descripcion,
                        tipo,
                        duracion_minutos,
                        intensidad,
                        calorias_estimadas,
                        creado_por
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_ejercicio
                """

                cursor.execute(
                    consulta,
                    (
                        ejercicio.nombre,
                        ejercicio.descripcion,
                        ejercicio.tipo,
                        ejercicio.duracion_minutos,
                        ejercicio.intensidad,
                        ejercicio.calorias_estimadas,
                        ejercicio.creado_por,
                    ),
                )

                ejercicio.id_ejercicio = cursor.fetchone()[0]

            conexion.commit()
            return ejercicio

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    def listar_ejercicios(self):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id_ejercicio,
                        nombre,
                        descripcion,
                        tipo,
                        duracion_minutos,
                        intensidad,
                        calorias_estimadas,
                        creado_por
                    FROM ejercicios
                    ORDER BY id_ejercicio
                    """
                )

                filas = cursor.fetchall()

                return [
                    EjercicioCardio(
                        id_ejercicio=fila[0],
                        nombre=fila[1],
                        descripcion=fila[2],
                        tipo=fila[3],
                        duracion_minutos=fila[4],
                        intensidad=fila[5],
                        calorias_estimadas=fila[6],
                        creado_por=fila[7],
                    )
                    for fila in filas
                ]

        finally:
            conexion.close()

    def eliminar_por_id(self, id_ejercicio):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM ejercicios
                    WHERE id_ejercicio = %s
                    """,
                    (id_ejercicio,),
                )

            conexion.commit()

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()