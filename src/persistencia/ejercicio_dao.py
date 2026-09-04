from typing import List, Optional, Tuple

from psycopg2 import IntegrityError

from src.modelos.ejercicio_cardio import EjercicioCardio
from src.persistencia.conexion_bd import ConexionBD


class EjercicioDAO:
    """
    Data Access Object para la entidad EjercicioCardio.
    Gestiona la persistencia de ejercicios en la base de datos.
    """

    def __init__(self) -> None:
        """Inicializa el DAO con la conexión Singleton."""
        self._bd = ConexionBD.obtener_instancia()

    def guardar(self, ejercicio: EjercicioCardio) -> EjercicioCardio:
        """
        Guarda un nuevo ejercicio en la base de datos.
        Retorna el ejercicio con el ID asignado.
        """
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
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

            self._bd._conexion.commit()
            return ejercicio

        except IntegrityError as error:
            self._bd._conexion.rollback()
            if error.pgcode == "23503":
                raise ValueError("El creador del ejercicio no existe.") from error
            raise ValueError("No se pudo guardar el ejercicio por una restricción de integridad.") from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def buscar_por_id(self, id_ejercicio: int) -> Optional[EjercicioCardio]:
        """Busca un ejercicio por su ID."""
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
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
        except Exception:
            raise

    def listar(self) -> List[EjercicioCardio]:
        """Lista todos los ejercicios."""
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
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
                return [self._crear_ejercicio_desde_fila(fila) for fila in filas]
        except Exception:
            raise

    def listar_ejercicios(self) -> List[EjercicioCardio]:
        """Alias de listar() para mantener compatibilidad con controladores."""
        return self.listar()

    def actualizar(self, ejercicio: EjercicioCardio) -> EjercicioCardio:
        """
        Actualiza los datos de un ejercicio existente.
        Requiere que el ejercicio tenga un ID.
        """
        if ejercicio.id_ejercicio is None:
            raise ValueError("El ejercicio debe tener un id para actualizarse.")

        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
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
                    raise ValueError("No se encontró el ejercicio.")

            self._bd._conexion.commit()
            return ejercicio

        except IntegrityError as error:
            self._bd._conexion.rollback()
            if error.pgcode == "23503":
                raise ValueError("El creador del ejercicio no existe.") from error
            raise ValueError("No se pudo actualizar el ejercicio por una restricción de integridad.") from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def eliminar_por_id(self, id_ejercicio: int) -> bool:
        """
        Elimina un ejercicio por su ID.
        Retorna True si se eliminó, False si no existía.
        """
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM ejercicios
                    WHERE id_ejercicio = %s
                    """,
                    (id_ejercicio,),
                )
                eliminado = cursor.rowcount > 0

            self._bd._conexion.commit()
            return eliminado

        except IntegrityError as error:
            self._bd._conexion.rollback()
            if error.pgcode == "23503":
                raise ValueError("No se puede eliminar el ejercicio porque está asociado a una rutina.") from error
            raise ValueError("No se puede eliminar el ejercicio por una restricción de integridad.") from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    @staticmethod
    def _crear_ejercicio_desde_fila(fila: Tuple) -> EjercicioCardio:
        """Método auxiliar para crear un objeto EjercicioCardio desde una fila de la BD."""
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