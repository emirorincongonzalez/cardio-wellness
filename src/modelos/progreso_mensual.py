from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional


class ProgresoMensual:
    """
    Representa el progreso mensual de un cliente.
    """

    def __init__(
        self,
        mes: date,
        peso: float,
        sesiones_completadas: int = 0,
        sesiones_planificadas: int = 12,
        porcentaje_cumplimiento: Optional[
            float
        ] = None,
        id_progreso: Optional[int] = None,
        id_cliente: Optional[int] = None,
    ) -> None:
        self.id_progreso = id_progreso
        self.id_cliente = id_cliente
        self.mes = mes
        self.peso = peso

        self.sesiones_planificadas = (
            sesiones_planificadas
        )

        self.sesiones_completadas = (
            sesiones_completadas
        )

        # El porcentaje se calcula a partir de las
        # sesiones para evitar inconsistencias.
        porcentaje_calculado = (
            self._calcular_porcentaje()
        )

        if porcentaje_cumplimiento is None:
            self._porcentaje_cumplimiento = (
                porcentaje_calculado
            )
        else:
            self.porcentaje_cumplimiento = (
                porcentaje_cumplimiento
            )

    @property
    def id_progreso(self) -> Optional[int]:
        return self._id_progreso

    @id_progreso.setter
    def id_progreso(
        self,
        valor: Optional[int],
    ) -> None:
        if valor is not None:
            if isinstance(valor, bool):
                raise ValueError(
                    "El ID de progreso debe ser entero."
                )

            if not isinstance(valor, int) or valor <= 0:
                raise ValueError(
                    "El ID de progreso debe ser positivo."
                )

        self._id_progreso = valor

    @property
    def id_cliente(self) -> Optional[int]:
        return self._id_cliente

    @id_cliente.setter
    def id_cliente(
        self,
        valor: Optional[int],
    ) -> None:
        if valor is not None:
            if isinstance(valor, bool):
                raise ValueError(
                    "El ID de cliente debe ser entero."
                )

            if not isinstance(valor, int) or valor <= 0:
                raise ValueError(
                    "El ID de cliente debe ser positivo."
                )

        self._id_cliente = valor

    @property
    def mes(self) -> date:
        return self._mes

    @mes.setter
    def mes(
        self,
        valor: date,
    ) -> None:
        if not isinstance(valor, date):
            raise ValueError(
                "El mes debe ser una fecha válida."
            )

        self._mes = valor.replace(day=1)

    @property
    def peso(self) -> Decimal:
        return self._peso

    @peso.setter
    def peso(
        self,
        valor,
    ) -> None:
        if isinstance(valor, bool):
            raise ValueError(
                "El peso debe ser numérico."
            )

        if not isinstance(
            valor,
            (int, float, Decimal),
        ):
            raise ValueError(
                "El peso debe ser numérico."
            )

        try:
            peso_decimal = Decimal(str(valor))
        except (
            InvalidOperation,
            ValueError,
        ) as error:
            raise ValueError(
                "El peso no tiene un formato válido."
            ) from error

        if peso_decimal <= Decimal("0"):
            raise ValueError(
                "El peso debe ser mayor que cero."
            )

        self._peso = peso_decimal

    @property
    def sesiones_completadas(self) -> int:
        return self._sesiones_completadas

    @sesiones_completadas.setter
    def sesiones_completadas(
        self,
        valor: int,
    ) -> None:
        if isinstance(valor, bool):
            raise ValueError(
                "Las sesiones completadas deben ser enteras."
            )

        if not isinstance(valor, int) or valor < 0:
            raise ValueError(
                "Las sesiones completadas no pueden "
                "ser negativas."
            )

        self._sesiones_completadas = valor

        if hasattr(
            self,
            "_sesiones_planificadas",
        ):
            self._actualizar_porcentaje()

    @property
    def sesiones_planificadas(self) -> int:
        return self._sesiones_planificadas

    @sesiones_planificadas.setter
    def sesiones_planificadas(
        self,
        valor: int,
    ) -> None:
        if isinstance(valor, bool):
            raise ValueError(
                "Las sesiones planificadas deben ser enteras."
            )

        if not isinstance(valor, int) or valor < 0:
            raise ValueError(
                "Las sesiones planificadas no pueden "
                "ser negativas."
            )

        self._sesiones_planificadas = valor

        if hasattr(
            self,
            "_sesiones_completadas",
        ):
            self._actualizar_porcentaje()

    @property
    def porcentaje_cumplimiento(self) -> float:
        return self._porcentaje_cumplimiento

    @porcentaje_cumplimiento.setter
    def porcentaje_cumplimiento(
        self,
        valor,
    ) -> None:
        if isinstance(valor, bool):
            raise ValueError(
                "El porcentaje debe ser numérico."
            )

        if not isinstance(
            valor,
            (int, float, Decimal),
        ):
            raise ValueError(
                "El porcentaje debe ser numérico."
            )

        try:
            porcentaje = Decimal(str(valor))
        except (
            InvalidOperation,
            ValueError,
        ) as error:
            raise ValueError(
                "El porcentaje no tiene un formato válido."
            ) from error

        if porcentaje < Decimal("0"):
            raise ValueError(
                "El porcentaje no puede ser negativo."
            )

        # Un cumplimiento superior al 100 % se limita a 100.
        if porcentaje > Decimal("100"):
            porcentaje = Decimal("100")

        self._porcentaje_cumplimiento = float(
            porcentaje.quantize(
                Decimal("0.01")
            )
        )

    def _calcular_porcentaje(self) -> float:
        """
        Calcula el porcentaje usando las sesiones actuales.
        """
        if self.sesiones_planificadas <= 0:
            return 0.0

        porcentaje = (
            Decimal(self.sesiones_completadas)
            / Decimal(self.sesiones_planificadas)
            * Decimal("100")
        )

        if porcentaje > Decimal("100"):
            porcentaje = Decimal("100")

        return float(
            porcentaje.quantize(
                Decimal("0.01")
            )
        )

    def _actualizar_porcentaje(self) -> None:
        """
        Actualiza automáticamente el cumplimiento.
        """
        self._porcentaje_cumplimiento = (
            self._calcular_porcentaje()
        )

    def calcular_cumplimiento(self) -> float:
        """
        Recalcula y devuelve el porcentaje.
        """
        self._actualizar_porcentaje()
        return self.porcentaje_cumplimiento

    def actualizar_progreso(self) -> None:
        """
        Recalcula el porcentaje de cumplimiento.
        """
        self._actualizar_porcentaje()

    def generar_resumen(self) -> str:
        """
        Devuelve un resumen legible del progreso.
        """
        return (
            f"Progreso {self.mes.strftime('%B %Y')} | "
            f"Peso: {self.peso:.1f} kg | "
            "Sesiones: "
            f"{self.sesiones_completadas}/"
            f"{self.sesiones_planificadas} | "
            "Cumplimiento: "
            f"{self.porcentaje_cumplimiento:.2f}%"
        )

    def __repr__(self) -> str:
        return (
            "ProgresoMensual("
            f"id_progreso={self.id_progreso}, "
            f"id_cliente={self.id_cliente}, "
            f"mes={self.mes}, "
            f"peso={self.peso}, "
            "sesiones_completadas="
            f"{self.sesiones_completadas}, "
            "sesiones_planificadas="
            f"{self.sesiones_planificadas}, "
            "porcentaje_cumplimiento="
            f"{self.porcentaje_cumplimiento}"
            ")"
        )