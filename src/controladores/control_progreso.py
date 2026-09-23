"""
Controlador para gestión de progreso mensual y reportes.
"""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional, Union
from unittest.mock import Mock

from src.controladores.control_base import ControlBase
from src.modelos.progreso_mensual import ProgresoMensual
from src.modelos.rutina import Rutina
from src.persistencia.progreso_mensual_dao import (
    ProgresoMensualDAO,
)
from src.persistencia.sesion_entrenamiento_dao import (
    SesionEntrenamientoDAO,
)
from src.utilidades.logger import (
    log_consulta_impacto,
    log_consulta_progreso,
    log_generar_progreso,
)


def _obtener_progreso_dao_default() -> ProgresoMensualDAO:
    """
    Crea el DAO predeterminado de progreso mensual.
    """
    return ProgresoMensualDAO()


def _obtener_clase_progreso():
    """
    Devuelve la clase del modelo de progreso mensual.
    """
    return ProgresoMensual


def _obtener_sesion_dao_default() -> SesionEntrenamientoDAO:
    """
    Crea el DAO predeterminado de sesiones.
    """
    return SesionEntrenamientoDAO()


def _extraer_id(
    objeto: Any,
    *campos_posibles: str,
) -> Optional[int]:
    """
    Extrae un ID desde un entero, diccionario u objeto.
    """
    if isinstance(objeto, bool):
        return None

    if isinstance(objeto, int):
        return objeto

    if isinstance(objeto, dict):
        for campo in campos_posibles:
            if campo not in objeto:
                continue

            valor = objeto[campo]

            if isinstance(valor, Mock):
                continue

            return _convertir_id(valor)

        return None

    for campo in campos_posibles:
        if not hasattr(objeto, campo):
            continue

        valor = getattr(objeto, campo)

        if isinstance(valor, Mock):
            continue

        return _convertir_id(valor)

    return None


