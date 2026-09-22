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
    )

    def __init__(self) -> None:
        self._bd = ConexionBD.obtener_instancia()

    def guardar(
        self,
        sesion: SesionEntrenamiento,
    ) -> SesionEntrenamiento:
        """
        Guarda una nueva sesión.
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
                        completada
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
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
                        completada
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
                        sesion.completada,
                    ),
                )

                fila = cursor.fetchone()

            if fila is None:
                raise RuntimeError(
                    "No se recibió la sesión insertada."
                )

            self._bd._conexion.commit()

            return self._crear_sesion_desde_fila(fila)

        except IntegrityError as error:
            self._bd._conexion.rollback()

            if error.pgcode == "23503":
                raise ValueError(
                    "El cliente o la rutina referenciada "
                    "no existe."
                ) from error

            raise ValueError(
                "No se pudo guardar la sesión por una "
                "restricción de integridad."
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

            return self._crear_sesion_desde_fila(fila)

        except Exception:
            raise

    def listar_por_cliente(
        self,
        id_cliente: int,
    ) -> List[SesionEntrenamiento]:
        """
        Lista las sesiones de un cliente.
        """
        if isinstance(id_cliente, bool):
            raise ValueError(
                "El ID del cliente debe ser un entero."
            )

        try:
            id_cliente = int(id_cliente)
        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "El ID del cliente debe ser un entero."
            ) from error

        if id_cliente <= 0:
            raise ValueError(
                "El ID del cliente debe ser positivo."
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

            sesiones = []

            for fila in filas:
                try:
                    sesiones.append(
                        self._crear_sesion_desde_fila(
                            fila
                        )
                    )
                except Exception as error:
                    raise RuntimeError(
                        "Error al convertir la sesión "
                        f"recibida: {dict(fila)!r}. "
                        f"Causa: {error}"
                    ) from error

            return sesiones

        except Exception:
            raise

    def buscar_por_cliente(
        self,
        id_cliente: int,
    ) -> List[SesionEntrenamiento]:
        """
        Alias compatible para listar sesiones.
        """
        return self.listar_por_cliente(id_cliente)

    def actualizar(
        self,
        sesion: SesionEntrenamiento,
    ) -> SesionEntrenamiento:
        """
        Actualiza una sesión existente.
        """
        if sesion.id_sesion is None:
            raise ValueError(
                "La sesión debe tener un ID."
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
                        completada = %s
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
                        sesion.completada,
                        sesion.id_sesion,
                    ),
                )

                fila = cursor.fetchone()

            if fila is None:
                raise ValueError(
                    "No se encontró la sesión."
                )

            self._bd._conexion.commit()

            return self._crear_sesion_desde_fila(fila)

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
        if isinstance(id_sesion, bool):
            raise ValueError(
                "El ID de sesión debe ser un entero."
            )

        try:
            id_sesion = int(id_sesion)
        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "El ID de sesión debe ser un entero."
            ) from error

        if id_sesion <= 0:
            raise ValueError(
                "El ID de sesión debe ser positivo."
            )

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
    def _columnas_sql() -> str:
        """
        Devuelve las columnas SQL en orden.
        """
        return ", ".join(
            SesionEntrenamientoDAO.COLUMNAS
        )

    @staticmethod
    def _validar_sesion(
        sesion: SesionEntrenamiento,
    ) -> None:
        """
        Valida los datos mínimos de una sesión.
        """
        if sesion.id_cliente is None:
            raise ValueError(
                "La sesión debe tener un cliente."
            )

        if sesion.id_rutina is None:
            raise ValueError(
                "La sesión debe tener una rutina."
            )

        if not sesion.nombre_ejercicio:
            raise ValueError(
                "La sesión debe tener un ejercicio."
            )

    @staticmethod
    def _crear_sesion_desde_fila(
        fila,
    ) -> SesionEntrenamiento:
        """
        Convierte una fila de PostgreSQL en modelo.
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
                or "Sin ejercicio"
            ),
            duracion_real=int(duracion),
            intensidad_real=(
                SesionEntrenamientoDAO
                ._convertir_intensidad(intensidad)
            ),
            calorias_quemadas=calorias,
            observaciones=(
                datos.get(
                    "observaciones",
                    "",
                )
                or ""
            ),
            completada=bool(
                datos.get(
                    "completada",
                    False,
                )
            ),
        )

    @staticmethod
    def _convertir_intensidad(
        valor,
    ) -> Intensidad:
        """
        Convierte el valor recibido desde PostgreSQL.
        """
        if isinstance(valor, Intensidad):
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
                "Intensidad inválida recibida: "
                f"{valor!r}"
            )

        return equivalencias[texto]

    @staticmethod
    def _valor_intensidad(
        valor,
    ) -> str:
        """
        Convierte Intensidad a texto para PostgreSQL.
        """
        if isinstance(valor, Intensidad):
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