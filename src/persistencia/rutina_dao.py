from typing import List, Optional, Tuple

from psycopg2 import IntegrityError

from src.modelos.ejercicio_cardio import (
    EjercicioCardio,
)
from src.modelos.rutina import Rutina
from src.persistencia.conexion_bd import (
    ConexionBD,
)


class RutinaDAO:
    """
    Data Access Object para la entidad Rutina.
    """

    def __init__(self) -> None:
        self._bd = (
            ConexionBD.obtener_instancia()
        )

    def guardar(
        self,
        rutina: Rutina,
    ) -> Rutina:
        """
        Guarda una rutina nueva.
        """
        self._validar_rutina_para_guardar(
            rutina
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO rutinas (
                        nombre,
                        descripcion,
                        objetivo,
                        nivel,
                        duracion_semanas,
                        creado_por
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
                        id_rutina,
                        fecha_creacion
                    """,
                    (
                        rutina.nombre,
                        rutina.descripcion,
                        rutina.objetivo,
                        self._obtener_valor_nivel(
                            rutina.nivel
                        ),
                        rutina.duracion_semanas,
                        rutina.creado_por,
                    ),
                )

                resultado = cursor.fetchone()

                if resultado is None:
                    raise RuntimeError(
                        "La base de datos no devolvió "
                        "los datos de la rutina creada."
                    )

                rutina.id_rutina = resultado[0]
                rutina.fecha_creacion = resultado[1]

            self._bd._conexion.commit()

            return rutina

        except IntegrityError as error:
            self._bd._conexion.rollback()

            raise self._convertir_error_integridad(
                error,
                "No se pudo guardar la rutina.",
            ) from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def buscar_por_id(
        self,
        id_rutina: int,
    ) -> Optional[Rutina]:
        """
        Busca una rutina con sus ejercicios.
        """
        id_rutina = self._validar_id(
            id_rutina,
            "El ID de la rutina",
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
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
                    """,
                    (id_rutina,),
                )

                fila = cursor.fetchone()

                if fila is None:
                    return None

                rutina = (
                    self._crear_rutina_desde_fila(
                        fila
                    )
                )

                ejercicios = (
                    self._obtener_ejercicios(
                        cursor,
                        id_rutina,
                    )
                )

                rutina.reemplazar_ejercicios(
                    ejercicios
                )

                return rutina

        except Exception:
            self._bd._conexion.rollback()
            raise

    def listar(self) -> List[Rutina]:
        """
        Lista todas las rutinas con ejercicios.
        """
        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
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
                )

                filas = cursor.fetchall()
                rutinas: List[Rutina] = []

                for fila in filas:
                    rutina = (
                        self._crear_rutina_desde_fila(
                            fila
                        )
                    )

                    ejercicios = (
                        self._obtener_ejercicios(
                            cursor,
                            rutina.id_rutina,
                        )
                    )

                    rutina.reemplazar_ejercicios(
                        ejercicios
                    )

                    rutinas.append(rutina)

                return rutinas

        except Exception:
            self._bd._conexion.rollback()
            raise

    def listar_rutinas(self) -> List[Rutina]:
        """
        Alias de listar().
        """
        return self.listar()

    def actualizar(
        self,
        rutina: Rutina,
    ) -> Rutina:
        """
        Actualiza una rutina.
        """
        self._validar_rutina_para_guardar(
            rutina
        )

        id_rutina = self._validar_id(
            rutina.id_rutina,
            "El ID de la rutina",
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE rutinas
                    SET
                        nombre = %s,
                        descripcion = %s,
                        objetivo = %s,
                        nivel = %s,
                        duracion_semanas = %s
                    WHERE id_rutina = %s
                    RETURNING
                        id_rutina,
                        nombre,
                        descripcion,
                        objetivo,
                        nivel,
                        duracion_semanas,
                        creado_por,
                        fecha_creacion
                    """,
                    (
                        rutina.nombre,
                        rutina.descripcion,
                        rutina.objetivo,
                        self._obtener_valor_nivel(
                            rutina.nivel
                        ),
                        rutina.duracion_semanas,
                        id_rutina,
                    ),
                )

                fila = cursor.fetchone()

                if fila is None:
                    raise ValueError(
                        "No se encontró la rutina."
                    )

                rutina_actualizada = (
                    self._crear_rutina_desde_fila(
                        fila
                    )
                )

                ejercicios = (
                    self._obtener_ejercicios(
                        cursor,
                        id_rutina,
                    )
                )

                rutina_actualizada.reemplazar_ejercicios(
                    ejercicios
                )

            self._bd._conexion.commit()

            return rutina_actualizada

        except IntegrityError as error:
            self._bd._conexion.rollback()

            raise self._convertir_error_integridad(
                error,
                "No se pudo actualizar la rutina.",
            ) from error

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
        Asocia un ejercicio a una rutina.
        """
        id_rutina = self._validar_id(
            id_rutina,
            "El ID de la rutina",
        )

        id_ejercicio = self._validar_id(
            id_ejercicio,
            "El ID del ejercicio",
        )

        if (
            isinstance(
                orden_ejercicio,
                bool,
            )
            or not isinstance(
                orden_ejercicio,
                int,
            )
            or orden_ejercicio <= 0
        ):
            raise ValueError(
                "El orden debe ser un entero "
                "mayor que cero."
            )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO rutina_ejercicios (
                        id_rutina,
                        id_ejercicio,
                        orden_ejercicio
                    )
                    VALUES (
                        %s,
                        %s,
                        %s
                    )
                    RETURNING
                        id_rutina,
                        id_ejercicio,
                        orden_ejercicio
                    """,
                    (
                        id_rutina,
                        id_ejercicio,
                        orden_ejercicio,
                    ),
                )

                fila = cursor.fetchone()

                if fila is None:
                    raise RuntimeError(
                        "No se creó la asociación."
                    )

            self._bd._conexion.commit()

            return True

        except IntegrityError as error:
            self._bd._conexion.rollback()

            raise self._convertir_error_integridad(
                error,
                "No se pudo asociar el ejercicio.",
            ) from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def eliminar_ejercicio(
        self,
        id_rutina: int,
        id_ejercicio: int,
    ) -> bool:
        """
        Elimina exactamente una asociación.
        """
        id_rutina = self._validar_id(
            id_rutina,
            "El ID de la rutina",
        )

        id_ejercicio = self._validar_id(
            id_ejercicio,
            "El ID del ejercicio",
        )

        self._bd.abrir_conexion()

        try:
            conexion = self._bd._conexion

            # Limpia cualquier transacción anterior
            # que haya quedado abortada.
            conexion.rollback()

            with conexion.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 1
                    FROM rutina_ejercicios
                    WHERE id_rutina = %s
                      AND id_ejercicio = %s
                    LIMIT 1
                    """,
                    (
                        id_rutina,
                        id_ejercicio,
                    ),
                )

                asociada = (
                    cursor.fetchone()
                    is not None
                )

                if not asociada:
                    conexion.rollback()
                    return False

                cursor.execute(
                    """
                    DELETE FROM rutina_ejercicios
                    WHERE id_rutina = %s
                      AND id_ejercicio = %s
                    RETURNING
                        id_rutina,
                        id_ejercicio
                    """,
                    (
                        id_rutina,
                        id_ejercicio,
                    ),
                )

                fila_eliminada = (
                    cursor.fetchone()
                )

                if fila_eliminada is None:
                    conexion.rollback()
                    return False

            conexion.commit()

            return True

        except Exception:
            self._bd._conexion.rollback()
            raise

    def ejercicio_asociado(
        self,
        id_rutina: int,
        id_ejercicio: int,
    ) -> bool:
        """
        Comprueba una asociación exacta.
        """
        id_rutina = self._validar_id(
            id_rutina,
            "El ID de la rutina",
        )

        id_ejercicio = self._validar_id(
            id_ejercicio,
            "El ID del ejercicio",
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 1
                    FROM rutina_ejercicios
                    WHERE id_rutina = %s
                      AND id_ejercicio = %s
                    LIMIT 1
                    """,
                    (
                        id_rutina,
                        id_ejercicio,
                    ),
                )

                return (
                    cursor.fetchone()
                    is not None
                )

        except Exception:
            self._bd._conexion.rollback()
            raise

    def listar_ejercicios(
        self,
        id_rutina: int,
    ) -> List[EjercicioCardio]:
        """
        Lista los ejercicios asociados.
        """
        id_rutina = self._validar_id(
            id_rutina,
            "El ID de la rutina",
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                ejercicios = (
                    self._obtener_ejercicios(
                        cursor,
                        id_rutina,
                    )
                )

            return ejercicios

        except Exception:
            self._bd._conexion.rollback()
            raise

    def eliminar_por_id(
        self,
        id_rutina: int,
    ) -> bool:
        """
        Elimina una rutina por ID.
        """
        id_rutina = self._validar_id(
            id_rutina,
            "El ID de la rutina",
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM rutinas
                    WHERE id_rutina = %s
                    RETURNING id_rutina
                    """,
                    (id_rutina,),
                )

                eliminado = (
                    cursor.fetchone()
                    is not None
                )

            self._bd._conexion.commit()

            return eliminado

        except IntegrityError as error:
            self._bd._conexion.rollback()

            raise self._convertir_error_integridad(
                error,
                (
                    "No se puede eliminar la rutina "
                    "porque está asignada o tiene "
                    "dependencias."
                ),
            ) from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    @staticmethod
    def _crear_rutina_desde_fila(
        fila: Tuple,
    ) -> Rutina:
        """
        Convierte una fila en una Rutina.
        """
        if len(fila) < 8:
            raise ValueError(
                "La fila de rutina está incompleta."
            )

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
    def _obtener_ejercicios(
        cursor,
        id_rutina: int,
    ) -> List[EjercicioCardio]:
        """
        Obtiene ejercicios asociados.
        """
        cursor.execute(
            """
            SELECT
                re.id_ejercicio,
                e.nombre,
                e.descripcion,
                e.tipo,
                e.duracion_minutos,
                e.intensidad,
                e.calorias_estimadas,
                e.creado_por
            FROM rutina_ejercicios AS re
            LEFT JOIN ejercicios AS e
                ON e.id_ejercicio =
                   re.id_ejercicio
            WHERE re.id_rutina = %s
            ORDER BY
                re.orden_ejercicio,
                re.id_ejercicio
            """,
            (id_rutina,),
        )

        filas = cursor.fetchall()
        ejercicios: List[
            EjercicioCardio
        ] = []

        for fila in filas:
            ejercicios.append(
                EjercicioCardio(
                    id_ejercicio=fila[0],
                    nombre=(
                        fila[1]
                        if fila[1] is not None
                        else (
                            f"Ejercicio {fila[0]}"
                        )
                    ),
                    descripcion=(
                        fila[2]
                        if fila[2] is not None
                        else ""
                    ),
                    tipo=(
                        fila[3]
                        if fila[3] is not None
                        else "CARDIO"
                    ),
                    duracion_minutos=(
                        fila[4]
                        if fila[4] is not None
                        else 0
                    ),
                    intensidad=(
                        fila[5]
                        if fila[5] is not None
                        else "MEDIA"
                    ),
                    calorias_estimadas=(
                        fila[6]
                        if fila[6] is not None
                        else 0
                    ),
                    creado_por=fila[7],
                )
            )

        return ejercicios

    @staticmethod
    def _obtener_valor_nivel(
        nivel,
    ) -> str:
        """
        Devuelve el nivel como texto.
        """
        valor = getattr(
            nivel,
            "value",
            nivel,
        )

        if valor is None:
            raise ValueError(
                "El nivel es obligatorio."
            )

        valor = str(
            valor
        ).strip().upper()

        niveles_validos = {
            "BASICO",
            "INTERMEDIO",
            "AVANZADO",
        }

        if valor not in niveles_validos:
            raise ValueError(
                "El nivel debe ser BASICO, "
                "INTERMEDIO o AVANZADO."
            )

        return valor

    @staticmethod
    def _validar_rutina_para_guardar(
        rutina: Rutina,
    ) -> None:
        """
        Valida una rutina.
        """
        if not isinstance(
            rutina,
            Rutina,
        ):
            raise TypeError(
                "Debe proporcionar una instancia "
                "de Rutina."
            )

        if not rutina.nombre.strip():
            raise ValueError(
                "El nombre es obligatorio."
            )

        if not rutina.descripcion.strip():
            raise ValueError(
                "La descripción es obligatoria."
            )

        if not rutina.objetivo.strip():
            raise ValueError(
                "El objetivo es obligatorio."
            )

        if (
            not isinstance(
                rutina.duracion_semanas,
                int,
            )
            or isinstance(
                rutina.duracion_semanas,
                bool,
            )
            or rutina.duracion_semanas <= 0
        ):
            raise ValueError(
                "La duración debe ser un entero "
                "mayor que cero."
            )

        RutinaDAO._validar_id(
            rutina.creado_por,
            "El ID del creador",
        )

        RutinaDAO._obtener_valor_nivel(
            rutina.nivel
        )

    @staticmethod
    def _validar_id(
        identificador: Optional[int],
        nombre: str,
    ) -> int:
        """
        Convierte y valida un ID positivo.
        """
        if (
            identificador is None
            or isinstance(
                identificador,
                bool,
            )
        ):
            raise ValueError(
                f"{nombre} no es válido."
            )

        try:
            identificador = int(
                identificador
            )

        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                f"{nombre} no es válido."
            ) from error

        if identificador <= 0:
            raise ValueError(
                f"{nombre} debe ser mayor que cero."
            )

        return identificador

    @staticmethod
    def _convertir_error_integridad(
        error: IntegrityError,
        mensaje: str,
    ) -> ValueError:
        """
        Convierte errores de integridad.
        """
        codigo = getattr(
            error,
            "pgcode",
            None,
        )

        if codigo == "23503":
            return ValueError(
                "El usuario, rutina o ejercicio "
                "relacionado no existe."
            )

        if codigo == "23505":
            return ValueError(
                "La asociación o el registro "
                "ya existe."
            )

        if codigo == "23514":
            return ValueError(
                "Los datos no cumplen una "
                "restricción de la base de datos."
            )

        if codigo == "23502":
            return ValueError(
                "Falta un dato obligatorio."
            )

        return ValueError(mensaje)