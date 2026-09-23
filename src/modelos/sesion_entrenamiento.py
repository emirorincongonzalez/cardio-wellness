from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional, Union

from src.modelos.enums import Intensidad


class SesionEntrenamiento:
    """
    Representa una sesión de entrenamiento de un cliente.

    La sesión se considera completada automáticamente cuando
    las veces realizadas alcanzan las veces planificadas.
    """

    def __init__(
        self,
        fecha: date,
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
        completada: Optional[bool] = None,
        id_sesion: Optional[int] = None,
        id_cliente: Optional[int] = None,
        id_rutina: Optional[int] = None,
        nombre_ejercicio: str = "",
        veces_planificadas: int = 1,
        veces_realizadas: int = 0,
    ) -> None:
        self.id_sesion = id_sesion
        self.id_cliente = id_cliente
        self.id_rutina = id_rutina
        self.fecha = fecha
        self.nombre_ejercicio = nombre_ejercicio
        self.duracion_real = duracion_real
        self.intensidad_real = intensidad_real
        self.calorias_quemadas = calorias_quemadas
        self.observaciones = observaciones

        self.veces_planificadas = (
            veces_planificadas
        )

        self.veces_realizadas = (
            veces_realizadas
        )

        # Se conserva el parámetro por compatibilidad
        # con código antiguo, pero el estado real se
        # calcula mediante la propiedad completada.
        if completada is not None:
            if not isinstance(
                completada,
                bool,
            ):
                raise ValueError(
                    "Completada debe ser un booleano."
                )

            if completada != self.completada:
                raise ValueError(
                    (
                        "El valor de completada no coincide "
                        "con las veces realizadas y "
                        "planificadas."
                    )
                )

    @property
    def id_sesion(self) -> Optional[int]:
        return self._id_sesion

    @id_sesion.setter
    def id_sesion(
        self,
        valor: Optional[int],
    ) -> None:
        if valor is not None:
            if (
                isinstance(valor, bool)
                or not isinstance(valor, int)
                or valor <= 0
            ):
                raise ValueError(
                    (
                        "El ID de sesión debe ser "
                        "un entero positivo."
                    )
                )

        self._id_sesion = valor

    @property
    def id_cliente(self) -> Optional[int]:
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(
        self,
        valor: Optional[int],
    ) -> None:
        if valor is not None:
            if (
                isinstance(valor, bool)
                or not isinstance(valor, int)
                or valor <= 0
            ):
                raise ValueError(
                    (
                        "El ID de cliente debe ser "
                        "un entero positivo."
                    )
                )

        self._id_cliente = valor

    @property
    def id_rutina(self) -> Optional[int]:
        return self._id_rutina

    @id_rutina.setter
    def id_rutina(
        self,
        valor: Optional[int],
    ) -> None:
        """
        Puede ser None para sesiones antiguas.
        """
        if valor is not None:
            if (
                isinstance(valor, bool)
                or not isinstance(valor, int)
                or valor <= 0
            ):
                raise ValueError(
                    (
                        "El ID de rutina debe ser "
                        "un entero positivo."
                    )
                )

        self._id_rutina = valor

    @property
    def fecha(self) -> date:
        return self._fecha

    @fecha.setter
    def fecha(
        self,
        valor: date,
    ) -> None:
        if isinstance(valor, datetime):
            valor = valor.date()

        if not isinstance(valor, date):
            raise ValueError(
                "La fecha debe ser un objeto date."
            )

        self._fecha = valor

    @property
    def nombre_ejercicio(self) -> str:
        return self._nombre_ejercicio

    @nombre_ejercicio.setter
    def nombre_ejercicio(
        self,
        valor: str,
    ) -> None:
        if valor is None:
            self._nombre_ejercicio = ""
            return

        if not isinstance(valor, str):
            raise ValueError(
                (
                    "El nombre del ejercicio "
                    "debe ser texto."
                )
            )

        nombre = valor.strip()

        if len(nombre) > 100:
            raise ValueError(
                (
                    "El nombre del ejercicio no puede "
                    "superar 100 caracteres."
                )
            )

        self._nombre_ejercicio = nombre

    @property
    def duracion_real(self) -> int:
        return self._duracion_real

    @duracion_real.setter
    def duracion_real(
        self,
        valor: int,
    ) -> None:
        if isinstance(valor, bool):
            raise ValueError(
                "La duración debe ser un entero."
            )

        if not isinstance(valor, int):
            raise ValueError(
                "La duración debe ser un entero."
            )

        if valor <= 0:
            raise ValueError(
                "La duración debe ser mayor que cero."
            )

        self._duracion_real = valor

    @property
    def intensidad_real(self) -> Intensidad:
        return self._intensidad_real

    @intensidad_real.setter
    def intensidad_real(
        self,
        valor: Union[
            Intensidad,
            str,
        ],
    ) -> None:
        if isinstance(valor, Intensidad):
            self._intensidad_real = valor
            return

        if not isinstance(valor, str):
            raise ValueError(
                "La intensidad debe ser válida."
            )

        texto = valor.strip().upper()

        try:
            self._intensidad_real = (
                Intensidad[texto]
            )

        except KeyError:
            try:
                self._intensidad_real = (
                    Intensidad(texto)
                )

            except ValueError as error:
                raise ValueError(
                    (
                        "Intensidad inválida. Debe ser "
                        "BAJA, MEDIA o ALTA."
                    )
                ) from error

    @property
    def calorias_quemadas(self) -> Decimal:
        return self._calorias_quemadas

    @calorias_quemadas.setter
    def calorias_quemadas(
        self,
        valor: Union[
            int,
            float,
            Decimal,
        ],
    ) -> None:
        if isinstance(valor, bool):
            raise ValueError(
                "Las calorías deben ser numéricas."
            )

        try:
            calorias = Decimal(str(valor))

        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as error:
            raise ValueError(
                "Las calorías deben ser numéricas."
            ) from error

        if calorias < Decimal("0"):
            raise ValueError(
                "Las calorías no pueden ser negativas."
            )

        self._calorias_quemadas = calorias

    @property
    def observaciones(self) -> str:
        return self._observaciones

    @observaciones.setter
    def observaciones(
        self,
        valor: str,
    ) -> None:
        if valor is None:
            self._observaciones = ""
            return

        if not isinstance(valor, str):
            raise ValueError(
                "Las observaciones deben ser texto."
            )

        self._observaciones = valor.strip()

    @property
    def veces_planificadas(self) -> int:
        return self._veces_planificadas

    @veces_planificadas.setter
    def veces_planificadas(
        self,
        valor: int,
    ) -> None:
        if (
            isinstance(valor, bool)
            or not isinstance(valor, int)
            or valor <= 0
        ):
            raise ValueError(
                (
                    "Las veces planificadas deben ser "
                    "un entero mayor que cero."
                )
            )

        if hasattr(
            self,
            "_veces_realizadas",
        ):
            if valor < self._veces_realizadas:
                raise ValueError(
                    (
                        "Las veces planificadas no pueden "
                        "ser menores que las realizadas."
                    )
                )

        self._veces_planificadas = valor

    @property
    def veces_realizadas(self) -> int:
        return self._veces_realizadas

    @veces_realizadas.setter
    def veces_realizadas(
        self,
        valor: int,
    ) -> None:
        if (
            isinstance(valor, bool)
            or not isinstance(valor, int)
            or valor < 0
        ):
            raise ValueError(
                (
                    "Las veces realizadas deben ser "
                    "un entero igual o mayor que cero."
                )
            )

        if hasattr(
            self,
            "_veces_planificadas",
        ):
            if valor > self._veces_planificadas:
                raise ValueError(
                    (
                        "Las veces realizadas no pueden "
                        "superar las planificadas."
                    )
                )

        self._veces_realizadas = valor

    @property
    def completada(self) -> bool:
        """
        Calcula automáticamente el estado.
        """
        return (
            self.veces_realizadas
            >= self.veces_planificadas
        )

    @property
    def porcentaje_cumplimiento(self) -> float:
        """
        Devuelve el porcentaje de cumplimiento.
        """
        if self.veces_planificadas <= 0:
            return 0.0

        porcentaje = (
            self.veces_realizadas
            / self.veces_planificadas
            * 100
        )

        return round(
            min(porcentaje, 100.0),
            2,
        )

    def registrar_resultado(
        self,
        veces_realizadas: int,
    ) -> None:
        """
        Actualiza las veces realizadas.
        """
        self.veces_realizadas = (
            veces_realizadas
        )

    def marcar_como_completada(self) -> None:
        """
        Verifica que la sesión haya cumplido la meta.
        """
        if not self.completada:
            raise ValueError(
                (
                    "La sesión no puede marcarse como "
                    "completada: se realizaron "
                    f"{self.veces_realizadas} de "
                    f"{self.veces_planificadas} veces."
                )
            )

    def obtener_estado_cumplimiento(self) -> str:
        """
        Devuelve el estado de cumplimiento.
        """
        if self.completada:
            return "COMPLETADA"

        return "PENDIENTE"

    def obtener_resumen(self) -> str:
        """
        Devuelve un resumen legible.
        """
        rutina = (
            str(self.id_rutina)
            if self.id_rutina is not None
            else "Sin rutina"
        )

        ejercicio = (
            self.nombre_ejercicio
            or "Sin ejercicio"
        )

        return (
            f"Sesión {self.id_sesion} | "
            f"Cliente: {self.id_cliente} | "
            f"Rutina: {rutina} | "
            f"Ejercicio: {ejercicio} | "
            f"Fecha: {self.fecha} | "
            f"Duración: {self.duracion_real} min | "
            f"Intensidad: "
            f"{self.intensidad_real.value} | "
            f"Calorías: "
            f"{self.calorias_quemadas:.2f} | "
            f"Realizadas: "
            f"{self.veces_realizadas}/"
            f"{self.veces_planificadas} | "
            f"Cumplimiento: "
            f"{self.porcentaje_cumplimiento:.2f}% | "
            f"Estado: "
            f"{self.obtener_estado_cumplimiento()}"
        )

    def __repr__(self) -> str:
        return (
            "SesionEntrenamiento("
            f"id_sesion={self.id_sesion}, "
            f"id_cliente={self.id_cliente}, "
            f"id_rutina={self.id_rutina}, "
            f"fecha={self.fecha}, "
            "nombre_ejercicio="
            f"'{self.nombre_ejercicio}', "
            f"duracion_real={self.duracion_real}, "
            "intensidad_real="
            f"'{self.intensidad_real.value}', "
            f"calorias_quemadas="
            f"{self.calorias_quemadas}, "
            "veces_planificadas="
            f"{self.veces_planificadas}, "
            "veces_realizadas="
            f"{self.veces_realizadas}, "
            f"completada={self.completada}"
            ")"
        )