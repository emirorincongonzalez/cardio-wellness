from psycopg2 import IntegrityError

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
                        ejercicio.intensidad.value,
                        ejercicio.calorias_estimadas,
                        ejercicio.creado_por,
                    ),
                )

                resultado = cursor.fetchone()
                ejercicio.id_ejercicio = resultado[0]

            conexion.commit()
            return ejercicio

        except IntegrityError as error:
            conexion.rollback()

            if error.pgcode == "23503":
                raise ValueError(
                    "El creador del ejercicio no existe."
                ) from error

            raise ValueError(
                "No se pudo guardar el ejercicio por una "
                "restricción de integridad."
            ) from error

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    def buscar_por_id(self, id_ejercicio):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                consulta = """
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
                    WHERE id_ejercicio = %s
                """

                cursor.execute(consulta, (id_ejercicio,))
                fila = cursor.fetchone()

                if fila is None:
                    return None

                return self._crear_ejercicio_desde_fila(fila)

        finally:
            conexion.close()

    def listar(self):
        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                consulta = """
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

                cursor.execute(consulta)
                filas = cursor.fetchall()

                return [
                    self._crear_ejercicio_desde_fila(fila)
                    for fila in filas
                ]

        finally:
            conexion.close()

    def listar_ejercicios(self):
        return self.listar()

    def actualizar(self, ejercicio):
        if ejercicio.id_ejercicio is None:
            raise ValueError(
                "El ejercicio debe tener un id para actualizarse."
            )

        conexion = ConexionBD.obtener_conexion()

        try:
            with conexion.cursor() as cursor:
                consulta = """
                    UPDATE ejercicios
                    SET nombre = %s,
                        descripcion = %s,
                        tipo = %s,
                        duracion_minutos = %s,
                        intensidad = %s,
                        calorias_estimadas = %s,
                        creado_por = %s
                    WHERE id_ejercicio = %s
                """

                cursor.execute(
                    consulta,
                    (
                        ejercicio.nombre,
                        ejercicio.descripcion,
                        ejercicio.tipo,
                        ejercicio.duracion_minutos,
                        ejercicio.intensidad.value,
                        ejercicio.calorias_estimadas,
                        ejercicio.creado_por,
                        ejercicio.id_ejercicio,
                    ),
                )

                if cursor.rowcount == 0:
                    raise ValueError(
                        "No se encontró el ejercicio."
                    )

            conexion.commit()
            return ejercicio

        except IntegrityError as error:
            conexion.rollback()

            if error.pgcode == "23503":
                raise ValueError(
                    "El creador del ejercicio no existe."
                ) from error

            raise ValueError(
                "No se pudo actualizar el ejercicio por una "
                "restricción de integridad."
            ) from error

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()

    @staticmethod
    def _crear_ejercicio_desde_fila(fila):
        return EjercicioCardio(
            id_ejercicio=fila[0],
            nombre=fila[1],
            descripcion=fila[2],
            tipo=fila[3],
            duracion_minutos=fila[4],
            intensidad=fila[5],
            calorias_estimadas=fila[6],
            creado_por=fila[7],
        )

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

                eliminado = cursor.rowcount > 0

            conexion.commit()
            return eliminado

        except IntegrityError as error:
            conexion.rollback()

            if error.pgcode == "23503":
                raise ValueError(
                    "No se puede eliminar el ejercicio porque "
                    "está asociado a una rutina."
                ) from error

            raise ValueError(
                "No se puede eliminar el ejercicio por una "
                "restricción de integridad."
            ) from error

        except Exception:
            conexion.rollback()
            raise

        finally:
            conexion.close()