"""
DAO para la persistencia del progreso mensual.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional


from psycopg2 import IntegrityError
from psycopg2.extras import RealDictCursor


from src.modelos.progreso_mensual import ProgresoMensual
from src.persistencia.conexion_bd import ConexionBD


class ProgresoMensualDAO:
    """
    Data Access Object de ProgresoMensual.
    """

    def __init__(self) -> None:
        self._bd = ConexionBD.obtener_instancia()

    def guardar(
        self,
        progreso: ProgresoMensual,
    ) -> ProgresoMensual:
        """
        Inserta o actualiza el progreso del cliente para el mes.
        """
        self._validar_progreso(progreso)

        mes = self._normalizar_mes(
            progreso.mes
        )

        sesiones_completadas = int(
            progreso.sesiones_completadas or 0
        )

        sesiones_planificadas = int(
            progreso.sesiones_planificadas or 0
        )

        porcentaje = self._calcular_porcentaje(
            sesiones_completadas,
            sesiones_planificadas,
        )

        peso = Decimal(
            str(progreso.peso)
        ).quantize(
            Decimal("0.01")
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:
                cursor.execute(
                    """
                    SELECT id_progreso
                    FROM progreso_mensual
                    WHERE id_cliente = %s
                      AND mes = %s
                    LIMIT 1
                    """,
                    (
                        progreso.id_cliente,
                        mes,
                    ),
                )

                existente = cursor.fetchone()

                if existente is None:
                    cursor.execute(
                        """
                        INSERT INTO progreso_mensual (
                            id_cliente,
                            mes,
                            peso,
                            sesiones_completadas,
                            sesiones_planificadas,
                            porcentaje_cumplimiento
                        )
                        VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        )
                        RETURNING
                            id_progreso,
                            id_cliente,
                            mes,
                            peso,
                            sesiones_completadas,
                            sesiones_planificadas,
                            porcentaje_cumplimiento
                        """,
                        (
                            progreso.id_cliente,
                            mes,
                            peso,
                            sesiones_completadas,
                            sesiones_planificadas,
                            porcentaje,
                        ),
                    )

                else:
                    cursor.execute(
                        """
                        UPDATE progreso_mensual
                        SET
                            peso = %s,
                            sesiones_completadas = %s,
                            sesiones_planificadas = %s,
                            porcentaje_cumplimiento = %s
                        WHERE id_progreso = %s
                        RETURNING
                            id_progreso,
                            id_cliente,
                            mes,
                            peso,
                            sesiones_completadas,
                            sesiones_planificadas,
                            porcentaje_cumplimiento
                        """,
                        (
                            peso,
                            sesiones_completadas,
                            sesiones_planificadas,
                            porcentaje,
                            existente["id_progreso"],
                        ),
                    )

                fila = cursor.fetchone()

            if fila is None:
                raise RuntimeError(
                    "No se pudo recuperar el progreso guardado."
                )

            self._bd._conexion.commit()

            return self._crear_progreso_desde_fila(fila)

        except IntegrityError as error:
            self._bd._conexion.rollback()

            if error.pgcode == "23503":
                raise ValueError(
                    "El cliente referenciado no existe."
                ) from error

            raise ValueError(
                "No se pudo guardar el progreso mensual."
            ) from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def buscar_por_id(
        self,
        id_progreso: int,
    ) -> Optional[ProgresoMensual]:
        """
        Busca progreso por ID.
        """
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:
                cursor.execute(
                    """
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
                    """,
                    (id_progreso,),
                )

                fila = cursor.fetchone()

            if fila is None:
                return None

            return self._crear_progreso_desde_fila(fila)

        except Exception:
            raise

    def buscar_por_cliente(
        self,
        id_cliente: int,
    ) -> List[ProgresoMensual]:
        """
        Lista el historial de progreso de un cliente.
        """
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:
                cursor.execute(
                    """
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
                    """,
                    (id_cliente,),
                )

                filas = cursor.fetchall()

            return [
                self._crear_progreso_desde_fila(fila)
                for fila in filas
            ]

        except Exception:
            raise

    def listar_por_cliente(
        self,
        id_cliente: int,
    ) -> List[ProgresoMensual]:
        """
        Alias de buscar_por_cliente.
        """
        return self.buscar_por_cliente(id_cliente)

    def actualizar(
        self,
        progreso: ProgresoMensual,
    ) -> ProgresoMensual:
        """
        Actualiza un progreso existente por ID.
        """
        if progreso.id_progreso is None:
            raise ValueError(
                "El progreso debe tener un ID."
            )

        self._validar_progreso(progreso)

        mes = self._normalizar_mes(
            progreso.mes
        )

        sesiones_completadas = int(
            progreso.sesiones_completadas or 0
        )

        sesiones_planificadas = int(
            progreso.sesiones_planificadas or 0
        )

        porcentaje = self._calcular_porcentaje(
            sesiones_completadas,
            sesiones_planificadas,
        )

        peso = Decimal(
            str(progreso.peso)
        ).quantize(
            Decimal("0.01")
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:
                cursor.execute(
                    """
                    UPDATE progreso_mensual
                    SET
                        id_cliente = %s,
                        mes = %s,
                        peso = %s,
                        sesiones_completadas = %s,
                        sesiones_planificadas = %s,
                        porcentaje_cumplimiento = %s
                    WHERE id_progreso = %s
                    RETURNING
                        id_progreso,
                        id_cliente,
                        mes,
                        peso,
                        sesiones_completadas,
                        sesiones_planificadas,
                        porcentaje_cumplimiento
                    """,
                    (
                        progreso.id_cliente,
                        mes,
                        peso,
                        sesiones_completadas,
                        sesiones_planificadas,
                        porcentaje,
                        progreso.id_progreso,
                    ),
                )

                fila = cursor.fetchone()

            if fila is None:
                raise ValueError(
                    "No se encontró el progreso."
                )

            self._bd._conexion.commit()

            return self._crear_progreso_desde_fila(fila)

        except Exception:
            self._bd._conexion.rollback()
            raise

    def eliminar_por_id(
        self,
        id_progreso: int,
    ) -> bool:
        """
        Elimina un progreso por ID.
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
    def _crear_progreso_desde_fila(
        fila,
    ) -> ProgresoMensual:
        """
        Convierte una fila de PostgreSQL a ProgresoMensual.
        """
        if not hasattr(fila, "keys"):
            raise TypeError(
                "La fila de progreso debe ser tipo diccionario."
            )

        datos = dict(fila)

        return ProgresoMensual(
            id_progreso=datos["id_progreso"],
            id_cliente=datos["id_cliente"],
            mes=datos["mes"],
            peso=datos["peso"],
            sesiones_completadas=(
                datos["sesiones_completadas"]
            ),
            sesiones_planificadas=(
                datos["sesiones_planificadas"]
            ),
            porcentaje_cumplimiento=(
                datos["porcentaje_cumplimiento"]
            ),
        )

    @staticmethod
    def _normalizar_mes(
        valor,
    ) -> date:
        """
        Normaliza una fecha al primer día del mes.
        """
        if isinstance(valor, datetime):
            valor = valor.date()

        if not isinstance(valor, date):
            raise ValueError(
                "El mes debe ser una fecha válida."
            )

        return valor.replace(day=1)

    @staticmethod
    def _calcular_porcentaje(
        sesiones_completadas: int,
        sesiones_planificadas: int,
    ) -> Decimal:
        """
        Calcula el porcentaje y lo limita a 100.
        """
        if sesiones_planificadas <= 0:
            return Decimal("0.00")

        porcentaje = (
            Decimal(sesiones_completadas)
            / Decimal(sesiones_planificadas)
            * Decimal("100")
        )

        if porcentaje > Decimal("100"):
            porcentaje = Decimal("100")

        return porcentaje.quantize(
            Decimal("0.01")
        )

    @staticmethod
    def _validar_progreso(
        progreso: ProgresoMensual,
    ) -> None:
        """
        Valida los datos antes de guardar.
        """
        if progreso.id_cliente is None:
            raise ValueError(
                "El progreso debe tener un cliente."
            )

        if int(progreso.id_cliente) <= 0:
            raise ValueError(
                "El ID del cliente debe ser positivo."
            )

        if progreso.mes is None:
            raise ValueError(
                "El progreso debe tener un mes."
            )

        if progreso.peso is None:
            raise ValueError(
                "El progreso debe tener un peso."
            )

        peso = Decimal(
            str(progreso.peso)
        )

        if peso <= Decimal("0"):
            raise ValueError(
                "El peso debe ser mayor que cero."
            )

        if peso >= Decimal("1000"):
            raise ValueError(
                "El peso supera el máximo permitido "
                "por NUMERIC(5,2)."
            )