from datetime import date
from typing import List, Optional, Tuple

from psycopg2 import IntegrityError

from src.modelos.asignacion_rutina import AsignacionRutina
from src.modelos.enums import EstadoAsignacion
from src.persistencia.conexion_bd import ConexionBD


class AsignacionRutinaDAO:
    """
    Data Access Object para la entidad AsignacionRutina.
    Gestiona la persistencia de asignaciones de rutinas a clientes.
    """

    def __init__(self) -> None:
        """Inicializa el DAO con la conexión Singleton."""
        self._bd = ConexionBD.obtener_instancia()

    def guardar(self, asignacion: AsignacionRutina) -> AsignacionRutina:
        """
        Guarda una nueva asignación de rutina en la base de datos.
        Retorna la asignación con el ID generado.
        """
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                sql = """
                    INSERT INTO asignaciones_rutina (
                        id_cliente,
                        id_rutina,
                        fecha_asignacion,
                        estado,
                        observaciones
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id_asignacion
                """
                cursor.execute(
                    sql,
                    (
                        asignacion.id_cliente,
                        asignacion.id_rutina,
                        asignacion.fecha_asignacion,
                        asignacion.estado.value,
                        asignacion.observaciones,
                    ),
                )
                asignacion.id_asignacion = cursor.fetchone()[0]

            self._bd._conexion.commit()
            return asignacion

        except IntegrityError as error:
            self._bd._conexion.rollback()
            if error.pgcode == "23503":
                raise ValueError("El cliente o la rutina no existen.") from error
            if error.pgcode == "23505":
                raise ValueError("Ya existe una asignación activa para este cliente.") from error
            raise ValueError("No se pudo guardar la asignación por una restricción de integridad.") from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def buscar_por_id(self, id_asignacion: int) -> Optional[AsignacionRutina]:
        """Busca una asignación por su ID."""
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                sql = """
                    SELECT
                        id_asignacion,
                        id_cliente,
                        id_rutina,
                        fecha_asignacion,
                        fecha_finalizacion,
                        estado,
                        observaciones
                    FROM asignaciones_rutina
                    WHERE id_asignacion = %s
                """
                cursor.execute(sql, (id_asignacion,))
                fila = cursor.fetchone()
                if fila is None:
                    return None
                return self._crear_asignacion_desde_fila(fila)
        except Exception:
            raise

    def buscar_activa(self, id_cliente: int) -> Optional[AsignacionRutina]:
        """
        Busca la asignación activa de un cliente.
        Retorna la asignación o None si no tiene ninguna activa.
        """
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                sql = """
                    SELECT
                        id_asignacion,
                        id_cliente,
                        id_rutina,
                        fecha_asignacion,
                        fecha_finalizacion,
                        estado,
                        observaciones
                    FROM asignaciones_rutina
                    WHERE id_cliente = %s
                      AND estado = 'ACTIVA'
                    ORDER BY fecha_asignacion DESC
                    LIMIT 1
                """
                cursor.execute(sql, (id_cliente,))
                fila = cursor.fetchone()
                if fila is None:
                    return None
                return self._crear_asignacion_desde_fila(fila)
        except Exception:
            raise

    def listar_por_cliente(self, id_cliente: int) -> List[AsignacionRutina]:
        """
        Lista todo el historial de asignaciones de un cliente.
        """
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                sql = """
                    SELECT
                        id_asignacion,
                        id_cliente,
                        id_rutina,
                        fecha_asignacion,
                        fecha_finalizacion,
                        estado,
                        observaciones
                    FROM asignaciones_rutina
                    WHERE id_cliente = %s
                    ORDER BY fecha_asignacion DESC
                """
                cursor.execute(sql, (id_cliente,))
                filas = cursor.fetchall()
                return [self._crear_asignacion_desde_fila(fila) for fila in filas]
        except Exception:
            raise

    def actualizar(self, asignacion: AsignacionRutina) -> AsignacionRutina:
        """
        Actualiza una asignación existente (ej. cambiar estado, fecha_finalizacion).
        Requiere que la asignación tenga un ID.
        """
        if asignacion.id_asignacion is None:
            raise ValueError("La asignación debe tener un ID para actualizarse.")

        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                sql = """
                    UPDATE asignaciones_rutina
                    SET fecha_finalizacion = %s,
                        estado = %s,
                        observaciones = %s
                    WHERE id_asignacion = %s
                """
                cursor.execute(
                    sql,
                    (
                        asignacion.fecha_finalizacion,
                        asignacion.estado.value,
                        asignacion.observaciones,
                        asignacion.id_asignacion,
                    ),
                )
                if cursor.rowcount == 0:
                    raise ValueError("No se encontró la asignación.")

            self._bd._conexion.commit()
            return asignacion

        except Exception:
            self._bd._conexion.rollback()
            raise

    def eliminar_por_id(self, id_asignacion: int) -> bool:
        """
        Elimina una asignación por su ID (solo para casos excepcionales).
        Retorna True si se eliminó, False si no existía.
        """
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM asignaciones_rutina
                    WHERE id_asignacion = %s
                    """,
                    (id_asignacion,),
                )
                eliminado = cursor.rowcount > 0

            self._bd._conexion.commit()
            return eliminado

        except Exception:
            self._bd._conexion.rollback()
            raise

    @staticmethod
    def _crear_asignacion_desde_fila(fila: Tuple) -> AsignacionRutina:
        """Crea un objeto AsignacionRutina desde una fila de la BD."""
        return AsignacionRutina(
            id_asignacion=fila[0],
            id_cliente=fila[1],
            id_rutina=fila[2],
            fecha_asignacion=fila[3],
            fecha_finalizacion=fila[4],
            estado=EstadoAsignacion(fila[5]),
            observaciones=fila[6] or "",
        )