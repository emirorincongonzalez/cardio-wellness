"""
Controlador para la gestión de sesiones de entrenamiento.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, List, Optional, Union

from src.controladores.control_base import ControlBase
from src.modelos.enums import Intensidad
from src.modelos.sesion_entrenamiento import (
    SesionEntrenamiento,
)
from src.persistencia.sesion_entrenamiento_dao import (
    SesionEntrenamientoDAO,
)
from src.utilidades.logger import log_generar_progreso


class ControlSesiones(ControlBase):
    """
    Controlador para registrar, consultar y eliminar
    sesiones de entrenamiento.
    """

    def __init__(
        self,
        sesion_dao: Optional[
            SesionEntrenamientoDAO
        ] = None,
        ruta_log: str = "logs/LOG_CARDIO.txt",
    ) -> None:
        super().__init__(
            ruta_log=ruta_log,
        )

        self.sesion_dao = (
            sesion_dao
            if sesion_dao is not None
            else SesionEntrenamientoDAO()
        )

    def registrar_sesion(
        self,
        cliente: Any,
        rutina: Any,
        duracion_real: int,
        intensidad_real: Union[
            Intensidad,
            str,
        ],
        calorias_quemadas: Union[
            int,
            float,
            Decimal,
        ],
        observaciones: str = "",
        fecha: Optional[
            Union[
                date,
                datetime,
            ]
        ] = None,
        nombre_ejercicio: str = "",
        veces_planificadas: int = 1,
        veces_realizadas: int = 0,
    ) -> SesionEntrenamiento:
        """
        Registra una sesión diaria.

        La sesión queda completada únicamente cuando:

            veces_realizadas >= veces_planificadas
        """
        id_cliente = self._extraer_id(
            cliente,
            "id_usuario",
            "id_cliente",
            "id",
        )

        id_rutina = self._extraer_id(
            rutina,
            "id_rutina",
            "id",
        )

        if id_cliente is None or id_cliente <= 0:
            raise ValueError(
                "El ID del cliente debe ser "
                "un entero positivo."
            )

        if id_rutina is None or id_rutina <= 0:
            raise ValueError(
                "El ID de rutina debe ser "
                "un entero positivo."
            )

        if not isinstance(
            nombre_ejercicio,
            str,
        ):
            raise ValueError(
                "El nombre del ejercicio debe ser texto."
            )

        nombre_ejercicio = (
            nombre_ejercicio.strip()
        )

        if not nombre_ejercicio:
            raise ValueError(
                "El nombre del ejercicio "
                "es obligatorio."
            )

        if len(nombre_ejercicio) > 100:
            raise ValueError(
                "El nombre del ejercicio no puede "
                "superar 100 caracteres."
            )

        if (
            isinstance(
                duracion_real,
                bool,
            )
            or not isinstance(
                duracion_real,
                int,
            )
            or duracion_real <= 0
        ):
            raise ValueError(
                "La duración real debe ser un entero "
                "positivo."
            )

        if isinstance(
            calorias_quemadas,
            bool,
        ):
            raise ValueError(
                "Las calorías deben ser numéricas."
            )

        if not isinstance(
            calorias_quemadas,
            (
                int,
                float,
                Decimal,
            ),
        ):
            raise ValueError(
                "Las calorías deben ser numéricas."
            )

        try:
            calorias = Decimal(
                str(calorias_quemadas)
            )

        except Exception as error:
            raise ValueError(
                "Las calorías deben ser un valor válido."
            ) from error

        if calorias < Decimal("0"):
            raise ValueError(
                "Las calorías no pueden ser negativas."
            )

        veces_planificadas = (
            self._validar_cantidad(
                veces_planificadas,
                "Las veces planificadas",
                minimo=1,
            )
        )

        veces_realizadas = (
            self._validar_cantidad(
                veces_realizadas,
                "Las veces realizadas",
                minimo=0,
            )
        )

        if (
            veces_realizadas
            > veces_planificadas
        ):
            raise ValueError(
                "Las veces realizadas no pueden "
                "superar las planificadas."
            )

        intensidad = (
            self._normalizar_intensidad(
                intensidad_real
            )
        )

        fecha_sesion = (
            fecha
            if fecha is not None
            else date.today()
        )

        if isinstance(
            fecha_sesion,
            datetime,
        ):
            fecha_sesion = fecha_sesion.date()

        if not isinstance(
            fecha_sesion,
            date,
        ):
            raise ValueError(
                "La fecha debe ser un objeto date."
            )

        sesion = SesionEntrenamiento(
            id_cliente=id_cliente,
            id_rutina=id_rutina,
            fecha=fecha_sesion,
            nombre_ejercicio=(
                nombre_ejercicio
            ),
            duracion_real=duracion_real,
            intensidad_real=intensidad,
            calorias_quemadas=calorias,
            observaciones=(
                observaciones or ""
            ),
            veces_planificadas=(
                veces_planificadas
            ),
            veces_realizadas=(
                veces_realizadas
            ),
        )

        try:
            sesion_guardada = (
                self.sesion_dao.guardar(
                    sesion
                )
            )

            self._registrar_log(
                f"CLIENTE_{id_cliente}",
                (
                    "REGISTRO_SESION "
                    f"Rutina: {id_rutina}, "
                    f"Ejercicio: "
                    f"{nombre_ejercicio}, "
                    f"Realizadas: "
                    f"{veces_realizadas}/"
                    f"{veces_planificadas}"
                ),
            )

            log_generar_progreso(
                f"CLIENTE_{id_cliente}"
            )

            return sesion_guardada

        except ValueError as error:
            raise ValueError(
                f"Error al registrar la sesión: {error}"
            ) from error

        except Exception as error:
            raise RuntimeError(
                "Error inesperado al registrar "
                f"la sesión: {error}"
            ) from error

    def actualizar_sesion(
        self,
        sesion: SesionEntrenamiento,
        usuario_accion: Optional[str] = None,
    ) -> SesionEntrenamiento:
        """
        Actualiza una sesión existente.
        """
        if not isinstance(
            sesion,
            SesionEntrenamiento,
        ):
            raise TypeError(
                "Debe proporcionar una instancia "
                "de SesionEntrenamiento."
            )

        if sesion.id_sesion is None:
            raise ValueError(
                "La sesión debe tener un ID."
            )

        self._validar_cantidad(
            sesion.veces_planificadas,
            "Las veces planificadas",
            minimo=1,
        )

        self._validar_cantidad(
            sesion.veces_realizadas,
            "Las veces realizadas",
            minimo=0,
        )

        if (
            sesion.veces_realizadas
            > sesion.veces_planificadas
        ):
            raise ValueError(
                "Las veces realizadas no pueden "
                "superar las planificadas."
            )

        try:
            resultado = (
                self.sesion_dao.actualizar(
                    sesion
                )
            )

            self._registrar_log(
                usuario_accion
                or f"SESION_{sesion.id_sesion}",
                "ACTUALIZACION_SESION",
            )

            return resultado

        except ValueError as error:
            raise ValueError(
                f"Error al actualizar la sesión: {error}"
            ) from error

        except Exception as error:
            raise RuntimeError(
                "Error inesperado al actualizar "
                f"la sesión: {error}"
            ) from error

    def obtener_sesiones_cliente(
        self,
        id_cliente: int,
    ) -> List[SesionEntrenamiento]:
        """
        Obtiene las sesiones de un cliente.
        """
        id_cliente_validado = self._validar_id(
            id_cliente,
            "cliente",
        )

        self._registrar_log(
            f"CLIENTE_{id_cliente_validado}",
            "CONSULTA_SESIONES",
        )

        try:
            sesiones = (
                self.sesion_dao.listar_por_cliente(
                    id_cliente_validado
                )
            )

            return sesiones or []

        except Exception as error:
            raise RuntimeError(
                "Error al consultar las sesiones: "
                f"{error}"
            ) from error

    def listar_por_cliente(
        self,
        id_cliente: int,
    ) -> List[SesionEntrenamiento]:
        """
        Alias de obtener_sesiones_cliente().
        """
        return self.obtener_sesiones_cliente(
            id_cliente
        )

    def buscar_por_id(
        self,
        id_sesion: int,
    ) -> Optional[SesionEntrenamiento]:
        """
        Busca una sesión por ID.
        """
        id_validado = self._validar_id(
            id_sesion,
            "sesión",
        )

        try:
            return self.sesion_dao.buscar_por_id(
                id_validado
            )

        except Exception as error:
            raise RuntimeError(
                "Error al buscar la sesión: "
                f"{error}"
            ) from error

    def obtener_por_id(
        self,
        id_sesion: int,
    ) -> Optional[SesionEntrenamiento]:
        """
        Alias para buscar por ID.
        """
        return self.buscar_por_id(id_sesion)

    def eliminar_sesion(
        self,
        id_sesion: int,
        usuario_accion: Optional[str] = None,
    ) -> bool:
        """
        Elimina una sesión por ID.
        """
        id_validado = self._validar_id(
            id_sesion,
            "sesión",
        )

        try:
            resultado = (
                self.sesion_dao.eliminar_por_id(
                    id_validado
                )
            )

            if resultado:
                self._registrar_log(
                    usuario_accion
                    or f"SESION_{id_validado}",
                    "ELIMINACION_SESION",
                )

            return resultado

        except ValueError as error:
            raise ValueError(
                f"Error al eliminar la sesión: {error}"
            ) from error

        except Exception as error:
            raise RuntimeError(
                "Error inesperado al eliminar "
                f"la sesión: {error}"
            ) from error

    def contar_sesiones_completadas(
        self,
        id_cliente: int,
        fecha: Optional[date] = None,
    ) -> int:
        """
        Cuenta sesiones completadas.

        Este método utiliza las sesiones ya cargadas
        por el DAO y filtra por fecha si se indica.
        """
        id_cliente = self._validar_id(
            id_cliente,
            "cliente",
        )

        sesiones = (
            self.sesion_dao.listar_por_cliente(
                id_cliente
            )
        )

        if fecha is None:
            fecha = date.today()

        return sum(
            1
            for sesion in sesiones
            if sesion.fecha == fecha
            and sesion.completada
        )

        def porcentaje_cumplimiento_sesion(
        self,
        sesion: SesionEntrenamiento,
    ) -> float:
         """
        Calcula el porcentaje de cumplimiento.
        """
        if not isinstance(
            sesion,
            SesionEntrenamiento,
        ):
            raise TypeError(
                "La sesión no es válida."
            )

        porcentaje = sesion.porcentaje_cumplimiento

        if callable(porcentaje):
            porcentaje = porcentaje()

        return float(porcentaje)

    @staticmethod
    def _extraer_id(
        objeto: Any,
        *campos: str,
    ) -> Optional[int]:
        """
        Extrae un ID desde un entero, diccionario
        u objeto.
        """
        if isinstance(
            objeto,
            bool,
        ):
            return None

        if isinstance(
            objeto,
            int,
        ):
            return objeto

        if isinstance(
            objeto,
            dict,
        ):
            for campo in campos:
                if campo in objeto:
                    return (
                        ControlSesiones
                        ._convertir_id(
                            objeto[campo]
                        )
                    )

            return None

        for campo in campos:
            if hasattr(
                objeto,
                campo,
            ):
                return (
                    ControlSesiones
                    ._convertir_id(
                        getattr(
                            objeto,
                            campo,
                        )
                    )
                )

        return None

    @staticmethod
    def _convertir_id(
        valor: Any,
    ) -> Optional[int]:
        """
        Convierte un valor a ID entero.
        """
        if valor is None or isinstance(
            valor,
            bool,
        ):
            return None

        try:
            return int(valor)

        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _validar_id(
        valor: Any,
        nombre: str,
    ) -> int:
        """
        Valida un ID positivo.
        """
        if (
            isinstance(
                valor,
                bool,
            )
            or not isinstance(
                valor,
                int,
            )
            or valor <= 0
        ):
            raise ValueError(
                (
                    f"El ID de {nombre} debe ser "
                    "un entero positivo."
                )
            )

        return valor

    @staticmethod
    def _validar_cantidad(
        valor: Any,
        nombre: str,
        minimo: int,
    ) -> int:
        """
        Valida una cantidad entera.
        """
        if (
            isinstance(
                valor,
                bool,
            )
            or not isinstance(
                valor,
                int,
            )
        ):
            raise ValueError(
                f"{nombre} debe ser un entero."
            )

        if valor < minimo:
            raise ValueError(
                (
                    f"{nombre} debe ser mayor o igual "
                    f"a {minimo}."
                )
            )

        return valor

    @staticmethod
    def _normalizar_intensidad(
        valor: Union[
            Intensidad,
            str,
        ],
    ) -> Intensidad:
        """
        Convierte texto o enum a Intensidad.
        """
        if isinstance(
            valor,
            Intensidad,
        ):
            return valor

        if not isinstance(
            valor,
            str,
        ):
            raise ValueError(
                "La intensidad debe ser BAJA, "
                "MEDIA o ALTA."
            )

        texto = valor.strip().upper()

        try:
            return Intensidad[texto]

        except KeyError:
            try:
                return Intensidad(texto)

            except ValueError as error:
                raise ValueError(
                    (
                        "Intensidad inválida. Debe ser "
                        "BAJA, MEDIA o ALTA."
                    )
                ) from error