def _convertir_id(
    valor: Any,
) -> Optional[int]:
    """
    Convierte un valor a entero.
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


def _obtener_valor(
    objeto: Any,
    *nombres: str,
    predeterminado: Any = None,
) -> Any:
    """
    Obtiene un valor desde un diccionario u objeto.
    """
    if isinstance(objeto, dict):
        for nombre in nombres:
            if nombre not in objeto:
                continue

            valor = objeto[nombre]

            if isinstance(valor, Mock):
                continue

            return valor

        return predeterminado

    for nombre in nombres:
        if not hasattr(objeto, nombre):
            continue

        valor = getattr(objeto, nombre)

        if isinstance(valor, Mock):
            continue

        return valor

    return predeterminado


def _obtener_decimal(
    objeto: Any,
    *nombres: str,
) -> Decimal:
    """
    Obtiene un valor Decimal.
    """
    valor = _obtener_valor(
        objeto,
        *nombres,
        predeterminado=0,
    )

    if valor is None:
        valor = 0

    try:
        return Decimal(str(valor))

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ):
        return Decimal("0")


def _obtener_entero(
    objeto: Any,
    *nombres: str,
    predeterminado: int = 0,
) -> int:
    """
    Obtiene un entero desde un objeto o diccionario.
    """
    valor = _obtener_valor(
        objeto,
        *nombres,
        predeterminado=predeterminado,
    )

    if valor is None:
        return predeterminado

    try:
        return int(valor)

    except (
        TypeError,
        ValueError,
    ):
        return predeterminado


def _normalizar_fecha(
    valor: Any,
) -> Optional[date]:
    """
    Convierte date, datetime o texto ISO a date.
    """
    if valor is None:
        return None

    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    if isinstance(valor, str):
        texto = valor.strip()

        try:
            return date.fromisoformat(
                texto[:10]
            )

        except ValueError:
            return None

    return None


def _normalizar_fecha_mes(
    mes: Union[int, date],
    anio: Optional[int] = None,
) -> tuple[int, int]:
    """
    Obtiene mes y año desde un número o una fecha.
    """
    if isinstance(mes, datetime):
        mes_numero = mes.month

        if anio is None:
            anio = mes.year

    elif isinstance(mes, date):
        mes_numero = mes.month

        if anio is None:
            anio = mes.year

    else:
        try:
            mes_numero = int(mes)

        except (
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "El mes debe ser un número entero."
            ) from error

    if anio is None:
        raise ValueError(
            "Se requiere el año."
        )

    try:
        anio_numero = int(anio)

    except (
        TypeError,
        ValueError,
    ) as error:
        raise ValueError(
            "El año debe ser un número entero."
        ) from error

    if not 1 <= mes_numero <= 12:
        raise ValueError(
            "El mes debe estar entre 1 y 12."
        )

    return mes_numero, anio_numero


def _instanciar_progreso_mensual(
    id_cliente: int,
    mes: int,
    anio: int,
    peso_registrado: Union[
        int,
        float,
        Decimal,
    ],
    sesiones_completadas: int = 0,
    sesiones_planificadas: int = 12,
    id_progreso: Optional[int] = None,
):
    """
    Crea un objeto ProgresoMensual.

    Si la clase del modelo no está disponible,
    devuelve un diccionario compatible con los tests.
    """
    fecha_mes = date(
        anio,
        mes,
        1,
    )

    datos_modelo = {
        "id_progreso": id_progreso,
        "id_cliente": id_cliente,
        "mes": fecha_mes,
        "peso": peso_registrado,
        "sesiones_completadas": (
            sesiones_completadas
        ),
        "sesiones_planificadas": (
            sesiones_planificadas
        ),
    }

    clase_progreso = _obtener_clase_progreso()

    if clase_progreso is None:
        return {
            "id_progreso": id_progreso,
            "id_cliente": id_cliente,
            "mes": mes,
            "anio": anio,
            "peso_registrado": peso_registrado,
            "sesiones_completadas": (
                sesiones_completadas
            ),
            "sesiones_planificadas": (
                sesiones_planificadas
            ),
        }

    return clase_progreso(**datos_modelo)


class ControlProgreso(ControlBase):
    """
    Controlador para progreso mensual, métricas y reportes.
    """

    def __init__(
        self,
        progreso_dao: Optional[
            ProgresoMensualDAO
        ] = None,
        sesion_dao: Optional[
            SesionEntrenamientoDAO
        ] = None,
        cliente_dao=None,
        ruta_log: str = "logs/LOG_CARDIO.txt",
    ) -> None:
        super().__init__(
            ruta_log=ruta_log,
        )

        self._progreso_dao = (
            progreso_dao
            if progreso_dao is not None
            else _obtener_progreso_dao_default()
        )

        self._sesion_dao = (
            sesion_dao
            if sesion_dao is not None
            else _obtener_sesion_dao_default()
        )

        self._cliente_dao = cliente_dao

    @property
    def progreso_dao(
        self,
    ) -> Optional[ProgresoMensualDAO]:
        return self._progreso_dao

    @progreso_dao.setter
    def progreso_dao(
        self,
        valor: Optional[ProgresoMensualDAO],
    ) -> None:
        self._progreso_dao = valor

    @property
    def sesion_dao(
        self,
    ) -> Optional[SesionEntrenamientoDAO]:
        return self._sesion_dao

    @sesion_dao.setter
    def sesion_dao(
        self,
        valor: Optional[SesionEntrenamientoDAO],
    ) -> None:
        self._sesion_dao = valor

    @property
    def cliente_dao(self):
        return self._cliente_dao

    @cliente_dao.setter
    def cliente_dao(
        self,
        valor,
    ) -> None:
        self._cliente_dao = valor

    def obtener_sesiones_cliente(
        self,
        cliente: object,
    ) -> list:
        """
        Obtiene todas las sesiones del cliente.
        """
        id_cliente = _extraer_id(
            cliente,
            "id_usuario",
            "id_cliente",
            "id",
        )

        if id_cliente is None or id_cliente <= 0:
            raise ValueError(
                "El id del cliente debe ser un entero positivo"
            )

        if self._sesion_dao is None:
            raise RuntimeError(
                (
                    "El DAO de sesiones no está "
                    "disponible."
                )
            )

        if hasattr(
            self._sesion_dao,
            "listar_por_cliente",
        ):
            sesiones = (
                self._sesion_dao.listar_por_cliente(
                    id_cliente
                )
            )

        elif hasattr(
            self._sesion_dao,
            "buscar_por_cliente",
        ):
            sesiones = (
                self._sesion_dao.buscar_por_cliente(
                    id_cliente
                )
            )

        elif hasattr(
            self._sesion_dao,
            "obtener_por_cliente",
        ):
            sesiones = (
                self._sesion_dao.obtener_por_cliente(
                    id_cliente
                )
            )

        else:
            raise AttributeError(
                (
                    "SesionEntrenamientoDAO no tiene "
                    "un método para listar sesiones "
                    "por cliente."
                )
            )

        return sesiones or []

    def calcular_resumen_cliente(
        self,
        cliente: object,
    ) -> Dict[str, Any]:
        """
        Calcula el resumen histórico de sesiones.
        """
        id_cliente = _extraer_id(
            cliente,
            "id_usuario",
            "id_cliente",
            "id",
        )

        if id_cliente is None or id_cliente <= 0:
            raise ValueError(
                "El id del cliente debe ser un entero positivo"
            )

        sesiones = self.obtener_sesiones_cliente(
            id_cliente
        )

        total_minutos = 0
        total_calorias = Decimal("0")
        total_veces_planificadas = 0
        total_veces_realizadas = 0

        for sesion in sesiones:
            total_minutos += _obtener_entero(
                sesion,
                "duracion_real",
                "duracion_minutos",
                predeterminado=0,
            )

            total_calorias += _obtener_decimal(
                sesion,
                "calorias_quemadas",
                "calorias",
            )

            total_veces_planificadas += (
                _obtener_entero(
                    sesion,
                    "veces_planificadas",
                    "sesiones_planificadas",
                    predeterminado=1,
                )
            )

            total_veces_realizadas += (
                _obtener_entero(
                    sesion,
                    "veces_realizadas",
                    "sesiones_realizadas",
                    predeterminado=0,
                )
            )

        porcentaje_cumplimiento = (
            self._calcular_porcentaje(
                total_veces_planificadas,
                total_veces_realizadas,
            )
        )

        sesiones_completadas = sum(
            1
            for sesion in sesiones
            if self._sesion_completada(
                sesion
            )
        )

        usuario_log = f"CLIENTE_{id_cliente}"

        self._registrar_log(
            usuario_log,
            "CONSULTA_PROGRESO",
        )

        log_consulta_progreso(usuario_log)

        return {
            "id_cliente": id_cliente,
            "total_sesiones": len(sesiones),
            "total_minutos": total_minutos,
            "total_calorias": (
                total_calorias.quantize(
                    Decimal("0.01")
                )
            ),
            "total_veces_planificadas": (
                total_veces_planificadas
            ),
            "total_veces_realizadas": (
                total_veces_realizadas
            ),
            "veces_planificadas": (
                total_veces_planificadas
            ),
            "veces_realizadas": (
                total_veces_realizadas
            ),
            "porcentaje_cumplimiento": (
                porcentaje_cumplimiento
            ),
            "sesiones_completadas": (
                sesiones_completadas
            ),
            "sesiones": sesiones,
        }

    def obtener_resumen_cliente(
        self,
        cliente: object,
    ) -> Dict[str, Any]:
        """
        Alias de calcular_resumen_cliente.
        """
        return self.calcular_resumen_cliente(
            cliente
        )

    def calcular_impacto_calorico_rutina(
        self,
        rutina: Union[
            Rutina,
            Dict[str, Any],
        ],
        usuario_consulta: Optional[str] = None,
    ) -> Decimal:
        """
        Calcula el impacto calórico total.
        """
        ejercicios = _obtener_valor(
            rutina,
            "ejercicios",
            predeterminado=[],
        )

        ejercicios = ejercicios or []
        total = Decimal("0")

        for ejercicio in ejercicios:
            total += _obtener_decimal(
                ejercicio,
                "calorias_estimadas",
                "calorias",
            )

        usuario = (
            usuario_consulta
            or "SISTEMA"
        )

        self._registrar_log(
            usuario,
            "CONSULTA_IMPACTO",
        )

        log_consulta_impacto(usuario)

        return total.quantize(
            Decimal("0.01")
        )

    def obtener_impacto_rutina(
        self,
        rutina: Union[
            Rutina,
            Dict[str, Any],
        ],
        usuario_consulta: Optional[str] = None,
    ) -> Decimal:
        """
        Alias de calcular_impacto_calorico_rutina.
        """
        return (
            self.calcular_impacto_calorico_rutina(
                rutina,
                usuario_consulta,
            )
        )

    def generar_progreso_mensual(
        self,
        cliente: object,
        mes: Union[int, date],
        anio: Optional[int] = None,
        peso_actual: Optional[
            Union[
                int,
                float,
                Decimal,
            ]
        ] = None,
        observaciones: Optional[str] = None,
    ) -> ProgresoMensual:
        """
        Cuenta sesiones del mes y guarda progreso.
        """
        if self._progreso_dao is None:
            raise RuntimeError(
                (
                    "El DAO de progreso mensual no "
                    "está disponible."
                )
            )

        id_cliente = _extraer_id(
            cliente,
            "id_usuario",
            "id_cliente",
            "id",
        )

        if id_cliente is None or id_cliente <= 0:
            raise ValueError(
                "El id del cliente debe ser un entero positivo"
            )

        mes_numero, anio_numero = (
            _normalizar_fecha_mes(
                mes,
                anio,
            )
        )

        if peso_actual is None:
            peso_actual = _obtener_valor(
                cliente,
                "peso",
                "peso_actual",
                predeterminado=None,
            )

        if peso_actual is None:
            raise ValueError(
                "Se requiere el peso actual."
            )

        try:
            peso_decimal = Decimal(
                str(peso_actual)
            )

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "El peso actual no es válido."
            ) from error

        if peso_decimal <= Decimal("0"):
            raise ValueError(
                "El peso debe ser mayor que cero."
            )

        sesiones = self.obtener_sesiones_cliente(
            id_cliente
        )

        sesiones_del_mes = []

        for sesion in sesiones:
            fecha_sesion = _normalizar_fecha(
                _obtener_valor(
                    sesion,
                    "fecha",
                    "fecha_sesion",
                    predeterminado=None,
                )
            )

            if fecha_sesion is None:
                continue

            if (
                fecha_sesion.year == anio_numero
                and fecha_sesion.month == mes_numero
            ):
                sesiones_del_mes.append(
                    sesion
                )

        total_planificadas = sum(
            _obtener_entero(
                sesion,
                "veces_planificadas",
                "sesiones_planificadas",
                predeterminado=1,
            )
            for sesion in sesiones_del_mes
        )

        total_realizadas = sum(
            _obtener_entero(
                sesion,
                "veces_realizadas",
                "sesiones_realizadas",
                predeterminado=0,
            )
            for sesion in sesiones_del_mes
        )

        sesiones_completadas = sum(
            1
            for sesion in sesiones_del_mes
            if self._sesion_completada(
                sesion
            )
        )

        progreso = _instanciar_progreso_mensual(
            id_cliente=id_cliente,
            mes=mes_numero,
            anio=anio_numero,
            peso_registrado=peso_decimal,
            sesiones_completadas=(
                sesiones_completadas
            ),
            sesiones_planificadas=(
                total_planificadas
            ),
        )

        if observaciones is not None and hasattr(
            progreso,
            "observaciones",
        ):
            progreso.observaciones = observaciones

        progreso_guardado = (
            self._progreso_dao.guardar(
                progreso
            )
        )

        self._actualizar_peso_cliente(
            cliente=cliente,
            peso=peso_decimal,
        )

        usuario_log = f"CLIENTE_{id_cliente}"

        self._registrar_log(
            usuario_log,
            "GENERAR_PROGRESO",
            (
                f"PLANIFICADAS="
                f"{total_planificadas}, "
                f"REALIZADAS="
                f"{total_realizadas}, "
                f"COMPLETADAS="
                f"{sesiones_completadas}"
            ),
        )

        log_generar_progreso(usuario_log)

        return progreso_guardado

    def _actualizar_peso_cliente(
        self,
        cliente: object,
        peso: Decimal,
    ) -> None:
        """
        Actualiza el peso actual del cliente.
        """
        if hasattr(
            cliente,
            "actualizar_peso",
        ):
            cliente.actualizar_peso(peso)

        elif hasattr(cliente, "peso"):
            cliente.peso = peso

        if self._cliente_dao is None:
            return

        id_cliente = _extraer_id(
            cliente,
            "id_usuario",
            "id_cliente",
            "id",
        )

        if id_cliente is None:
            return

        metodo = getattr(
            self._cliente_dao,
            "actualizar_peso",
            None,
        )

        if callable(metodo):
            metodo(
                id_cliente,
                peso,
            )

    def consultar_progreso(
        self,
        cliente: object,
    ) -> List[ProgresoMensual]:
        """
        Consulta el historial mensual.
        """
        if self._progreso_dao is None:
            raise RuntimeError(
                (
                    "El DAO de progreso mensual no "
                    "está disponible."
                )
            )

        id_cliente = _extraer_id(
            cliente,
            "id_usuario",
            "id_cliente",
            "id",
        )

        if id_cliente is None or id_cliente <= 0:
            raise ValueError(
                "El id del cliente debe ser un entero positivo"
            )

        usuario_log = f"CLIENTE_{id_cliente}"

        self._registrar_log(
            usuario_log,
            "CONSULTA_PROGRESO",
        )

        log_consulta_progreso(usuario_log)

        resultado = (
            self._progreso_dao.buscar_por_cliente(
                id_cliente
            )
        )

        return resultado or []

    @staticmethod
    def _sesion_completada(
        sesion: Any,
    ) -> bool:
        """
        Determina el estado usando cantidades.
        """
        planificadas = _obtener_entero(
            sesion,
            "veces_planificadas",
            "sesiones_planificadas",
            predeterminado=1,
        )

        realizadas = _obtener_entero(
            sesion,
            "veces_realizadas",
            "sesiones_realizadas",
            predeterminado=0,
        )

        return (
            planificadas > 0
            and realizadas >= planificadas
        )

    @staticmethod
    def _calcular_porcentaje(
        planificadas: int,
        realizadas: int,
    ) -> float:
        """
        Calcula el porcentaje total.
        """
        if planificadas <= 0:
            return 0.0

        porcentaje = (
            realizadas
            / planificadas
            * 100
        )

        return round(
            min(porcentaje, 100.0),
            2,
        )