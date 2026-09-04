from datetime import date
from typing import List, Optional, Tuple

from psycopg2 import IntegrityError

from src.modelos.enums import Intensidad
from src.modelos.sesion_entrenamiento import SesionEntrenamiento
from src.persistencia.conexion_bd import ConexionBD


class SesionEntrenamientoDAO:
    """
    Data Access Object para la entidad SesionEntrenamiento.
    Gestiona la persistencia de sesiones de entrenamiento.
    """

    def __init__(self) -> None:
        """Inicializa el DAO con la conexión Singleton."""
        self._bd = ConexionBD.obtener_instancia()

    def guardar(self, sesion: SesionEntrenamiento) -> SesionEntrenamiento:
        """
        Guarda una nueva sesión de entrenamiento en la base de datos.
        Retorna la sesión con el ID generado.
        """
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                sql = """
                    INSERT INTO sesiones_entrenamiento (
                        id_cliente,
                        fecha,
                        duracion_real,
                        intensidad_real,
                        calorias_quemadas,
                        observaciones,
                        completada
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_sesion
                """
                cursor.execute(
                    sql,
                    (
                        sesion.id_cliente,
                        sesion.fecha,
                        sesion.duracion_real,
                        sesion.intensidad_real.value,
                        sesion.calorias_quemadas,
                        sesion.observaciones,
                        sesion.completada,
                    ),
                )
                sesion.id_sesion = cursor.fetchone()[0]

            self._bd._conexion.commit()
            return sesion

        except IntegrityError as error:
            self._bd._conexion.rollback()
            if error.pgcode == "23503":
                raise ValueError("El cliente referenciado no existe.") from error
            raise ValueError("No se pudo guardar la sesión por una restricción de integridad.") from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def buscar_por_id(self, id_sesion: int) -> Optional[SesionEntrenamiento]:
        """Busca una sesión por su ID."""
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                sql = """
                    SELECT
                        id_sesion,
                        id_cliente,
                        fecha,
                        duracion_real,
                        intensidad_real,
                        calorias_quemadas,
                        observaciones,
                        completada
                    FROM sesiones_entrenamiento
                    WHERE id_sesion = %s
                """
                cursor.execute(sql, (id_sesion,))
                fila = cursor.fetchone()
                if fila is None:
                    return None
                return self._crear_sesion_desde_fila(fila)
        except Exception:
            raise

    def listar_por_cliente(self, id_cliente: int) -> List[SesionEntrenamiento]:
        """
        Lista todas las sesiones de un cliente, ordenadas por fecha descendente.
        """
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                sql = """
                    SELECT
                        id_sesion,
                        id_cliente,
                        fecha,
                        duracion_real,
                        intensidad_real,
                        calorias_quemadas,
                        observaciones,
                        completada
                    FROM sesiones_entrenamiento
                    WHERE id_cliente = %s
                    ORDER BY fecha DESC, id_sesion DESC
                """
                cursor.execute(sql, (id_cliente,))
                filas = cursor.fetchall()
                return [self._crear_sesion_desde_fila(fila) for fila in filas]
        except Exception:
            raise

    def actualizar(self, sesion: SesionEntrenamiento) -> SesionEntrenamiento:
        """
        Actualiza los datos de una sesión existente.
        Requiere que la sesión tenga un ID.
        """
        if sesion.id_sesion is None:
            raise ValueError("La sesión debe tener un ID para actualizarse.")

        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                sql = """
                    UPDATE sesiones_entrenamiento
                    SET fecha = %s,
                        duracion_real = %s,
                        intensidad_real = %s,
                        calorias_quemadas = %s,
                        observaciones = %s,
                        completada = %s
                    WHERE id_sesion = %s
                """
                cursor.execute(
                    sql,
                    (
                        sesion.fecha,
                        sesion.duracion_real,
                        sesion.intensidad_real.value,
                        sesion.calorias_quemadas,
                        sesion.observaciones,
                        sesion.completada,
                        sesion.id_sesion,
                    ),
                )
                if cursor.rowcount == 0:
                    raise ValueError("No se encontró la sesión.")

            self._bd._conexion.commit()
            return sesion

        except Exception:
            self._bd._conexion.rollback()
            raise

    def eliminar_por_id(self, id_sesion: int) -> bool:
        """
        Elimina una sesión por su ID.
        Retorna True si se eliminó, False si no existía.
        """
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM sesiones_entrenamiento
                    WHERE id_sesion = %s
                    """,
                    (id_sesion,),
                )
                eliminado = cursor.rowcount > 0

            self._bd._conexion.commit()
            return eliminado

        except Exception:
            self._bd._conexion.rollback()
            raise

    @staticmethod
    def _crear_sesion_desde_fila(fila: Tuple) -> SesionEntrenamiento:
        """Crea un objeto SesionEntrenamiento desde una fila de la BD."""
        return SesionEntrenamiento(
            id_sesion=fila[0],
            id_cliente=fila[1],
            fecha=fila[2],
            duracion_real=fila[3],
            intensidad_real=Intensidad(fila[4]),
            calorias_quemadas=fila[5],
            observaciones=fila[6] or "",
            completada=fila[7],
        )