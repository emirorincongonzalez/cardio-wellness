from typing import List, Optional, Tuple

from psycopg2 import IntegrityError

from src.modelos.ejercicio_cardio import (
    EjercicioCardio,
)
from src.persistencia.conexion_bd import (
    ConexionBD,
)


class EjercicioDAO:
    """
    Data Access Object para la entidad EjercicioCardio.
    """

    def __init__(self) -> None:
        self._bd = (
            ConexionBD.obtener_instancia()
        )

    def guardar(
        self,
        ejercicio: EjercicioCardio,
    ) -> EjercicioCardio:
        """
        Guarda un ejercicio nuevo.
        """
        self._validar_ejercicio(ejercicio)

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
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
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

                resultado = (
                    cursor.fetchone()
                )

                if resultado is None:
                    raise RuntimeError(
                        "No se pudo obtener el ID "
                        "del ejercicio creado."
                    )

                ejercicio.id_ejercicio = (
                    resultado[0]
                )

            self._bd._conexion.commit()

            return ejercicio

        except IntegrityError as error:
            self._bd._conexion.rollback()

            if error.pgcode == "23503":
                raise ValueError(
                    "El creador del ejercicio "
                    "no existe."
                ) from error

            raise ValueError(
                "No se pudo guardar el ejercicio "
                "por una restricción de integridad."
            ) from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def buscar_por_id(
        self,
        id_ejercicio: int,
    ) -> Optional[EjercicioCardio]:
        """
        Busca un ejercicio por su ID.
        """
        self._validar_id(id_ejercicio)

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

                cursor.execute(
                    consulta,
                    (id_ejercicio,),
                )

                fila = cursor.fetchone()

                if fila is None:
                    return None

                return (
                    self._crear_ejercicio_desde_fila(
                        fila
                    )
                )

        except Exception:
            raise

    def listar(self) -> List[EjercicioCardio]:
        """
        Lista todos los ejercicios.
        """
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

            return [
                self._crear_ejercicio_desde_fila(
                    fila
                )
                for fila in filas
            ]

        except Exception:
            raise

    def listar_ejercicios(
        self,
    ) -> List[EjercicioCardio]:
        """
        Alias de listar().
        """
        return self.listar()

    def actualizar(
        self,
        ejercicio: EjercicioCardio,
    ) -> EjercicioCardio:
        """
        Actualiza un ejercicio existente.
        """
        self._validar_ejercicio(ejercicio)

        self._validar_id(
            ejercicio.id_ejercicio
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                consulta = """
                    UPDATE ejercicios
                    SET
                        nombre = %s,
                        descripcion = %s,
                        tipo = %s,
                        duracion_minutos = %s,
                        intensidad = %s,
                        calorias_estimadas = %s,
                        creado_por = %s
                    WHERE id_ejercicio = %s
                    RETURNING
                        id_ejercicio,
                        nombre,
                        descripcion,
                        tipo,
                        duracion_minutos,
                        intensidad,
                        calorias_estimadas,
                        creado_por
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

                fila = cursor.fetchone()

                if fila is None:
                    raise ValueError(
                        "No se encontró el ejercicio."
                    )

            self._bd._conexion.commit()

            return (
                self._crear_ejercicio_desde_fila(
                    fila
                )
            )

        except IntegrityError as error:
            self._bd._conexion.rollback()

            if error.pgcode == "23503":
                raise ValueError(
                    "El creador del ejercicio "
                    "no existe."
                ) from error

            raise ValueError(
                "No se pudo actualizar el ejercicio "
                "por una restricción de integridad."
            ) from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def eliminar_por_id(
        self,
        id_ejercicio: int,
    ) -> bool:
        """
        Elimina un ejercicio por su ID.
        """
        self._validar_id(id_ejercicio)

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

                eliminado = (
                    cursor.rowcount > 0
                )

            self._bd._conexion.commit()

            return eliminado

        except IntegrityError as error:
            self._bd._conexion.rollback()

            if error.pgcode == "23503":
                raise ValueError(
                    "No se puede eliminar el ejercicio "
                    "porque está asociado a una rutina."
                ) from error

            raise ValueError(
                "No se puede eliminar el ejercicio "
                "por una restricción de integridad."
            ) from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    @staticmethod
    def _crear_ejercicio_desde_fila(
        fila: Tuple,
    ) -> EjercicioCardio:
        """
        Convierte una fila de PostgreSQL en objeto.
        """
        if len(fila) < 8:
            raise ValueError(
                "La fila del ejercicio está incompleta."
            )

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

    @staticmethod
    def _validar_ejercicio(
        ejercicio: EjercicioCardio,
    ) -> None:
        """
        Valida el objeto de ejercicio.
        """
        if not isinstance(
            ejercicio,
            EjercicioCardio,
        ):
            raise TypeError(
                "Debe proporcionar una instancia "
                "de EjercicioCardio."
            )

    @staticmethod
    def _validar_id(
        id_ejercicio: Optional[int],
    ) -> None:
        """
        Valida un ID positivo.
        """
        if (
            id_ejercicio is None
            or isinstance(id_ejercicio, bool)
            or not isinstance(id_ejercicio, int)
            or id_ejercicio <= 0
        ):
            raise ValueError(
                "El ID del ejercicio debe ser "
                "un entero positivo."
            )