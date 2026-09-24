"""
DAO para la persistencia de sesiones de entrenamiento.
"""

from typing import List, Optional

from psycopg2 import IntegrityError
from psycopg2.extras import RealDictCursor

from src.modelos.enums import Intensidad
from src.modelos.sesion_entrenamiento import (
    SesionEntrenamiento,
)
from src.persistencia.conexion_bd import ConexionBD


class SesionEntrenamientoDAO:
    """
    Data Access Object de SesionEntrenamiento.
    """

    COLUMNAS = (
        "id_sesion",
        "id_cliente",
        "id_rutina",
        "fecha",
        "nombre_ejercicio",
        "duracion_real",
        "intensidad_real",
        "calorias_quemadas",
        "observaciones",
        "completada",
        "veces_planificadas",
        "veces_realizadas",
    )

    def __init__(self) -> None:
        self._bd = ConexionBD.obtener_instancia()

    def guardar(
        self,
        sesion: SesionEntrenamiento,
    ) -> SesionEntrenamiento:
        """
        Guarda una nueva sesión.

        Una sesión puede no estar asociada a una rutina
        específica ni requerir nombre de ejercicio.
        """
        self._validar_sesion(sesion)

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:
                cursor.execute(
                    """
                    INSERT INTO sesiones_entrenamiento (
                        id_cliente,
                        id_rutina,
                        fecha,
                        nombre_ejercicio,
                        duracion_real,
                        intensidad_real,
                        calorias_quemadas,
                        observaciones,
                        veces_planificadas,
                        veces_realizadas
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    RETURNING
                        id_sesion,
                        id_cliente,
                        id_rutina,
                        fecha,
                        nombre_ejercicio,
                        duracion_real,
                        intensidad_real,
                        calorias_quemadas,
                        observaciones,
                        completada,
                        veces_planificadas,
                        veces_realizadas
                    """,
                    (
                        sesion.id_cliente,
                        sesion.id_rutina,
                        sesion.fecha,
                        sesion.nombre_ejercicio,
                        sesion.duracion_real,
                        self._valor_intensidad(
                            sesion.intensidad_real
                        ),
                        sesion.calorias_quemadas,
                        sesion.observaciones,
                        sesion.veces_planificadas,
                        sesion.veces_realizadas,
                    ),
                )

                fila = cursor.fetchone()

                if fila is None:
                    raise RuntimeError(
                        "No se recibió la sesión insertada."
                    )

            self._bd._conexion.commit()

            return self._crear_sesion_desde_fila(
                fila
            )

        except IntegrityError as error:
            self._bd._conexion.rollback()

            codigo = getattr(
                error,
                "pgcode",
                None,
            )

            if codigo == "23503":
                raise ValueError(
                    "El cliente referenciado no existe."
                ) from error

            if codigo == "23514":
                raise ValueError(
                    (
                        "Las veces realizadas deben ser "
                        "mayores o iguales a cero y no "
                        "pueden superar las planificadas."
                    )
                ) from error

            raise ValueError(
                (
                    "No se pudo guardar la sesión por "
                    "una restricción de integridad."
                )
            ) from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def buscar_por_id(
        self,
        id_sesion: int,
    ) -> Optional[SesionEntrenamiento]:
        """
        Busca una sesión por ID.
        """
        id_sesion = self._validar_id(
            id_sesion,
            "El ID de sesión",
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {self._columnas_sql()}
                    FROM sesiones_entrenamiento
                    WHERE id_sesion = %s
                    """,
                    (id_sesion,),
                )

                fila = cursor.fetchone()

            if fila is None:
                return None

            return self._crear_sesion_desde_fila(
                fila
            )

        except Exception:
            self._bd._conexion.rollback()
            raise

    def listar_por_cliente(
        self,
        id_cliente: int,
    ) -> List[SesionEntrenamiento]:
        """
        Lista las sesiones de un cliente.
        """
        id_cliente = self._validar_id(
            id_cliente,
            "El ID del cliente",
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:
                cursor.execute(
                    f"""
                    SELECT
                        {self._columnas_sql()}
                    FROM sesiones_entrenamiento
                    WHERE id_cliente = %s
                    ORDER BY fecha DESC, id_sesion DESC
                    """,
                    (id_cliente,),
                )

                filas = cursor.fetchall()

            sesiones: List[SesionEntrenamiento] = []

            for fila in filas:
                try:
                    sesiones.append(
                        self._crear_sesion_desde_fila(
                            fila
                        )
                    )

                except Exception as error:
                    raise RuntimeError(
                        (
                            "Error al convertir la sesión "
                            f"recibida: {dict(fila)!r}. "
                            f"Causa: {error}"
                        )
                    ) from error

            return sesiones

        except Exception:
            self._bd._conexion.rollback()
            raise

    def buscar_por_cliente(
        self,
        id_cliente: int,
    ) -> List[SesionEntrenamiento]:
        """
        Alias compatible para listar sesiones.
        """
        return self.listar_por_cliente(
            id_cliente
        )

    def actualizar(
        self,
        sesion: SesionEntrenamiento,
    ) -> SesionEntrenamiento:
        """
        Actualiza una sesión existente.
        """
        if not isinstance(
            sesion,
            SesionEntrenamiento,
        ):
            raise TypeError(
                (
                    "Debe proporcionar una instancia "
                    "de SesionEntrenamiento."
                )
            )

        if sesion.id_sesion is None:
            raise ValueError(
                "La sesión debe tener un ID."
            )

        id_sesion = self._validar_id(
            sesion.id_sesion,
            "El ID de sesión",
        )

        self._validar_sesion(sesion)

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor(
                cursor_factory=RealDictCursor
            ) as cursor:
                cursor.execute(
                    f"""
                    UPDATE sesiones_entrenamiento
                    SET
                        id_cliente = %s,
                        id_rutina = %s,
                        fecha = %s,
                        nombre_ejercicio = %s,
                        duracion_real = %s,
                        intensidad_real = %s,
                        calorias_quemadas = %s,
                        observaciones = %s,
                        veces_planificadas = %s,
                        veces_realizadas = %s
                    WHERE id_sesion = %s
                    RETURNING
                        {self._columnas_sql()}
                    """,
                    (
                        sesion.id_cliente,
                        sesion.id_rutina,
                        sesion.fecha,
                        sesion.nombre_ejercicio,
                        sesion.duracion_real,
                        self._valor_intensidad(
                            sesion.intensidad_real
                        ),
                        sesion.calorias_quemadas,
                        sesion.observaciones,
                        sesion.veces_planificadas,
                        sesion.veces_realizadas,
                        id_sesion,
                    ),
                )

                fila = cursor.fetchone()

            if fila is None:
                raise ValueError(
                    "No se encontró la sesión."
                )

            self._bd._conexion.commit()

            return self._crear_sesion_desde_fila(
                fila
            )

        except IntegrityError as error:
            self._bd._conexion.rollback()

            codigo = getattr(
                error,
                "pgcode",
                None,
            )

            if codigo == "23503":
                raise ValueError(
                    "El cliente referenciado no existe."
                ) from error

            if codigo == "23514":
                raise ValueError(
                    (
                        "Las veces realizadas no pueden "
                        "superar las planificadas."
                    )
                ) from error

            raise ValueError(
                "No se pudo actualizar la sesión."
            ) from error

        except Exception:
            self._bd._conexion.rollback()
            raise

    def eliminar_por_id(
        self,
        id_sesion: int,
    ) -> bool:
        """
        Elimina una sesión por ID.
        """
        id_sesion = self._validar_id(
            id_sesion,
            "El ID de sesión",
        )

        self._bd.abrir_conexion()

        try:
            with self._bd._conexion.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM sesiones_entrenamiento
                    WHERE id_sesion = %s
                    RETURNING id_sesion
                    """,
                    (id_sesion,),
                )

                eliminado = (
                    cursor.fetchone()
                    is not None
                )

            self._bd._conexion.commit()

            return eliminado

        except Exception:
            self._bd._conexion.rollback()
            raise

    @staticmethod
    def _columnas_sql() -> str:
        """
        Devuelve las columnas SQL en orden.
        """
        return ", ".join(
            SesionEntrenamientoDAO.COLUMNAS
        )

    @staticmethod
    def _validar_id(
        valor: object,
        nombre: str,
    ) -> int:
        """
        Convierte y valida un ID positivo.
        """
        if valor is None or isinstance(
            valor,
            bool,
        ):
            raise ValueError(
                f"{nombre} debe ser un entero positivo."
            )

        try:
            identificador = int(valor)

        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                f"{nombre} debe ser un entero positivo."
            ) from error

        if identificador <= 0:
            raise ValueError(
                f"{nombre} debe ser positivo."
            )

        return identificador

    @staticmethod
    def _validar_sesion(
        sesion: SesionEntrenamiento,
    ) -> None:
        """
        Valida los datos mínimos de una sesión.

        id_rutina y nombre_ejercicio son opcionales:
        existen sesiones libres o registros antiguos sin
        una rutina o ejercicio individual asociado.
        """
        if not isinstance(
            sesion,
            SesionEntrenamiento,
        ):
            raise TypeError(
                (
                    "Debe proporcionar una instancia "
                    "de SesionEntrenamiento."
                )
            )

        if sesion.id_cliente is None:
            raise ValueError(
                "La sesión debe tener un cliente."
            )

        SesionEntrenamientoDAO._validar_id(
            sesion.id_cliente,
            "El ID del cliente",
        )

        if sesion.id_rutina is not None:
            SesionEntrenamientoDAO._validar_id(
                sesion.id_rutina,
                "El ID de la rutina",
            )

        if sesion.veces_planificadas <= 0:
            raise ValueError(
                (
                    "Las veces planificadas deben ser "
                    "mayores que cero."
                )
            )

        if sesion.veces_realizadas < 0:
            raise ValueError(
                (
                    "Las veces realizadas no pueden "
                    "ser negativas."
                )
            )

        if (
            sesion.veces_realizadas
            > sesion.veces_planificadas
        ):
            raise ValueError(
                (
                    "Las veces realizadas no pueden "
                    "superar las planificadas."
                )
            )

    @staticmethod
    def _crear_sesion_desde_fila(
        fila,
    ) -> SesionEntrenamiento:
        """
        Convierte una fila de PostgreSQL en una entidad.
        """
        if not hasattr(fila, "keys"):
            raise TypeError(
                "La fila no es un diccionario."
            )

        datos = dict(fila)

        fecha = datos.get("fecha")
        duracion = datos.get("duracion_real")
        intensidad = datos.get("intensidad_real")
        calorias = datos.get(
            "calorias_quemadas",
            0,
        )

        if fecha is None:
            raise ValueError(
                "La sesión no tiene fecha."
            )

        if duracion is None:
            raise ValueError(
                "La sesión no tiene duración."
            )

        if intensidad is None:
            raise ValueError(
                "La sesión no tiene intensidad."
            )

        veces_planificadas = datos.get(
            "veces_planificadas",
            1,
        )

        veces_realizadas = datos.get(
            "veces_realizadas",
            0,
        )

        return SesionEntrenamiento(
            id_sesion=datos.get("id_sesion"),
            id_cliente=datos.get("id_cliente"),
            id_rutina=datos.get("id_rutina"),
            fecha=fecha,
            nombre_ejercicio=(
                datos.get(
                    "nombre_ejercicio",
                    "",
                )
                or ""
            ),
            duracion_real=int(duracion),
            intensidad_real=(
                SesionEntrenamientoDAO
                ._convertir_intensidad(
                    intensidad
                )
            ),
            calorias_quemadas=calorias,
            observaciones=(
                datos.get(
                    "observaciones",
                    "",
                )
                or ""
            ),
            veces_planificadas=int(
                veces_planificadas
            ),
            veces_realizadas=int(
                veces_realizadas
            ),
        )

    @staticmethod
    def _convertir_intensidad(
        valor,
    ) -> Intensidad:
        """
        Convierte la intensidad recibida desde PostgreSQL.
        """
        if isinstance(
            valor,
            Intensidad,
        ):
            return valor

        if valor is None:
            raise ValueError(
                "La intensidad no puede ser NULL."
            )

        texto = str(valor).strip().upper()

        equivalencias = {
            "BAJA": Intensidad.BAJA,
            "MEDIA": Intensidad.MEDIA,
            "ALTA": Intensidad.ALTA,
        }

        if texto not in equivalencias:
            raise ValueError(
                (
                    "Intensidad inválida recibida: "
                    f"{valor!r}"
                )
            )

        return equivalencias[texto]

    @staticmethod
    def _valor_intensidad(
        valor,
    ) -> str:
        """
        Convierte Intensidad a texto para PostgreSQL.
        """
        if isinstance(
            valor,
            Intensidad,
        ):
            return valor.value

        texto = str(valor).strip().upper()

        if texto not in {
            "BAJA",
            "MEDIA",
            "ALTA",
        }:
            raise ValueError(
                f"Intensidad inválida: {valor!r}"
            )

        return texto