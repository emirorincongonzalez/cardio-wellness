from datetime import date
from typing import List, Optional

from psycopg2 import IntegrityError
from psycopg2.extras import RealDictCursor

from src.modelos.asignacion_rutina import AsignacionRutina
from src.modelos.enums import EstadoAsignacion
from src.persistencia.conexion_bd import ConexionBD


class AsignacionRutinaDAO:
    """
    DAO para la entidad AsignacionRutina.
    """

    def __init__(self) -> None:
        self._bd = ConexionBD.obtener_instancia()

    def guardar(
        self,
        asignacion: AsignacionRutina,
    ) -> AsignacionRutina:
        """
        Guarda una nueva asignación de rutina.
        """
        self._validar_asignacion(asignacion)
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:
                cursor.execute(
                    """
                    INSERT INTO asignaciones_rutina (
                        id_cliente,
                        id_rutina,
                        fecha_asignacion,
                        fecha_finalizacion,
                        estado,
                        observaciones
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING
                        id_asignacion,
                        id_cliente,
                        id_rutina,
                        fecha_asignacion,
                        fecha_finalizacion,
                        estado,
                        observaciones
                    """,
                    (
                        asignacion.id_cliente,
                        asignacion.id_rutina,
                        asignacion.fecha_asignacion,
                        asignacion.fecha_finalizacion,
                        asignacion.estado.value,
                        asignacion.observaciones,
                    ),
                )

                fila = cursor.fetchone()

            self._bd._conexion.commit()

            if fila is None:
                raise RuntimeError(
                    "No se pudo recuperar la asignación guardada."
                )

            return self._crear_asignacion_desde_fila(fila)

        except IntegrityError as error:
            self._bd._conexion.rollback()

            if error.pgcode == "23503":
                raise ValueError(
                    "El cliente o la rutina no existen."
                ) from error

            if error.pgcode == "23505":
                raise ValueError(
                    "El cliente ya tiene una asignación activa."
                ) from error

            raise ValueError(
                "No se pudo guardar la asignación por "
                "una restricción de integridad."
            ) from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def asignar(
        self,
        id_cliente: int,
        id_rutina: int,
        asignado_por: int,
        observaciones: str = "",
    ) -> dict:
        """
        Crea una asignación activa.

        El parámetro asignado_por se conserva por compatibilidad
        con el controlador. La tabla actual no tiene una columna
        asignado_por.
        """
        if not isinstance(id_cliente, int) or id_cliente <= 0:
            raise ValueError(
                "El ID del cliente debe ser positivo."
            )

        if not isinstance(id_rutina, int) or id_rutina <= 0:
            raise ValueError(
                "El ID de rutina debe ser positivo."
            )

        if not isinstance(asignado_por, int) or asignado_por <= 0:
            raise ValueError(
                "El ID del usuario asignador debe ser positivo."
            )

        asignacion = AsignacionRutina(
            id_cliente=id_cliente,
            id_rutina=id_rutina,
            fecha_asignacion=date.today(),
            fecha_finalizacion=None,
            estado=EstadoAsignacion.ACTIVA,
            observaciones=observaciones or "",
        )

        asignacion_guardada = self.guardar(asignacion)

        return {
            "id_asignacion": (
                asignacion_guardada.id_asignacion
            ),
            "id_cliente": asignacion_guardada.id_cliente,
            "id_rutina": asignacion_guardada.id_rutina,
            "fecha_asignacion": (
                asignacion_guardada.fecha_asignacion
            ),
            "fecha_finalizacion": (
                asignacion_guardada.fecha_finalizacion
            ),
            "estado": (
                asignacion_guardada.estado.value
            ),
            "observaciones": (
                asignacion_guardada.observaciones
            ),
        }

    def buscar_por_id(
        self,
        id_asignacion: int,
    ) -> Optional[AsignacionRutina]:
        """
        Busca una asignación por ID.
        """
        if not isinstance(id_asignacion, int) or id_asignacion <= 0:
            raise ValueError(
                "El ID de asignación debe ser positivo."
            )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:
                cursor.execute(
                    """
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
                    """,
                    (id_asignacion,),
                )

                fila = cursor.fetchone()

            if fila is None:
                return None

            return self._crear_asignacion_desde_fila(fila)

        except Exception:
            raise

    def buscar_activa(
        self,
        id_cliente: int,
    ) -> Optional[AsignacionRutina]:
        """
        Busca la asignación activa de un cliente.
        """
        if not isinstance(id_cliente, int) or id_cliente <= 0:
            raise ValueError(
                "El ID del cliente debe ser positivo."
            )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:
                cursor.execute(
                    """
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
                      AND estado = %s
                      AND fecha_finalizacion IS NULL
                    ORDER BY
                        fecha_asignacion DESC,
                        id_asignacion DESC
                    LIMIT 1
                    """,
                    (
                        id_cliente,
                        EstadoAsignacion.ACTIVA.value,
                    ),
                )

                fila = cursor.fetchone()

            if fila is None:
                return None

            return self._crear_asignacion_desde_fila(fila)

        except Exception:
            raise

    def obtener_activa_por_cliente(
        self,
        id_cliente: int,
    ) -> Optional[AsignacionRutina]:
        """
        Alias compatible con ControlRutinas.
        """
        return self.buscar_activa(id_cliente)

    def finalizar_asignacion(
        self,
        id_asignacion: int,
    ) -> bool:
        """
        Finaliza una asignación activa.
        """
        if not isinstance(id_asignacion, int) or id_asignacion <= 0:
            raise ValueError(
                "El ID de asignación debe ser positivo."
            )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE asignaciones_rutina
                    SET
                        estado = %s,
                        fecha_finalizacion = %s
                    WHERE id_asignacion = %s
                      AND estado = %s
                    """,
                    (
                        EstadoAsignacion.FINALIZADA.value,
                        date.today(),
                        id_asignacion,
                        EstadoAsignacion.ACTIVA.value,
                    ),
                )

                actualizado = cursor.rowcount > 0

            self._bd._conexion.commit()
            return actualizado

        except Exception:
            self._bd._conexion.rollback()
            raise

    def listar_por_cliente(
        self,
        id_cliente: int,
    ) -> List[AsignacionRutina]:
        """
        Lista el historial de asignaciones de un cliente.
        """
        if not isinstance(id_cliente, int) or id_cliente <= 0:
            raise ValueError(
                "El ID del cliente debe ser positivo."
            )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:
                cursor.execute(
                    """
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
                    ORDER BY
                        fecha_asignacion DESC,
                        id_asignacion DESC
                    """,
                    (id_cliente,),
                )

                filas = cursor.fetchall()

            return [
                self._crear_asignacion_desde_fila(fila)
                for fila in filas
            ]

        except Exception:
            raise

    def actualizar(
        self,
        asignacion: AsignacionRutina,
    ) -> AsignacionRutina:
        """
        Actualiza una asignación existente.
        """
        if asignacion.id_asignacion is None:
            raise ValueError(
                "La asignación debe tener un ID."
            )

        self._validar_asignacion(asignacion)
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:
                cursor.execute(
                    """
                    UPDATE asignaciones_rutina
                    SET
                        id_cliente = %s,
                        id_rutina = %s,
                        fecha_asignacion = %s,
                        fecha_finalizacion = %s,
                        estado = %s,
                        observaciones = %s
                    WHERE id_asignacion = %s
                    RETURNING
                        id_asignacion,
                        id_cliente,
                        id_rutina,
                        fecha_asignacion,
                        fecha_finalizacion,
                        estado,
                        observaciones
                    """,
                    (
                        asignacion.id_cliente,
                        asignacion.id_rutina,
                        asignacion.fecha_asignacion,
                        asignacion.fecha_finalizacion,
                        asignacion.estado.value,
                        asignacion.observaciones,
                        asignacion.id_asignacion,
                    ),
                )

                fila = cursor.fetchone()

            if fila is None:
                raise ValueError(
                    "No se encontró la asignación."
                )

            self._bd._conexion.commit()

            return self._crear_asignacion_desde_fila(fila)

        except IntegrityError as error:
            self._bd._conexion.rollback()

            if error.pgcode == "23505":
                raise ValueError(
                    "El cliente ya tiene otra asignación activa."
                ) from error

            raise ValueError(
                "No se pudo actualizar la asignación."
            ) from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def eliminar_por_id(
        self,
        id_asignacion: int,
    ) -> bool:
        """
        Elimina una asignación por ID.
        """
        if not isinstance(id_asignacion, int) or id_asignacion <= 0:
            raise ValueError(
                "El ID de asignación debe ser positivo."
            )

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
    def _crear_asignacion_desde_fila(
        fila,
    ) -> AsignacionRutina:
        """
        Convierte una fila de PostgreSQL a un modelo.
        """
        if isinstance(fila, dict):
            return AsignacionRutina(
                id_asignacion=fila["id_asignacion"],
                id_cliente=fila["id_cliente"],
                id_rutina=fila["id_rutina"],
                fecha_asignacion=fila["fecha_asignacion"],
                fecha_finalizacion=fila[
                    "fecha_finalizacion"
                ],
                estado=(
                    AsignacionRutinaDAO._convertir_estado(
                        fila["estado"]
                    )
                ),
                observaciones=fila["observaciones"] or "",
            )

        return AsignacionRutina(
            id_asignacion=fila[0],
            id_cliente=fila[1],
            id_rutina=fila[2],
            fecha_asignacion=fila[3],
            fecha_finalizacion=fila[4],
            estado=(
                AsignacionRutinaDAO._convertir_estado(
                    fila[5]
                )
            ),
            observaciones=fila[6] or "",
        )

    @staticmethod
    def _convertir_estado(
        valor,
    ) -> EstadoAsignacion:
        """
        Convierte el valor de PostgreSQL a EstadoAsignacion.
        """
        if isinstance(valor, EstadoAsignacion):
            return valor

        try:
            return EstadoAsignacion(valor)
        except ValueError:
            return EstadoAsignacion[str(valor).upper()]

    @staticmethod
    def _validar_asignacion(
        asignacion: AsignacionRutina,
    ) -> None:
        """
        Valida una asignación antes de guardarla.
        """
        if not isinstance(asignacion, AsignacionRutina):
            raise TypeError(
                "Debe proporcionar una instancia de "
                "AsignacionRutina."
            )

        if (
            not isinstance(asignacion.id_cliente, int)
            or asignacion.id_cliente <= 0
        ):
            raise ValueError(
                "El ID del cliente debe ser positivo."
            )

        if (
            not isinstance(asignacion.id_rutina, int)
            or asignacion.id_rutina <= 0
        ):
            raise ValueError(
                "El ID de rutina debe ser positivo."
            )

        if not isinstance(
            asignacion.estado,
            EstadoAsignacion,
        ):
            raise ValueError(
                "El estado de la asignación no es válido."
            )