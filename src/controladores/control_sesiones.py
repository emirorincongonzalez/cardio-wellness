"""
Controlador para la gestión de sesiones de entrenamiento.
"""

from datetime import date
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
        sesion_dao: Optional[SesionEntrenamientoDAO] = None,
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
        fecha: Optional[date] = None,
        nombre_ejercicio: str = "",
    ) -> SesionEntrenamiento:
        """
        Registra una sesión de entrenamiento.
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
                "El ID del cliente debe ser un entero positivo."
            )

        if id_rutina is None or id_rutina <= 0:
            raise ValueError(
                "El ID de rutina debe ser un entero positivo."
            )

        if not isinstance(nombre_ejercicio, str):
            raise ValueError(
                "El nombre del ejercicio debe ser texto."
            )

        nombre_ejercicio = nombre_ejercicio.strip()

        if not nombre_ejercicio:
            raise ValueError(
                "El nombre del ejercicio es obligatorio."
            )

        if len(nombre_ejercicio) > 100:
            raise ValueError(
                "El nombre del ejercicio no puede superar "
                "100 caracteres."
            )

        if isinstance(duracion_real, bool):
            raise ValueError(
                "La duración real debe ser un entero."
            )

        if (
            not isinstance(duracion_real, int)
            or duracion_real <= 0
        ):
            raise ValueError(
                "La duración real debe ser un entero positivo."
            )

        if isinstance(calorias_quemadas, bool):
            raise ValueError(
                "Las calorías deben ser un valor numérico."
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
                "Las calorías deben ser un valor numérico."
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

        intensidad = self._normalizar_intensidad(
            intensidad_real
        )

        fecha_sesion = (
            fecha
            if fecha is not None
            else date.today()
        )

        if not isinstance(fecha_sesion, date):
            raise ValueError(
                "La fecha debe ser un objeto date."
            )

        sesion = SesionEntrenamiento(
            id_cliente=id_cliente,
            id_rutina=id_rutina,
            fecha=fecha_sesion,
            nombre_ejercicio=nombre_ejercicio,
            duracion_real=duracion_real,
            intensidad_real=intensidad,
            calorias_quemadas=calorias,
            observaciones=observaciones or "",
            completada=True,
        )

        try:
            sesion_guardada = (
                self.sesion_dao.guardar(sesion)
            )

            self._registrar_log(
                f"CLIENTE_{id_cliente}",
                "REGISTRO_SESION",
            )

            log_generar_progreso(
                f"CLIENTE_{id_cliente}"
            )

            return sesion_guardada

        except ValueError as error:
            raise ValueError(
                f"Error al registrar la sesion: {error}"
            ) from error

        except Exception as error:
            raise RuntimeError(
                "Error inesperado al registrar la sesion: "
                f"{error}"
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
        Busca una sesión por su ID.
        """
        id_validado = self._validar_id(
            id_sesion,
            "sesion",
        )

        try:
            return self.sesion_dao.buscar_por_id(
                id_validado
            )

        except Exception as error:
            raise RuntimeError(
                "Error al buscar la sesion: "
                f"{error}"
            ) from error

    def obtener_por_id(
        self,
        id_sesion: int,
    ) -> Optional[SesionEntrenamiento]:
        """
        Alias para buscar una sesión por ID.
        """
        return self.buscar_por_id(id_sesion)

    def eliminar_sesion(
        self,
        id_sesion: int,
        usuario_accion: Optional[str] = None,
    ) -> bool:
        """
        Elimina una sesión por su ID.
        """
        id_validado = self._validar_id(
            id_sesion,
            "sesion",
        )

        try:
            resultado = (
                self.sesion_dao.eliminar_por_id(
                    id_validado
                )
            )

            self._registrar_log(
                usuario_accion
                or f"SESION_{id_validado}",
                "ELIMINACION_SESION",
            )

            return resultado

        except ValueError as error:
            raise ValueError(
                f"Error al eliminar la sesion: {error}"
            ) from error

        except Exception as error:
            raise RuntimeError(
                "Error inesperado al eliminar la sesion: "
                f"{error}"
            ) from error

    @staticmethod
    def _extraer_id(
        objeto: Any,
        *campos: str,
    ) -> Optional[int]:
        """
        Extrae un ID desde un entero, diccionario u objeto.
        """
        if isinstance(objeto, bool):
            return None

        if isinstance(objeto, int):
            return objeto

        if isinstance(objeto, dict):
            for campo in campos:
                if campo in objeto:
                    return (
                        ControlSesiones._convertir_id(
                            objeto[campo]
                        )
                    )

            return None

        for campo in campos:
            if hasattr(objeto, campo):
                return (
                    ControlSesiones._convertir_id(
                        getattr(objeto, campo)
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
        if valor is None or isinstance(valor, bool):
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
        if isinstance(valor, bool):
            raise ValueError(
                f"El ID de {nombre} debe ser un entero positivo."
            )

        if not isinstance(valor, int) or valor <= 0:
            raise ValueError(
                f"El ID de {nombre} debe ser un entero positivo."
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
        Convierte un texto o enum a Intensidad.
        """
        if isinstance(valor, Intensidad):
            return valor

        if not isinstance(valor, str):
            raise ValueError(
                "La intensidad debe ser BAJA, MEDIA o ALTA."
            )

        texto = valor.strip().upper()

        try:
            return Intensidad[texto]
        except KeyError:
            try:
                return Intensidad(texto)
            except ValueError as error:
                raise ValueError(
                    "Intensidad invalida. Debe ser "
                    "BAJA, MEDIA o ALTA."
                ) from error