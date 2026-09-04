from typing import List, Optional, Tuple

from psycopg2 import IntegrityError

from src.modelos.ejercicio_cardio import EjercicioCardio
from src.modelos.rutina import Rutina
from src.persistencia.conexion_bd import ConexionBD


class RutinaDAO:
    """
    Data Access Object para la entidad Rutina.
    Gestiona la persistencia de rutinas y su relación con ejercicios (tabla puente).
    """

    def __init__(self) -> None:
        """Inicializa el DAO con la conexión Singleton."""
        self._bd = ConexionBD.obtener_instancia()

    def guardar(self, rutina: Rutina) -> Rutina:
        """
        Guarda una nueva rutina en la base de datos.
        Retorna la rutina con el ID y fecha de creación asignados.
        """
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
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
                        rutina.nivel.value,
                        rutina.duracion_semanas,
                        rutina.creado_por,
                    ),
                )
                resultado = cursor.fetchone()
                rutina.id_rutina = resultado[0]
                rutina.fecha_creacion = resultado[1]

            self._bd._conexion.commit()
            return rutina

        except IntegrityError as error:
            self._bd._conexion.rollback()
            if error.pgcode == "23503":
                raise ValueError("El creador de la rutina no existe.") from error
            raise ValueError("No se pudo guardar la rutina por una restricción de integridad.") from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def buscar_por_id(self, id_rutina: int) -> Optional[Rutina]:
        """
        Busca una rutina por su ID, incluyendo sus ejercicios asociados.
        """
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                consulta = """
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
                """
                cursor.execute(consulta, (id_rutina,))
                fila = cursor.fetchone()
                if fila is None:
                    return None

                rutina = self._crear_rutina_desde_fila(fila)
                rutina._ejercicios = self._obtener_ejercicios(cursor, id_rutina)
                return rutina
        except Exception:
            raise

    def listar(self) -> List[Rutina]:
        """
        Lista todas las rutinas, incluyendo sus ejercicios asociados.
        """
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                consulta = """
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
                cursor.execute(consulta)
                filas = cursor.fetchall()

                rutinas = []
                for fila in filas:
                    rutina = self._crear_rutina_desde_fila(fila)
                    rutina._ejercicios = self._obtener_ejercicios(cursor, rutina.id_rutina)
                    rutinas.append(rutina)

                return rutinas
        except Exception:
            raise

    def actualizar(self, rutina: Rutina) -> Rutina:
        """
        Actualiza los datos de una rutina existente.
        Requiere que la rutina tenga un ID.
        """
        if rutina.id_rutina is None:
            raise ValueError("La rutina debe tener un id para actualizarse.")

        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                consulta = """
                    UPDATE rutinas
                    SET nombre = %s,
                        descripcion = %s,
                        objetivo = %s,
                        nivel = %s,
                        duracion_semanas = %s,
                        creado_por = %s
                    WHERE id_rutina = %s
                """
                cursor.execute(
                    consulta,
                    (
                        rutina.nombre,
                        rutina.descripcion,
                        rutina.objetivo,
                        rutina.nivel.value,
                        rutina.duracion_semanas,
                        rutina.creado_por,
                        rutina.id_rutina,
                    ),
                )
                if cursor.rowcount == 0:
                    raise ValueError("No se encontró la rutina.")

            self._bd._conexion.commit()
            return rutina

        except IntegrityError as error:
            self._bd._conexion.rollback()
            if error.pgcode == "23503":
                raise ValueError("El creador de la rutina no existe.") from error
            raise ValueError("No se pudo actualizar la rutina por una restricción de integridad.") from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def agregar_ejercicio(
        self,
        id_rutina: int,
        id_ejercicio: int,
        orden_ejercicio: int,
    ) -> bool:
        """
        Asocia un ejercicio a una rutina con un orden específico.
        Retorna True si se agregó correctamente.
        """
        if orden_ejercicio <= 0:
            raise ValueError("El orden del ejercicio debe ser mayor que cero.")

        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                consulta = """
                    INSERT INTO rutina_ejercicios (
                        id_rutina,
                        id_ejercicio,
                        orden_ejercicio
                    )
                    VALUES (%s, %s, %s)
                """
                cursor.execute(consulta, (id_rutina, id_ejercicio, orden_ejercicio))

            self._bd._conexion.commit()
            return True

        except IntegrityError as error:
            self._bd._conexion.rollback()
            if error.pgcode == "23505":
                raise ValueError("El ejercicio ya pertenece a la rutina.") from error
            if error.pgcode == "23503":
                raise ValueError("La rutina o el ejercicio no existe.") from error
            raise ValueError("No se pudo asociar el ejercicio.") from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def eliminar_ejercicio(
        self,
        id_rutina: int,
        id_ejercicio: int,
    ) -> bool:
        """
        Elimina la asociación entre una rutina y un ejercicio.
        Retorna True si se eliminó, False si no existía.
        """
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM rutina_ejercicios
                    WHERE id_rutina = %s
                      AND id_ejercicio = %s
                    """,
                    (id_rutina, id_ejercicio),
                )
                eliminado = cursor.rowcount > 0

            self._bd._conexion.commit()
            return eliminado

        except Exception:
            self._bd._conexion.rollback()
            raise

    def listar_ejercicios(self, id_rutina: int) -> List[EjercicioCardio]:
        """
        Lista los ejercicios asociados a una rutina específica.
        """
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                return self._obtener_ejercicios(cursor, id_rutina)
        except Exception:
            raise

    def eliminar_por_id(self, id_rutina: int) -> bool:
        """
        Elimina una rutina por su ID.
        Retorna True si se eliminó, False si no existía.
        """
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM rutinas
                    WHERE id_rutina = %s
                    """,
                    (id_rutina,),
                )
                eliminado = cursor.rowcount > 0

            self._bd._conexion.commit()
            return eliminado

        except IntegrityError as error:
            self._bd._conexion.rollback()
            if error.pgcode == "23503":
                raise ValueError("No se puede eliminar la rutina porque está asignada a un cliente.") from error
            raise ValueError("No se puede eliminar la rutina por una restricción de integridad.") from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    @staticmethod
    def _crear_rutina_desde_fila(fila: Tuple) -> Rutina:
        """Crea un objeto Rutina desde una fila de la BD."""
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

    @staticmethod
    def _obtener_ejercicios(cursor, id_rutina: int) -> List[EjercicioCardio]:
        """
        Obtiene los ejercicios asociados a una rutina desde la tabla puente.
        """
        consulta = """
            SELECT
                e.id_ejercicio,
                e.nombre,
                e.descripcion,
                e.tipo,
                e.duracion_minutos,
                e.intensidad,
                e.calorias_estimadas,
                e.creado_por
            FROM ejercicios e
            INNER JOIN rutina_ejercicios re
                ON e.id_ejercicio = re.id_ejercicio
            WHERE re.id_rutina = %s
            ORDER BY re.orden_ejercicio
        """
        cursor.execute(consulta, (id_rutina,))
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