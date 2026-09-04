from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple

from psycopg2 import IntegrityError

from src.modelos.progreso_mensual import ProgresoMensual
from src.persistencia.conexion_bd import ConexionBD


class ProgresoMensualDAO:
    """
    Data Access Object para la entidad ProgresoMensual.
    Gestiona la persistencia del progreso mensual de los clientes.
    """

    def __init__(self) -> None:
        """Inicializa el DAO con la conexión Singleton."""
        self._bd = ConexionBD.obtener_instancia()

    def guardar(self, progreso: ProgresoMensual) -> ProgresoMensual:
        """
        Guarda un nuevo registro de progreso mensual en la base de datos.
        Retorna el progreso con el ID generado.
        """
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                # Asegurar que mes sea el primer día del mes
                mes = progreso.mes.replace(day=1)

                sql = """
                    INSERT INTO progreso_mensual (
                        id_cliente,
                        mes,
                        peso,
                        sesiones_completadas,
                        sesiones_planificadas,
                        porcentaje_cumplimiento
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_progreso
                """
                cursor.execute(
                    sql,
                    (
                        progreso.id_cliente,
                        mes,
                        progreso.peso,
                        progreso.sesiones_completadas,
                        progreso.sesiones_planificadas,
                        progreso.porcentaje_cumplimiento,
                    ),
                )
                progreso.id_progreso = cursor.fetchone()[0]
                progreso.mes = mes  # Actualizar el objeto con el mes normalizado

            self._bd._conexion.commit()
            return progreso

        except IntegrityError as error:
            self._bd._conexion.rollback()
            if error.pgcode == "23503":
                raise ValueError("El cliente referenciado no existe.") from error
            if error.pgcode == "23505":
                raise ValueError("Ya existe un registro de progreso para este cliente y mes.") from error
            raise ValueError("No se pudo guardar el progreso por una restricción de integridad.") from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def buscar_por_id(self, id_progreso: int) -> Optional[ProgresoMensual]:
        """Busca un registro de progreso por su ID."""
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                sql = """
                    SELECT
                        id_progreso,
                        id_cliente,
                        mes,
                        peso,
                        sesiones_completadas,
                        sesiones_planificadas,
                        porcentaje_cumplimiento
                    FROM progreso_mensual
                    WHERE id_progreso = %s
                """
                cursor.execute(sql, (id_progreso,))
                fila = cursor.fetchone()
                if fila is None:
                    return None
                return self._crear_progreso_desde_fila(fila)
        except Exception:
            raise

    def buscar_por_cliente(self, id_cliente: int) -> List[ProgresoMensual]:
        """
        Lista todo el historial de progreso de un cliente,
        ordenado por mes descendente.
        """
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                sql = """
                    SELECT
                        id_progreso,
                        id_cliente,
                        mes,
                        peso,
                        sesiones_completadas,
                        sesiones_planificadas,
                        porcentaje_cumplimiento
                    FROM progreso_mensual
                    WHERE id_cliente = %s
                    ORDER BY mes DESC, id_progreso DESC
                """
                cursor.execute(sql, (id_cliente,))
                filas = cursor.fetchall()
                return [self._crear_progreso_desde_fila(fila) for fila in filas]
        except Exception:
            raise

    # Alias para mantener compatibilidad con posibles controladores
    def listar_por_cliente(self, id_cliente: int) -> List[ProgresoMensual]:
        """Alias de buscar_por_cliente."""
        return self.buscar_por_cliente(id_cliente)

    def actualizar(self, progreso: ProgresoMensual) -> ProgresoMensual:
        """
        Actualiza un registro de progreso existente.
        Requiere que el progreso tenga un ID.
        """
        if progreso.id_progreso is None:
            raise ValueError("El progreso debe tener un ID para actualizarse.")

        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                mes = progreso.mes.replace(day=1)

                sql = """
                    UPDATE progreso_mensual
                    SET mes = %s,
                        peso = %s,
                        sesiones_completadas = %s,
                        sesiones_planificadas = %s,
                        porcentaje_cumplimiento = %s
                    WHERE id_progreso = %s
                """
                cursor.execute(
                    sql,
                    (
                        mes,
                        progreso.peso,
                        progreso.sesiones_completadas,
                        progreso.sesiones_planificadas,
                        progreso.porcentaje_cumplimiento,
                        progreso.id_progreso,
                    ),
                )
                if cursor.rowcount == 0:
                    raise ValueError("No se encontró el registro de progreso.")

            self._bd._conexion.commit()
            progreso.mes = mes
            return progreso

        except IntegrityError as error:
            self._bd._conexion.rollback()
            if error.pgcode == "23505":
                raise ValueError("Ya existe un registro para este cliente y mes.") from error
            raise ValueError("No se pudo actualizar el progreso por una restricción de integridad.") from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def eliminar_por_id(self, id_progreso: int) -> bool:
        """
        Elimina un registro de progreso por su ID.
        Retorna True si se eliminó, False si no existía.
        """
        self._bd.abrir_conexion()
        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM progreso_mensual
                    WHERE id_progreso = %s
                    """,
                    (id_progreso,),
                )
                eliminado = cursor.rowcount > 0

            self._bd._conexion.commit()
            return eliminado

        except Exception:
            self._bd._conexion.rollback()
            raise

    @staticmethod
    def _crear_progreso_desde_fila(fila: Tuple) -> ProgresoMensual:
        """Crea un objeto ProgresoMensual desde una fila de la BD."""
        return ProgresoMensual(
            id_progreso=fila[0],
            id_cliente=fila[1],
            mes=fila[2],
            peso=fila[3],
            sesiones_completadas=fila[4],
            sesiones_planificadas=fila[5],
            porcentaje_cumplimiento=fila[6],
        )